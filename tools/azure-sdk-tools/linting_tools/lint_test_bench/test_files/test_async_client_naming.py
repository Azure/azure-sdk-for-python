# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Any
# This code violates async-client-bad-name
class AsyncSomeClient():
    def __init__(self, credential: str, *, api_version: str ="2018", **kwargs: Any) -> None:
        """
        :param credential: The credential to use for authentication.
        :type credential: str
        :keyword api_version: The API version to use for the client.
        :paramtype api_version: str
        :keyword eight: The eighth parameter.
        :paramtype eight: str
        """
        self.credential: str = credential
        self.eight: str = kwargs.get("eight")
        self._api_version: str = api_version

class _AsyncSomeClient():
    def __init__(self, credential: str, *, api_version: str ="2018", **kwargs: Any) -> None:
        """
        :param credential: The credential to use for authentication.
        :type credential: str
        :keyword api_version: The API version to use for the client.
        :paramtype api_version: str
        :keyword eight: The eighth parameter.
        :paramtype eight: str
        """
        self.credential: str = credential
        self.eight: str = kwargs.get("eight")
        self._api_version: str = api_version

class AsyncSomeClientBase():
    def __init__(self, credential: str, *, api_version: str ="2018", **kwargs: Any) -> None:
        """
        :param credential: The credential to use for authentication.
        :type credential: str
        :keyword api_version: The API version to use for the client.
        :paramtype api_version: str
        :keyword eight: The eighth parameter.
        :paramtype eight: str
        """
        self.credential: str = credential
        self.eight: str = kwargs.get("eight")
        self._api_version: str = api_version
