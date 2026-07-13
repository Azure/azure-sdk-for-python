# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from pathlib import Path
from typing import Any, Dict

from azure.ai.evaluation import AzureOpenAIModelConfiguration
from azure.ai.evaluation._legacy.prompty import AsyncPrompty
from azure.ai.evaluation._constants import DEFAULT_MAX_COMPLETION_TOKENS_REASONING_MODELS

PROMPTY_TEST_DIR = Path(__file__).resolve().parents[1] / "e2etests" / "data"
BASIC_PROMPTY = PROMPTY_TEST_DIR / "basic.prompty"


def _build_prompty_config(model_config: AzureOpenAIModelConfiguration) -> Dict[str, Any]:
    return {"model": {"configuration": {"type": "azure_openai", **model_config}}}


def test_reasoning_model_uses_reasoning_effort_from_kwargs(mock_model_config: AzureOpenAIModelConfiguration):
    prompty = AsyncPrompty(
        BASIC_PROMPTY,
        is_reasoning_model=True,
        reasoning_effort="high",
        **_build_prompty_config(mock_model_config),
    )

    parameters = prompty._data["model"]["parameters"]
    assert parameters["reasoning_effort"] == "high"
    assert "max_tokens" not in parameters
    assert parameters["max_completion_tokens"] == DEFAULT_MAX_COMPLETION_TOKENS_REASONING_MODELS


def test_reasoning_model_does_not_set_reasoning_effort_without_kwargs(
    mock_model_config: AzureOpenAIModelConfiguration,
):
    prompty = AsyncPrompty(
        BASIC_PROMPTY,
        is_reasoning_model=True,
        **_build_prompty_config(mock_model_config),
    )

    parameters = prompty._data["model"]["parameters"]
    assert "reasoning_effort" not in parameters
