from queue import Empty, Queue
from urllib.parse import urlencode


class Occurrences:
    def __init__(self, client, id_state, id_cities=None, format=None):
        self.client = client
        self.id_state = id_state
        self.id_cities = id_cities
        self.format = format

        self.buffer = Queue()
        self.next_page = 1

        self.params = {
            "idState": self.id_state,
            "idCities": self.id_cities,
        }

    def __iter__(self):
        return self

    def __next__(self):
        if self.buffer.empty():
            if not self.next_page:
                raise StopIteration
            self.load_occurrences()

        try:
            occurrence = self.buffer.get_nowait()
        except Empty:
            raise StopIteration

        return occurrence

    def load_occurrences(self):
        if not self.next_page:
            return

        self.params.update({"page": self.next_page})
        cleaned_params = urlencode(
            {key: value for key, value in self.params.items() if value}
        )
        occurrences, has_next_page = self.client.get(
            f"{self.client.URL}/occurrences?{cleaned_params}"
        )

        for occurrence in occurrences:
            self.buffer.put(occurrence)

        if has_next_page:
            self.next_page += 1
        else:
            self.next_page = None
