# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Any, List
from azure.core.tracing.decorator import distributed_trace

class ClientClass():
    def __init__(self, credential: str, *, api_version: str = "2018", **kwargs: Any) -> None:
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

class ClassNameGoodClient:
    @distributed_trace
    def get_function_name_long(self, **kwargs: Any) -> str:
        seven = kwargs.get("seven")
        return seven

    @distributed_trace
    def get_function_good(self, **kwargs: Any) -> List:
        result_list = []
        six = kwargs.get("six")
        six = six + ""
        return result_list

    def _private_function(self, **kwargs) -> str:
        result_list = []
        five = kwargs.get("five")
        five = five + ""
        return result_list

    def __init__(self, credential: str, name_long: str, *, api_version: str = "2018", **kwargs: Any) -> None:
        """
        :param credential: The credential to use for authentication.
        :type credential: str
        :param name_long: The first parameter.
        :paramtype name_long: str
        :keyword api_version: The API version to use for the client.
        :paramtype api_version: str
        :keyword four: The fourth parameter.
        :paramtype four: str
        """
        self.credential: str = credential
        self.name_long: str = name_long
        self._api_version: str = api_version
        self.four: str = kwargs.get("four")

    NAME_LONG_CONSTANT = 10
