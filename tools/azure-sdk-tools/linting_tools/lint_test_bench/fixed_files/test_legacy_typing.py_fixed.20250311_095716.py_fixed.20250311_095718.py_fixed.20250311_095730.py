from typing import Any, MutableMapping

class ClassNameClient:
    def __init__(self, credential: str, *, api_version: str = "2018", **kwargs: MutableMapping[str, Any]) -> None:
        """
        :param credential: The credential to use for authentication.
        :type credential: str
        :keyword api_version: The API version to use for the client.
        :paramtype api_version: str
        :keyword eight: The eighth parameter.
        :paramtype eight: str
        """
        self.credential: str = credential
        self.api_version: str = api_version
        self.eight: str = kwargs.get("eight")
