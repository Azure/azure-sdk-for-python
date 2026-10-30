# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Offline tests for decision model support in the built-in evaluators.

A fake transport answers every Decision request, so these tests cover the request each evaluator sends,
the scored result and the configuration rules without a network or a Prompty flow.
"""

import asyncio
import hashlib
import json
import logging
import math
import os
import sys
from copy import deepcopy
from unittest.mock import patch

import pytest
from azure.core.credentials import AccessToken
from azure.core.pipeline.transport import HttpResponse
from ruamel.yaml import YAML

from azure.ai.evaluation import (
    CoherenceEvaluator,
    FluencyEvaluator,
    GroundednessEvaluator,
    IntentResolutionEvaluator,
    QAEvaluator,
    RelevanceEvaluator,
    ResponseCompletenessEvaluator,
    RetrievalEvaluator,
    SimilarityEvaluator,
    TaskAdherenceEvaluator,
    ToolCallAccuracyEvaluator,
    _ToolCallSuccessEvaluator,
    _ToolOutputUtilizationEvaluator,
)
from azure.ai.evaluation._evaluators._common import (
    BinaryScoring,
    LikertScoring,
    ModelEvaluatorBase,
    PromptyEvaluatorBase,
    _model_runners,
)
from azure.ai.evaluation._evaluators._common._decision_rubric import decode_message_list, final_assistant_text
from azure.ai.evaluation._evaluators._task_completion import _TaskCompletionEvaluator
from azure.ai.evaluation._evaluators._tool_input_accuracy import _ToolInputAccuracyEvaluator
from azure.ai.evaluation._evaluators._tool_selection import _ToolSelectionEvaluator
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, EvaluationException

pytestmark = pytest.mark.unittest

DECISION_CONFIG = {
    "type": "decision",
    "azure_endpoint": "https://example.services.ai.azure.com",
    "azure_deployment": "Decision-1",
    "api_key": "test-key-value",
}
CHAT_CONFIG = {
    "azure_endpoint": "https://example.openai.azure.com",
    "azure_deployment": "chat-deployment",
    "api_key": "chat-key",
}

QUERY = "What is the weather in Paris?"
RESPONSE = "It is 20C and sunny in Paris."
CONTEXT = "Paris weather report: 20C and sunny."
GROUND_TRUTH = "Paris is 20C and sunny."
TOOL_DEFINITIONS = [
    {
        "name": "fetch_weather",
        "type": "function",
        "description": "Fetches the weather for a location.",
        "parameters": {"type": "object", "properties": {"location": {"type": "string", "description": "City."}}},
    }
]
TOOL_CALLS = [
    {"type": "tool_call", "tool_call_id": "call_1", "name": "fetch_weather", "arguments": {"location": "Paris"}}
]
QUERY_MESSAGES = [
    {"role": "system", "content": "You are a weather assistant."},
    {"role": "user", "content": [{"type": "text", "text": QUERY}]},
]
RESPONSE_MESSAGES = [
    {"role": "assistant", "content": deepcopy(TOOL_CALLS)},
    {
        "role": "tool",
        "tool_call_id": "call_1",
        "content": [{"type": "tool_result", "tool_result": {"temperature": "20C", "sky": "sunny"}}],
    },
    {"role": "assistant", "content": [{"type": "text", "text": RESPONSE}]},
]
TEXT_CONTENT = [{"type": "text", "text": RESPONSE}]
INTERMEDIATE_RESPONSE = [
    {
        "role": "assistant",
        "content": [
            {
                "type": "function_call",
                "tool_call_id": "call_1",
                "name": "fetch_weather",
                "arguments": {"location": "Paris"},
            }
        ],
    }
]
CONVERSATION = {
    "messages": [
        {"role": "user", "content": QUERY, "context": "The user asks about Paris."},
        {"role": "assistant", "content": RESPONSE, "context": CONTEXT, "ground_truth": GROUND_TRUTH},
        {"role": "user", "content": "And in Rome?"},
        {"role": "assistant", "content": "Rome is 25C.", "ground_truth": "Rome is 25C and cloudy."},
    ],
    "context": "Weather data for European cities.",
}

QUERY_HISTORY_TEXT = (
    "SYSTEM_PROMPT:\n  You are a weather assistant.\n\nUser turn 1:\n  What is the weather in Paris?\n\n"
)
AGENT_RESPONSE_TEXT = (
    '[TOOL_CALL] fetch_weather(location="Paris")\n'
    '[TOOL_RESULT] {"temperature": "20C", "sky": "sunny"}\n'
    "It is 20C and sunny in Paris."
)
TOOL_CALL_RESULTS_TEXT = (
    '[TOOL_CALL] fetch_weather(location="Paris")\n[TOOL_RESULT] {"temperature": "20C", "sky": "sunny"}'
)
TOOL_DEFINITIONS_TEXT = "TOOL_DEFINITIONS:\n- fetch_weather: Fetches the weather for a location. (inputs: location)"
GLOBAL_CONTEXT = "Weather data for European cities."

# Single-turn cases: evaluator, result key, rubric file, inputs, the exact Decision state (None when it is the
# inputs) and the result threshold.
LIKERT_CASES = [
    (CoherenceEvaluator, "coherence", "coherence.decision.yaml", {"query": QUERY, "response": RESPONSE}, None, 3),
    (FluencyEvaluator, "fluency", "fluency.decision.yaml", {"response": RESPONSE_MESSAGES}, {"response": RESPONSE}, 3),
    (
        GroundednessEvaluator,
        "groundedness",
        "groundedness.decision.yaml",
        {"query": QUERY, "response": RESPONSE, "context": CONTEXT},
        None,
        3,
    ),
    (
        IntentResolutionEvaluator,
        "intent_resolution",
        "intent_resolution.decision.yaml",
        {"query": QUERY, "response": RESPONSE},
        None,
        3,
    ),
    (RelevanceEvaluator, "relevance", "relevance.decision.yaml", {"query": QUERY, "response": RESPONSE}, None, 3),
    (
        ResponseCompletenessEvaluator,
        "response_completeness",
        "response_completeness.decision.yaml",
        {"response": RESPONSE, "ground_truth": GROUND_TRUTH},
        None,
        3,
    ),
    (RetrievalEvaluator, "retrieval", "retrieval.decision.yaml", {"query": QUERY, "context": CONTEXT}, None, 3),
    (
        SimilarityEvaluator,
        "similarity",
        "similarity.decision.yaml",
        {"query": QUERY, "response": RESPONSE, "ground_truth": GROUND_TRUTH},
        None,
        3,
    ),
    (
        ToolCallAccuracyEvaluator,
        "tool_call_accuracy",
        "tool_call_accuracy.decision.yaml",
        {"query": QUERY, "tool_calls": TOOL_CALLS, "tool_definitions": TOOL_DEFINITIONS},
        None,
        3,
    ),
]
BINARY_CASES = [
    (
        TaskAdherenceEvaluator,
        "task_adherence",
        "task_adherence.decision.yaml",
        {"query": QUERY, "response": RESPONSE},
        {"system_message": "", "query": QUERY, "response": RESPONSE, "tool_calls": ""},
        3,
    ),
    (
        _TaskCompletionEvaluator,
        "task_completion",
        "task_completion.decision.yaml",
        {"query": QUERY, "response": RESPONSE},
        {"query": QUERY, "response": RESPONSE, "tool_definitions": None},
        3,
    ),
    (
        _ToolCallSuccessEvaluator,
        "tool_call_success",
        "tool_call_success.decision.yaml",
        {"response": RESPONSE_MESSAGES, "tool_definitions": TOOL_DEFINITIONS},
        {"tool_calls": TOOL_CALL_RESULTS_TEXT, "tool_definitions": TOOL_DEFINITIONS_TEXT},
        1,
    ),
    (
        _ToolInputAccuracyEvaluator,
        "tool_input_accuracy",
        "tool_input_accuracy.decision.yaml",
        {"query": QUERY, "response": RESPONSE_MESSAGES, "tool_definitions": TOOL_DEFINITIONS},
        {"query": QUERY, "tool_calls": AGENT_RESPONSE_TEXT, "tool_definitions": TOOL_DEFINITIONS},
        1,
    ),
    (
        _ToolOutputUtilizationEvaluator,
        "tool_output_utilization",
        "tool_output_utilization.decision.yaml",
        {"query": QUERY, "response": RESPONSE, "tool_definitions": TOOL_DEFINITIONS},
        {"query": QUERY, "response": RESPONSE, "tool_definitions": TOOL_DEFINITIONS_TEXT},
        1,
    ),
    (
        _ToolSelectionEvaluator,
        "tool_selection",
        "tool_selection.decision.yaml",
        {"query": QUERY, "tool_calls": TOOL_CALLS, "tool_definitions": TOOL_DEFINITIONS},
        {"query": QUERY, "tool_calls": ["fetch_weather"], "tool_definitions": TOOL_DEFINITIONS},
        1,
    ),
]
ALL_CASES = LIKERT_CASES + BINARY_CASES
BINARY_TYPES = [case[0] for case in BINARY_CASES]

# Further inputs and the exact state each sends.
STATE_CASES = [
    (FluencyEvaluator, {"response": RESPONSE}, {"response": RESPONSE}),
    (FluencyEvaluator, {"response": json.dumps(RESPONSE_MESSAGES)}, {"response": RESPONSE}),
    # An assistant message's string content is its text.
    (FluencyEvaluator, {"response": json.dumps([{"role": "assistant", "content": RESPONSE}])}, {"response": RESPONSE}),
    # A conversation turn's content list is sent as the chat prompt receives it.
    (FluencyEvaluator, {"messages": QUERY_MESSAGES[1:] + RESPONSE_MESSAGES[2:]}, {"response": TEXT_CONTENT}),
    (GroundednessEvaluator, {"response": RESPONSE, "context": CONTEXT}, {"response": RESPONSE, "context": CONTEXT}),
    (
        ResponseCompletenessEvaluator,
        {"response": json.dumps(RESPONSE_MESSAGES), "ground_truth": GROUND_TRUTH},
        {"response": RESPONSE_MESSAGES, "ground_truth": GROUND_TRUTH},
    ),
    (
        SimilarityEvaluator,
        {"query": QUERY, "response": json.dumps(RESPONSE_MESSAGES), "ground_truth": GROUND_TRUTH},
        {"query": QUERY, "response": RESPONSE_MESSAGES, "ground_truth": GROUND_TRUTH},
    ),
    (
        IntentResolutionEvaluator,
        {"query": QUERY_MESSAGES, "response": RESPONSE_MESSAGES, "tool_definitions": TOOL_DEFINITIONS},
        {"query": "User turn 1:\n  What is the weather in Paris?\n\n", "response": RESPONSE},
    ),
    (_ToolCallSuccessEvaluator, {"response": RESPONSE}, {"tool_calls": RESPONSE}),
    (
        _ToolOutputUtilizationEvaluator,
        {"query": QUERY_MESSAGES, "response": RESPONSE_MESSAGES, "tool_definitions": TOOL_DEFINITIONS},
        {"query": QUERY_HISTORY_TEXT, "response": AGENT_RESPONSE_TEXT, "tool_definitions": TOOL_DEFINITIONS_TEXT},
    ),
    (
        _ToolSelectionEvaluator,
        {"query": QUERY_MESSAGES, "response": RESPONSE_MESSAGES, "tool_definitions": TOOL_DEFINITIONS},
        {"query": QUERY_HISTORY_TEXT, "tool_calls": ["fetch_weather"], "tool_definitions": TOOL_DEFINITIONS},
    ),
]


def _turns(first, second):
    return [first, second]


# Conversation inputs are split into user and assistant turns, as for chat models.
CONVERSATION_CASES = [
    (
        CoherenceEvaluator,
        "coherence",
        _turns({"query": QUERY, "response": RESPONSE}, {"query": "And in Rome?", "response": "Rome is 25C."}),
    ),
    (FluencyEvaluator, "fluency", _turns({"response": RESPONSE}, {"response": "Rome is 25C."})),
    (
        GroundednessEvaluator,
        "groundedness",
        _turns(
            {
                "query": QUERY,
                "response": RESPONSE,
                "context": str(
                    {
                        "global_context": GLOBAL_CONTEXT,
                        "query_context": "The user asks about Paris.",
                        "response_context": CONTEXT,
                    }
                ),
            },
            {"query": "And in Rome?", "response": "Rome is 25C.", "context": str({"global_context": GLOBAL_CONTEXT})},
        ),
    ),
    (
        IntentResolutionEvaluator,
        "intent_resolution",
        _turns({"query": QUERY, "response": RESPONSE}, {"query": "And in Rome?", "response": "Rome is 25C."}),
    ),
    (
        RelevanceEvaluator,
        "relevance",
        _turns({"query": QUERY, "response": RESPONSE}, {"query": "And in Rome?", "response": "Rome is 25C."}),
    ),
    (
        ResponseCompletenessEvaluator,
        "response_completeness",
        _turns(
            {"response": RESPONSE, "ground_truth": GROUND_TRUTH},
            {"response": "Rome is 25C.", "ground_truth": "Rome is 25C and cloudy."},
        ),
    ),
    (
        RetrievalEvaluator,
        "retrieval",
        _turns(
            {
                "query": QUERY,
                "context": str({"global_context": GLOBAL_CONTEXT, "query_context": "The user asks about Paris."}),
            },
            {"query": "And in Rome?", "context": str({"global_context": GLOBAL_CONTEXT})},
        ),
    ),
    (
        SimilarityEvaluator,
        "similarity",
        _turns(
            {"query": QUERY, "response": RESPONSE, "ground_truth": GROUND_TRUTH},
            {"query": "And in Rome?", "response": "Rome is 25C.", "ground_truth": "Rome is 25C and cloudy."},
        ),
    ),
    (
        TaskAdherenceEvaluator,
        "task_adherence",
        _turns(
            {"system_message": "", "query": QUERY, "response": RESPONSE, "tool_calls": ""},
            {"system_message": "", "query": "And in Rome?", "response": "Rome is 25C.", "tool_calls": ""},
        ),
    ),
    (
        _TaskCompletionEvaluator,
        "task_completion",
        _turns({"query": QUERY, "response": RESPONSE}, {"query": "And in Rome?", "response": "Rome is 25C."}),
    ),
    (_ToolCallSuccessEvaluator, "tool_call_success", _turns({"tool_calls": RESPONSE}, {"tool_calls": "Rome is 25C."})),
]

# SHA-256 of each rubric in the Microsoft Foundry catalog (azureml-assets fde9122a71).
CATALOG_RUBRIC_SHA256 = {
    "coherence.decision.yaml": "2b2cb56137d4385fb7cfca5b43c6c8c67d80811f47f8e4fe0ee67a476fed40a7",
    "fluency.decision.yaml": "cc0c0e604272cec3c1431ad2953684752675e0f089c47920abe35416c4317ea3",
    "groundedness.decision.yaml": "ca94c8b7356d0685037ca93ce2e05ee92780949b4b16642db2665791f989db9d",
    "groundedness_without_query.decision.yaml": "8f74c945f9ebad2f29882f2fe159d57cfe02e6b35aa7727a1b4aba56fa579309",
    "intent_resolution.decision.yaml": "663c236bd75a488407822b576f48da2e90d9f1e4e0c200de92fc04905b751d3e",
    "relevance.decision.yaml": "6a37d62c0b5ac102347a1bdc9808f4f4eaf16f56e6665fe30155b63b0013741e",
    "response_completeness.decision.yaml": "bb7c0134197ed3d1a2082fc8a58cb95f8c7ff64fcee0039d73f0e5b13603b6a6",
    "retrieval.decision.yaml": "aa2987e77817c5736eb09344c0281e2be8b96602bfcb3dcccdbeb84a00e6d17c",
    "similarity.decision.yaml": "4d77809979b39ff9a7a073b489921739eb4de0496b87f176c9e7a54b733812ab",
    "tool_call_accuracy.decision.yaml": "b57df84e8a5a7fdfc874ae643e2bf1b9d777778b028a3c43c023def61726601c",
    "task_adherence.decision.yaml": "1190ce46bfd8a6546d44afde9b50862baa4c86fe0a1807ba62d0c3692b20629b",
    "task_completion.decision.yaml": "e86c1665f78c180cab435c1db9dbcceab71f7b3de2b518cce16a34d652e760b6",
    "tool_call_success.decision.yaml": "b189c70fb10e8e343e3f58e13b334943c67bed8dbc229cb62f54c3c09da49d6e",
    "tool_input_accuracy.decision.yaml": "99c2e2cc3a0771b47242e48e2096d79183c593236152d0a888048c8d6eca4202",
    "tool_output_utilization.decision.yaml": "3c2e0e5500281f74e918718d0772f1b5ed9da87ae0ece7048d425699dd46d6fe",
    "tool_selection.decision.yaml": "64e6c0480e46972798fadfdf8aa7904562724fbddc8f40395f7a446614cb0682",
}
RUBRICS = [(case[0], case[0]._DECISION_FILE) for case in ALL_CASES] + [
    (GroundednessEvaluator, GroundednessEvaluator._NO_QUERY_DECISION_FILE)
]

LEVELS = [0.05, 0.05, 0.1, 0.7, 0.1]


class _Response(HttpResponse):
    def __init__(self, body):
        super().__init__(None, None)
        self.status_code = 200
        self._body = body

    def body(self):
        return self._body


class FakeDecisionService:
    """Records Decision requests and answers each question; the status answer decides applicability."""

    def __init__(self):
        self.status = 0.9
        self.noul = 0.8
        self.requests = []

    def with_policies(self, **_):
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return False

    async def post(self, url, content=None, headers=None, **_):
        request = json.loads(content)
        self.requests.append(request)
        answers = {}
        for question_id, question in request["questions"].items():
            if question_id == "status":
                answers[question_id] = {"type": "noul", "noul": self.status}
            elif question["type"] == "noul":
                answers[question_id] = {"type": "noul", "noul": self.noul}
            else:
                answers[question_id] = {
                    "type": "score",
                    "score": sum(level * value for level, value in enumerate(LEVELS)),
                    "confidence": max(LEVELS),
                    "probabilities": {str(level): value for level, value in enumerate(LEVELS)},
                }
        payload = {"model": "decision-model", "answers": answers, "usage": {"input_tokens": 40, "output_tokens": 2}}
        return _Response(json.dumps(payload).encode("utf-8"))


@pytest.fixture
def service(monkeypatch):
    fake = FakeDecisionService()
    monkeypatch.setattr(_model_runners, "get_async_http_client", lambda **_: fake)
    monkeypatch.setattr(
        _model_runners.AsyncPrompty, "load", lambda *_, **__: pytest.fail("A decision evaluator loaded a Prompty flow.")
    )
    return fake


def _rubric_path(evaluator_type, file_name):
    return os.path.join(os.path.dirname(sys.modules[evaluator_type.__module__].__file__), file_name)


def _questions(evaluator_type, file_name, result_key):
    with open(_rubric_path(evaluator_type, file_name), encoding="utf-8") as rubric_file:
        rubric = YAML(typ="safe").load(rubric_file)
    return {"status": rubric["status"], result_key: rubric["result"]}


def _digest(question):
    return hashlib.sha256(json.dumps(question, sort_keys=True).encode("utf-8")).hexdigest()


def _decision(evaluator_type, **kwargs):
    return evaluator_type(deepcopy(DECISION_CONFIG), **kwargs)


@pytest.mark.parametrize("evaluator_type,key,rubric,inputs,state,threshold", ALL_CASES)
def test_sends_the_prepared_prompt_inputs_and_rubric(service, evaluator_type, key, rubric, inputs, state, threshold):
    _decision(evaluator_type)(**deepcopy(inputs))

    [request] = service.requests
    assert request["model"] == "Decision-1"
    assert request["state"] == (inputs if state is None else state)
    assert request["questions"] == _questions(evaluator_type, rubric, key)


@pytest.mark.parametrize("evaluator_type,inputs,state", STATE_CASES)
def test_sends_the_exact_state_for_each_input_shape(service, evaluator_type, inputs, state):
    _decision(evaluator_type)(**deepcopy(inputs))

    assert [request["state"] for request in service.requests] == [state]


@pytest.mark.parametrize("evaluator_type,key,rubric,inputs,state,threshold", LIKERT_CASES)
def test_likert_result(service, evaluator_type, key, rubric, inputs, state, threshold):
    result = _decision(evaluator_type)(**deepcopy(inputs))

    properties = result.pop(f"{key}_properties")
    label = key.replace("_", " ")
    assert result == {
        key: 4.0,
        f"{key}_score": 4.0,
        f"{key}_passed": True,
        f"{key}_result": "pass",
        f"{key}_reason": f"Selected {label} level 4 from the highest-probability level. No model rationale is available.",
        f"{key}_status": "completed",
        f"{key}_threshold": threshold,
        f"{key}_prompt_tokens": 40,
        f"{key}_completion_tokens": 2,
        f"{key}_total_tokens": 42,
        f"{key}_model": "decision-model",
    }
    native = properties["decision_model"]
    assert native["probabilities"] == {str(level): value for level, value in enumerate(LEVELS)}
    assert math.isclose(native["expected_score"], 1 + sum(level * value for level, value in enumerate(LEVELS)))
    assert native["native_answer"]["type"] == "score" and "probability_threshold" not in native


@pytest.mark.parametrize("noul,score,verdict", [(0.8, 1.0, "pass"), (0.7, 0.0, "fail")])
@pytest.mark.parametrize("evaluator_type,key,rubric,inputs,state,threshold", BINARY_CASES)
def test_binary_result(service, evaluator_type, key, rubric, inputs, state, threshold, noul, score, verdict):
    service.noul = noul
    result = _decision(evaluator_type)(**deepcopy(inputs))

    properties = result.pop(f"{key}_properties")
    relation = "at or above" if score else "below"
    label = key.replace("_", " ").capitalize()
    assert result == {
        key: score,
        f"{key}_score": score,
        f"{key}_passed": verdict == "pass",
        f"{key}_result": verdict,
        f"{key}_reason": f"{label} probability {noul:.4f} is {relation} the 0.7500 cutoff. No model rationale is available.",
        f"{key}_status": "completed",
        f"{key}_threshold": threshold,
        f"{key}_prompt_tokens": 40,
        f"{key}_completion_tokens": 2,
        f"{key}_total_tokens": 42,
        f"{key}_model": "decision-model",
    }
    assert properties["decision_model"]["probability_threshold"] == 0.75
    assert properties["decision_model"]["probabilities"] == {"false": pytest.approx(1 - noul), "true": noul}


@pytest.mark.parametrize("evaluator_type,key,rubric,inputs,state,threshold", ALL_CASES)
def test_usage_model_and_provenance(service, evaluator_type, key, rubric, inputs, state, threshold):
    properties = _decision(evaluator_type)(**deepcopy(inputs))[f"{key}_properties"]

    questions = _questions(evaluator_type, rubric, key)
    assert {name: properties[name] for name in ("prompt_tokens", "completion_tokens", "total_tokens", "model")} == {
        "prompt_tokens": 40,
        "completion_tokens": 2,
        "total_tokens": 42,
        "model": "decision-model",
    }
    native = properties["decision_model"]
    assert native["deployment"] == "Decision-1" and native["model"] == "decision-model"
    assert native["rubric_hash"] == _digest(questions[key])
    assert native["status_rubric_hash"] == _digest(questions["status"])
    assert native["status_probability_threshold"] == 0.5 and native["status_completion_probability"] == 0.9
    assert native["reason_type"] == "templated"


@pytest.mark.parametrize("evaluator_type,key,rubric,inputs,state,threshold", ALL_CASES)
def test_status_false_is_not_applicable(service, evaluator_type, key, rubric, inputs, state, threshold):
    service.status = 0.2
    result = _decision(evaluator_type)(**deepcopy(inputs))

    properties = result.pop(f"{key}_properties")
    assert result == {
        key: None,
        f"{key}_score": None,
        f"{key}_passed": None,
        f"{key}_result": "not_applicable",
        f"{key}_reason": "Not applicable: Status completion probability 0.2000 is below 0.5000; evaluation skipped. "
        "No model rationale is available.",
        f"{key}_status": "skipped",
        f"{key}_threshold": threshold,
        f"{key}_prompt_tokens": 40,
        f"{key}_completion_tokens": 2,
        f"{key}_total_tokens": 42,
        f"{key}_model": "decision-model",
    }
    assert properties["prompt_tokens"] == 40 and properties["decision_model"]["status_completion_probability"] == 0.2


@pytest.mark.parametrize("evaluator_type", [case[0] for case in ALL_CASES])
def test_construction_selects_the_strategy_from_the_model_type(service, evaluator_type):
    with patch.object(_model_runners.AsyncPrompty, "load"):
        chat = evaluator_type(deepcopy(CHAT_CONFIG))
    decision = _decision(evaluator_type)

    assert evaluator_type._supports_decision_models is True
    assert evaluator_type._binary_decision is (evaluator_type in BINARY_TYPES)
    assert not chat._uses_decision_model and chat._decision is None
    assert decision._uses_decision_model and decision._decision.runner is decision._decision_model_runner
    expected_scoring = BinaryScoring(0.75) if evaluator_type in BINARY_TYPES else LikertScoring(5, minimum=1)
    assert decision._decision.scoring == expected_scoring
    assert decision._decision.timeout == 120 and decision._decision.threshold == decision._threshold


def test_groundedness_chat_construction_has_no_decision_strategies():
    with patch.object(_model_runners.AsyncPrompty, "load"):
        evaluator = GroundednessEvaluator(deepcopy(CHAT_CONFIG))

    assert evaluator._decision is None and evaluator._no_query_decision is None


def test_groundedness_selects_the_rubric_for_each_call(service):
    evaluator = _decision(GroundednessEvaluator)

    evaluator(response=RESPONSE, context=CONTEXT)
    evaluator(query=QUERY, response=RESPONSE, context=CONTEXT)
    evaluator(response=RESPONSE, context=CONTEXT)

    without_query = _questions(GroundednessEvaluator, "groundedness_without_query.decision.yaml", "groundedness")
    with_query = _questions(GroundednessEvaluator, "groundedness.decision.yaml", "groundedness")
    assert without_query != with_query
    assert [request["questions"] for request in service.requests] == [without_query, with_query, without_query]
    assert [request["state"] for request in service.requests] == [
        {"response": RESPONSE, "context": CONTEXT},
        {"query": QUERY, "response": RESPONSE, "context": CONTEXT},
        {"response": RESPONSE, "context": CONTEXT},
    ]


@pytest.mark.parametrize(
    "inputs", [{"query": QUERY, "response": RESPONSE}, {"query": QUERY, "response": RESPONSE, "context": ""}]
)
def test_groundedness_without_context_is_not_applicable(service, inputs):
    result = _decision(GroundednessEvaluator)(**inputs)

    assert service.requests == []
    assert result == {
        "groundedness": None,
        "groundedness_score": None,
        "groundedness_passed": None,
        "groundedness_result": "not_applicable",
        "groundedness_reason": "Not applicable: Groundedness requires grounding context; none was provided with a "
        "plain text response.",
        "groundedness_status": "skipped",
        "groundedness_threshold": 3,
        "groundedness_properties": None,
    }


@pytest.mark.parametrize(
    "evaluator_type,inputs",
    [
        (CoherenceEvaluator, {"query": QUERY, "response": INTERMEDIATE_RESPONSE}),
        (FluencyEvaluator, {"response": json.dumps(INTERMEDIATE_RESPONSE)}),
        (ResponseCompletenessEvaluator, {"response": json.dumps(INTERMEDIATE_RESPONSE), "ground_truth": "x"}),
        (SimilarityEvaluator, {"query": QUERY, "response": json.dumps(INTERMEDIATE_RESPONSE), "ground_truth": "x"}),
        (_TaskCompletionEvaluator, {"query": QUERY, "response": INTERMEDIATE_RESPONSE}),
    ],
)
def test_intermediate_responses_are_not_sent(service, evaluator_type, inputs):
    evaluator = _decision(evaluator_type)
    result = evaluator(**inputs)

    assert service.requests == []
    assert result[f"{evaluator._result_key}_result"] == "not_applicable"
    assert result[f"{evaluator._result_key}_reason"] == (
        "Not applicable: Intermediate response. Please provide the agent's final response for evaluation."
    )


@pytest.mark.parametrize("evaluator_type,key,turns", CONVERSATION_CASES)
def test_conversations_are_evaluated_turn_by_turn(service, evaluator_type, key, turns):
    result = _decision(evaluator_type)(conversation=deepcopy(CONVERSATION))

    assert [request["state"] for request in service.requests] == turns
    assert result["evaluation_per_turn"][f"{key}_status"] == ["completed", "completed"]
    assert result[f"{key}_prompt_tokens"] == 80 and result[f"{key}_total_tokens"] == 84
    assert result[f"{key}_model"] == "decision-model"


@pytest.mark.parametrize(
    "evaluator_type,message",
    [
        (ToolCallAccuracyEvaluator, "Query is a required input"),
        (_ToolInputAccuracyEvaluator, "Tool definitions input is required"),
        (_ToolOutputUtilizationEvaluator, "Tool definitions input is required"),
        (_ToolSelectionEvaluator, "Query is a required input"),
    ],
)
def test_tool_evaluators_reject_conversations_as_before(service, evaluator_type, message):
    with pytest.raises(EvaluationException, match=message):
        _decision(evaluator_type)(conversation=deepcopy(CONVERSATION))
    assert service.requests == []


@pytest.mark.parametrize("evaluator_type", BINARY_TYPES)
def test_probability_threshold_keyword_overrides_the_configuration_copy(service, evaluator_type):
    config = {**DECISION_CONFIG, "probability_threshold": 0.9}
    original = deepcopy(config)

    evaluator = evaluator_type(config, probability_threshold=0.6)

    assert config == original
    assert evaluator._decision_model_runner.probability_threshold == 0.6
    assert evaluator._decision.scoring == BinaryScoring(0.6)


@pytest.mark.parametrize("evaluator_type", BINARY_TYPES)
def test_probability_threshold_from_the_configuration_applies(service, evaluator_type):
    config = {**DECISION_CONFIG, "probability_threshold": 0.9}

    evaluator = evaluator_type(config)

    assert evaluator._decision_model_runner.probability_threshold == 0.9
    assert evaluator._decision.scoring == BinaryScoring(0.9)


@pytest.mark.parametrize("evaluator_type,key,rubric,inputs,state,threshold", BINARY_CASES)
def test_probability_threshold_sets_the_binary_cutoff(service, evaluator_type, key, rubric, inputs, state, threshold):
    service.noul = 0.7
    config = {**DECISION_CONFIG, "probability_threshold": 0.9}

    above = evaluator_type(deepcopy(config), probability_threshold=0.6)(**deepcopy(inputs))
    below = evaluator_type(deepcopy(config))(**deepcopy(inputs))

    assert (above[key], above[f"{key}_result"]) == (1.0, "pass")
    assert above[f"{key}_properties"]["decision_model"]["probability_threshold"] == 0.6
    assert (below[key], below[f"{key}_result"]) == (0.0, "fail")
    assert below[f"{key}_properties"]["decision_model"]["probability_threshold"] == 0.9


@pytest.mark.parametrize("value", [1.5, -0.1, "high", True, float("nan")])
@pytest.mark.parametrize("evaluator_type", BINARY_TYPES)
def test_invalid_decision_probability_threshold_is_rejected(evaluator_type, value):
    config = deepcopy(DECISION_CONFIG)

    with pytest.raises(EvaluationException, match=r"'probability_threshold' must be a number in \[0, 1\]\.") as raised:
        evaluator_type(config, probability_threshold=value)

    assert raised.value.blame == ErrorBlame.USER_ERROR and raised.value.category == ErrorCategory.INVALID_VALUE
    assert config == DECISION_CONFIG


@pytest.mark.parametrize("value", [0.6, "high"])
@pytest.mark.parametrize("evaluator_type", BINARY_TYPES)
def test_chat_ignores_probability_threshold_with_one_warning(monkeypatch, caplog, evaluator_type, value):
    base_kwargs = {}
    initialize = ModelEvaluatorBase.__init__

    def record(self, **kwargs):
        base_kwargs.update(kwargs)
        initialize(self, **kwargs)

    monkeypatch.setattr(ModelEvaluatorBase, "__init__", record)
    config = deepcopy(CHAT_CONFIG)
    with patch.object(_model_runners.AsyncPrompty, "load") as load, caplog.at_level(logging.WARNING):
        evaluator = evaluator_type(config, probability_threshold=value)

    assert not evaluator._uses_decision_model and evaluator._decision is None
    assert base_kwargs["model_config"] is config and "probability_threshold" not in config
    assert "probability_threshold" not in base_kwargs
    assert "probability_threshold" not in json.dumps(load.call_args.kwargs["model"], default=str)
    warnings = [record for record in caplog.records if "probability_threshold" in record.getMessage()]
    assert len(warnings) == 1 and warnings[0].levelno == logging.WARNING
    assert evaluator_type.__name__ in warnings[0].getMessage() and str(value) not in warnings[0].getMessage()


def test_non_binary_evaluators_still_reject_a_configured_probability_threshold(service):
    with pytest.raises(EvaluationException, match="only supported by binary evaluators"):
        CoherenceEvaluator({**DECISION_CONFIG, "probability_threshold": 0.6})


def test_prompty_base_requires_decision_evaluators_to_define_their_inputs(service):
    class UnmappedEvaluator(PromptyEvaluatorBase):
        _supports_decision_models = True

    evaluator = UnmappedEvaluator(result_key="unmapped", model_config=deepcopy(DECISION_CONFIG))

    with pytest.raises(NotImplementedError, match="UnmappedEvaluator"):
        asyncio.run(evaluator._do_eval({"query": QUERY, "response": RESPONSE}))
    assert service.requests == []


class _Credential:
    def __init__(self):
        self.scopes = []

    def get_token(self, *scopes, **_):
        self.scopes.append(scopes)
        return AccessToken("decision-token", 4102444800)


def _never_cancelled():
    return False


QA_KEYS = ["groundedness", "relevance", "coherence", "fluency", "similarity"]


def _qa_model_members(evaluator):
    return [member for member in evaluator._evaluators if isinstance(member, ModelEvaluatorBase)]


def test_qa_passes_the_credential_and_decision_controls_to_its_members(service):
    credential = _Credential()
    config = {key: value for key, value in DECISION_CONFIG.items() if key != "api_key"}

    evaluator = QAEvaluator(
        config, credential=credential, timeout=30, max_retries=1, cancellation_requested=_never_cancelled
    )
    result = evaluator(query=QUERY, response=RESPONSE, context=CONTEXT, ground_truth=GROUND_TRUTH)

    members = _qa_model_members(evaluator)
    assert [member._result_key for member in members] == QA_KEYS
    for member in members:
        runner = member._decision_model_runner
        assert runner._credential is credential and member._LLM_CALL_TIMEOUT == 30
        assert runner._max_retries == 1 and runner._cancellation_requested is _never_cancelled
    assert len(service.requests) == len(QA_KEYS) and len(credential.scopes) == len(QA_KEYS)
    assert [result[f"{key}_status"] for key in QA_KEYS] == ["completed"] * len(QA_KEYS)
    assert result["f1_score"] == pytest.approx(5 / 6)


def test_qa_decision_without_an_api_key_or_credential_is_rejected(service):
    config = {key: value for key, value in DECISION_CONFIG.items() if key != "api_key"}

    with pytest.raises(EvaluationException, match="require an 'api_key' or a credential"):
        QAEvaluator(config)


def test_qa_chat_members_are_unchanged():
    config = deepcopy(CHAT_CONFIG)
    with patch.object(_model_runners.AsyncPrompty, "load") as load:
        evaluator = QAEvaluator(config, credential=_Credential(), timeout=30, is_reasoning_model=True)

    assert not any(member._uses_decision_model for member in _qa_model_members(evaluator))
    assert [call.kwargs["token_credential"] for call in load.call_args_list] == [None] * len(QA_KEYS)
    assert [call.kwargs["is_reasoning_model"] for call in load.call_args_list] == [True] * len(QA_KEYS)


@pytest.mark.parametrize(
    "value,decoded",
    [
        (json.dumps(RESPONSE_MESSAGES), RESPONSE_MESSAGES),
        (RESPONSE, RESPONSE),
        ('{"role": "assistant"}', '{"role": "assistant"}'),
        (RESPONSE_MESSAGES, RESPONSE_MESSAGES),
        (None, None),
    ],
)
def test_decode_message_list(value, decoded):
    assert decode_message_list(value) == decoded


def test_final_assistant_text_keeps_only_assistant_text():
    messages = [
        {"role": "user", "content": [{"type": "text", "text": QUERY}]},
        *deepcopy(RESPONSE_MESSAGES),
        {"role": "assistant", "content": [{"type": "text", "text": "Anything else?"}]},
        {"role": "assistant", "content": "plain"},
        {"role": "user", "content": "ignored"},
    ]

    assert final_assistant_text(messages) == f"{RESPONSE}\nAnything else?\nplain"
    assert final_assistant_text(RESPONSE) == RESPONSE
    assert final_assistant_text([{"type": "text", "text": RESPONSE}]) == [{"type": "text", "text": RESPONSE}]


@pytest.mark.parametrize("evaluator_type,file_name", RUBRICS)
def test_rubrics_are_packaged_beside_their_evaluators(evaluator_type, file_name):
    with open(_rubric_path(evaluator_type, file_name), "rb") as rubric_file:
        content = rubric_file.read()
    # Git may check text files out with CRLF line endings; the catalog files use LF.
    assert hashlib.sha256(content.replace(b"\r\n", b"\n")).hexdigest() == CATALOG_RUBRIC_SHA256[file_name]


def test_every_rubric_comes_from_the_catalog():
    assert [case[2] for case in ALL_CASES] == [case[0]._DECISION_FILE for case in ALL_CASES]
    assert sorted(file_name for _, file_name in RUBRICS) == sorted(CATALOG_RUBRIC_SHA256)


def test_manifest_includes_the_rubrics():
    manifest = os.path.join(os.path.dirname(__file__), "..", "..", "MANIFEST.in")
    with open(manifest, encoding="utf-8") as manifest_file:
        assert "recursive-include azure/ai/evaluation *.decision.yaml" in manifest_file.read().splitlines()
