# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Supported async operation subclasses preserving the tested preview API."""

from collections.abc import MutableMapping
from typing import Any, IO, Literal, Optional, Union, overload

from azure.core.polling import AsyncLROPoller
from azure.core.tracing.decorator_async import distributed_trace_async

from ... import models as _models
from ...models._enums import FoundryFeaturesOptInKeys
from ..._operation_compat import _begin_async, _read_async, _build_sampling_request
from ...operations import _operations as _builders
from . import _operations as _generated

JSON = MutableMapping[str, Any]


class SessionsOperations(_generated.SessionsOperations):
    @overload
    async def begin_create(
        self,
        session: _models.CreateSessionRequest,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...
    @overload
    async def begin_create(
        self,
        session: JSON,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...
    @overload
    async def begin_create(
        self,
        session: IO[bytes],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...

    @distributed_trace_async
    async def begin_create(
        self,
        session: Union[_models.CreateSessionRequest, JSON, IO[bytes]],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]:
        return await _begin_async(
            self,
            _builders.build_sessions_create_request,
            dict(foundry_features=foundry_features, api_version=api_version),
            kwargs,
            session,
        )

    @distributed_trace_async
    async def create(
        self,
        session: Union[_models.CreateSessionRequest, JSON, IO[bytes]],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> JSON:
        return await _read_async(
            self,
            _builders.build_sessions_create_request,
            dict(foundry_features=foundry_features, api_version=api_version),
            None,
            kwargs,
            session,
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
            dict(foundry_features=foundry_features, api_version=api_version, limit=limit, offset=offset),
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
            dict(session_id=session_id, foundry_features=foundry_features, api_version=api_version),
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
            dict(session_id=session_id, foundry_features=foundry_features, api_version=api_version),
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
            dict(session_id=session_id, foundry_features=foundry_features, api_version=api_version),
            _models.HeartbeatResponse,
            kwargs,
        )


class TrainingOperations(_generated.TrainingOperations):
    @overload
    async def begin_forward_backward(
        self,
        session_id: str,
        request: _models.ForwardBackwardRequest,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...
    @overload
    async def begin_forward_backward(
        self,
        session_id: str,
        request: JSON,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...
    @overload
    async def begin_forward_backward(
        self,
        session_id: str,
        request: IO[bytes],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...

    @distributed_trace_async
    async def begin_forward_backward(
        self,
        session_id: str,
        request: Union[_models.ForwardBackwardRequest, JSON, IO[bytes]],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]:
        return await _begin_async(
            self,
            _builders.build_training_forward_backward_request,
            dict(session_id=session_id, foundry_features=foundry_features, api_version=api_version),
            kwargs,
            request,
        )

    @overload
    async def begin_optim_step(
        self,
        session_id: str,
        request: _models.OptimStepRequest,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...
    @overload
    async def begin_optim_step(
        self,
        session_id: str,
        request: JSON,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...
    @overload
    async def begin_optim_step(
        self,
        session_id: str,
        request: IO[bytes],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...

    @distributed_trace_async
    async def begin_optim_step(
        self,
        session_id: str,
        request: Union[_models.OptimStepRequest, JSON, IO[bytes]],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]:
        return await _begin_async(
            self,
            _builders.build_training_optim_step_request,
            dict(session_id=session_id, foundry_features=foundry_features, api_version=api_version),
            kwargs,
            request,
        )


class CheckpointsOperations(_generated.CheckpointsOperations):
    @overload
    async def begin_save(
        self,
        session_id: str,
        checkpoint: _models.SaveCheckpointRequest,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...
    @overload
    async def begin_save(
        self,
        session_id: str,
        checkpoint: JSON,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...
    @overload
    async def begin_save(
        self,
        session_id: str,
        checkpoint: IO[bytes],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...

    @distributed_trace_async
    async def begin_save(
        self,
        session_id: str,
        checkpoint: Union[_models.SaveCheckpointRequest, JSON, IO[bytes]],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]:
        return await _begin_async(
            self,
            _builders.build_checkpoints_save_request,
            dict(session_id=session_id, foundry_features=foundry_features, api_version=api_version),
            kwargs,
            checkpoint,
        )

    @overload
    async def begin_save_sampler_weights(
        self,
        session_id: str,
        checkpoint: _models.SaveSamplerWeightsRequest,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...
    @overload
    async def begin_save_sampler_weights(
        self,
        session_id: str,
        checkpoint: JSON,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...
    @overload
    async def begin_save_sampler_weights(
        self,
        session_id: str,
        checkpoint: IO[bytes],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...

    @distributed_trace_async
    async def begin_save_sampler_weights(
        self,
        session_id: str,
        checkpoint: Union[_models.SaveSamplerWeightsRequest, JSON, IO[bytes]],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]:
        return await _begin_async(
            self,
            _builders.build_checkpoints_save_sampler_weights_request,
            dict(session_id=session_id, foundry_features=foundry_features, api_version=api_version),
            kwargs,
            checkpoint,
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
            dict(session_id=session_id, foundry_features=foundry_features, api_version=api_version),
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
            dict(
                session_id=session_id,
                checkpoint_id=checkpoint_id,
                foundry_features=foundry_features,
                api_version=api_version,
            ),
            _models.CheckpointInfo,
            kwargs,
        )


class SamplingOperations(_generated.SamplingOperations):
    @overload
    async def begin_sample(
        self,
        session_id: str,
        sample: _models.SampleRequest,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...
    @overload
    async def begin_sample(
        self,
        session_id: str,
        sample: JSON,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...
    @overload
    async def begin_sample(
        self,
        session_id: str,
        sample: IO[bytes],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]: ...

    @distributed_trace_async
    async def begin_sample(
        self,
        session_id: str,
        sample: Union[_models.SampleRequest, JSON, IO[bytes]],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.OperationResult]:
        return await _begin_async(
            self,
            _build_sampling_request,
            dict(session_id=session_id, foundry_features=foundry_features, api_version=api_version),
            kwargs,
            sample,
        )


class Operations(_generated.Operations):
    @distributed_trace_async
    async def get(
        self,
        session_id: str,
        operation_id: str,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> _models.OperationResult:
        return await _read_async(
            self,
            _builders.build_operations_get_request,
            dict(
                session_id=session_id,
                request_id_parameter=operation_id,
                foundry_features=foundry_features,
                api_version=api_version,
            ),
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
