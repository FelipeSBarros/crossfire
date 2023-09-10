from datetime import date
from unittest import TestCase
from unittest.mock import patch

import numpy
from crossfire.fogocruzado_utils import extract_data_api, extract_cities_api
from crossfire.get_cities import get_cities
from crossfire.client import Client
from crossfire.load_data import InvalidDateIntervalError, get_fogocruzado
from geopandas import GeoDataFrame
from pandas import DataFrame


def fake_api_row(**extra_fields):
    row = {
        "latitude_ocorrencia": 42.0,
        "longitude_ocorrencia": 4.2,
        "densidade_demo_cidade": 42,
        "uf_estado": "RJ",
        "nome_cidade": "Rio de Janeiro",
        "presen_agen_segur_ocorrencia": 1,
    }
    if extra_fields:
        row.update(extra_fields)
    return row


def fake_api_data(*rows):
    return DataFrame(rows or [fake_api_row()])


class TestExtractDataAPI(TestCase):
    def test_extract_data_api(self):
        with patch.object(Client, "get") as mock:
            mock.return_value.content = b"[]"
            data = extract_data_api(
                link="https://api.fogocruzado.org.br/api/v1/occurrences?data_ocorrencia[gt]=2020-01-01&data_ocorrencia[lt]=2020-02-01"
            )
        self.assertIsInstance(data, DataFrame)


class TestExtractCitiesAPI(TestCase):
    def test_extract_cities_api(self):
        with patch.object(Client, "get") as mock:
            mock.return_value.content = b"[]"
            data = extract_cities_api()
        self.assertIsInstance(data, DataFrame)


class TestGetCitiesAPI(TestCase):
    def test_extract_cities_api(self):
        with patch.object(Client, "get") as mock:
            mock.return_value.json.return_value = [{"DensidadeDemografica": 42.0}]
            cities = get_cities()

        self.assertIsInstance(cities, DataFrame)
        self.assertIsInstance(cities.DensidadeDemografica[0], numpy.float64)


class TestGetFogoCruzado(TestCase):
    def test_sucessful_get_fogocruzado(self):
        with patch("crossfire.load_data.extract_data_api") as mock:
            mock.return_value = fake_api_data()
            sucessful_get_fogocruzado = get_fogocruzado()
        self.assertIsInstance(sucessful_get_fogocruzado, GeoDataFrame)

    def test_unsucessful_get_fogocruzado(self):
        with self.assertRaises(InvalidDateIntervalError):
            self.sucessful_get_fogocruzado = get_fogocruzado(
                initial_date=date(2020, 1, 1), final_date=date(2021, 10, 1)
            )


class TestFilterCityFogoCruzado(TestCase):
    def test_sucessful_filter_city_from_string(self):
        with patch("crossfire.load_data.extract_data_api") as mock:
            mock.return_value = fake_api_data(
                fake_api_row(nome_cidade="Rio de Janeiro"),
                fake_api_row(nome_cidade="Niterói"),
            )
            sucessful_get_fogocruzado = get_fogocruzado(city="Rio de Janeiro")
            self.assertEqual(
                sucessful_get_fogocruzado.nome_cidade.unique(), ["Rio de Janeiro"]
            )

    def test_sucessful_filter_city_from_list(self):
        with patch("crossfire.load_data.extract_data_api") as mock:
            mock.return_value = fake_api_data(
                fake_api_row(nome_cidade="Rio de Janeiro"),
                fake_api_row(nome_cidade="Niterói"),
                fake_api_row(nome_cidade="Belford Roxo"),
            )
            sucessful_get_fogocruzado = get_fogocruzado(
                city=["Rio de Janeiro", "Belford Roxo"]
            )
        self.assertEqual(
            list(sucessful_get_fogocruzado.nome_cidade.unique()),
            ["Rio de Janeiro", "Belford Roxo"],
        )

    def test_sucessful_filter_state_from_string(self):
        with patch("crossfire.load_data.extract_data_api") as mock:
            mock.return_value = fake_api_data(
                fake_api_row(uf_estado="RJ"),
                fake_api_row(uf_estado="PE"),
            )
            sucessful_get_fogocruzado = get_fogocruzado(state="RJ")
            self.assertEqual(sucessful_get_fogocruzado.uf_estado.unique(), ["RJ"])

    def test_sucessful_filter_state_from_list(self):
        with patch("crossfire.load_data.extract_data_api") as mock:
            mock.return_value = fake_api_data(
                fake_api_row(uf_estado="RJ"),
                fake_api_row(uf_estado="ES"),
                fake_api_row(uf_estado="PE"),
            )
            sucessful_get_fogocruzado = get_fogocruzado(state=["RJ", "PE"])
            self.assertEqual(
                list(sucessful_get_fogocruzado.uf_estado.unique()), ["RJ", "PE"]
            )

    def test_sucessful_filter_security_agent_from_string(self):
        with patch("crossfire.load_data.extract_data_api") as mock:
            mock.return_value = fake_api_data(
                fake_api_row(presen_agen_segur_ocorrencia=1),
                fake_api_row(presen_agen_segur_ocorrencia=0),
            )
            sucessful_get_fogocruzado = get_fogocruzado(security_agent=1)
            self.assertEqual(
                sucessful_get_fogocruzado.presen_agen_segur_ocorrencia.unique(), [1]
            )

    def test_sucessful_filter_security_agent_from_list(self):
        with patch("crossfire.load_data.extract_data_api") as mock:
            mock.return_value = fake_api_data(
                fake_api_row(presen_agen_segur_ocorrencia=2),
                fake_api_row(presen_agen_segur_ocorrencia=0),
                fake_api_row(presen_agen_segur_ocorrencia=1),
            )
            sucessful_get_fogocruzado = get_fogocruzado(security_agent=[0, 1])
            self.assertEqual(
                list(sucessful_get_fogocruzado.presen_agen_segur_ocorrencia.unique()),
                [0, 1],
            )