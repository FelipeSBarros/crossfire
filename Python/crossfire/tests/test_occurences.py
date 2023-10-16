from unittest.mock import Mock

from crossfire.occurrences import Occurrences


def dummy_response(last_page=False):
    return [
        {
            "id": "a7bfebed-ce9c-469d-a656-924ed8248e95",
            "latitude": "-8.1576367000",
            "longitude": "-34.9696372000",
        },
        {
            "id": "a14d18dd-b28f-4c30-af07-5fa40d88b3f7",
            "latitude": "-7.9800434000",
            "longitude": "-35.0553350000",
        },
    ], not last_page


def test_occurrences_from_at_least_two_pages():
    client = Mock()
    client.get.return_value = dummy_response()
    occurrences = tuple(Occurrences(client, id_state="42", limit=3))

    assert client.get.call_count == 2
    assert len(occurrences) == 3


def test_occurrences_stops_when_there_are_no_more_pages():
    client = Mock()
    client.get.side_effect = (
        dummy_response(False),
        dummy_response(True),
    )
    occurrences = tuple(occurence for occurence in Occurrences(client, id_state="42"))
    assert client.get.call_count == 2
    assert len(occurrences) == 4


def test_occurances_with_limit():
    client = Mock()
    client.get.return_value = dummy_response()
    occurences = tuple(Occurrences(client, id_state="42", limit=42))
    assert len(occurences) == 42


def test_occurrences_with_obligtory_parameters():
    client = Mock()
    client.get.return_value = dummy_response()
    client.URL = "https://127.0.0.1/"
    tuple(Occurrences(client, id_state="42", limit=1))
    client.get.assert_called_once_with(f"{client.URL}/occurrences?idState=42&page=1")


def test_occurrences_with_obligtory_and_id_cities_parameters():
    client = Mock()
    client.get.return_value = dummy_response()
    client.URL = "https://127.0.0.1/"
    tuple(Occurrences(client, id_state="42", id_cities="21", limit=1))
    client.get.assert_called_once_with(
        f"{client.URL}/occurrences?idState=42&idCities=21&page=1"
    )


def test_occurrences_with_obligtory_and_two_id_cities_parameters():
    client = Mock()
    client.get.return_value = dummy_response(True)
    client.URL = "https://127.0.0.1/"
    tuple(
        occurence
        for occurence in Occurrences(
            client, id_state="42", id_cities=["21", "11"], limit=1
        )
    )
    client.get.assert_called_once_with(
        f"{client.URL}/occurrences?idState=42&idCities=21&idCities=11&page=1"
    )


def test_occurrence_url_with_only_mandatory_params():
    client = Mock()
    client.URL = "https://127.0.0.1"
    occurence = Occurrences(client, id_state=42)
    assert occurence.url == "https://127.0.0.1/occurrences?idState=42"


def test_occurrence_url_with_one_city():
    client = Mock()
    client.URL = "https://127.0.0.1"
    occurence = Occurrences(client, id_state=42, id_cities="fourty-two")
    assert (
        occurence.url == "https://127.0.0.1/occurrences?idState=42&idCities=fourty-two"
    )


def test_occurrence_url_with_two_cities():
    client = Mock()
    client.URL = "https://127.0.0.1"
    occurence = Occurrences(client, id_state=42, id_cities=["fourty-two", 42])
    assert (
        occurence.url
        == "https://127.0.0.1/occurrences?idState=42&idCities=fourty-two&idCities=42"
    )
