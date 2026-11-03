# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Tool Call Success reads the judge's score where judge models put it, and skips responses without tool calls."""

import json
import math
import re
from pathlib import Path
from unittest.mock import AsyncMock

import pandas as pd
import pytest

from azure.ai.evaluation import evaluate
from azure.ai.evaluation._evaluators._tool_call_success import _tool_call_success as module
from azure.ai.evaluation._evaluators._tool_call_success._tool_call_success import (
    _ToolCallSuccessEvaluator,
    _has_no_tool_calls,
)
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException

CHAT_CONFIG = {
    "azure_endpoint": "https://example.openai.azure.com",
    "azure_deployment": "judge",
    "api_key": "test-key",
}
DECISION_CONFIG = {
    "type": "decision",
    "azure_endpoint": "https://example.services.ai.azure.com",
    "azure_deployment": "Decision-1",
    "api_key": "test-key",
}
PROMPTY = Path(module.__file__).parent / "tool_call_success.prompty"
TOOL_CALL_RESPONSE = [
    {
        "role": "assistant",
        "content": [
            {"type": "tool_call", "tool_call_id": "call_1", "name": "fetch_weather", "arguments": {"city": "Paris"}}
        ],
    },
    {"role": "tool", "tool_call_id": "call_1", "content": [{"type": "tool_result", "tool_result": {"sky": "sunny"}}]},
    {"role": "assistant", "content": [{"type": "text", "text": "It is sunny in Paris."}]},
]
TEXT_RESPONSE = [
    {"role": "user", "content": [{"type": "text", "text": "What is the weather in Paris?"}]},
    {"role": "assistant", "content": [{"type": "output_text", "text": "I can't check the weather."}]},
]
# What OpenAI's ChatCompletionMessage.model_dump() returns for a reply without tool calls.
OPENAI_TEXT_REPLY = {
    "content": "Hello.",
    "refusal": None,
    "role": "assistant",
    "annotations": [],
    "audio": None,
    "function_call": None,
    "tool_calls": None,
}
JUDGE_USAGE = {"input_token_count": 11, "output_token_count": 7, "total_token_count": 18}


def judge(llm_output):
    """Return a chat evaluator whose judge model answers with ``llm_output``."""
    evaluator = _ToolCallSuccessEvaluator(model_config=dict(CHAT_CONFIG))
    evaluator._flow = AsyncMock(return_value={"llm_output": llm_output, **JUDGE_USAGE})
    return evaluator


def evaluate_with(llm_output):
    return judge(llm_output)(response=TOOL_CALL_RESPONSE)


def prompty_example_outputs():
    text = PROMPTY.read_text(encoding="utf-8")
    decoder = json.JSONDecoder()
    return [
        decoder.raw_decode(text, text.index("{", match.end()))[0] for match in re.finditer(r"EXPECTED OUTPUT", text)
    ]


@pytest.mark.unittest
class TestToolCallSuccessPrompty:
    def test_every_example_output_is_valid_json_with_a_top_level_score(self):
        outputs = prompty_example_outputs()

        assert len(outputs) == 14
        for output in outputs:
            assert set(output) == {"reason", "properties", "score", "status"}
            assert output["status"] == "completed" and output["score"] in (0, 1)
            assert set(output["properties"]) == {"failed_tools"}


