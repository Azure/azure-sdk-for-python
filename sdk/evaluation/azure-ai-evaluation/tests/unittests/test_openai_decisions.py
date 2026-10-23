# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""OpenAI protocol checks on the shared Decision transport and scoring path."""

import asyncio
import json
from copy import deepcopy
from unittest.mock import AsyncMock

import pytest
from aiohttp import web

from azure.ai.evaluation._evaluators._common._model_runners import DecisionModelRunner
from azure.ai.evaluation._evaluators._common._decision_strategy import DecisionEvaluationStrategy, LikertScoring
from azure.ai.evaluation._evaluators._common._decision_strategy import _native_answer_provenance
from azure.ai.evaluation._evaluators._common._openai_decisions import encode_request, decode_response
from azure.ai.evaluation._exceptions import EvaluationException, ErrorTarget

CONFIG = {
    "type": "decision",
    "decision_protocol": "openai",
    "azure_endpoint": "https://test.openai.azure.com",
    "azure_deployment": "judge",
    "api_key": "test-only",
}
QUESTIONS = {
    "status": {"type": "noul", "instructions": "Applicable?", "criteria": {"true": "Has evidence", "false": "Empty"}},
    "quality": {"type": "score", "instructions": "Quality?", "criteria": ["Bad", "Okay", "Good"]},
}


def response():
    return {
        "model": "gpt-6-luna-2026-09-22",
        "usage": {
            "input_tokens": 12,
            "output_tokens": 3,
            "total_tokens": 15,
            "input_tokens_details": {"cached_tokens": 4, "cache_write_tokens": 2},
            "output_tokens_details": {"reasoning_tokens": 1},
        },
        "answers": [
            {"type": "predicate", "name": "status", "probability": 0.9},
            {
                "type": "score",
                "name": "quality",
                "confidence": 0.4,
                "score": 0.8,
                "probabilities": [
                    {"value": 0, "label": "0", "probability": 0.4},
                    {"value": 1, "label": "1", "probability": 0.4},
                    {"value": 2, "label": "2", "probability": 0.2},
                ],
            },
        ],
    }


def test_encode_keeps_evidence_and_both_boolean_criteria():
    request = encode_request({"response": "\u00e9vidence"}, QUESTIONS, "judge")
    assert json.loads(request["input"]) == {"response": "\u00e9vidence"}
    assert request["model"] == "judge" and "state" not in request
    assert request["questions"][0] == {
        "name": "status",
        "type": "predicate",
        "instructions": "Applicable?\n\nThe predicate is true when: Has evidence\nThe predicate is false when: Empty",
    }
    assert request["questions"][1]["levels"] == [
        {"label": str(i), "description": value} for i, value in enumerate(["Bad", "Okay", "Good"])
    ]


@pytest.mark.parametrize(
    "questions",
    [
        {},
        {str(i): QUESTIONS["status"] for i in range(401)},
        {"q": {"type": "choice", "instructions": "Choose"}},
        {"q": {"type": "score", "instructions": "Score", "criteria": ["one"]}},
        {"q": {"type": "noul", "instructions": "Boolean", "criteria": {"true": "yes"}}},
    ],
)
def test_unsupported_requests_fail_before_transport(questions):
    with pytest.raises(ValueError):
        encode_request("evidence", questions, "judge")


@pytest.mark.parametrize(
    "endpoint",
    [
        "https://test.openai.azure.com",
        "https://test.openai.azure.com/openai/",
        "https://test.openai.azure.com/openai/v1/",
    ],
)
def test_endpoint_forms(endpoint):
    runner = DecisionModelRunner({**CONFIG, "azure_endpoint": endpoint})
    assert runner._url == "https://test.openai.azure.com/openai/v1/decisions"


def test_selection_is_explicit_and_preserves_microsoft_default():
    config = dict(CONFIG)
    config.pop("decision_protocol")
    assert DecisionModelRunner(config)._url.endswith("/providers/microsoft/v1/systemone")
    for changes in (
        {"decision_protocol": "invalid"},
        {"decision_protocol": []},
        {"azure_endpoint": "https://test.services.ai.azure.com/api/projects/test"},
    ):
        with pytest.raises(EvaluationException):
            DecisionModelRunner({**CONFIG, **changes})


