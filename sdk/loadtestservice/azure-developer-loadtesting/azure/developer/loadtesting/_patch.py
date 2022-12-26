# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from copy import deepcopy
from typing import Any, TYPE_CHECKING, List

from azure.core import PipelineClient
from azure.core.rest import HttpRequest, HttpResponse

from ._configuration import LoadTestingClientConfiguration
from ._serialization import Deserializer, Serializer
from .operations import LoadTestAdministrationOperations, LoadTestRunOperations

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from azure.core.credentials import TokenCredential

class LoadTestingClient:
    """
    LoadTestingClient is deprecated, use LoadTestAdministrationClient or LoadTestRunClient instead.
    """
    pass

class LoadTestAdministrationClient(LoadTestAdministrationOperations):  # pylint: disable=client-accepts-api-version-keyword
    """These APIs allow end users to perform load test administration operations on Azure Load Test Service.

    :param endpoint: URL to perform data plane API operations on the resource. Required.
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure. Required.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword api_version: Api Version. Default value is "2022-11-01". Note that overriding this
     default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(self, endpoint: str, credential: "TokenCredential", *args, **kwargs: Any) -> None:
        _endpoint = "https://{Endpoint}"
        self._config = LoadTestingClientConfiguration(endpoint=endpoint, credential=credential, **kwargs)
        self._client = PipelineClient(base_url=_endpoint, config=self._config, **kwargs)

        self._serialize = Serializer()
        self._deserialize = Deserializer()
        self._serialize.client_side_validation = False

        # call super to initialize the load test administration operations
        super().__init__(self._client, self._config, self._serialize, self._deserialize)

    def send_request(self, request: HttpRequest, **kwargs: Any) -> HttpResponse:
        """Runs the network request through the client's chained policies.

        >>> from azure.core.rest import HttpRequest
        >>> request = HttpRequest("GET", "https://www.example.org/")
        <HttpRequest [GET], url: 'https://www.example.org/'>
        >>> response = client.send_request(request)
        <HttpResponse: 200 OK>

        For more information on this code flow, see https://aka.ms/azsdk/dpcodegen/python/send_request

        :param request: The network request you want to make. Required.
        :type request: ~azure.core.rest.HttpRequest
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call. Does not do error handling on your response.
        :rtype: ~azure.core.rest.HttpResponse
        """

        request_copy = deepcopy(request)
        path_format_arguments = {
            "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        request_copy.url = self._client.format_url(request_copy.url, **path_format_arguments)
        return self._client.send_request(request_copy, **kwargs)

    def close(self):
        # type: () -> None
        self._client.close()

    def __enter__(self):
        # type: () -> LoadTestAdministrationClient
        self._client.__enter__()
        return self

    def __exit__(self, *exc_details):
        # type: (Any) -> None
        self._client.__exit__(*exc_details)

class LoadTestRunClient(LoadTestRunOperations):  # pylint: disable=client-accepts-api-version-keyword
    """These APIs allow end users to perform load test run operations on Azure Load Test Service.

    :param endpoint: URL to perform data plane API operations on the resource. Required.
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure. Required.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword api_version: Api Version. Default value is "2022-11-01". Note that overriding this
     default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(self, endpoint: str, credential: "TokenCredential", *args, **kwargs: Any) -> None:
        _endpoint = "https://{Endpoint}"
        self._config = LoadTestingClientConfiguration(endpoint=endpoint, credential=credential, **kwargs)
        self._client = PipelineClient(base_url=_endpoint, config=self._config, **kwargs)

        self._serialize = Serializer()
        self._deserialize = Deserializer()
        self._serialize.client_side_validation = False

        # call super to initialize the load test run operations
        super().__init__(self._client, self._config, self._serialize, self._deserialize)

    def send_request(self, request: HttpRequest, **kwargs: Any) -> HttpResponse:
        """Runs the network request through the client's chained policies.

        >>> from azure.core.rest import HttpRequest
        >>> request = HttpRequest("GET", "https://www.example.org/")
        <HttpRequest [GET], url: 'https://www.example.org/'>
        >>> response = client.send_request(request)
        <HttpResponse: 200 OK>

        For more information on this code flow, see https://aka.ms/azsdk/dpcodegen/python/send_request

        :param request: The network request you want to make. Required.
        :type request: ~azure.core.rest.HttpRequest
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call. Does not do error handling on your response.
        :rtype: ~azure.core.rest.HttpResponse
        """

        request_copy = deepcopy(request)
        path_format_arguments = {
            "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        request_copy.url = self._client.format_url(request_copy.url, **path_format_arguments)
        return self._client.send_request(request_copy, **kwargs)

    def close(self):
        # type: () -> None
        self._client.close()

    def __enter__(self):
        # type: () -> LoadTestRunClient
        self._client.__enter__()
        return self

    def __exit__(self, *exc_details):
        # type: (Any) -> None
        self._client.__exit__(*exc_details)


__all__: List[str] = ["LoadTestingClient", "LoadTestAdministrationClient", "LoadTestRunClient"]  # Add all objects you want publicly available to users at this
# package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