@pytest.mark.unittest
class TestToolCallSuccessScore:
    @pytest.mark.parametrize(
        "llm_output, expected",
        [
            ({"score": 1, "status": "completed", "properties": {"failed_tools": ""}}, 1.0),
            ({"score": 0, "status": "completed", "properties": {"failed_tools": "fetch_weather"}}, 0.0),
            # Judge models such as gpt-4.1 and gpt-4o nested the score and status in properties.
            ({"properties": {"failed_tools": "", "score": 1, "status": "completed"}}, 1.0),
            ({"properties": {"failed_tools": "fetch_weather", "score": 0, "status": "completed"}}, 0.0),
            # A top-level value wins over a nested one.
            ({"score": 0, "properties": {"score": 1}}, 0.0),
            ({"score": 1, "properties": {"score": 0}}, 1.0),
            ({"score": None, "properties": {"score": 1}}, 1.0),
            # Values that were already read as 0 or 1 still are.
            ({"score": 1.0}, 1.0),
            ({"score": "1"}, 1.0),
            ({"score": "0"}, 0.0),
            ({"score": True}, 1.0),
            ({"score": False}, 0.0),
        ],
    )
    def test_the_score_is_read_from_the_top_level_or_from_properties(self, llm_output, expected):
        result = evaluate_with({"reason": "Recorded reason.", **llm_output})

        assert result["tool_call_success"] == expected
        assert result["tool_call_success_score"] == expected
        assert result["tool_call_success_result"] == ("pass" if expected == 1.0 else "fail")
        assert result["tool_call_success_passed"] is (expected == 1.0)
        assert result["tool_call_success_status"] == "completed"
        assert result["tool_call_success_reason"] == "Recorded reason."
        assert result["tool_call_success_properties"]["prompt_tokens"] == 11

    def test_nested_keys_stay_in_the_returned_properties(self):
        result = evaluate_with({"reason": "r", "properties": {"failed_tools": "", "score": 1, "status": "completed"}})

        assert {"failed_tools": "", "score": 1, "status": "completed"}.items() <= (
            result["tool_call_success_properties"].items()
        )

    @pytest.mark.parametrize(
        "llm_output",
        [
            {"status": "skipped", "reason": "No tool calls."},
            {"properties": {"status": "skipped"}, "reason": "No tool calls."},
            {"properties": {"status": "skipped", "reason": "No tool calls."}},
        ],
    )
    def test_a_skipped_status_is_not_applicable(self, llm_output):
        result = evaluate_with(llm_output)

        assert result["tool_call_success_result"] == "not_applicable"
        assert result["tool_call_success_reason"] == "Not applicable: No tool calls."
        assert result["tool_call_success_status"] == "skipped"
        assert result["tool_call_success"] is None

    def test_a_top_level_status_wins_over_a_nested_skip(self):
        result = evaluate_with({"status": "completed", "score": 1, "properties": {"status": "skipped"}})

        assert result["tool_call_success_status"] == "completed"
        assert result["tool_call_success_result"] == "pass"

    @pytest.mark.parametrize(
        "llm_output, shown",
        [
            ({"reason": "No score anywhere.", "status": "completed"}, "None"),
            ({"score": None, "properties": None}, "None"),
            ({"score": None, "properties": {"failed_tools": ""}}, "None"),
            ({"score": 0.5}, "0.5"),
            ({"score": 2}, "2"),
            ({"score": -1}, "-1"),
            ({"score": math.nan}, "nan"),
            ({"score": math.inf}, "inf"),
            ({"score": "pass"}, "'pass'"),
            ({"score": [1]}, "[1]"),
            ({"score": {"value": 1}}, "{'value': 1}"),
            ({"properties": {"score": 0.5}}, "0.5"),
            ({"score": 0.5, "properties": {"score": 1}}, "0.5"),
            ({"properties": "score: 1"}, "None"),
        ],
    )
    def test_an_output_without_a_score_of_0_or_1_is_an_error_not_a_failed_tool_call(self, llm_output, shown):
        with pytest.raises(EvaluationException) as raised:
            evaluate_with(llm_output)

        assert str(raised.value) == f"(InternalError) Invalid score value: {shown}. Expected 0 or 1."
        assert raised.value.internal_message == "Invalid score value."
        assert raised.value.blame == ErrorBlame.SYSTEM_ERROR
        assert raised.value.category == ErrorCategory.FAILED_EXECUTION
        assert raised.value.target == ErrorTarget.TOOL_CALL_SUCCESS_EVALUATOR

    def test_an_invalid_score_is_shown_shortened(self):
        with pytest.raises(EvaluationException) as raised:
            evaluate_with({"score": "x" * 500})

        assert len(str(raised.value)) < 100

    def test_evaluate_reports_a_row_without_a_score_as_an_error(self, tmp_path):
        rows = [
            {"response": TOOL_CALL_RESPONSE, "case": "valid"},
            {"response": TOOL_CALL_RESPONSE, "case": "missing"},
            {"response": TOOL_CALL_RESPONSE, "case": "nested"},
        ]
        data = tmp_path / "rows.jsonl"
        data.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
        outputs = iter(
            [
                {"score": 1, "status": "completed", "reason": "valid"},
                {"status": "completed", "reason": "missing"},
                {"properties": {"score": 1, "status": "completed"}, "reason": "nested"},
            ]
        )
        evaluator = _ToolCallSuccessEvaluator(model_config=dict(CHAT_CONFIG))

        async def flow(timeout, **kwargs):
            return {"llm_output": next(outputs), **JUDGE_USAGE}

        evaluator._flow = flow
        result = evaluate(
            data=str(data),
            evaluators={"tool_call_success": evaluator},
            evaluator_config={"tool_call_success": {"column_mapping": {"response": "${data.response}"}}},
            _use_run_submitter_client=True,
        )
        reason, score = (
            "outputs.tool_call_success.tool_call_success_reason",
            "outputs.tool_call_success.tool_call_success",
        )
        completed = {row[reason]: row[score] for row in result["rows"] if isinstance(row.get(reason), str)}
        errored = [row for row in result["rows"] if not isinstance(row.get(reason), str)]

        assert completed == {"valid": 1.0, "nested": 1.0}
        assert len(errored) == 1 and pd.isna(errored[0][score])


