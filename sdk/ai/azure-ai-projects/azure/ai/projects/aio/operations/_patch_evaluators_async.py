# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Custom async evaluator operations."""

from collections.abc import MutableMapping
from typing import Any, IO, Optional, Union, cast, overload

from azure.core.polling import AsyncNoPolling, AsyncPollingMethod
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.utils import case_insensitive_dict

from ._operations import EvaluatorsOperations as EvaluatorsOperationsGenerated
from ... import models as _models
from ..._utils.model_base import _deserialize
from ..._utils.polling import AsyncAIProjectsLROBasePolling
from ...models import AsyncEvaluatorGenerationLROPoller
from ...operations._patch_evaluators import _add_evaluations_preview_header

JSON = MutableMapping[str, Any]


class EvaluatorsOperations(EvaluatorsOperationsGenerated):
    """Custom async evaluator operations."""

    @overload
    async def create_version(
        self,
        name: str,
        evaluator_version: _models.EvaluatorVersion,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.EvaluatorVersion: ...

    @overload
    async def create_version(
        self, name: str, evaluator_version: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.EvaluatorVersion: ...

    @overload
    async def create_version(
        self, name: str, evaluator_version: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.EvaluatorVersion: ...

    @distributed_trace_async
    async def create_version(
        self, name: str, evaluator_version: Union[_models.EvaluatorVersion, JSON, IO[bytes]], **kwargs: Any
    ) -> _models.EvaluatorVersion:
        """Create an evaluator version.

        Creates a new evaluator version with an auto-incremented version identifier. Custom
        prompt-based, code-based, and endpoint-based evaluators are in preview. To create them,
        construct the client with ``allow_preview=True``.

        :param name: The name of the resource. Required.
        :type name: str
        :param evaluator_version: Is one of the following types: EvaluatorVersion, JSON, IO[bytes]
         Required.
        :type evaluator_version: ~azure.ai.projects.models.EvaluatorVersion or JSON or IO[bytes]
        :return: EvaluatorVersion. The EvaluatorVersion is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.EvaluatorVersion
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _add_evaluations_preview_header(getattr(self._config, "allow_preview", False), kwargs)
        return await super().create_version(name, evaluator_version, **kwargs)

    @overload
    async def update_version(
        self,
        name: str,
        version: str,
        evaluator_version: _models.EvaluatorVersion,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.EvaluatorVersion: ...

    @overload
    async def update_version(
        self, name: str, version: str, evaluator_version: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.EvaluatorVersion: ...

    @overload
    async def update_version(
        self,
        name: str,
        version: str,
        evaluator_version: IO[bytes],
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.EvaluatorVersion: ...

    @distributed_trace_async
    async def update_version(
        self,
        name: str,
        version: str,
        evaluator_version: Union[_models.EvaluatorVersion, JSON, IO[bytes]],
        **kwargs: Any,
    ) -> _models.EvaluatorVersion:
        """Update an evaluator version.

        Updates the specified evaluator version in place. Custom prompt-based, code-based, and
        endpoint-based evaluators are in preview. To update them, construct the client with
        ``allow_preview=True``.

        :param name: The name of the resource. Required.
        :type name: str
        :param version: The version of the EvaluatorVersion to update. Required.
        :type version: str
        :param evaluator_version: Evaluator resource. Is one of the following types: EvaluatorVersion,
         JSON, IO[bytes] Required.
        :type evaluator_version: ~azure.ai.projects.models.EvaluatorVersion or JSON or IO[bytes]
        :return: EvaluatorVersion. The EvaluatorVersion is compatible with MutableMapping
        :rtype: ~azure.ai.projects.models.EvaluatorVersion
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _add_evaluations_preview_header(getattr(self._config, "allow_preview", False), kwargs)
        return await super().update_version(name, version, evaluator_version, **kwargs)

    @overload
    async def begin_create_generation_job(
        self,
        job: _models.EvaluatorGenerationInputs,
        *,
        operation_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncEvaluatorGenerationLROPoller: ...

    @overload
    async def begin_create_generation_job(
        self,
        job: JSON,
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
    async def begin_create_generation_job(
        self,
        job: Union[_models.EvaluatorGenerationInputs, JSON, IO[bytes]],
        *,
        operation_id: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncEvaluatorGenerationLROPoller:
        """Create an evaluator generation job.

        :param job: The evaluator generation inputs. Required.
        :type job: ~azure.ai.projects.models.EvaluatorGenerationInputs or JSON or IO[bytes]
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
                job=job,
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
                AsyncAIProjectsLROBasePolling(lro_delay, path_format_arguments=path_format_arguments, **kwargs),
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
