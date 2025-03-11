from typing import Any


class AsyncSomeClient:
    credential: str
    eight: str
    _api_version: str

    def __init__(self, credential: str, *, api_version: str = "2018", **kwargs: Any) -> None:
        """
        :param credential: The credential to use for authentication.
        :type credential: str
        :keyword api_version: The API version to use for the client.
        :paramtype api_version: str
        :keyword eight: The eighth parameter.
        :paramtype eight: str
        """
        self.credential = credential
        self.eight = kwargs.get("eight")
        self._api_version = api_version


class _AsyncSomeClient:
    credential: str
    eight: str
    _api_version: str

    def __init__(self, credential: str, *, api_version: str = "2018", **kwargs: Any) -> None:
        """
        :param credential: The credential to use for authentication.
        :type credential: str
        :keyword api_version: The API version to use for the client.
        :paramtype api_version: str
        :keyword eight: The eighth parameter.
        :paramtype eight: str
        """
        self.credential = credential
        self.eight = kwargs.get("eight")
        self._api_version = api_version


class AsyncSomeClientBase:
    credential: str
    eight: str
    _api_version: str

    def __init__(self, credential: str, *, api_version: str = "2018", **kwargs: Any) -> None:
        """
        :param credential: The credential to use for authentication.
        :type credential: str
        :keyword api_version: The API version to use for the client.
        :paramtype api_version: str
        :keyword eight: The eighth parameter.
        :paramtype eight: str
        """
        self.credential = credential
        self.eight = kwargs.get("eight")
        self._api_version = api_version
