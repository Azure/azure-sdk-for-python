# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Offline training-loop smoke test; no credentials or endpoint required."""

from azure.ai.finetuningsessions.models import AdamParams, OperationResult, SamplingParams


def test_training_and_sampling_loop(session, batch, transport):
    assert isinstance(session.forward_backward(batch, loss_fn="cross_entropy"), OperationResult)
    assert isinstance(session.optim_step(AdamParams(learning_rate=1e-4)), OperationResult)
    assert isinstance(session.save_weights("checkpoint"), OperationResult)
    sampler = session.save_weights_for_sampler(seq_id=0, path="sampler")
    assert sampler.checkpoint_id == "sampler"
    result = session.sample(
        prompt_tokens=[1, 2, 3],
        sampling_params=SamplingParams(max_tokens=16),
        checkpoint_id=sampler.checkpoint_id,
        num_samples=2,
    )
    assert isinstance(result, OperationResult)
    session.close()
    assert all("/fine_tuning_sessions/" in request.url for request in transport.requests)
