# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------

from copy import deepcopy
from typing import Any, Awaitable, Optional, TYPE_CHECKING
from typing_extensions import Self

from azure.core import AsyncPipelineClient
from azure.core.pipeline import policies
from azure.core.rest import AsyncHttpResponse, HttpRequest

from .. import models as _models
from .._utils.serialization import Deserializer, Serializer
from ._configuration import AzureDigitalTwinsAPIConfiguration
from .operations import (
    DeleteJobsOperations,
    DigitalTwinModelsOperations,
    DigitalTwinsOperations,
    EventRoutesOperations,
    ImportJobsOperations,
    QueryOperations,
)

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class AzureDigitalTwinsAPI:
    """A service for managing and querying digital twins and digital twin models.

    :ivar digital_twin_models: DigitalTwinModelsOperations operations
    :vartype digital_twin_models:
     azure.digitaltwins.core.aio.operations.DigitalTwinModelsOperations
    :ivar query: QueryOperations operations
    :vartype query: azure.digitaltwins.core.aio.operations.QueryOperations
    :ivar digital_twins: DigitalTwinsOperations operations
    :vartype digital_twins: azure.digitaltwins.core.aio.operations.DigitalTwinsOperations
    :ivar event_routes: EventRoutesOperations operations
    :vartype event_routes: azure.digitaltwins.core.aio.operations.EventRoutesOperations
    :ivar import_jobs: ImportJobsOperations operations
    :vartype import_jobs: azure.digitaltwins.core.aio.operations.ImportJobsOperations
    :ivar delete_jobs: DeleteJobsOperations operations
    :vartype delete_jobs: azure.digitaltwins.core.aio.operations.DeleteJobsOperations
    :param credential: Credential needed for the client to connect to Azure. Required.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :param operation_id: ID for the operation's status monitor. The ID is generated if header was
     not passed by the client. Default value is None.
    :type operation_id: str
    :param timeout_in_minutes: Desired timeout for the delete job. Once the specified timeout is
     reached, service will stop any delete operations triggered by the current delete job that are
     in progress, and go to a failed state. Please note that this will leave your instance in an
     unknown state as there won't be any rollback operation. Default value is None.
    :type timeout_in_minutes: int
    :param base_url: Service URL. Default value is "https://digitaltwins-hostname".
    :type base_url: str
    :keyword api_version: Api Version. Default value is "2023-10-31". Note that overriding this
     default value may result in unsupported behavior.
    :paramtype api_version: str
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
     Retry-After header is present.
    """

    def __init__(
        self,
        credential: "AsyncTokenCredential",
        operation_id: Optional[str] = None,
        timeout_in_minutes: Optional[int] = None,
        base_url: str = "https://digitaltwins-hostname",
        **kwargs: Any
    ) -> None:
        self._config = AzureDigitalTwinsAPIConfiguration(
            credential=credential, operation_id=operation_id, timeout_in_minutes=timeout_in_minutes, **kwargs
        )

        _policies = kwargs.pop("policies", None)
        if _policies is None:
            _policies = [
                policies.RequestIdPolicy(**kwargs),
                self._config.headers_policy,
                self._config.user_agent_policy,
                self._config.proxy_policy,
                policies.ContentDecodePolicy(**kwargs),
                self._config.redirect_policy,
                self._config.retry_policy,
                self._config.authentication_policy,
                self._config.custom_hook_policy,
                self._config.logging_policy,
                policies.DistributedTracingPolicy(**kwargs),
                policies.SensitiveHeaderCleanupPolicy(**kwargs) if self._config.redirect_policy else None,
                self._config.http_logging_policy,
            ]
        self._client: AsyncPipelineClient = AsyncPipelineClient(base_url=base_url, policies=_policies, **kwargs)

        client_models = {k: v for k, v in _models.__dict__.items() if isinstance(v, type)}
        self._serialize = Serializer(client_models)
        self._deserialize = Deserializer(client_models)
        self._serialize.client_side_validation = False
        self.digital_twin_models = DigitalTwinModelsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.query = QueryOperations(self._client, self._config, self._serialize, self._deserialize)
        self.digital_twins = DigitalTwinsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.event_routes = EventRoutesOperations(self._client, self._config, self._serialize, self._deserialize)
        self.import_jobs = ImportJobsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.delete_jobs = DeleteJobsOperations(self._client, self._config, self._serialize, self._deserialize)

    def _send_request(
        self, request: HttpRequest, *, stream: bool = False, **kwargs: Any
    ) -> Awaitable[AsyncHttpResponse]:
        """Runs the network request through the client's chained policies.

        >>> from azure.core.rest import HttpRequest
        >>> request = HttpRequest("GET", "https://www.example.org/")
        <HttpRequest [GET], url: 'https://www.example.org/'>
        >>> response = await client._send_request(request)
        <AsyncHttpResponse: 200 OK>

        For more information on this code flow, see https://aka.ms/azsdk/dpcodegen/python/send_request

        :param request: The network request you want to make. Required.
        :type request: ~azure.core.rest.HttpRequest
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call. Does not do error handling on your response.
        :rtype: ~azure.core.rest.AsyncHttpResponse
        """

        request_copy = deepcopy(request)
        request_copy.url = self._client.format_url(request_copy.url)
        return self._client.send_request(request_copy, stream=stream, **kwargs)  # type: ignore

    async def close(self) -> None:
        await self._client.close()

    async def __aenter__(self) -> Self:
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *exc_details: Any) -> None:
        await self._client.__aexit__(*exc_details)
