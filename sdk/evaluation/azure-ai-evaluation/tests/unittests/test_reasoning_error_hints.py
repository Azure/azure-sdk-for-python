import pytest

from azure.ai.evaluation._legacy.prompty._exceptions import WrappedOpenAIError


class _FakeOpenAIError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        self._msg = msg

    def __str__(self) -> str:  # pragma: no cover
        return self._msg


def test_reasoning_hint_for_max_tokens():
    # Simulate common service error when using reasoning models with max_tokens
    fake = _FakeOpenAIError("Unrecognized request argument supplied: max_tokens")
    msg = WrappedOpenAIError.to_openai_error_message(fake)
    assert "is_reasoning_model=True" in msg
    assert "max_completion_tokens" in msg


def test_reasoning_hint_for_sampling_params():
    # Simulate a not supported message for temperature
    fake = _FakeOpenAIError("Parameter 'temperature' is not supported by this model")
    msg = WrappedOpenAIError.to_openai_error_message(fake)
    assert "is_reasoning_model=True" in msg
    assert "sampling parameters" in msg or "temperature/top_p" in msg
