# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Any, List
from azure.core.tracing.decorator import distributed_trace

class Client:
    def __init__(self, credential: str, *, api_version: str = "2018", **kwargs: Any) -> None:
        """
        :param credential: The credential to use for authentication.
        :type credential: str
        :keyword api_version: The API version to use for the client.
        :paramtype api_version: str
        :keyword eighth: The eighth parameter.
        :paramtype eighth: str
        """
        self.credential: str = credential
        self.eighth: str = kwargs.get("eighth")
        self._api_version: str = api_version


class GoodClient:
    @distributed_trace
    def get_long_function_name(self, **kwargs: Any) -> str:
        seven = kwargs.get("seven")
        return seven

    @distributed_trace
    def get_function(self, **kwargs: Any) -> List:
        items_list = []
        six = kwargs.get("six")
        six = six + ""
        return items_list

    def _private_function(self, **kwargs) -> str:
        items_list = []
        five = kwargs.get("five")
        five = five + ""
        return items_list

    def __init__(self,
                 credential: str,
                 req_name: str,
                 *, api_version: str = "2018", **kwargs: Any) -> None:
        """
        :param credential: The credential to use for authentication.
        :type credential: str
        :param req_name: The first parameter.
        :paramtype req_name: str
        :keyword api_version: The API version to use for the client.
        :paramtype api_version: str
        :keyword four: The fourth parameter.
        :paramtype four: str
        """
        self.credential: str = credential
        self.req_name: str = req_name
        self._api_version: str = api_version
        self.four: str = kwargs.get("four")

    CONSTANT_VALUE = 10
