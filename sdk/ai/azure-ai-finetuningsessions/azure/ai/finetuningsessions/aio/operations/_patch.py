# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Supported async operation subclasses preserving the tested preview API.

The seven local override annotations document intentional legacy keyword
replacements, not unchecked implementation or arbitrary API changes.
"""

from collections.abc import MutableMapping
from os import PathLike
from typing import Any, IO, Literal, Optional, Union, overload

from azure.core.polling import AsyncLROPoller
from azure.core.tracing.decorator_async import distributed_trace_async

from ... import models as _models
from ...models._enums import FoundryFeaturesOptInKeys
from ..._checkpoint_download import _prepare_checkpoint_download_async, _validate_checkpoint_output_path
from ..._operation_compat import _begin_async, _read_async, _build_sampling_request
from ...operations import _operations as _builders
from . import _operations as _generated

JSON = MutableMapping[str, Any]


class SessionsOperations(_generated.SessionsOperations):
    # Preserve the published preview 'body' keyword across overloads and implementation.
    @overload  # type: ignore[override]
    async def begin_create(  # pylint: disable=arguments-renamed
        self,
        body: _models.CreateSessionRequest,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...
    @overload
    async def begin_create(  # pylint: disable=arguments-renamed
        self,
        body: JSON,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...
    @overload
    async def begin_create(  # pylint: disable=arguments-renamed
        self,
        body: IO[bytes],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...

    @distributed_trace_async
    async def begin_create(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        body: Union[_models.CreateSessionRequest, JSON, IO[bytes]],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]:
        # pylint: disable=arguments-renamed
        return await _begin_async(
            self,
            _builders.build_sessions_create_request,
            {"foundry_features": foundry_features, "api_version": api_version},
            kwargs,
            body,
        )

    @distributed_trace_async
    async def create(
        self,
        body: Union[_models.CreateSessionRequest, JSON, IO[bytes]],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> JSON:
        return await _read_async(
            self,
            _builders.build_sessions_create_request,
            {"foundry_features": foundry_features, "api_version": api_version},
            None,
            kwargs,
            body,
        )

    @distributed_trace_async
    async def list(
        self,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **kwargs: Any,
    ) -> _models.SessionList:
        return await _read_async(
            self,
            _builders.build_sessions_list_request,
            {
                "foundry_features": foundry_features,
                "api_version": api_version,
                "limit": limit,
                "offset": offset,
            },
            _models.SessionList,
            kwargs,
        )

    @distributed_trace_async
    async def get(
        self,
        session_id: str,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> _models.Session:
        return await _read_async(
            self,
            _builders.build_sessions_get_request,
            {"session_id": session_id, "foundry_features": foundry_features, "api_version": api_version},
            _models.Session,
            kwargs,
        )

    @distributed_trace_async
    async def begin_unload(
        self,
        session_id: str,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]:
        return await _begin_async(
            self,
            _builders.build_sessions_unload_request,
            {"session_id": session_id, "foundry_features": foundry_features, "api_version": api_version},
            kwargs,
        )

    @distributed_trace_async
    async def heartbeat(
        self,
        session_id: str,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> _models.HeartbeatResponse:
        return await _read_async(
            self,
            _builders.build_sessions_heartbeat_request,
            {"session_id": session_id, "foundry_features": foundry_features, "api_version": api_version},
            _models.HeartbeatResponse,
            kwargs,
        )


class TrainingOperations(_generated.TrainingOperations):
    # Preserve the published preview 'body' keyword across overloads and implementation.
    @overload  # type: ignore[override]
    async def begin_forward_backward(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: _models.ForwardBackwardRequest,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...
    @overload
    async def begin_forward_backward(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: JSON,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...
    @overload
    async def begin_forward_backward(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: IO[bytes],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...

    @distributed_trace_async
    async def begin_forward_backward(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        session_id: str,
        body: Union[_models.ForwardBackwardRequest, JSON, IO[bytes]],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]:
        # pylint: disable=arguments-renamed
        return await _begin_async(
            self,
            _builders.build_training_forward_backward_request,
            {"session_id": session_id, "foundry_features": foundry_features, "api_version": api_version},
            kwargs,
            body,
        )

    # Preserve the published preview 'body' keyword across overloads and implementation.
    @overload  # type: ignore[override]
    async def begin_optim_step(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: _models.OptimStepRequest,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...
    @overload
    async def begin_optim_step(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: JSON,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...
    @overload
    async def begin_optim_step(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: IO[bytes],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...

    @distributed_trace_async
    async def begin_optim_step(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        session_id: str,
        body: Union[_models.OptimStepRequest, JSON, IO[bytes]],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]:
        # pylint: disable=arguments-renamed
        return await _begin_async(
            self,
            _builders.build_training_optim_step_request,
            {"session_id": session_id, "foundry_features": foundry_features, "api_version": api_version},
            kwargs,
            body,
        )


class CheckpointsOperations(_generated.CheckpointsOperations):
    async def download_weights(
        self, session_id: str, checkpoint_id: str, output_path: Union[str, PathLike[str]]
    ) -> None:
        """Validate the local destination and prepare checkpoint weights on the service.

        First check ``output_path/<session_id>/<checkpoint_id>``. The checkpoint directory must
        be empty or absent; parent directories may contain unrelated entries.
        Identifiers are used verbatim and must be single portable directory names.
        Resolved session/checkpoint paths must remain inside the output root.
        Then poll the canonical download preparation API and validate its complete private
        file manifest. No directories are created, files written, or weights transferred.

        :param str session_id: Identifier of the session that owns the checkpoint.
        :param str checkpoint_id: Identifier of the checkpoint within the session.
        :param output_path: Local output root, which may already contain other files.
        :type output_path: str or ~os.PathLike[str]
        :return: None after server-side preparation, not confirmation of file delivery.
        :rtype: None
        :raises TypeError: If an identifier or output path has an incompatible type.
        :raises ValueError: If an identifier is unsafe, a path escapes the output root,
            the checkpoint directory is nonempty, or a request option is invalid.
        :raises OSError: If a needed directory is a file or another filesystem check fails.
        :raises ~azure.ai.finetuningsessions.FineTuningSessionsError: If preparation fails.
        :raises ~azure.core.exceptions.HttpResponseError: If a service request fails.
        :raises ~azure.ai.finetuningsessions.MalformedResponseError: If preparation status or file metadata is invalid.
        """
        _validate_checkpoint_output_path(session_id, checkpoint_id, output_path)
        await _prepare_checkpoint_download_async(self, session_id, checkpoint_id)

    # Preserve the published preview 'body' keyword across overloads and implementation.
    @overload  # type: ignore[override]
    async def begin_save(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: _models.SaveCheckpointRequest,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...
    @overload
    async def begin_save(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: JSON,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...
    @overload
    async def begin_save(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: IO[bytes],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...

    @distributed_trace_async
    async def begin_save(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        session_id: str,
        body: Union[_models.SaveCheckpointRequest, JSON, IO[bytes]],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]:
        # pylint: disable=arguments-renamed
        return await _begin_async(
            self,
            _builders.build_checkpoints_save_request,
            {"session_id": session_id, "foundry_features": foundry_features, "api_version": api_version},
            kwargs,
            body,
        )

    # Preserve the published preview 'body' keyword across overloads and implementation.
    @overload  # type: ignore[override]
    async def begin_save_sampler_weights(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: _models.SaveSamplerWeightsRequest,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...
    @overload
    async def begin_save_sampler_weights(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: JSON,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...
    @overload
    async def begin_save_sampler_weights(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: IO[bytes],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...

    @distributed_trace_async
    async def begin_save_sampler_weights(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        session_id: str,
        body: Union[_models.SaveSamplerWeightsRequest, JSON, IO[bytes]],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]:
        # pylint: disable=arguments-renamed
        return await _begin_async(
            self,
            _builders.build_checkpoints_save_sampler_weights_request,
            {"session_id": session_id, "foundry_features": foundry_features, "api_version": api_version},
            kwargs,
            body,
        )

    @distributed_trace_async
    async def list(
        self,
        session_id: str,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> _models.CheckpointList:
        return await _read_async(
            self,
            _builders.build_checkpoints_list_request,
            {"session_id": session_id, "foundry_features": foundry_features, "api_version": api_version},
            _models.CheckpointList,
            kwargs,
        )

    @distributed_trace_async
    async def get(
        self,
        session_id: str,
        checkpoint_id: str,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> _models.CheckpointInfo:
        return await _read_async(
            self,
            _builders.build_checkpoints_get_request,
            {
                "session_id": session_id,
                "checkpoint_id": checkpoint_id,
                "foundry_features": foundry_features,
                "api_version": api_version,
            },
            _models.CheckpointInfo,
            kwargs,
        )


class SamplingOperations(_generated.SamplingOperations):
    # Preserve the published preview 'body' keyword across overloads and implementation.
    @overload  # type: ignore[override]
    async def begin_sample(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: _models.SampleRequest,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...
    @overload
    async def begin_sample(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: JSON,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...
    @overload
    async def begin_sample(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: IO[bytes],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...

    @distributed_trace_async
    async def begin_sample(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        session_id: str,
        body: Union[_models.SampleRequest, JSON, IO[bytes]],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]:
        # pylint: disable=arguments-renamed
        return await _begin_async(
            self,
            _build_sampling_request,
            {"session_id": session_id, "foundry_features": foundry_features, "api_version": api_version},
            kwargs,
            body,
        )


class Operations(_generated.Operations):
    # Preserve the published preview 'operation_id' keyword.
    @distributed_trace_async
    async def get(  # type: ignore[override]  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        session_id: str,
        operation_id: str,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> _models.OperationResult:
        # pylint: disable=arguments-renamed
        return await _read_async(
            self,
            _builders.build_operations_get_request,
            {
                "session_id": session_id,
                "request_id_parameter": operation_id,
                "foundry_features": foundry_features,
                "api_version": api_version,
            },
            _models.OperationResult,
            kwargs,
        )


__all__: list[str] = [
    "SessionsOperations",
    "TrainingOperations",
    "CheckpointsOperations",
    "SamplingOperations",
    "Operations",
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
