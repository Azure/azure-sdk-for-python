# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Any, List
from azure.core.tracing.decorator import distributed_trace

class LongClientName():
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


class GoodClient():
    @distributed_trace
    def get_function_with_long_name_for_rule(self, **kwargs: Any) -> str:
        seven = kwargs.get("seven")
        return seven

    @distributed_trace
    def get_function_good(self, **kwargs: Any) -> List:
        long_list_name = []
        six = kwargs.get("six")
        six = six + ""
        return long_list_name

    def _private_function_over_length(self, **kwargs) -> str:
        short_list_name = []
        five = kwargs.get("five")
        five = five + ""
        return short_list_name

    def __init__(self,
                 credential:str,
                 short_param_name: str,
                 *, api_version: str ="2018", **kwargs: Any) -> None:
        """
        :param credential: The credential to use for authentication.
        :type credential: str
        :param short_param_name: The first parameter.
        :paramtype short_param_name: str
        :keyword api_version: The API version to use for the client.
        :paramtype api_version: str
        :keyword four: The fourth parameter.
        :paramtype four: str
        """
        self.credential: str = credential
        self.short_param_name: str = short_param_name
        self._api_version: str = api_version
        self.four: str = kwargs.get("four")

    NAME_REQ_CONST = 10
