# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any, IO, Optional, Union, cast, overload
from collections.abc import MutableMapping

from azure.core.polling import AsyncNoPolling, AsyncPollingMethod
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.utils import case_insensitive_dict

from ._operations import (
    AgentInsightMonitorsOperations as AgentInsightMonitorsOperationsGenerated,
    _Unset,
)
from ... import models as _models
from ..._utils.model_base import _deserialize
from ..._utils.polling import AsyncAIProjectsLROBasePolling
from ...models import AsyncAgentInsightRunLROPoller

JSON = MutableMapping[str, Any]


class AgentInsightMonitorsOperations(AgentInsightMonitorsOperationsGenerated):
    """Custom async operations for generally available Agent Insights monitors."""

    @overload
    async def begin_create_run(
        self,
        monitor_id: str,
        *,
        operation_id: Optional[str] = None,
        content_type: str = "application/json",
        lookback_hours: Optional[float] = None,
        **kwargs: Any,
    ) -> AsyncAgentInsightRunLROPoller: ...

    @overload
    async def begin_create_run(
        self,
        monitor_id: str,
        body: JSON,
        *,
        operation_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncAgentInsightRunLROPoller: ...

    @overload
    async def begin_create_run(
        self,
        monitor_id: str,
        body: IO[bytes],
        *,
        operation_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncAgentInsightRunLROPoller: ...

    @distributed_trace_async
    async def begin_create_run(
        self,
        monitor_id: str,
        body: Union[JSON, IO[bytes]] = _Unset,
        *,
        operation_id: Optional[str] = None,
        lookback_hours: Optional[float] = None,
        **kwargs: Any,
    ) -> AsyncAgentInsightRunLROPoller:
        """Start an Agent Insights run for a monitor.

        :param monitor_id: The identifier of the monitor. Required.
        :type monitor_id: str
        :param body: Run inputs as JSON or a binary stream. Omit to use keyword inputs.
        :type body: MutableMapping[str, Any] or IO[bytes]
        :keyword operation_id: Client-generated unique ID for idempotent retries. When absent, the
         server creates the run unconditionally. Default value is None.
        :paramtype operation_id: str
        :keyword lookback_hours: Positive hours of trace history to analyze, up to 2,160.
         Defaults to 168 when omitted.
        :paramtype lookback_hours: float
        :return: A poller that returns AgentInsightRunResult and exposes the run ID in ``details``.
        :rtype: ~azure.ai.projects.models.AsyncAgentInsightRunLROPoller
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", headers.pop("Content-Type", None))
        cls = kwargs.pop("cls", None)
        polling: Union[bool, AsyncPollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        continuation_token: Optional[str] = kwargs.pop("continuation_token", None)
        raw_result = None
        if continuation_token is None:
            raw_result = await self._create_run_initial(
                monitor_id=monitor_id,
                body=body,
                operation_id=operation_id,
                lookback_hours=lookback_hours,
                content_type=content_type,
                cls=lambda x, y, z: x,
                headers=headers,
                params=params,
                **kwargs,
            )
            await raw_result.http_response.read()  # type: ignore
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            response_headers = {}
            response = pipeline_response.http_response
            response_headers["Operation-Location"] = self._deserialize(
                "str", response.headers.get("Operation-Location")
            )
            response_headers["Location"] = self._deserialize("str", response.headers.get("Location"))

            deserialized = _deserialize(_models.AgentInsightRunResult, response.json().get("result", {}))
            if cls:
                return cls(pipeline_response, deserialized, response_headers)
            return deserialized

        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        if polling is True:
            polling_method: AsyncPollingMethod = cast(
                AsyncPollingMethod,
                AsyncAIProjectsLROBasePolling(
                    lro_delay,
                    path_format_arguments=path_format_arguments,
                    headers=headers,
                    **kwargs,
                ),
            )
        elif polling is False:
            polling_method = cast(AsyncPollingMethod, AsyncNoPolling())
        else:
            polling_method = polling
        if continuation_token:
            return AsyncAgentInsightRunLROPoller.from_continuation_token(
                polling_method=polling_method,
                continuation_token=continuation_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )
        assert raw_result is not None
        return AsyncAgentInsightRunLROPoller(  # type: ignore
            self._client, raw_result, get_long_running_output, polling_method
        )
