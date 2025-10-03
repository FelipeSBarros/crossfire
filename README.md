<div style="text-align: center">
<img src="https://raw.githubusercontent.com/voltdatalab/crossfire/master/crossfire_hexagono.png" width="130px" alt="hexagon crossfire"/>

# `crossfire` Python client
</div>

`crossfire` is a package created to give easier access to [Fogo Cruzado](https://fogocruzado.org.br/)'s datasets, which is a digital collaborative platform of gun shooting occurrences in the metropolitan areas of Rio de Janeiro and Recife.

The package facilitates data extraction from [Fogo Cruzado's open API](https://api.fogocruzado.org.br/).

## Requirements

* Python 3.9 or newer

## Install

```console
$ pip install crossfire
```

If you want to have access to the data as [Pandas `DataFrame`s](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html):

```console
$ pip install crossfire[df]
```

If you want to have access to the data as [GeoPandas `GeoDataFrame`s](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.html):

```console
$ pip install crossfire[geodf]
```

## Authentication

To have access to the API data, [registration is required](https://api.fogocruzado.org.br/sign-up).

The `email` and `password` used in the registration can be configured as `FOGOCRUZADO_EMAIL` and `FOGOCRUZADO_PASSWORD` environment variables in a `.env` file:

```env
FOGOCRUZADO_EMAIL=your@mail.com
FOGOCRUZADO_PASSWORD=YOUR_PASSWORD
```

If you prefer _not_ to use these environment variables, you can still use the credentials [when instantiating a client](#custom-client).

## Usage

### List of states covered by the project

Get all states with at least one city covered by the Fogo Cruzado project:

```python
from crossfire import states


states()
```

It is possible to get results in `DataFrame`:

```python
states(format='df')
```

### List of cities covered by the project

Get cities from a specific state covered by the Fogo Cruzado project.

```python
from crossfire import cities


cities()
```

It is possible to get results in `DataFrame`:

```python
cities(format='df')
```

#### `Cities` parameters

| Name        | Required | Description          | Type   | Default value | Example                                  |
|-------------|----------|----------------------|--------|---------------|------------------------------------------|
| `state_id`  | ❌        | ID of the state      | string | `None`        | `'b112ffbe-17b3-4ad0-8f2a-2038745d1d14'` |
| `city_id`   | ❌        | ID of the city       | string | `None`        | `'88959ad9-b2f5-4a33-a8ec-ceff5a572ca5'` |
| `city_name` | ❌        | Name of the city     | string | `None`        | `'Rio de Janeiro'`                       |
| `format`    | ❌        | Format of the result | string | `'dict'`      | `'dict'`, `'df'` or `'geodf'`            |


### Listing occurrences

To get shooting occurrences from Fogo Cruzado dataset it is necessary to specify a state id in `id_state` parameter:

```python
from crossfire import occurrences


occurrences('813ca36b-91e3-4a18-b408-60b27a1942ef')
```

It is possible to get results in `DataFrame`:

```python
occurrences('813ca36b-91e3-4a18-b408-60b27a1942ef', format='df')
```

Or as `GeoDataFrame`:

```python
occurrences('813ca36b-91e3-4a18-b408-60b27a1942ef', format='geodf')
```

#### `Occurrences` parameters

| Name                    | Required | Description                                    | Type                         | Default value | Example                                                                                                                        |
|-------------------------|----------|------------------------------------------------|------------------------------|---------------|--------------------------------------------------------------------------------------------------------------------------------|
| `id_state`              | ✅        | ID of the state                                | string                       | `None`        | `'b112ffbe-17b3-4ad0-8f2a-2038745d1d14'`                                                                                       |
| `id_cities`             | ❌        | ID of the city                                 | string or list of strings    | `None`        | `'88959ad9-b2f5-4a33-a8ec-ceff5a572ca5'` or `['88959ad9-b2f5-4a33-a8ec-ceff5a572ca5', '9d7b569c-ec84-4908-96ab-3706ec3bfc57']` |
| `type_occurrence`       | ❌        | Type of occurrence                             | string                       | `'all'`       | `'all'`, `'withVictim'` or `'withoutVictim'`                                                                                   |
| `initial_date`          | ❌        | Initial date of the occurrences                | string, `date` or `datetime` | `None`        | `'2020-01-01'`, `'2020/01/01'`, `'20200101'`, `datetime.datetime(2023, 1, 1)` or `datetime.date(2023, 1, 1)`                   | 
| `final_date`            | ❌        | Final date of the occurrences                  | string, `date` or `datetime` | `None`        | `'2020-01-01'`, `'2020/01/01'`, `'20200101'`, `datetime.datetime(2023, 1, 1)` or `datetime.date(2023, 1, 1)`                   |
| `max_parallel_requests` | ❌        | Maximum number of parallel requests to the API | int                          | `16`          | `32`                                                                                                                           |
| `format`                | ❌        | Format of the result                           | string                       | `'dict'`      | `'dict'`, `'df'` or `'geodf'`                                                                                                  |
| `flat`                  | ❌        | Return nested columns as separate columns      | bool                         | `False`       | `True` or `False`                                                                                                              |


##### About `flat` parameter

Occurrence data often contains nested information in several columns. By setting the parameter `flat=True`, you can simplify the analysis by separating nested data into individual columns. This feature is particularly useful for columns such as `contextInfo`, `state`, `region`, `city`, `neighborhood`, and `locality`.

For example, to access detailed information about the context of occurrences, such as identifying the main reason, you would typically need to access the `contextInfo` column and then look for the mainReason key. With the `flat=True` parameter, this nested information is automatically split into separate columns, making the data easier to work with.

When `flat=True` is set, the function returns occurrences with the flattened columns. Each new column retains the original column name as a prefix and the nested key as a suffix. For instance, the `contextInfo` column will be split into the following columns: `contextInfo_mainReason`, `contextInfo_complementaryReasons`, `contextInfo_clippings`, `contextInfo_massacre`, and `contextInfo_policeUnit`.


###### Example

```python
from crossfire import occurrences
from crossfire.clients.occurrences import flatten

occs = occurrences('813ca36b-91e3-4a18-b408-60b27a1942ef')
occs[0].keys()
# dict_keys(['id', 'documentNumber', 'address', 'state', 'region', 'city', 'neighborhood', 'subNeighborhood', 'locality', 'latitude', 'longitude', 'date', 'policeAction', 'agentPresence', 'relatedRecord', 'contextInfo', 'transports', 'victims', 'animalVictims'])
flattened_occs = occurrences('813ca36b-91e3-4a18-b408-60b27a1942ef', flat=True)
occs[0].keys()
# dict_keys(['id', 'documentNumber', 'address', 'state', 'region', 'city', 'neighborhood', 'subNeighborhood', 'locality', 'latitude', 'longitude', 'date', 'policeAction', 'agentPresence', 'relatedRecord', 'transports', 'victims', 'animalVictims', 'contextInfo', 'contextInfo_mainReason', 'contextInfo_complementaryReasons', 'contextInfo_clippings', 'contextInfo_massacre', 'contextInfo_policeUnit'])
```

By using the `flat=True parameter`, you ensure that all nested data is expanded into individual columns, simplifying data analysis and making it more straightforward to access specific details within your occurrence data.

### Custom client

If not using the environment variables for authentication, it is recommended to use a custom client:

```python
from crossfire import Client


client = Client(email="fogo@cruza.do", password="Rio&Pernambuco") # credentials are optional, the default are the environment variables
client.states()
client.cities()
client.occurrences('813ca36b-91e3-4a18-b408-60b27a1942ef')
```

### Asynchronous use with `asyncio`

```python
from crossfire import AsyncClient


client = AsyncClient()  # credentials are optional, the default are the environment variables
await client.states()
await client.cities()
await client.occurrences('813ca36b-91e3-4a18-b408-60b27a1942ef')
```

## Credits

[@FelipeSBarros](https://github.com/FelipeSBarros) is the creator of the Python package. This implementation was funded by CYTED project number `520RT0010 redGeoLIBERO`.

### Contributors

* [@sergiospagnuolo](https://github.com/sergiospagnuolo)
* [@silvadenisson](https://github.com/silvadenisson)
* [@cuducos](https://github.com/cuducos)
