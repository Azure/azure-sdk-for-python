# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Pins the chat (Prompty) behavior of the Decision-capable built-in evaluators.

The fixture was recorded from the evaluators before they supported decision models. Each case runs offline with a
fake Prompty flow and compares the loaded prompts, the exact flow inputs and the evaluator output (or error) with
the recording. Run this module as a script to regenerate the fixture after an intentional chat change.
"""

import json
import os
import sys
from copy import deepcopy
from unittest.mock import patch

import pytest

from azure.ai.evaluation import (
    CoherenceEvaluator,
    FluencyEvaluator,
    GroundednessEvaluator,
    IntentResolutionEvaluator,
    RelevanceEvaluator,
    ResponseCompletenessEvaluator,
    RetrievalEvaluator,
    SimilarityEvaluator,
    TaskAdherenceEvaluator,
    ToolCallAccuracyEvaluator,
    _ToolCallSuccessEvaluator,
    _ToolOutputUtilizationEvaluator,
)
from azure.ai.evaluation._evaluators._common import _model_runners
from azure.ai.evaluation._evaluators._task_completion import _TaskCompletionEvaluator
from azure.ai.evaluation._evaluators._tool_input_accuracy import _ToolInputAccuracyEvaluator
from azure.ai.evaluation._evaluators._tool_selection import _ToolSelectionEvaluator

pytestmark = pytest.mark.unittest

FIXTURE = os.path.join(os.path.dirname(__file__), "data", "builtin_chat_golden.json")

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
FILE_SEARCH_RESPONSE = [
    {
        "role": "assistant",
        "content": [{"type": "tool_call", "tool_call_id": "call_fs", "name": "file_search", "arguments": {}}],
    },
    {
        "role": "tool",
        "tool_call_id": "call_fs",
        "content": [
            {"type": "tool_result", "tool_result": [{"file_name": "weather.txt", "content": [{"text": CONTEXT}]}]}
        ],
    },
    {"role": "assistant", "content": [{"type": "text", "text": RESPONSE}]},
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
JSON_RESPONSE = json.dumps(RESPONSE_MESSAGES)

# evaluator name: (class, chat score, [(case name, inputs), ...])
CASES = {
    "coherence": (
        CoherenceEvaluator,
        4,
        [
            ("strings", {"query": QUERY, "response": RESPONSE}),
            ("messages", {"query": QUERY_MESSAGES, "response": RESPONSE_MESSAGES}),
            ("conversation", {"conversation": CONVERSATION}),
        ],
    ),
    "fluency": (
        FluencyEvaluator,
        4,
        [
            ("strings", {"response": RESPONSE}),
            ("messages", {"response": RESPONSE_MESSAGES}),
            ("json_response", {"response": JSON_RESPONSE}),
            ("conversation", {"conversation": CONVERSATION}),
        ],
    ),
    "groundedness": (
        GroundednessEvaluator,
        4,
        [
            ("context", {"response": RESPONSE, "context": CONTEXT}),
            ("query_context", {"query": QUERY, "response": RESPONSE, "context": CONTEXT}),
            ("query_without_context", {"query": QUERY, "response": RESPONSE}),
            ("file_search", {"query": QUERY_MESSAGES, "response": FILE_SEARCH_RESPONSE}),
            ("conversation", {"conversation": CONVERSATION}),
        ],
    ),
    "intent_resolution": (
        IntentResolutionEvaluator,
        4,
        [
            ("strings", {"query": QUERY, "response": RESPONSE}),
            (
                "messages",
                {"query": QUERY_MESSAGES, "response": RESPONSE_MESSAGES, "tool_definitions": TOOL_DEFINITIONS},
            ),
            ("conversation", {"conversation": CONVERSATION}),
        ],
    ),
    "relevance": (
        RelevanceEvaluator,
        4,
        [
            ("strings", {"query": QUERY, "response": RESPONSE}),
            ("messages", {"query": QUERY_MESSAGES, "response": RESPONSE_MESSAGES}),
            ("conversation", {"conversation": CONVERSATION}),
        ],
    ),
    "response_completeness": (
        ResponseCompletenessEvaluator,
        4,
        [
            ("strings", {"response": RESPONSE, "ground_truth": GROUND_TRUTH}),
            ("messages", {"response": RESPONSE_MESSAGES, "ground_truth": GROUND_TRUTH}),
            ("conversation", {"conversation": CONVERSATION}),
        ],
    ),
    "retrieval": (
        RetrievalEvaluator,
        4,
        [
            ("strings", {"query": QUERY, "context": CONTEXT}),
            ("conversation", {"conversation": CONVERSATION}),
        ],
    ),
    "similarity": (
        SimilarityEvaluator,
        4,
        [
            ("strings", {"query": QUERY, "response": RESPONSE, "ground_truth": GROUND_TRUTH}),
            ("messages", {"query": QUERY_MESSAGES, "response": RESPONSE_MESSAGES, "ground_truth": GROUND_TRUTH}),
            ("json_response", {"query": QUERY, "response": JSON_RESPONSE, "ground_truth": GROUND_TRUTH}),
            ("conversation", {"conversation": CONVERSATION}),
        ],
    ),
    "tool_call_accuracy": (
        ToolCallAccuracyEvaluator,
        4,
        [
            ("tool_calls", {"query": QUERY, "tool_calls": TOOL_CALLS, "tool_definitions": TOOL_DEFINITIONS}),
            (
                "messages",
                {"query": QUERY_MESSAGES, "response": RESPONSE_MESSAGES, "tool_definitions": TOOL_DEFINITIONS},
            ),
            ("conversation", {"conversation": CONVERSATION}),
        ],
    ),
    "task_adherence": (
        TaskAdherenceEvaluator,
        1,
        [
            ("strings", {"query": QUERY, "response": RESPONSE}),
            (
                "messages",
                {"query": QUERY_MESSAGES, "response": RESPONSE_MESSAGES, "tool_definitions": TOOL_DEFINITIONS},
            ),
            ("conversation", {"conversation": CONVERSATION}),
        ],
    ),
    "task_completion": (
        _TaskCompletionEvaluator,
        1,
        [
            ("strings", {"query": QUERY, "response": RESPONSE}),
            (
                "messages",
                {"query": QUERY_MESSAGES, "response": RESPONSE_MESSAGES, "tool_definitions": TOOL_DEFINITIONS},
            ),
            ("conversation", {"conversation": CONVERSATION}),
        ],
    ),
    "tool_call_success": (
        _ToolCallSuccessEvaluator,
        1,
        [
            ("messages", {"response": RESPONSE_MESSAGES, "tool_definitions": TOOL_DEFINITIONS}),
            ("string", {"response": RESPONSE}),
            ("conversation", {"conversation": CONVERSATION}),
        ],
    ),
    "tool_input_accuracy": (
        _ToolInputAccuracyEvaluator,
        1,
        [
            (
                "messages",
                {"query": QUERY_MESSAGES, "response": RESPONSE_MESSAGES, "tool_definitions": TOOL_DEFINITIONS},
            ),
            ("conversation", {"conversation": CONVERSATION}),
        ],
    ),
    "tool_output_utilization": (
        _ToolOutputUtilizationEvaluator,
        1,
        [
            (
                "messages",
                {"query": QUERY_MESSAGES, "response": RESPONSE_MESSAGES, "tool_definitions": TOOL_DEFINITIONS},
            ),
            ("strings", {"query": QUERY, "response": RESPONSE, "tool_definitions": TOOL_DEFINITIONS}),
            ("conversation", {"conversation": CONVERSATION}),
        ],
    ),
    "tool_selection": (
        _ToolSelectionEvaluator,
        1,
        [
            (
                "messages",
                {"query": QUERY_MESSAGES, "response": RESPONSE_MESSAGES, "tool_definitions": TOOL_DEFINITIONS},
            ),
            ("tool_calls", {"query": QUERY, "tool_calls": TOOL_CALLS, "tool_definitions": TOOL_DEFINITIONS}),
            ("conversation", {"conversation": CONVERSATION}),
        ],
    ),
}


def _chat_output(score, status):
    return {
        "llm_output": {"score": score, "reason": "Recorded reason.", "status": status, "properties": {"note": 1}},
        "input_token_count": 11,
        "output_token_count": 7,
        "total_token_count": 18,
        "finish_reason": "stop",
        "model_id": "chat-model",
        "sample_input": "sample input",
        "sample_output": "sample output",
    }


class _Recorder:
    """Stands in for AsyncPrompty.load and records every prompt load and flow call."""

    def __init__(self, output):
        self.output = output
        self.events = []

    def load(self, source, **kwargs):
        self.events.append({"load": os.path.basename(str(source)), "is_reasoning_model": kwargs["is_reasoning_model"]})
        name = os.path.basename(str(source))

        async def flow(**inputs):
            self.events.append({"flow": name, "inputs": deepcopy(inputs)})
            return deepcopy(self.output)

        return flow


ALTERNATING_GROUNDEDNESS_CALLS = [
    {"response": RESPONSE, "context": CONTEXT},
    {"query": QUERY, "response": RESPONSE, "context": CONTEXT},
    {"response": RESPONSE, "context": CONTEXT},
]


def _outcome(evaluator_type, calls, output):
    recorder = _Recorder(output)
    record = {"results": []}
    with patch.object(_model_runners.AsyncPrompty, "load", side_effect=recorder.load):
        try:
            evaluator = evaluator_type(deepcopy(CHAT_CONFIG))
            for inputs in calls:
                record["results"].append(evaluator(**deepcopy(inputs)))
        except Exception as error:  # pylint: disable=broad-except
            record["error"] = {
                "type": type(error).__name__,
                "message": str(error),
                "category": str(getattr(getattr(error, "category", None), "value", None)),
                "target": str(getattr(getattr(error, "target", None), "value", None)),
            }
    record["calls"] = recorder.events
    return record


def _case_runs():
    for name, (evaluator_type, score, cases) in CASES.items():
        for case, inputs in cases:
            yield f"{name}/{case}", evaluator_type, [inputs], _chat_output(score, "completed")
        yield f"{name}/skipped", evaluator_type, [cases[0][1]], _chat_output(score, "skipped")
    yield "groundedness/alternating", GroundednessEvaluator, ALTERNATING_GROUNDEDNESS_CALLS, _chat_output(
        4, "completed"
    )


CASE_IDS = [case_id for case_id, *_ in _case_runs()]


def run_case(case_id):
    """Run one case and return its prompt loads, flow inputs and outputs."""
    for candidate, evaluator_type, calls, output in _case_runs():
        if candidate == case_id:
            return _outcome(evaluator_type, calls, output)
    raise KeyError(case_id)


def _canonical(value):
    # Key order is not compared: some evaluators build inputs from set iteration, which varies per process.
    return json.dumps(value, default=repr, sort_keys=True)


@pytest.fixture(scope="module")
def recorded():
    with open(FIXTURE, encoding="utf-8") as fixture:
        return json.load(fixture)


def test_fixture_covers_every_case(recorded):
    assert sorted(recorded) == sorted(CASE_IDS)


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_chat_behavior_matches_recording(recorded, case_id):
    assert _canonical(run_case(case_id)) == _canonical(recorded[case_id])


if __name__ == "__main__":
    recording = {case_id: run_case(case_id) for case_id in CASE_IDS}
    with open(FIXTURE, "w", encoding="utf-8", newline="\n") as output_file:
        json.dump(json.loads(_canonical(recording)), output_file, indent=1, sort_keys=True)
        output_file.write("\n")
    sys.exit(0)
