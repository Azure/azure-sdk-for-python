# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Any, List
from azure.core.tracing.decorator import distributed_trace
# This code violates name-too-long
class ThisClassNameShouldEndUpBeingTooLongForAClient():
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
    def get_function_name_should_be_too_long_for_rule(self, **kwargs: Any) -> str:
        seven = kwargs.get("seven")
        return seven

    @distributed_trace
    def get_function_good(self, **kwargs: Any) -> List:
        this_lists_name_is_too_long_to_work_with_linter_rule = []
        six = kwargs.get("six")
        six = six + ""
        return this_lists_name_is_too_long_to_work_with_linter_rule

    def _this_function_is_private_but_over_length_reqs(self, **kwargs) -> str:
        this_lists_name = []
        five = kwargs.get("five")
        five = five + ""
        return this_lists_name

    def __init__(self,
                 credential:str,
                 this_name_is_too_long_to_use_anymore_reqs: str,
                 *, api_version: str ="2018", **kwargs: Any) -> None:
        """
        :param credential: The credential to use for authentication.
        :type credential: str
        :param this_name_is_too_long_to_use_anymore_reqs: The first parameter.
        :paramtype this_name_is_too_long_to_use_anymore_reqs: str
        :keyword api_version: The API version to use for the client.
        :paramtype api_version: str
        :keyword four: The fourth parameter.
        :paramtype four: str
        """
        self.credential: str = credential
        self.this_name_is_too_long_to_use_anymore_reqs: str = this_name_is_too_long_to_use_anymore_reqs
        self._api_version: str = api_version
        self.four: str = kwargs.get("four")

    THIS_NAME_IS_TOO_LONG_TO_USE_ANYMORE_REQS = 10
