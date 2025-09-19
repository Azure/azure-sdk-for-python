# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Unit tests covering evaluator metric aggregation and sample ordering checks."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

import pandas as pd
import pytest

from azure.ai.evaluation._constants import ROW_ID_COLUMN
import azure.ai.evaluation._evaluate._evaluate as evaluate_module

from azure.ai.evaluation._evaluate._evaluate import _run_callable_evaluators


class _DummyEvalRunContext:  # pylint: disable=too-few-public-methods
    """Simple stand-in for EvalRunContext used in unit tests."""

    def __init__(self, client: Any) -> None:  # pragma: no cover - trivial
        self._client = client

    def __enter__(self) -> Any:  # pragma: no cover - trivial
        return self._client

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:  # pragma: no cover - trivial
        return False


class _FakeBatchRunClient:
    """Minimal batch run client that returns canned results."""

    def __init__(
        self,
        result_df: pd.DataFrame,
        metrics: Dict[str, float],
        run_summary: Dict[str, int],
    ) -> None:
        self._result_df = result_df
        self._metrics = metrics
        self._run_summary = run_summary
        self.run_calls: List[Dict[str, Any]] = []

    def run(self, **kwargs) -> str:  # pragma: no cover - trivial
        self.run_calls.append(kwargs)
        return "fake-run"

    def get_details(self, run: str, all_results: bool = True) -> pd.DataFrame:  # pragma: no cover - simple
        return self._result_df.copy()

    def get_metrics(self, run: str) -> Dict[str, float]:  # pragma: no cover - simple
        return dict(self._metrics)

    def get_run_summary(self, run: str) -> Dict[str, int]:  # pragma: no cover - simple
        return dict(self._run_summary)


@pytest.mark.unittest
def test_run_callable_evaluators_adds_summary_metrics(monkeypatch):
    """_run_callable_evaluators should surface total/failed/errored metrics from run summaries."""

    result_df = pd.DataFrame({"outputs.score": [0.9, 0.1]})
    fake_client = _FakeBatchRunClient(
        result_df=result_df,
        metrics={"score": 0.42},
        run_summary={
            "failed_lines": 1,
            "errored_lines": 2,
            "total_lines": 5,
            "status": "Completed",
            "log_path": "/tmp/dummy",
        },
    )

    validated_data = {
        "batch_run_client": fake_client,
        "target_run": None,
        "batch_run_data": pd.DataFrame(),
        "column_mapping": {"default": {}},
        "evaluators": {"test_eval": object()},
        "graders": {},
        "input_data_df": pd.DataFrame({"query": ["a", "b"], "response": ["x", "y"]}),
    }

    monkeypatch.setattr(
        evaluate_module,
        "EvalRunContext",
        _DummyEvalRunContext,
    )
    monkeypatch.setattr(
        evaluate_module,
        "_aggregate_metrics",
        lambda df, evaluators: {"aggregate": 0.5},
    )

    eval_df, metrics, per_results = _run_callable_evaluators(validated_data, fail_on_evaluator_errors=False)

    assert ROW_ID_COLUMN in eval_df.columns
    assert metrics["aggregate"] == 0.5
    assert metrics["test_eval.score"] == 0.42
    assert metrics["test_eval.total"] == 5
    assert metrics["test_eval.failed"] == 1
    assert metrics["test_eval.errored"] == 2
    assert set(per_results.keys()) == {"test_eval"}


def _make_conversation(user_text: str, assistant_text: str) -> Dict[str, List[Dict[str, str]]]:
    return {
        "messages": [
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": assistant_text},
        ]
    }


@pytest.mark.unittest
def test_inspect_alignment_reports_success(capsys):
    conversation = _make_conversation("Hello?", "Hi there!")
    input_df = pd.DataFrame(
        [{"conversation": conversation, "context": "greeting", "expected_quality": "high"}]
    )
    eval_df = pd.DataFrame(
        [
            {
                ROW_ID_COLUMN: "row_0",
                "inputs.conversation": conversation,
                "inputs.context": "greeting",
                "inputs.expected_quality": "high",
                "outputs.helpfulness.score": 4.0,
            }
        ]
    )

    _inspect_alignment(input_df, eval_df)
    captured = capsys.readouterr().out
    assert "All rows preserved their conversation content and order." in captured
    assert "⚠️" not in captured


