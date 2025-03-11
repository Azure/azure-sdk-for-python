from typing import Any

class SomeClient:
    def __init__(self, credential: str, *, api_version: str = "2018", **kwargs: Any) -> None:
        """
        :param credential: The credential to use for authentication.
        :param api_version: The API version to use for the client.
        :keyword one: The first parameter.
        """
        self.credential = credential
        self._api_version = api_version
        self.one = kwargs.get("one")

    def _private_method(self) -> None:
        pass

    @staticmethod
    def create_configuration() -> None:
        pass

class SomethingElse:
    @staticmethod
    def download_thing(some: str) -> None:
        some = str(int(some) + 1)
