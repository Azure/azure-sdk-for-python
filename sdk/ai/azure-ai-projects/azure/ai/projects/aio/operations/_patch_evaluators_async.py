# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Custom async evaluator operations."""

from typing import Any, IO, Optional, Union, cast, overload

from azure.core.polling import AsyncNoPolling, AsyncPollingMethod
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.utils import case_insensitive_dict

from ._operations import BetaEvaluatorsOperations as BetaEvaluatorsOperationsGenerated
from ... import models as _models, types as _types
from ..._utils.model_base import _deserialize
from ...models import AsyncEvaluatorGenerationLROPoller


class BetaEvaluatorsOperations(BetaEvaluatorsOperationsGenerated):
    """Custom async operations for beta evaluator generation jobs."""

    @overload  # type: ignore[override]
    async def begin_create_generation_job(
        self,
        job: _models.EvaluatorGenerationJob,
        *,
        operation_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncEvaluatorGenerationLROPoller: ...

    @overload
    async def begin_create_generation_job(
        self,
        job: _types.EvaluatorGenerationJob,
        *,
        operation_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncEvaluatorGenerationLROPoller: ...

    @overload
    async def begin_create_generation_job(
        self,
        job: IO[bytes],
        *,
        operation_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncEvaluatorGenerationLROPoller: ...

    @distributed_trace_async
    async def begin_create_generation_job(  # type: ignore[reportIncompatibleMethodOverride, override]
        self,
        job: Union[_models.EvaluatorGenerationJob, _types.EvaluatorGenerationJob, IO[bytes]],
        *,
        operation_id: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncEvaluatorGenerationLROPoller:
        """Create an evaluator generation job.

        :param job: The job to create. Required.
        :type job: ~azure.ai.projects.models.EvaluatorGenerationJob or ~azure.ai.projects.types.EvaluatorGenerationJob or IO[bytes]
        :keyword operation_id: Client-generated unique ID for idempotent retries. When absent, the
         server creates the job unconditionally. Default value is None.
        :paramtype operation_id: str
        :return: A poller that returns EvaluatorVersion and exposes the job ID in ``details``.
        :rtype: ~azure.ai.projects.models.AsyncEvaluatorGenerationLROPoller
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
            raw_result = await self._create_generation_job_initial(
                job=job,  # type: ignore[reportArgumentType, arg-type]
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
            response_headers["Location"] = self._deserialize("str", response.headers.get("Location"))

            deserialized = _deserialize(_models.EvaluatorVersion, response.json().get("result", {}))
            if cls:
                return cls(pipeline_response, deserialized, response_headers)
            return deserialized

        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }

        if polling is True:
            polling_method: AsyncPollingMethod = cast(
                AsyncPollingMethod,
                AsyncLROBasePolling(lro_delay, path_format_arguments=path_format_arguments, **kwargs),
            )
        elif polling is False:
            polling_method = cast(AsyncPollingMethod, AsyncNoPolling())
        else:
            polling_method = polling
        if continuation_token:
            return AsyncEvaluatorGenerationLROPoller.from_continuation_token(
                polling_method=polling_method,
                continuation_token=continuation_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )
        assert raw_result is not None
        return AsyncEvaluatorGenerationLROPoller(  # type: ignore
            self._client, raw_result, get_long_running_output, polling_method
        )
