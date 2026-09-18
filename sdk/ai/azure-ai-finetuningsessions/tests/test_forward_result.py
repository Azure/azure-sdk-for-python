from azure.ai.finetuning_sessions._patch import (
    _combine_fwd_bwd_results,
    _LOOM_SUBPATH_TO_OP_TYPE,
    _normalize_loom_result,
)
from azure.ai.finetuning_sessions.aio import _patch as _aio_patch
from azure.ai.finetuning_sessions._utils.model_base import _deserialize
from azure.ai.finetuning_sessions.models import (
    ForwardBackwardOperationResult,
    OperationResult,
    SampleOperationResult,
)


def _forward_result(output_id: str, *, tokens: int = 0, duration_s: float = 0.0) -> ForwardBackwardOperationResult:
    return ForwardBackwardOperationResult(
        {
            "loss_fn_output_type": "scalar",
            "loss_fn_outputs": [{"id": output_id}],
            "metrics": {
                "prefill_tokens": tokens,
                "prefill_duration_s": duration_s,
                "prefill_tokens_per_sec": tokens / duration_s if duration_s else None,
                "prefill_cache_hit_tokens": None,
            },
        }
    )


def test_forward_result_does_not_invent_total_loss():
    normalized = _normalize_loom_result(
        {
            "loss_fn_output_type": "scalar",
            "loss_fn_outputs": [{"logprobs": [-0.3, -0.2]}],
            "metrics": {},
        },
        _LOOM_SUBPATH_TO_OP_TYPE["forward"],
        "request-1",
    )

    result = _deserialize(OperationResult, normalized)

    assert isinstance(result, ForwardBackwardOperationResult)
    assert result.loss_fn_output_type == "scalar"
    assert result.loss_fn_outputs == [{"logprobs": [-0.3, -0.2]}]
    assert result.metrics == {}
    assert result.total_loss is None


def test_combine_forward_results_preserves_outputs_without_total_loss():
    result = _combine_fwd_bwd_results(
        [
            _forward_result("first", tokens=30, duration_s=2.0),
            _forward_result("second", tokens=20, duration_s=3.0),
        ],
        [1, 1],
    )

    assert isinstance(result, ForwardBackwardOperationResult)
    assert result.loss_fn_outputs == [{"id": "first"}, {"id": "second"}]
    assert result.total_loss is None
    assert result.metrics["prefill_tokens"] == 50
    assert result.metrics["prefill_duration_s"] == 5.0
    assert result.metrics["prefill_tokens_per_sec"] == 10.0
    assert result.metrics["prefill_cache_hit_tokens"] is None


def test_combine_training_results_sums_windows_and_recomputes_throughput():
    results = [
        ForwardBackwardOperationResult(
            {
                "loss_fn_output_type": "scalar",
                "loss_fn_outputs": [],
                "metrics": {
                    "training_tokens": 30,
                    "training_duration_s": 2.0,
                    "training_tokens_per_sec": 15.0,
                },
            }
        ),
        ForwardBackwardOperationResult(
            {
                "loss_fn_output_type": "scalar",
                "loss_fn_outputs": [],
                "metrics": {
                    "training_tokens": 20,
                    "training_duration_s": 3.0,
                    "training_tokens_per_sec": 6.7,
                },
            }
        ),
    ]

    combined = _combine_fwd_bwd_results(results, [1, 1])

    assert combined.metrics["training_tokens"] == 50
    assert combined.metrics["training_duration_s"] == 5.0
    assert combined.metrics["training_tokens_per_sec"] == 10.0


def test_forward_backward_promotes_reported_total_loss():
    normalized = _normalize_loom_result(
        {"metrics": {"total_loss:sum": 1.25}},
        "forward_backward",
        "request-2",
    )

    result = _deserialize(OperationResult, normalized)

    assert isinstance(result, ForwardBackwardOperationResult)
    assert result.total_loss == 1.25


def test_sample_result_preserves_cogs_metrics():
    normalized = _normalize_loom_result(
        {
            "sequences": [],
            "metrics": {
                "prefill_tokens": 12,
                "prefill_duration_s": 0.25,
                "prefill_tokens_per_sec": 48.0,
                "prefill_cache_hit_tokens": 8,
                "sample_tokens": 6,
                "sample_duration_s": 0.25,
                "sample_tokens_per_sec": 24.0,
            },
        },
        "sample",
        "request-sample",
    )

    result = _deserialize(OperationResult, normalized)

    assert isinstance(result, SampleOperationResult)
    assert result.metrics["prefill_cache_hit_tokens"] == 8
    assert result.metrics["sample_tokens_per_sec"] == 24.0


async def test_pending_forward_results_use_forward_combiner(monkeypatch):
    async def _poll_with_resubmit(client, session_id, request_id, *args, **kwargs):
        del client, session_id, args, kwargs
        return _forward_result(request_id)

    monkeypatch.setattr(_aio_patch, "_poll_with_resubmit", _poll_with_resubmit)
    posted = [
        _aio_patch._PostSpec("first", "forward", "/forward", {}),
        _aio_patch._PostSpec("second", "forward", "/forward", {}),
    ]
    pending = _aio_patch.PendingRequests(
        object(),
        "model_test",
        posted,
        chunks=[["datum-1"], ["datum-2"]],
    )

    result = await pending.poll_result()

    assert isinstance(result, ForwardBackwardOperationResult)
    assert result.loss_fn_outputs == [{"id": "first"}, {"id": "second"}]
    assert result.total_loss is None
