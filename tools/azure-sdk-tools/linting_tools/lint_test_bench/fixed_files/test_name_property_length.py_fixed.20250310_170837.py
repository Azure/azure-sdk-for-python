from typing import Any, List
from azure.core.tracing.decorator import distributed_trace

# This code violates name-too-long
class TooLongClientClassName:
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


class GoodClientClassName:
    @distributed_trace
    def function_name_too_long_for_rule(self, **kwargs: Any) -> str:
        seven = kwargs.get("seven")
        return seven

    @distributed_trace
    def get_function_good(self, **kwargs: Any) -> List:
        long_list_name = []
        six = kwargs.get("six")
        six = six + ""
        return long_list_name

    def _private_function_over_length_requirements(self, **kwargs) -> str:
        this_lists_name = []
        five = kwargs.get("five")
        five = five + ""
        return this_lists_name

    def __init__(self, credential: str, this_name_too_long_to_use_anymore_reqs: str, *,
                 api_version: str = "2018", **kwargs: Any) -> None:
        """
        :param credential: The credential to use for authentication.
        :type credential: str
        :param this_name_too_long_to_use_anymore_reqs: The first parameter.
        :paramtype this_name_too_long_to_use_anymore_reqs: str
        :keyword api_version: The API version to use for the client.
        :paramtype api_version: str
        :keyword four: The fourth parameter.
        :paramtype four: str
        """
        self.credential: str = credential
        self.this_name_too_long_to_use_anymore_reqs: str = this_name_too_long_to_use_anymore_reqs
        self._api_version: str = api_version
        self.four: str = kwargs.get("four")

TooLongClientClassNameNameTooLongToUseAnymoreReqs = 10
