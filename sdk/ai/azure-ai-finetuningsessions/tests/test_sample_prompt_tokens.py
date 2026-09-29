import json

import pytest
from azure.ai.finetuningsessions._patch import _normalize_loom_result
from azure.ai.finetuningsessions._utils.model_base import _deserialize
from azure.ai.finetuningsessions.models import (
    OperationResult,
    SampledSequence,
    SampleOperationResult,
)


def _read_result(body):
    body = json.loads(json.dumps(body))
    return _deserialize(OperationResult, _normalize_loom_result(body, "sample", "request-sample"))


@pytest.mark.parametrize("num_samples", [1, 4])
@pytest.mark.parametrize("count", [0, 262144])
def test_backend_prompt_tokens_counted_once(num_samples, count):
    result = _read_result(
        {
            "sequences": [{"tokens": [123], "logprobs": [-0.5]} for _ in range(num_samples)],
            "prompt_tokens": count,
        }
    )

    assert isinstance(result, SampleOperationResult)
    assert len(result.sequences) == num_samples
    assert all(isinstance(seq, SampledSequence) for seq in result.sequences)
    assert result.prompt_tokens == count
    assert type(result.prompt_tokens) is int


@pytest.mark.parametrize(
    "extra",
    [
        {},
        {"prompt_tokens": None},
        {"metrics": {"prefill_tokens": 262144}},
        {"usage": {"prompt_tokens": 262144}},
        {"prompt_logprobs": [-0.5, -0.2]},
    ],
)
def test_missing_prompt_count_is_unverified_without_fallback(extra):
    result = _read_result({"sequences": [], **extra})

    assert isinstance(result, SampleOperationResult)
    assert result.prompt_tokens is None


@pytest.mark.parametrize("invalid", [True, False, -1, 262144.0, 1.5, "262144", [], {}, [262144]])
def test_invalid_prompt_count_is_not_coerced(invalid):
    result = _read_result({"sequences": [], "prompt_tokens": invalid})

    assert result.prompt_tokens is None


def test_direct_generated_style_deserialization():
    result = _deserialize(SampleOperationResult, {"sequences": [], "prompt_tokens": 262144})
    assert result.prompt_tokens == 262144
    assert _deserialize(SampleOperationResult, {"sequences": []}).prompt_tokens is None