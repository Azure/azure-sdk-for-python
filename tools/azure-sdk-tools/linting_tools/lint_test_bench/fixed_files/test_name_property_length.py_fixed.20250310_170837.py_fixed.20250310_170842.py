from typing import Any, List
from azure.core.tracing.decorator import distributed_trace

# This code violates name-too-long
class Client:
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
    def function_name(self, **kwargs: Any) -> str:
        seven = kwargs.get("seven")
        return seven

    @distributed_trace
    def get_function(self, **kwargs: Any) -> List:
        long_list_name = []
        six = kwargs.get("six")
        six = six + ""
        return long_list_name

    def _private_function(self, **kwargs) -> str:
        this_lists_name = []
        five = kwargs.get("five")
        five = five + ""
        return this_lists_name

    def __init__(self, credential: str, first_param: str, *,
                 api_version: str = "2018", **kwargs: Any) -> None:
        """
        :param credential: The credential to use for authentication.
        :type credential: str
        :param first_param: The first parameter.
        :paramtype first_param: str
        :keyword api_version: The API version to use for the client.
        :paramtype api_version: str
        :keyword four: The fourth parameter.
        :paramtype four: str
        """
        self.credential: str = credential
        self.first_param: str = first_param
        self._api_version: str = api_version
        self.four: str = kwargs.get("four")

NameTooLong = 10
