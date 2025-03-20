# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Any, List
from azure.core.tracing.decorator import distributed_trace

class ClientLongName():
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


class ClassNameClient():
    @distributed_trace
    def long_function(self, **kwargs: Any) -> str:
        seven = kwargs.get("seven")
        return seven

    @distributed_trace
    def get_function(self, **kwargs: Any) -> List:
        result_list = []
        six = kwargs.get("six")
        six = six + ""
        return result_list

    def _private_function(self, **kwargs) -> str:
        result_list = []
        five = kwargs.get("five")
        five = five + ""
        return result_list

    def __init__(self,
                 credential:str,
                 param_name: str,
                 *, api_version: str ="2018", **kwargs: Any) -> None:
        """
        :param credential: The credential to use for authentication.
        :type credential: str
        :param param_name: The first parameter.
        :paramtype param_name: str
        :keyword api_version: The API version to use for the client.
        :paramtype api_version: str
        :keyword four: The fourth parameter.
        :paramtype four: str
        """
        self.credential: str = credential
        self.param_name: str = param_name
        self._api_version: str = api_version
        self.four: str = kwargs.get("four")

    CONSTANT = 10