@pytest.mark.unittest
class TestToolCallSuccessWithoutToolCalls:
    @pytest.mark.parametrize("config", [CHAT_CONFIG, DECISION_CONFIG], ids=["chat", "decision"])
    @pytest.mark.parametrize(
        "response",
        [
            TEXT_RESPONSE,
            [{"role": "assistant", "content": "I can't check the weather."}],
            [
                {"role": "system", "content": "Answer briefly."},
                {"role": "developer", "content": [{"type": "input_text", "text": "Be polite."}]},
                {"role": "assistant", "content": [{"type": "text", "text": "Hello."}]},
            ],
            [
                {
                    "role": "assistant",
                    "content": [{"type": "mcp_approval_request", "name": "search", "arguments": "{}"}],
                },
                {
                    "role": "tool",
                    "tool_call_id": "approval_1",
                    "content": [{"type": "mcp_approval_response", "approve": False}],
                },
            ],
            [{"role": "assistant", "content": "Hello.", "tool_calls": None}],
            [{"role": "assistant", "content": [{"type": "text", "text": "Hello."}], "tool_calls": []}],
            [{"role": "assistant", "content": "Hello.", "function_call": None}],
            [{"role": "user", "content": "Hi.", "tool_call_id": None}, {"role": "assistant", "content": "Hello."}],
            [OPENAI_TEXT_REPLY],
        ],
        ids=[
            "text-items",
            "string-content",
            "every-text-role",
            "mcp-approval-only",
            "null-tool-calls",
            "empty-tool-calls",
            "null-function-call",
            "null-tool-call-id",
            "openai-model-dump",
        ],
    )
    def test_a_response_without_tool_calls_is_not_applicable_without_a_judge_call(self, config, response):
        evaluator = _ToolCallSuccessEvaluator(model_config=dict(config))
        if evaluator._decision is None:
            evaluator._flow = AsyncMock(side_effect=AssertionError("The judge was called."))
        else:
            evaluator._decision.evaluate = AsyncMock(side_effect=AssertionError("The judge was called."))

        result = evaluator(response=response)

        assert result == {
            "tool_call_success": None,
            "tool_call_success_score": None,
            "tool_call_success_passed": None,
            "tool_call_success_result": "not_applicable",
            "tool_call_success_reason": "Not applicable: No tool calls found in response.",
            "tool_call_success_status": "skipped",
            "tool_call_success_threshold": 1,
            "tool_call_success_properties": None,
        }

    @pytest.mark.parametrize(
        "response",
        [
            TOOL_CALL_RESPONSE,
            [
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "function_call",
                            "tool_call_id": "call_1",
                            "name": "fetch_weather",
                            "arguments": {"city": "Paris"},
                        },
                    ],
                },
                {"role": "assistant", "content": [{"type": "text", "text": "Done."}]},
            ],
            "[TOOL_CALL] fetch_weather(city=Paris)",
            "It is sunny in Paris.",
            [
                {
                    "role": "assistant",
                    "content": '[TOOL_CALL] fetch_weather(city="Paris")\n[TOOL_RESULT] {"error": "timed out"}',
                }
            ],
            [{"role": "assistant", "content": [{"type": "text", "text": '[TOOL_RESULT] {"error": "timed out"}'}]}],
            [
                {
                    "role": "assistant",
                    "content": [
                        {"type": "mcp_approval_request", "name": "search", "arguments": "{}"},
                        {
                            "type": "tool_call",
                            "tool_call_id": "call_1",
                            "name": "fetch_weather",
                            "arguments": {"city": "Paris"},
                        },
                    ],
                },
                {"role": "assistant", "content": [{"type": "text", "text": "Done."}]},
            ],
            [
                {
                    **OPENAI_TEXT_REPLY,
                    "content": "Checking the weather.",
                    "tool_calls": [
                        {
                            "id": "call_1",
                            "type": "function",
                            "function": {"name": "fetch_weather", "arguments": '{"city": "Paris"}'},
                        }
                    ],
                },
                {
                    "role": "tool",
                    "tool_call_id": "call_1",
                    "content": [{"type": "tool_result", "tool_result": {"error": "timed out"}}],
                },
                {**OPENAI_TEXT_REPLY, "content": "The weather service timed out."},
            ],
        ],
        ids=[
            "tool-call",
            "function-call",
            "tool-call-text",
            "plain-text",
            "trace-in-message",
            "trace-in-text-item",
            "approval-with-tool-call",
            "openai-model-dump-tool-call",
        ],
    )
    def test_tool_calls_and_text_responses_still_go_to_the_judge(self, response):
        evaluator = judge({"score": 1, "status": "completed", "reason": "r"})

        result = evaluator(response=response)

        assert evaluator._flow.await_count == 1
        assert result["tool_call_success_result"] == "pass"

    def test_a_decision_judge_still_gets_tool_calls(self):
        evaluator = _ToolCallSuccessEvaluator(model_config=dict(DECISION_CONFIG))
        evaluator._decision.evaluate = AsyncMock(return_value={"tool_call_success": 1.0})

        assert evaluator(response=TOOL_CALL_RESPONSE)["tool_call_success"] == 1.0
        state = evaluator._decision.evaluate.await_args.args[0]
        assert "[TOOL_CALL] fetch_weather" in state["tool_calls"]

    def test_evaluate_leaves_rows_without_tool_calls_out_of_the_pass_rate(self, tmp_path):
        failed_call = json.loads(json.dumps(TOOL_CALL_RESPONSE).replace("sunny", "timed out"))
        rows = [{"response": TOOL_CALL_RESPONSE}, {"response": failed_call}, {"response": [OPENAI_TEXT_REPLY]}]
        data = tmp_path / "rows.jsonl"
        data.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
        evaluator = _ToolCallSuccessEvaluator(model_config=dict(CHAT_CONFIG))

        async def flow(timeout, **kwargs):
            score = 0 if "timed out" in str(kwargs["tool_calls"]) else 1
            return {"llm_output": {"score": score, "status": "completed", "reason": "r"}, **JUDGE_USAGE}

        evaluator._flow = flow
        result = evaluate(
            data=str(data),
            evaluators={"tool_call_success": evaluator},
            evaluator_config={"tool_call_success": {"column_mapping": {"response": "${data.response}"}}},
            _use_run_submitter_client=True,
        )

        results = sorted(row["outputs.tool_call_success.tool_call_success_result"] for row in result["rows"])
        assert results == ["fail", "not_applicable", "pass"]
        assert result["metrics"]["tool_call_success.tool_call_success"] == 0.5
        assert result["metrics"]["tool_call_success.binary_aggregate"] == 0.5

    @pytest.mark.parametrize(
        "messages",
        [
            [],
            "text",
            [{"role": "tool", "tool_call_id": "call_1", "content": [{"type": "tool_result", "tool_result": "ok"}]}],
            [{"role": "assistant", "content": [{"type": "tool_call", "name": "t", "arguments": {}}]}],
            [{"role": "assistant", "content": "Calling a tool.", "tool_calls": [{"id": "call_1"}]}],
            [{"role": "assistant", "content": "Calling a tool.", "function_call": {"name": "t"}}],
            [
                {
                    "role": "assistant",
                    "content": "Calling a tool.",
                    "tool_calls": [{"id": "call_1"}],
                    "function_call": None,
                }
            ],
            [{"role": "assistant", "content": "Calling a tool.", "tool_calls": [None]}],
            [{"role": "assistant", "content": "Calling a tool.", "function_call": "t"}],
            [{"role": "assistant", "content": "Calling a tool.", "tool_calls": False}],
            [{"role": "assistant", "content": "Result.", "tool_call_id": "call_1"}],
            [{"role": "function", "content": "Result."}],
            [{"content": "No role."}],
            [{"role": "assistant", "content": None}],
            [{"role": "assistant", "content": [{"type": "mcp_call", "name": "t"}]}],
            [{"role": "assistant", "content": [{"type": "image_url", "image_url": "https://example.com"}]}],
            [{"role": "assistant", "content": ["text"]}],
            ["text"],
            [{"role": "assistant", "content": "[TOOL_CALL] fetch_weather()"}],
            [{"role": "assistant", "content": [{"type": "output_text", "text": "[TOOL_RESULT] ok"}]}],
            [{"role": "assistant", "content": [{"type": "text", "text": None}]}],
        ],
    )
    def test_only_recognized_text_messages_count_as_having_no_tool_calls(self, messages):
        assert _has_no_tool_calls(messages) is False

    def test_text_messages_have_no_tool_calls(self):
        assert _has_no_tool_calls(TEXT_RESPONSE) is True
        assert _has_no_tool_calls([{"role": "assistant", "content": []}]) is True

    @pytest.mark.parametrize("key", ["tool_calls", "function_call", "tool_call_id"])
    @pytest.mark.parametrize("value", [None, "", [], {}], ids=["none", "empty-string", "empty-list", "empty-dict"])
    def test_a_call_field_that_holds_nothing_counts_as_absent(self, key, value):
        assert _has_no_tool_calls([{"role": "assistant", "content": "Hello.", key: value}]) is True

    def test_mcp_approvals_are_not_tool_calls_but_a_tool_call_beside_one_is(self):
        approval = {"type": "mcp_approval_request", "name": "search", "arguments": "{}"}
        response = {"type": "mcp_approval_response", "approve": True}
        text = {"type": "text", "text": "Searching."}
        tool_call = {"type": "tool_call", "tool_call_id": "call_1", "name": "search", "arguments": {}}

        assert _has_no_tool_calls(
            [
                {"role": "assistant", "content": [approval, text]},
                {"role": "tool", "tool_call_id": "approval_1", "content": [response]},
            ]
        )
        assert not _has_no_tool_calls([{"role": "assistant", "content": [approval, tool_call]}])
        assert not _has_no_tool_calls(
            [{"role": "tool", "tool_call_id": "call_1", "content": [response, {"type": "tool_result"}]}]
        )
        # Tool calls in message fields count even beside approval-only content.
        assert not _has_no_tool_calls(
            [
                {"role": "assistant", "content": [approval], "tool_calls": [{"id": "call_1", "type": "function"}]},
                {"role": "assistant", "content": [text]},
            ]
        )
        assert not _has_no_tool_calls([{"role": "assistant", "content": [approval], "function_call": {"name": "t"}}])
        assert _has_no_tool_calls([{"role": "assistant", "content": [approval], "tool_calls": None}])