def test_reordered_answers_preserve_original_provenance():
    payload = response()
    payload["answers"].reverse()
    payload["answers"][0]["additive_field"] = "allowed"
    decoded = decode_response(payload, QUESTIONS)
    assert decoded["answers"]["status"]["noul"] == 0.9
    assert decoded["answers"]["quality"]["_native_answer"] == payload["answers"][0]


def test_legacy_provider_fields_cannot_select_openai_provenance():
    answer = {"type": "noul", "noul": 0.9, "_native_answer": {"type": "predicate", "probability": 0.1}}
    assert _native_answer_provenance(answer) == answer


@pytest.mark.parametrize(
    "mutation",
    [
        lambda p: p["answers"].pop(),
        lambda p: p["answers"].append(deepcopy(p["answers"][0])),
        lambda p: p["answers"][0].update(name="unknown"),
        lambda p: p["answers"][0].update(type="refusal"),
        lambda p: p["answers"][1].update(type="refusal"),
        lambda p: p["answers"][0].update(probability=float("nan")),
        lambda p: p["answers"][0].update(probability=True),
        lambda p: p["answers"][1].update(score=float("inf")),
        lambda p: p["answers"][1]["probabilities"][0].update(value=True),
        lambda p: p["answers"][1]["probabilities"][0].update(value=1),
        lambda p: p["answers"][1]["probabilities"][0].update(label="wrong"),
        lambda p: p["answers"][1]["probabilities"][0].update(probability=0.1),
    ],
)
def test_malformed_or_refused_answers_are_not_scores(mutation):
    payload = response()
    mutation(payload)
    with pytest.raises(ValueError):
        decode_response(payload, QUESTIONS)


def test_shared_strategy_keeps_argmax_ties_threshold_and_usage():
    async def run():
        runner = DecisionModelRunner(CONFIG)
        runner._post = AsyncMock(return_value=response())
        strategy = DecisionEvaluationStrategy(
            runner,
            result_key="quality",
            error_target=ErrorTarget.EVALUATE,
            questions=QUESTIONS,
            scoring=LikertScoring(3),
            threshold=2,
            timeout=5,
        )
        result = await strategy.evaluate({"response": "Evidence"})
        assert result["quality"] == 1 and result["quality_passed"] is False
        assert result["quality_total_tokens"] == 15
        provenance = result["quality_properties"]["decision_model"]
        assert provenance["protocol"] == "openai"
        assert provenance["native_answer"]["score"] == 0.8
        assert provenance["native_status_answer"]["type"] == "predicate"
        assert provenance["usage_details"]["input_tokens_details"]["cached_tokens"] == 4

    asyncio.run(run())


def test_refusal_preserves_known_usage_on_failure():
    async def run():
        runner = DecisionModelRunner(CONFIG)
        payload = response()
        payload["answers"][1] = {"name": "quality", "type": "refusal"}
        runner._post = AsyncMock(return_value=payload)
        with pytest.raises(EvaluationException, match="refused") as failure:
            await runner(state="input", questions=QUESTIONS, timeout=5)
        assert failure.value.properties["total_tokens"] == 15
        assert failure.value.properties["decision_model"]["protocol"] == "openai"

    asyncio.run(run())


def test_native_http_transport_uses_decisions_route_key_and_retries():
    async def run():
        calls = []

        async def handle(request):
            calls.append((request.path, request.headers.get("api-key"), await request.json()))
            if len(calls) == 1:
                return web.json_response(
                    {"error": {"code": "RateLimitExceeded"}}, status=429, headers={"Retry-After": "0"}
                )
            return web.json_response(response())

        app = web.Application()
        app.router.add_post("/openai/v1/decisions", handle)
        server = web.AppRunner(app)
        await server.setup()
        site = web.TCPSite(server, "127.0.0.1", 0)
        await site.start()
        try:
            port = site._server.sockets[0].getsockname()[1]
            runner = DecisionModelRunner({**CONFIG, "azure_endpoint": f"http://127.0.0.1:{port}"}, max_retries=1)
            result = await runner(state="text", questions=QUESTIONS, timeout=5)
            assert len(calls) == 2
            assert calls[0][0:2] == ("/openai/v1/decisions", "test-only")
            assert calls[0][2]["input"] == "text"
            assert result["answers"]["status"]["noul"] == 0.9
        finally:
            await server.cleanup()

    asyncio.run(run())
