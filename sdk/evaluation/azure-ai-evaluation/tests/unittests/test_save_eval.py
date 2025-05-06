import inspect
import os
import pathlib
from enum import Enum
from typing import Any, Dict, List, Optional, Type

import pytest

import azure.ai.evaluation as evaluators
from azure.ai.evaluation._legacy._adapters._check import MISSING_LEGACY_SDK


@pytest.fixture
def data_file():
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, "evaluate_test_data.jsonl")


def get_evaluators_from_module(namespace: Any, exceptions: Optional[List[str]] = None) -> List[Type]:
    evaluators = []
    for name, obj in inspect.getmembers(namespace):
        if inspect.isclass(obj) and not issubclass(obj, Enum) and not issubclass(obj, dict):
            if exceptions and name in exceptions:
                continue
            evaluators.append(obj)
    return evaluators


@pytest.mark.unittest
class TestSaveEval:
    """Test saving evaluators."""

    EVALUATORS = get_evaluators_from_module(evaluators, exceptions=["AIAgentConverter", "RedTeam", "RedTeamOutput"])

    @pytest.mark.parametrize("evaluator", EVALUATORS)
    def test_save_evaluators(self, tmpdir, pf_client, evaluator) -> None:
        """Test regular evaluator saving."""
        pf_client.flows.save(evaluator, path=tmpdir)
        assert os.path.isfile(os.path.join(tmpdir, "flow.flex.yaml"))

    def test_load_and_run_evaluators(self, tmpdir, pf_client, data_file) -> None:
        """Test regular evaluator saving."""
        # Use a test eval because save/load feature breaks, seemingly in multiple ways, when
        # evaluators have complex imports.
        from test_evaluators.test_inputs_evaluators import EchoEval

        pf_client.flows.save(EchoEval, path=tmpdir)
        run = pf_client.run(tmpdir, data=data_file)
        results_df = pf_client.get_details(run.name)
        assert results_df is not None
        all(results_df["outputs.echo_query"] == results_df["inputs.query"])
        all(results_df["outputs.echo_response"] == results_df["inputs.response"])

    def test_load_and_run_evaluators_new(self, tmpdir, data_file) -> None:
        """Test saving and loading evaluators using the ported code"""
        from test_evaluators.test_inputs_evaluators import EchoEval
        from azure.ai.evaluation._legacy._persist import save_evaluator, load_evaluator, LoadedEvaluator
        from azure.ai.evaluation import evaluate

        save_evaluator(EchoEval, path=tmpdir)
        assert os.path.isfile(os.path.join(tmpdir, "flow.flex.yaml"))

        loaded_eval: LoadedEvaluator = load_evaluator(tmpdir)
        assert isinstance(loaded_eval, LoadedEvaluator)

        result = evaluate(
            data=data_file,
            evaluators={
                "echo_eval": loaded_eval,
            },
            evaluator_config={
                "echo_eval": {
                    "column_mapping": {
                        "query": "${data.query}",
                        "response": "${data.response}",
                    }
                }
            },
            _use_run_submitter_client=True,
        )
        assert result
        result_df: List[Dict] = result["rows"]
        assert all(row["outputs.echo_eval.echo_query"] == row["inputs.query"] for row in result_df)
        assert all(row["outputs.echo_eval.echo_response"] == row["inputs.response"] for row in result_df)
