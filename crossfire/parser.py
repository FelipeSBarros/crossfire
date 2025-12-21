from dataclasses import dataclass
from re import compile

try:
    from pandas import DataFrame

    HAS_PANDAS = True
except ModuleNotFoundError:
    HAS_PANDAS = False

try:
    from geopandas import GeoDataFrame, points_from_xy

    HAS_GEOPANDAS = True
except ModuleNotFoundError:
    HAS_GEOPANDAS = False


from crossfire.errors import CrossfireError
from crossfire.logger import Logger

FORMATS = {"df", "dict", "geodf"}
CRS = "EPSG:4326"

logger = Logger(__name__)


class UnknownFormatError(CrossfireError):
    def __init__(self, format):
        message = f"Unknown format `{format}`. Valid formats are: {', '.join(FORMATS)}"
        super().__init__(message)


class IncompatibleDataError(CrossfireError):
    pass


def to_geo_dataframe(df):
    if not {"latitude", "longitude"}.issubset(df.columns):
        raise IncompatibleDataError(
            "Missing columns `latitude` and `longitude`. "
            "They are needed to create a GeoDataFrame."
        )

    geometry = points_from_xy(df.longitude, df.latitude)
    return GeoDataFrame(df, geometry=geometry, crs=CRS)


@dataclass
class Metadata:
    page: int
    take: int
    item_count: int
    page_count: int
    has_previous_page: bool
    has_next_page: bool
    last_update: str = None
    last_update_timestamp: int = None
    last_update_state_id: str = None
    last_update_state: str = None
    last_update_state_timestamp: int = None

    SNAKE_CASE_REGEX = compile("([A-Z])")

    @classmethod
    def to_snake_case(cls, name):
        return cls.SNAKE_CASE_REGEX.sub(r"_\1", name).lower()

    @classmethod
    def from_response(cls, response, headers=None):
        kwargs = {
            cls.to_snake_case(key): value
            for key, value in response.get("pageMeta", {}).items()
        }
        
        if headers:
            if "X-Last-Update" in headers:
                kwargs["last_update"] = headers["X-Last-Update"]
            
            if "X-Last-Update-Timestamp" in headers:
                try:
                    kwargs["last_update_timestamp"] = int(headers["X-Last-Update-Timestamp"])
                except (ValueError, TypeError):
                    kwargs["last_update_timestamp"] = None
            
            if "X-Last-Update-State-Id" in headers:
                kwargs["last_update_state_id"] = headers["X-Last-Update-State-Id"]
            
            if "X-Last-Update-State" in headers:
                kwargs["last_update_state"] = headers["X-Last-Update-State"]
            
            if "X-Last-Update-State-Timestamp" in headers:
                try:
                    kwargs["last_update_state_timestamp"] = int(headers["X-Last-Update-State-Timestamp"])
                except (ValueError, TypeError):
                    kwargs["last_update_state_timestamp"] = None
        
        for key in cls.__dataclass_fields__.keys() - kwargs.keys():
            kwargs[key] = None
        return cls(**kwargs)


def parse_response(response, format=None):
    """Converts API response to a dictionary, Pandas DataFrame or GeoDataFrame."""
    if format and format not in FORMATS:
        raise UnknownFormatError(format)

    try:
        contents = response.json()
    except:
        logger.error(
            "Failed to decode response as JSON (HTTP Status "
            f"{response.status_code} {response.url} {response.headers}): {response.text}"
        )
        raise

    metadata = Metadata.from_response(contents, headers=response.headers)
    data = contents.get("data", [])

    if HAS_GEOPANDAS and format == "geodf":
        return to_geo_dataframe(DataFrame(data)), metadata

    if HAS_PANDAS and format == "df":
        return DataFrame(data), metadata

    return data, metadata
