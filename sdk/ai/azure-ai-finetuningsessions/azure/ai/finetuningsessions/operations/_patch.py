# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Supported operation subclasses preserving the tested preview signatures.

The seven renamed legacy methods deliberately replace the generated Python
keywords. Local override annotations below are limited to that verified API
adaptation; they do not suppress argument or implementation checking.
"""

from collections.abc import MutableMapping
from typing import Any, IO, Literal, Optional, Union, overload

from azure.core.polling import LROPoller
from azure.core.tracing.decorator import distributed_trace

from .. import models as _models
from ..models._enums import FoundryFeaturesOptInKeys
from .._operation_compat import _begin, _read, _build_sampling_request
from . import _operations as _generated

JSON = MutableMapping[str, Any]


class SessionsOperations(_generated.SessionsOperations):
    # Preserve the published preview 'body' keyword across overloads and implementation.
    @overload  # type: ignore[override]
    def begin_create(  # pylint: disable=arguments-renamed
        self,
        body: _models.CreateSessionRequest,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> LROPoller[_models.OperationResult]: ...
    @overload
    def begin_create(  # pylint: disable=arguments-renamed
        self,
        body: JSON,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> LROPoller[_models.OperationResult]: ...
    @overload
    def begin_create(  # pylint: disable=arguments-renamed
        self,
        body: IO[bytes],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> LROPoller[_models.OperationResult]: ...

    @distributed_trace
    def begin_create(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        body: Union[_models.CreateSessionRequest, JSON, IO[bytes]],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> LROPoller[_models.OperationResult]:
        # pylint: disable=arguments-renamed
        return _begin(
            self,
            _generated.build_sessions_create_request,
            {"foundry_features": foundry_features, "api_version": api_version},
            kwargs,
            body,
        )

    @distributed_trace
    def create(
        self,
        body: Union[_models.CreateSessionRequest, JSON, IO[bytes]],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> JSON:
        return _read(
            self,
            _generated.build_sessions_create_request,
            {"foundry_features": foundry_features, "api_version": api_version},
            None,
            kwargs,
            body,
        )

    @distributed_trace
    def list(
        self,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **kwargs: Any,
    ) -> _models.SessionList:
        return _read(
            self,
            _generated.build_sessions_list_request,
            {
                "foundry_features": foundry_features,
                "api_version": api_version,
                "limit": limit,
                "offset": offset,
            },
            _models.SessionList,
            kwargs,
        )

    @distributed_trace
    def get(
        self,
        session_id: str,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> _models.Session:
        return _read(
            self,
            _generated.build_sessions_get_request,
            {"session_id": session_id, "foundry_features": foundry_features, "api_version": api_version},
            _models.Session,
            kwargs,
        )

    @distributed_trace
    def begin_unload(
        self,
        session_id: str,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> LROPoller[_models.OperationResult]:
        return _begin(
            self,
            _generated.build_sessions_unload_request,
            {"session_id": session_id, "foundry_features": foundry_features, "api_version": api_version},
            kwargs,
        )

    @distributed_trace
    def heartbeat(
        self,
        session_id: str,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> _models.HeartbeatResponse:
        return _read(
            self,
            _generated.build_sessions_heartbeat_request,
            {"session_id": session_id, "foundry_features": foundry_features, "api_version": api_version},
            _models.HeartbeatResponse,
            kwargs,
        )


class TrainingOperations(_generated.TrainingOperations):
    # Preserve the published preview 'body' keyword across overloads and implementation.
    @overload  # type: ignore[override]
    def begin_forward_backward(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: _models.ForwardBackwardRequest,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> LROPoller[_models.OperationResult]: ...
    @overload
    def begin_forward_backward(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: JSON,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> LROPoller[_models.OperationResult]: ...
    @overload
    def begin_forward_backward(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: IO[bytes],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> LROPoller[_models.OperationResult]: ...

    @distributed_trace
    def begin_forward_backward(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        session_id: str,
        body: Union[_models.ForwardBackwardRequest, JSON, IO[bytes]],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> LROPoller[_models.OperationResult]:
        # pylint: disable=arguments-renamed
        return _begin(
            self,
            _generated.build_training_forward_backward_request,
            {"session_id": session_id, "foundry_features": foundry_features, "api_version": api_version},
            kwargs,
            body,
        )

    # Preserve the published preview 'body' keyword across overloads and implementation.
    @overload  # type: ignore[override]
    def begin_optim_step(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: _models.OptimStepRequest,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> LROPoller[_models.OperationResult]: ...
    @overload
    def begin_optim_step(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: JSON,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> LROPoller[_models.OperationResult]: ...
    @overload
    def begin_optim_step(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: IO[bytes],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> LROPoller[_models.OperationResult]: ...

    @distributed_trace
    def begin_optim_step(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        session_id: str,
        body: Union[_models.OptimStepRequest, JSON, IO[bytes]],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> LROPoller[_models.OperationResult]:
        # pylint: disable=arguments-renamed
        return _begin(
            self,
            _generated.build_training_optim_step_request,
            {"session_id": session_id, "foundry_features": foundry_features, "api_version": api_version},
            kwargs,
            body,
        )


class CheckpointsOperations(_generated.CheckpointsOperations):
    # Preserve the published preview 'body' keyword across overloads and implementation.
    @overload  # type: ignore[override]
    def begin_save(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: _models.SaveCheckpointRequest,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> LROPoller[_models.OperationResult]: ...
    @overload
    def begin_save(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: JSON,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> LROPoller[_models.OperationResult]: ...
    @overload
    def begin_save(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: IO[bytes],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> LROPoller[_models.OperationResult]: ...

    @distributed_trace
    def begin_save(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        session_id: str,
        body: Union[_models.SaveCheckpointRequest, JSON, IO[bytes]],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> LROPoller[_models.OperationResult]:
        # pylint: disable=arguments-renamed
        return _begin(
            self,
            _generated.build_checkpoints_save_request,
            {"session_id": session_id, "foundry_features": foundry_features, "api_version": api_version},
            kwargs,
            body,
        )

    # Preserve the published preview 'body' keyword across overloads and implementation.
    @overload  # type: ignore[override]
    def begin_save_sampler_weights(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: _models.SaveSamplerWeightsRequest,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> LROPoller[_models.OperationResult]: ...
    @overload
    def begin_save_sampler_weights(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: JSON,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> LROPoller[_models.OperationResult]: ...
    @overload
    def begin_save_sampler_weights(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: IO[bytes],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> LROPoller[_models.OperationResult]: ...

    @distributed_trace
    def begin_save_sampler_weights(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        session_id: str,
        body: Union[_models.SaveSamplerWeightsRequest, JSON, IO[bytes]],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> LROPoller[_models.OperationResult]:
        # pylint: disable=arguments-renamed
        return _begin(
            self,
            _generated.build_checkpoints_save_sampler_weights_request,
            {"session_id": session_id, "foundry_features": foundry_features, "api_version": api_version},
            kwargs,
            body,
        )

    @distributed_trace
    def list(
        self,
        session_id: str,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> _models.CheckpointList:
        return _read(
            self,
            _generated.build_checkpoints_list_request,
            {"session_id": session_id, "foundry_features": foundry_features, "api_version": api_version},
            _models.CheckpointList,
            kwargs,
        )

    @distributed_trace
    def get(
        self,
        session_id: str,
        checkpoint_id: str,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> _models.CheckpointInfo:
        return _read(
            self,
            _generated.build_checkpoints_get_request,
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
    def begin_sample(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: _models.SampleRequest,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> LROPoller[_models.OperationResult]: ...
    @overload
    def begin_sample(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: JSON,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> LROPoller[_models.OperationResult]: ...
    @overload
    def begin_sample(  # pylint: disable=arguments-renamed
        self,
        session_id: str,
        body: IO[bytes],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        content_type: str = "application/json",
        **kwargs: Any,
    ) -> LROPoller[_models.OperationResult]: ...

    @distributed_trace
    def begin_sample(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        session_id: str,
        body: Union[_models.SampleRequest, JSON, IO[bytes]],
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> LROPoller[_models.OperationResult]:
        # pylint: disable=arguments-renamed
        return _begin(
            self,
            _build_sampling_request,
            {"session_id": session_id, "foundry_features": foundry_features, "api_version": api_version},
            kwargs,
            body,
        )


class Operations(_generated.Operations):
    # Preserve the published preview 'operation_id' keyword.
    @distributed_trace
    def get(  # type: ignore[override]  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        session_id: str,
        operation_id: str,
        *,
        foundry_features: Literal[FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW],
        api_version: str,
        **kwargs: Any,
    ) -> _models.OperationResult:
        # pylint: disable=arguments-renamed
        return _read(
            self,
            _generated.build_operations_get_request,
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
