import inspect
import os
import pathlib
from enum import Enum
from typing import Any, List, Optional, Type

import pytest

import azure.ai.evaluation as evaluators


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

    EVALUATORS = get_evaluators_from_module(evaluators)

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
