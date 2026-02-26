# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from __future__ import annotations

import json
import os
from typing import Any, Mapping, Optional

from devtools_testutils import add_general_string_sanitizer

from test_samples_helpers import get_sample_env_vars

fine_tuning_instructions = """We just ran Python code and captured a Python array of print statements.
Validate whether sample execution/output is correct for a fine-tuning workflow.

Successful output typically shows one or more of:
- Training/validation files prepared or uploaded successfully.
- Fine-tuning job creation with a returned job id/name.
- Job details/status output that indicates the request was accepted and processed.

Mark `correct = false` for:
- Exceptions, stack traces, explicit error/failure messages.
- Authentication/authorization/service errors that block job creation.
- File upload/read failures for required training/validation data.
- Fine-tuning job creation failures or malformed output that indicates broken processing.

Important distinction:
- Intermediate/transitional job states (for example queued/running) are valid and should not fail by themselves.
- The output does not need to show completed training unless the sample is explicitly designed to wait for completion.

Mark `correct = true` when execution succeeds and output is consistent with initiating/inspecting
the intended fine-tuning workflow.

Always include `reason` with a concise explanation tied to the observed print output."""


SCRUBBED_FINE_TUNING_CONFIG: dict[str, Any] = {
    "sft": {
        "openai": {"model_name": "sanitized-sft-openai-model"},
        "oss": {"model_name": "sanitized-sft-oss-model"},
        "training_file_name": "sft_training_set.jsonl",
        "validation_file_name": "sft_validation_set.jsonl",
    },
    "dpo": {
        "openai": {"model_name": "sanitized-dpo-openai-model"},
        "training_file_name": "dpo_training_set.jsonl",
        "validation_file_name": "dpo_validation_set.jsonl",
    },
    "rft": {
        "openai": {"model_name": "sanitized-rft-openai-model"},
        "training_file_name": "rft_training_set.jsonl",
        "validation_file_name": "rft_validation_set.jsonl",
    },
    "n_epochs": 1,
    "batch_size": 1,
    "learning_rate_multiplier": 1.0,
}

scrubbed_fine_tuning_bindings = json.dumps(SCRUBBED_FINE_TUNING_CONFIG)


def _is_live_mode() -> bool:
    return os.environ.get("AZURE_TEST_RUN_LIVE") == "true"


def _get_customization_from_sample_name(sample_name: str) -> str:
    if "dpo" in sample_name:
        return "dpo"
    if "reinforcement" in sample_name or "rft" in sample_name:
        return "rft"
    if "supervised" in sample_name:
        return "sft"
    return ""


def _get_env_vars_from_fine_tuning_bindings(
    *,
    sample_name: str,
    customization_config: Mapping[str, Any],  # from fine_tuning_bindings env vars
) -> tuple[str, str, str]:
    model_name = ""
    model_type = "oss" if "oss" in sample_name else "openai"
    model_config = customization_config.get(model_type)
    if isinstance(model_config, dict):
        model_name = str(model_config.get("model_name"))

    training_file_path = customization_config.get("training_file_name", "")
    validation_file_path = customization_config.get("validation_file_name", "")

    return model_name, training_file_path, validation_file_path


def _parse_fine_tuning_bindings(bindings: Any) -> Optional[Mapping[str, Any]]:
    if isinstance(bindings, str):
        bindings = bindings.strip()
        if not bindings:
            return None
        try:
            parsed = json.loads(bindings)
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, dict) else None

    if isinstance(bindings, dict):
        return bindings

    return None


def get_fine_tuning_sample_env_vars(
    sample_path: str,
    env_kwargs: Mapping[str, Any],
) -> dict[str, str]:
    """Build fine-tuning sample environment variables for the target sample file.

    This helper determines the fine-tuning customization type from ``sample_path``
    (``sft``, ``dpo``, or ``rft``), reads fine-tuning bindings from live or playback
    sources, and returns a sample env-var mapping with:

    - ``MODEL_NAME``
    - ``TRAINING_FILE_PATH``
    - ``VALIDATION_FILE_PATH``

    Behavior by mode:
    - Live mode (``AZURE_TEST_RUN_LIVE=true``): reads ``FINE_TUNING_BINDINGS`` from
      process environment and registers test-proxy sanitizers so real values in
      recordings are replaced by scrubbed values.
    - Playback mode: uses ``scrubbed_fine_tuning_bindings`` directly.

    Args:
        sample_path: Absolute or relative path of the sample file being executed.
        env_kwargs: Existing environment key/value mapping used by sample executors.

    Returns:
        A dictionary of environment variables for sample execution. Returns an empty
        dictionary when customization type cannot be inferred or bindings are invalid.
    """
    sample_name = os.path.basename(sample_path).lower()
    customization = _get_customization_from_sample_name(sample_name)
    live_mode = _is_live_mode()

    if not customization:
        return {}

    fine_tuning_source = os.environ.get("FINE_TUNING_BINDINGS") if live_mode else SCRUBBED_FINE_TUNING_CONFIG
    fine_tuning_config = _parse_fine_tuning_bindings(fine_tuning_source)
    if fine_tuning_config is None:
        return {}

    customization_config = fine_tuning_config.get(customization)
    if not isinstance(customization_config, dict):
        return {}

    model_name, training_file_path, validation_file_path = _get_env_vars_from_fine_tuning_bindings(
        sample_name=sample_name,
        customization_config=customization_config,
    )

    scrubbed_customization_config = SCRUBBED_FINE_TUNING_CONFIG.get(customization)
    if not isinstance(scrubbed_customization_config, dict):
        return {}

    scrubbed_model_name, scrubbed_training_file_path, scrubbed_validation_file_path = (
        _get_env_vars_from_fine_tuning_bindings(
            sample_name=sample_name,
            customization_config=scrubbed_customization_config,
        )
    )

    mapping = get_sample_env_vars(env_kwargs=env_kwargs)
    mapping.update(
        {
            "MODEL_NAME": model_name,
            "TRAINING_FILE_PATH": training_file_path,
            "VALIDATION_FILE_PATH": validation_file_path,
        }
    )

    if live_mode:
        sanitizer_pairs = [
            (model_name, scrubbed_model_name),
            (training_file_path, scrubbed_training_file_path),
            (validation_file_path, scrubbed_validation_file_path),
        ]
        for target_value, scrubbed_value in sanitizer_pairs:
            if not isinstance(target_value, str) or not isinstance(scrubbed_value, str):
                continue
            if not target_value or not scrubbed_value or target_value == scrubbed_value:
                continue
            add_general_string_sanitizer(
                function_scoped=True,
                value=scrubbed_value,
                target=target_value,
            )

    return mapping
