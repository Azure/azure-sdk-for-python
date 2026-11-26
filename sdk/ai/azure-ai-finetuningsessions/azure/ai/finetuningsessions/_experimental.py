# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Validate and warn about experimental SDK requests."""

from collections.abc import Mapping
import json
import warnings

from .experimental import ExperimentalSettings


class ExperimentalWarning(FutureWarning):
    """Warn about an unstable feature without blocking its use."""


def _resolve_experimental_settings(settings: ExperimentalSettings | None) -> ExperimentalSettings:
    if settings is not None and not isinstance(settings, ExperimentalSettings):
        raise TypeError("experimental_settings must be an ExperimentalSettings instance or None")
    return settings if settings is not None else ExperimentalSettings()


def _check_experimental_request(body: object, settings: ExperimentalSettings | None = None) -> None:
    if isinstance(body, bytes):
        body = json.loads(body)
    if not isinstance(body, Mapping):
        return
    losses = []
    for name in ("forward_input", "forward_backward_input", "text_only_input"):
        training_input = body.get(name)
        if isinstance(training_input, Mapping):
            losses.append(training_input.get("loss_fn"))
    sampling_params = body.get("sampling_params")
    capture = isinstance(sampling_params, Mapping) and sampling_params.get("score_centering_head_size", 0)
    if "score_centering" in losses or capture:
        if settings is None or not settings.enable_score_centering:
            raise ValueError(
                "Score centering requires experimental_settings="
                "ExperimentalSettings(enable_score_centering=True) on the client. "
                "Import ExperimentalSettings from azure.ai.finetuningsessions.experimental. "
                "This SDK opt-in does not enable service support or guarantee deployment availability."
            )
        feature, deployments = "score centering", "API, sampler and trainer"
    elif "tis" in losses:
        feature, deployments = "TIS", "API and trainer"
    else:
        return
    warnings.warn(
        f"Native {feature} is experimental and under development. It requires compatible {deployments} "
        "deployments, may change or be unavailable, and is used at your own risk.",
        ExperimentalWarning,
        stacklevel=2,
    )
