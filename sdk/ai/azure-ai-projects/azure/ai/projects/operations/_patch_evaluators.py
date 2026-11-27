# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Custom evaluator operations."""

from collections.abc import MutableMapping
from typing import Any, IO, Optional, Union, cast, overload

from azure.core.polling import NoPolling, PollingMethod
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict

from ._operations import EvaluatorsOperations as EvaluatorsOperationsGenerated
from .. import models as _models
from .._utils.model_base import _deserialize
from .._utils.polling import AIProjectsLROBasePolling
from ..models import EvaluatorGenerationLROPoller
from ..models._enums import _FoundryFeaturesOptInKeys
from ..models._patch import _FOUNDRY_FEATURES_HEADER_NAME

JSON = MutableMapping[str, Any]


def _add_evaluations_preview_header(allow_preview: bool, kwargs: MutableMapping[str, Any]) -> None:
    """Add the Evaluations preview opt-in header to *kwargs* when *allow_preview* is enabled.

    The service requires ``Foundry-Features: Evaluations=V1Preview`` to create or update custom
    prompt-based, code-based, and endpoint-based evaluators. A caller-supplied Foundry-Features
    header is left unchanged.

    :param allow_preview: Whether the client was constructed with ``allow_preview=True``.
    :type allow_preview: bool
    :param kwargs: Keyword arguments for the operation. Updated in place.
    :type kwargs: MutableMapping[str, Any]
    """
    if not allow_preview:
        return
    headers = case_insensitive_dict(kwargs.get("headers") or {})
    if _FOUNDRY_FEATURES_HEADER_NAME not in headers:
        headers[_FOUNDRY_FEATURES_HEADER_NAME] = _FoundryFeaturesOptInKeys.EVALUATIONS_V1_PREVIEW.value
    kwargs["headers"] = headers


class EvaluatorsOperations(EvaluatorsOperationsGenerated):
    """Custom evaluator operations."""

    @overload
    def create_version(
        self,
        name: str,
        evaluator_version: _models.EvaluatorVersion,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.EvaluatorVersion: ...

    @overload
    def create_version(
        self, name: str, evaluator_version: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.EvaluatorVersion: ...

    @overload
    def create_version(
        self, name: str, evaluator_version: IO[bytes], *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.EvaluatorVersion: ...

    @distributed_trace
    def create_version(
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
        return super().create_version(name, evaluator_version, **kwargs)

    @overload
    def update_version(
        self,
        name: str,
        version: str,
        evaluator_version: _models.EvaluatorVersion,
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.EvaluatorVersion: ...

    @overload
    def update_version(
        self, name: str, version: str, evaluator_version: JSON, *, content_type: str = "application/json", **kwargs: Any
    ) -> _models.EvaluatorVersion: ...

    @overload
    def update_version(
        self,
        name: str,
        version: str,
        evaluator_version: IO[bytes],
        *,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> _models.EvaluatorVersion: ...

    @distributed_trace
    def update_version(
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
        return super().update_version(name, version, evaluator_version, **kwargs)

    @overload
    def begin_create_generation_job(
        self,
        job: _models.EvaluatorGenerationInputs,
        *,
        operation_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> EvaluatorGenerationLROPoller: ...

    @overload
    def begin_create_generation_job(
        self,
        job: JSON,
        *,
        operation_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> EvaluatorGenerationLROPoller: ...

    @overload
    def begin_create_generation_job(
        self,
        job: IO[bytes],
        *,
        operation_id: Optional[str] = None,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> EvaluatorGenerationLROPoller: ...

    @distributed_trace
    def begin_create_generation_job(
        self,
        job: Union[_models.EvaluatorGenerationInputs, JSON, IO[bytes]],
        *,
        operation_id: Optional[str] = None,
        **kwargs: Any,
    ) -> EvaluatorGenerationLROPoller:
        """Create an evaluator generation job.

        :param job: The evaluator generation inputs. Required.
        :type job: ~azure.ai.projects.models.EvaluatorGenerationInputs or JSON or IO[bytes]
        :keyword operation_id: Client-generated unique ID for idempotent retries. When absent, the
         server creates the job unconditionally. Default value is None.
        :paramtype operation_id: str
        :return: A poller that returns EvaluatorVersion and exposes the job ID in ``details``.
        :rtype: ~azure.ai.projects.models.EvaluatorGenerationLROPoller
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = kwargs.pop("content_type", headers.pop("Content-Type", None))
        cls = kwargs.pop("cls", None)
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        continuation_token: Optional[str] = kwargs.pop("continuation_token", None)
        raw_result = None
        if continuation_token is None:
            raw_result = self._create_generation_job_initial(
                job=job,
                operation_id=operation_id,
                content_type=content_type,
                cls=lambda x, y, z: x,
                headers=headers,
                params=params,
                **kwargs,
            )
            raw_result.http_response.read()  # type: ignore
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
            polling_method: PollingMethod = cast(
                PollingMethod,
                AIProjectsLROBasePolling(lro_delay, path_format_arguments=path_format_arguments, **kwargs),
            )
        elif polling is False:
            polling_method = cast(PollingMethod, NoPolling())
        else:
            polling_method = polling
        if continuation_token:
            return EvaluatorGenerationLROPoller.from_continuation_token(
                polling_method=polling_method,
                continuation_token=continuation_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )
        assert raw_result is not None
        return EvaluatorGenerationLROPoller(self._client, raw_result, get_long_running_output, polling_method)  # type: ignore
