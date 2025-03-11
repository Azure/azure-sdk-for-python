# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Any

class SomeClient:
    def __init__(self, credential: str, *, api_version: str = "2018", **kwargs: Any) -> None:
        """
        :param credential: The credential to use for authentication.
        :type credential: str
        :keyword api_version: The API version to use for the client.
        :paramtype api_version: str
        :keyword one: The first parameter.
        :paramtype one: str
        """
        self.credential: str = credential
        self._api_version: str = api_version
        self.one: str = kwargs.get("one")

    def _private_method(self) -> None:
        pass

    def create_configuration2(self) -> None:
        pass

class SomethingElse:
    @staticmethod
    def download_thing(some: str) -> None:
        some = some + "1"  # Assuming the intention is to concatenate a string.
