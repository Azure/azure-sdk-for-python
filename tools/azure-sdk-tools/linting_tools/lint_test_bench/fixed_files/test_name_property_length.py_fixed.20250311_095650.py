# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Any, List
from azure.core.tracing.decorator import distributed_trace

class ClientClassName():
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


class ClassNameGoodClient():
    @distributed_trace
    def get_function_name(self, **kwargs: Any) -> str:
        seven = kwargs.get("seven")
        return seven

    @distributed_trace
    def get_function_good(self, **kwargs: Any) -> List:
        list_with_short_name = []
        six = kwargs.get("six")
        six = six + ""
        return list_with_short_name

    def _private_func(self, **kwargs: Any) -> str:
        list_name = []
        five = kwargs.get("five")
        five = five + ""
        return list_name

    def __init__(self,
                 credential:str,
                 name_needed: str,
                 *, api_version: str ="2018", **kwargs: Any) -> None:
        """
        :param credential: The credential to use for authentication.
        :type credential: str
        :param name_needed: The first parameter.
        :paramtype name_needed: str
        :keyword api_version: The API version to use for the client.
        :paramtype api_version: str
        :keyword four: The fourth parameter.
        :paramtype four: str
        """
        self.credential: str = credential
        self.name_needed: str = name_needed
        self._api_version: str = api_version
        self.four: str = kwargs.get("four")

    NAME_NEEDED = 10
