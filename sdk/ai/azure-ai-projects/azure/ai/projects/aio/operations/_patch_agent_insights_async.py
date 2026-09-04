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
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.utils import case_insensitive_dict

from ._operations import (
    BetaAgentInsightMonitorsOperations as BetaAgentInsightMonitorsOperationsGenerated,
)
from ... import models as _models
from ..._utils.model_base import _deserialize
from ...models import AsyncAgentInsightRunLROPoller

JSON = MutableMapping[str, Any]


class BetaAgentInsightMonitorsOperations(BetaAgentInsightMonitorsOperationsGenerated):
    """Custom async operations for beta Agent Insights monitors."""

    @overload
    async def begin_create_run(
        self,
        monitor_id: str,
        run: _models.AgentInsightRunCreate,
        *,
        operation_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncAgentInsightRunLROPoller: ...

    @overload
    async def begin_create_run(
        self,
        monitor_id: str,
        run: JSON,
        *,
        operation_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncAgentInsightRunLROPoller: ...

    @overload
    async def begin_create_run(
        self,
        monitor_id: str,
        run: IO[bytes],
        *,
        operation_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncAgentInsightRunLROPoller: ...

    @distributed_trace_async
    async def begin_create_run(
        self,
        monitor_id: str,
        run: Union[_models.AgentInsightRunCreate, JSON, IO[bytes]],
        *,
        operation_id: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncAgentInsightRunLROPoller:
        """Start an Agent Insights run for a monitor.

        :param monitor_id: The identifier of the monitor. Required.
        :type monitor_id: str
        :param run: Run inputs. Send an empty object to use the default 168-hour lookback window. Is
         one of the following types: AgentInsightRunCreate, JSON, IO[bytes] Required.
        :type run: ~azure.ai.projects.models.AgentInsightRunCreate or JSON or IO[bytes]
        :keyword operation_id: Client-generated unique ID for idempotent retries. When absent, the
         server creates the run unconditionally. Default value is None.
        :paramtype operation_id: str
        :return: A poller that returns AgentInsightRunResult and exposes the run ID in ``details``.
        :rtype: ~azure.ai.projects.models.AsyncAgentInsightRunLROPoller
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop(
            "content_type", headers.pop("Content-Type", None)
        )
        cls = kwargs.pop("cls", None)
        polling: Union[bool, AsyncPollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        lro_options = dict(kwargs.pop("lro_options", {}) or {})
        lro_options["final-state-via"] = "operation-location"
        continuation_token: Optional[str] = kwargs.pop("continuation_token", None)
        raw_result = None
        if continuation_token is None:
            raw_result = await self._create_run_initial(
                monitor_id=monitor_id,
                run=run,
                operation_id=operation_id,
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
            response_headers["Location"] = self._deserialize(
                "str", response.headers.get("Location")
            )

            deserialized = _deserialize(
                _models.AgentInsightRunResult, response.json().get("result", {})
            )
            if cls:
                return cls(pipeline_response, deserialized, response_headers)
            return deserialized

        path_format_arguments = {
            "endpoint": self._serialize.url(
                "self._config.endpoint", self._config.endpoint, "str", skip_quote=True
            ),
        }

        if polling is True:
            polling_method: AsyncPollingMethod = cast(
                AsyncPollingMethod,
                AsyncLROBasePolling(
                    lro_delay,
                    lro_options=lro_options,
                    path_format_arguments=path_format_arguments,
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