@pytest.mark.unittest
def test_inspect_alignment_reports_mismatch(capsys):
    input_conversation = _make_conversation("What time is it?", "It's noon.")
    mismatched_conversation = _make_conversation("What time is it?", "No idea.")

    input_df = pd.DataFrame(
        [{"conversation": input_conversation, "context": "time", "expected_quality": "medium"}]
    )
    eval_df = pd.DataFrame(
        [
            {
                ROW_ID_COLUMN: "row_0",
                "inputs.conversation": mismatched_conversation,
                "inputs.context": "time",
                "inputs.expected_quality": "medium",
                "outputs.helpfulness.score": 1.0,
            }
        ]
    )

    _inspect_alignment(input_df, eval_df)
    captured = capsys.readouterr().out
    assert "⚠️  Alignment issues detected:" in captured
    assert "conversation content differs" in captured
def _inspect_alignment(input_df: pd.DataFrame, eval_df: pd.DataFrame) -> None:
    """Local copy of the alignment checker used by the order-debug sample."""

    def _normalize_conversation(conv: Any) -> List[Tuple[str, str]]:
        if isinstance(conv, dict):
            messages = conv.get("messages", [])
        else:
            messages = []
        normalized: List[Tuple[str, str]] = []
        for message in messages:
            if isinstance(message, dict):
                role = str(message.get("role", ""))
                content = str(message.get("content", ""))
            else:
                role, content = "", str(message)
            normalized.append((role, content))
        return normalized

    print("\n======= Input ordering (shuffled) =======")
    display_cols = [col for col in ["context", "expected_quality"] if col in input_df.columns]
    print(input_df[display_cols])

    print("\n======= Evaluation ordering =======")
    score_columns = sorted(
        col for col in eval_df.columns if col.startswith("outputs.") and col.endswith(".score")
    )
    eval_display_cols = [
        col
        for col in [ROW_ID_COLUMN, "inputs.context", "inputs.expected_quality", "context"]
        if col in eval_df.columns
    ] + [col for col in score_columns if col in eval_df.columns]
    print(eval_df[eval_display_cols])

    mismatches = []
    expected_conversations = input_df["conversation"].apply(_normalize_conversation)
    eval_conversations_column = eval_df.get("inputs.conversation")
    if eval_conversations_column is None:
        eval_conversations = pd.Series([[] for _ in range(len(eval_df))], dtype=object)
    else:
        eval_conversations = eval_conversations_column.apply(_normalize_conversation)

    max_len = max(len(input_df), len(eval_df))
    for idx in range(max_len):
        if idx >= len(eval_df):
            mismatches.append((idx, "<missing>", "evaluation output missing for this row"))
            continue
        eval_row = eval_df.iloc[idx]
        sdk_row_id = str(eval_row.get(ROW_ID_COLUMN, "<missing>"))

        if idx >= len(input_df):
            mismatches.append((idx, sdk_row_id, "extra evaluation row with no matching input"))
            continue

        expected_conv = expected_conversations.iloc[idx]
        result_conv = eval_conversations.iloc[idx]
        if expected_conv != result_conv:
            mismatches.append((idx, sdk_row_id, "conversation content differs"))
            continue

        expected_context = input_df.iloc[idx].get("context")
        result_context = eval_row.get("inputs.context", eval_row.get("context"))
        if expected_context != result_context:
            mismatches.append((idx, sdk_row_id, "context value differs"))

    if not mismatches:
        print("\nAll rows preserved their conversation content and order.")
    else:
        print("\n⚠️  Alignment issues detected:")
        for idx, row_id, reason in mismatches:
            print(f"  - Eval row {idx} (row_id={row_id}): {reason}")
