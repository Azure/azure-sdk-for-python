# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import json

import pytest

from azure.ai.finetuningsessions._experimental import ExperimentalWarning, _check_experimental_request
from azure.ai.finetuningsessions._patch import _SdkJSONEncoder
from azure.ai.finetuningsessions.experimental import ExperimentalSettings
from azure.ai.finetuningsessions.models import LossFn, LossFnInputs, SampledSequence, SamplingParams, TensorData


def test_native_score_centering_request_preserves_multidimensional_head_tensors():
    inputs = LossFnInputs(
        target_tokens=TensorData(data=[2, 3]),
        weights=TensorData(data=[1.0, 1.0]),
        score_centering_head_tokens=TensorData(data=[2, 7, 3, 8], shape=[2, 2]),
        score_centering_head_logprobs=TensorData(data=[-1.0, -2.0, -3.0, -4.0], shape=[2, 2]),
        score_centering_head_mask=TensorData(data=[1, 1, 1, 0], shape=[2, 2]),
    )
    payload = json.loads(
        json.dumps(
            {"forward_backward_input": {"loss_fn": LossFn.SCORE_CENTERING, "data": [{"loss_fn_inputs": inputs}]}},
            cls=_SdkJSONEncoder,
            exclude_readonly=True,
        )
    )
    heads = payload["forward_backward_input"]["data"][0]["loss_fn_inputs"]
    assert heads["score_centering_head_tokens"] == {"data": [2, 7, 3, 8], "shape": [2, 2]}
    assert heads["score_centering_head_logprobs"]["shape"] == [2, 2]
    with pytest.warns(ExperimentalWarning, match="Native score centering"):
        _check_experimental_request(payload, ExperimentalSettings(enable_score_centering=True))


def test_decode_head_capture_and_provenance_roundtrip():
    params = SamplingParams(
        max_tokens=4,
        temperature=1.0,
        top_p=1.0,
        top_k=-1,
        score_centering_head_size=2,
    )
    assert json.loads(json.dumps(params, cls=_SdkJSONEncoder))["score_centering_head_size"] == 2
    sequence = SampledSequence(
        {
            "tokens": [9],
            "logprobs": [-2.0],
            "score_centering_head_tokens": [[2, 3]],
            "score_centering_head_logprobs": [[-1.0, -1.0]],
            "score_centering_provenance": {"checkpoint_id": "test", "source": "decode_time"},
        }
    )
    assert sequence.score_centering_head_tokens == [[2, 3]]
    assert sequence.score_centering_head_logprobs == [[-1.0, -1.0]]
    assert sequence.score_centering_provenance["source"] == "decode_time"


@pytest.mark.parametrize("settings", [None, ExperimentalSettings()])
@pytest.mark.parametrize(
    "body",
    [
        {"forward_input": {"loss_fn": "score_centering"}},
        {"forward_backward_input": {"loss_fn": "score_centering"}},
        {"text_only_input": {"loss_fn": "score_centering"}},
        {"sampling_params": {"score_centering_head_size": 128}},
    ],
)
def test_score_centering_requires_explicit_opt_in(settings, body):
    with pytest.raises(ValueError, match="ExperimentalSettings\\(enable_score_centering=True\\)"):
        _check_experimental_request(body, settings)


@pytest.mark.parametrize("value", [1, "true", None])
def test_score_centering_opt_in_rejects_non_boolean_values(value):
    with pytest.raises(TypeError, match="enable_score_centering must be a bool"):
        ExperimentalSettings(enable_score_centering=value)
