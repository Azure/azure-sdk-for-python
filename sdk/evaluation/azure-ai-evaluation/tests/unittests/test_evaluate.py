from typing import List, Dict, Union
import json
import math
import os
import pathlib
import numpy as np
from unittest.mock import patch

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from azure.ai.evaluation._legacy._adapters.client import PFClient

from azure.ai.evaluation._common.math import list_mean
from azure.ai.evaluation import (
    ContentSafetyEvaluator,
    F1ScoreEvaluator,
    GroundednessEvaluator,
    SimilarityEvaluator,
    ProtectedMaterialEvaluator,
    evaluate,
    ViolenceEvaluator,
    FluencyEvaluator,
    SexualEvaluator,
    SelfHarmEvaluator,
    HateUnfairnessEvaluator,
    AzureOpenAIModelConfiguration,
)
from azure.ai.evaluation._aoai.label_grader import AzureOpenAILabelGrader
from azure.ai.evaluation._constants import (
    DEFAULT_EVALUATION_RESULTS_FILE_NAME,
    _AggregationType,
    EvaluationRunProperties,
)
from azure.ai.evaluation._evaluate._evaluate import (
    _aggregate_metrics,
    _apply_target_to_data,
    _rename_columns_conditionally,
    _convert_results_to_aoai_evaluation_results,
    _process_rows,
    _aggregate_label_defect_metrics,
)
from azure.ai.evaluation._evaluate._utils import _convert_name_map_into_property_entries
from azure.ai.evaluation._evaluate._utils import _apply_column_mapping, _trace_destination_from_project_scope
from azure.ai.evaluation._evaluators._eci._eci import ECIEvaluator
from azure.ai.evaluation._exceptions import EvaluationException


def _get_file(name):
    """Get the file from the unittest data folder."""
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, name)


@pytest.fixture
def unsupported_file_type():
    return _get_file("unsupported_file_type.txt")


@pytest.fixture
def missing_header_csv_file():
    return _get_file("no_header_evaluate_test_data.csv")


@pytest.fixture
def invalid_jsonl_file():
    return _get_file("invalid_evaluate_test_data.jsonl")


@pytest.fixture
def missing_columns_jsonl_file():
    return _get_file("missing_columns_evaluate_test_data.jsonl")


@pytest.fixture
def evaluate_test_data_jsonl_file():
    return _get_file("evaluate_test_data.jsonl")


@pytest.fixture
def evaluate_test_data_conversion_jsonl_file():
    return _get_file("evaluate_test_data_conversation.jsonl")


@pytest.fixture
def evaluate_test_data_alphanumeric():
    return _get_file("evaluate_test_data_alphanumeric.jsonl")


@pytest.fixture
def evaluate_test_data_for_groundedness():
    return _get_file("evaluate_test_data_for_groundedness.jsonl")


@pytest.fixture
def questions_file():
    return _get_file("questions.jsonl")


@pytest.fixture
def questions_wrong_file():
    return _get_file("questions_wrong.jsonl")


@pytest.fixture
def questions_answers_file():
    return _get_file("questions_answers.jsonl")


@pytest.fixture
def questions_answers_basic_file():
    return _get_file("questions_answers_basic.jsonl")


@pytest.fixture
def questions_answers_korean_file():
    return _get_file("questions_answers_korean.jsonl")


@pytest.fixture
def restore_env_vars():
    """Fixture to restore environment variables after the test."""
    original_vars = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_vars)


def _target_fn(query):
    """An example target function."""
    if "LV-426" in query:
        return {"response": "There is nothing good there."}
    if "central heating" in query:
        return {"response": "There is no central heating on the streets today, but it will be, I promise."}
    if "strange" in query:
        return {"response": "The life is strange..."}


def _yeti_evaluator(query, response):
    if "yeti" in query.lower():
        raise ValueError("Do not ask about Yeti!")
    return {"result": len(response)}


def _target_fn2(query):
    response = _target_fn(query)
    response["query"] = f"The query is as follows: {query}"
    return response


def _target_that_fails(query):
    raise Exception("I am failing")


def _new_answer_target():
    return {"response": "new response"}


def _question_override_target(query):
    return {"query": "new query"}


def _question_answer_override_target(query, response):
    return {"query": "new query", "response": "new response"}


@pytest.mark.usefixtures("mock_model_config")
@pytest.mark.unittest
class TestEvaluate:
    def test_evaluate_evaluators_not_a_dict(self, mock_model_config, questions_file):
        with pytest.raises(EvaluationException) as exc_info:
            evaluate(
                data=questions_file,
                evaluators=[GroundednessEvaluator(model_config=mock_model_config)],
            )

        assert "The 'evaluators' parameter must be a dictionary." in exc_info.value.args[0]

    def test_evaluate_invalid_data(self, mock_model_config):
        with pytest.raises(EvaluationException) as exc_info:
            evaluate(
                data=123,
                evaluators={"g": GroundednessEvaluator(model_config=mock_model_config)},
            )

        assert "The 'data' parameter must be a string or a path-like object." in exc_info.value.args[0]

    def test_evaluate_data_not_exist(self, mock_model_config):
        with pytest.raises(EvaluationException) as exc_info:
            evaluate(
                data="not_exist.jsonl",
                evaluators={"g": GroundednessEvaluator(model_config=mock_model_config)},
            )

        assert "The input data file path 'not_exist.jsonl' does not exist." in exc_info.value.args[0]

    def test_target_not_callable(self, mock_model_config, questions_file):
        with pytest.raises(EvaluationException) as exc_info:
            evaluate(
                data=questions_file,
                evaluators={"g": GroundednessEvaluator(model_config=mock_model_config)},
                target="not_callable",
            )

        assert "The 'target' parameter must be a callable function." in exc_info.value.args[0]

    def test_evaluate_invalid_jsonl_data(self, mock_model_config, invalid_jsonl_file):
        with pytest.raises(EvaluationException) as exc_info:
            evaluate(
                data=invalid_jsonl_file,
                evaluators={"g": GroundednessEvaluator(model_config=mock_model_config)},
            )

        assert "Unable to load data from " in exc_info.value.args[0]
        assert "Supported formats are JSONL and CSV. Detailed error:" in exc_info.value.args[0]

    def test_evaluate_missing_required_inputs(self, missing_columns_jsonl_file):
        with pytest.raises(EvaluationException) as exc_info:
            evaluate(
                data=missing_columns_jsonl_file, evaluators={"g": F1ScoreEvaluator()}, fail_on_evaluator_errors=True
            )
        expected_message = "Either 'conversation' or individual inputs must be provided."
        assert expected_message in exc_info.value.args[0]
        # Same call without failure flag shouldn't produce an exception.
        evaluate(data=missing_columns_jsonl_file, evaluators={"g": F1ScoreEvaluator()})

    def test_evaluate_missing_required_inputs_target(self, questions_wrong_file):
        with pytest.raises(EvaluationException) as exc_info:
            evaluate(data=questions_wrong_file, evaluators={"g": F1ScoreEvaluator()}, target=_target_fn)
        assert "Missing required inputs for target: ['query']." in exc_info.value.args[0]

    def test_target_not_generate_required_columns(self, questions_file):
        with pytest.raises(EvaluationException) as exc_info:
            # target_fn will generate the "response", but not "ground_truth".
            evaluate(
                data=questions_file,
                evaluators={"g": F1ScoreEvaluator()},
                target=_target_fn,
                fail_on_evaluator_errors=True,
            )

        expected_message = "Either 'conversation' or individual inputs must be provided."

        assert expected_message in exc_info.value.args[0]

        # Same call without failure flag shouldn't produce an exception.
        evaluate(data=questions_file, evaluators={"g": F1ScoreEvaluator()}, target=_target_fn)

    def test_target_raises_on_outputs(self):
        """Test we are raising exception if the output is column is present in the input."""
        data = _get_file("questions_answers_outputs.jsonl")
        with pytest.raises(EvaluationException) as cm:
            evaluate(
                data=data,
                target=_target_fn,
                evaluators={"g": F1ScoreEvaluator()},
            )
        assert 'The column cannot start from "__outputs." if target was defined.' in cm.value.args[0]

    @pytest.mark.parametrize(
        "input_file,out_file,expected_columns,fun",
        [
            ("questions.jsonl", "questions_answers.jsonl", {"response"}, _target_fn),
            (
                "questions_ground_truth.jsonl",
                "questions_answers_ground_truth.jsonl",
                {"response", "query"},
                _target_fn2,
            ),
        ],
    )
    @pytest.mark.skip(reason="Breaking CI by crashing pytest somehow")
    def test_apply_target_to_data(self, pf_client, input_file, out_file, expected_columns, fun):
        """Test that target was applied correctly."""
        data = _get_file(input_file)
        expexted_out = _get_file(out_file)
        initial_data = pd.read_json(data, lines=True)
        qa_df, columns, _ = _apply_target_to_data(fun, data, pf_client, initial_data)
        assert columns == expected_columns
        ground_truth = pd.read_json(expexted_out, lines=True)
        assert_frame_equal(qa_df, ground_truth, check_like=True)

    @pytest.mark.skip(reason="Breaking CI by crashing pytest somehow")
    def test_apply_column_mapping(self):
        json_data = [
            {
                "query": "How are you?",
                "ground_truth": "I'm fine",
            }
        ]
        inputs_mapping = {
            "query": "${data.query}",
            "response": "${data.ground_truth}",
        }

        data_df = pd.DataFrame(json_data)
        new_data_df = _apply_column_mapping(data_df, inputs_mapping)

        assert "query" in new_data_df.columns
        assert "response" in new_data_df.columns

        assert new_data_df["query"][0] == "How are you?"
        assert new_data_df["response"][0] == "I'm fine"

    @pytest.mark.parametrize(
        "json_data,inputs_mapping,response",
        [
            (
                [
                    {
                        "query": "How are you?",
                        "__outputs.response": "I'm fine",
                    }
                ],
                {
                    "query": "${data.query}",
                    "response": "${run.outputs.response}",
                },
                "I'm fine",
            ),
            (
                [
                    {
                        "query": "How are you?",
                        "response": "I'm fine",
                        "__outputs.response": "I'm great",
                    }
                ],
                {
                    "query": "${data.query}",
                    "response": "${run.outputs.response}",
                },
                "I'm great",
            ),
            (
                [
                    {
                        "query": "How are you?",
                        "response": "I'm fine",
                        "__outputs.response": "I'm great",
                    }
                ],
                {
                    "query": "${data.query}",
                    "response": "${data.response}",
                },
                "I'm fine",
            ),
            (
                [
                    {
                        "query": "How are you?",
                        "response": "I'm fine",
                        "__outputs.response": "I'm great",
                    }
                ],
                {
                    "query": "${data.query}",
                    "response": "${data.response}",
                    "another_response": "${run.outputs.response}",
                },
                "I'm fine",
            ),
            (
                [
                    {
                        "query": "How are you?",
                        "response": "I'm fine",
                        "__outputs.response": "I'm great",
                    }
                ],
                {
                    "query": "${data.query}",
                    "response": "${run.outputs.response}",
                    "another_response": "${data.response}",
                },
                "I'm great",
            ),
            (
                [
                    {
                        "query": "How are you?",
                        "__outputs.response": "I'm fine",
                        "else": "Another column",
                        "else1": "Another column 1",
                    }
                ],
                {
                    "query": "${data.query}",
                    "response": "${run.outputs.response}",
                    "else1": "${data.else}",
                    "else2": "${data.else1}",
                },
                "I'm fine",
            ),
        ],
    )
    def test_apply_column_mapping_target(self, json_data, inputs_mapping, response):

        data_df = pd.DataFrame(json_data)
        new_data_df = _apply_column_mapping(data_df, inputs_mapping)

        assert "query" in new_data_df.columns
        assert "response" in new_data_df.columns

        assert new_data_df["query"][0] == "How are you?"
        assert new_data_df["response"][0] == response
        if "another_response" in inputs_mapping:
            assert "another_response" in new_data_df.columns
            assert new_data_df["another_response"][0] != response
        if "else" in inputs_mapping:
            assert "else1" in new_data_df.columns
            assert new_data_df["else1"][0] == "Another column"
            assert "else2" in new_data_df.columns
            assert new_data_df["else2"][0] == "Another column 1"

    @pytest.mark.parametrize(
        "column_mapping",
        [
            {"query": "${foo.query}"},
            {"query": "${data.query"},
            {"query": "data.query", "response": "target.response"},
        ],
    )
    def test_evaluate_invalid_column_mapping(self, mock_model_config, evaluate_test_data_jsonl_file, column_mapping):
        # Invalid source reference
        with pytest.raises(EvaluationException) as exc_info:
            evaluate(
                data=evaluate_test_data_jsonl_file,
                evaluators={"g": GroundednessEvaluator(model_config=mock_model_config)},
                evaluator_config={
                    "g": {
                        "column_mapping": column_mapping,
                    }
                },
            )

        assert (
            "Unexpected references detected in 'column_mapping'. Ensure only ${target.} and ${data.} are used."
            in exc_info.value.args[0]
        )

    def test_evaluate_valid_column_mapping_with_numeric_chars(self, mock_model_config, evaluate_test_data_alphanumeric):
        # Valid column mappings that include numeric characters
        # This test validates the fix for the regex pattern that now accepts numeric characters
        # Previous regex was `re.compile(r"^\$\{(target|data)\.[a-zA-Z_]+\}$")`
        # New regex is `re.compile(r"^\$\{(target|data)\.[a-zA-Z0-9_]+\}$")`

        column_mappings_with_numbers = {
            "response": "${data.response123}",
            "query": "${data.query456}",
            "context": "${data.context789}",
        }  # This should not raise an exception with the updated regex for column mapping format validation
        # The test passes if no exception about "Unexpected references" is raised
        result = evaluate(
            data=evaluate_test_data_alphanumeric,
            evaluators={"g": GroundednessEvaluator(model_config=mock_model_config)},
            evaluator_config={
                "g": {
                    "column_mapping": column_mappings_with_numbers,
                }
            },
            fail_on_evaluator_errors=False,
        )

        # Verify that the test completed without errors related to column mapping format
        # The test data has the fields with numeric characters, so it should work correctly
        assert result is not None
        # Verify we're getting data from the numerically-named fields
        row_result_df = pd.DataFrame(result["rows"])
        assert "inputs.response123" in row_result_df.columns
        assert "inputs.query456" in row_result_df.columns
        assert "inputs.context789" in row_result_df.columns

    def test_evaluate_groundedness_tool_result(self, mock_model_config, evaluate_test_data_for_groundedness):
        # Validates if groundedness evaluator does not add tool_call results to tool call messages

        result = evaluate(
            data=evaluate_test_data_for_groundedness,
            evaluators={"g": GroundednessEvaluator(model_config=mock_model_config)},
            fail_on_evaluator_errors=False,
        )

        # Verify that the test completed without errors related to column mapping format
        # The test data has the fields with numeric characters, so it should work correctly
        assert result is not None
        # Verify we're getting data from the numerically-named fields
        row_result_df = pd.DataFrame(result["rows"])
        assert "inputs.response" in row_result_df.columns
        assert "inputs.query" in row_result_df.columns

        # Break down the assertion for better error handling
        response_data = row_result_df["inputs.response"][0]
        first_message = response_data[0]
        content_data = first_message["content"][0]

        # Now check if "tool_result" is in the keys
        assert "tool_result" not in content_data.keys()

    def test_renaming_column(self):
        """Test that the columns are renamed correctly."""
        df = pd.DataFrame(
            {
                "just_column": ["just_column."],
                "presnt_generated": ["Is present in data set."],
                "__outputs.presnt_generated": ["This was generated by target."],
                "__outputs.generated": ["Generaged by target"],
                "outputs.before": ["Despite prefix this column was before target."],
            }
        )
        df_expected = pd.DataFrame(
            {
                "inputs.just_column": ["just_column."],
                "inputs.presnt_generated": ["Is present in data set."],
                "outputs.presnt_generated": ["This was generated by target."],
                "outputs.generated": ["Generaged by target"],
                "inputs.outputs.before": ["Despite prefix this column was before target."],
            }
        )
        df_actuals = _rename_columns_conditionally(df)
        assert_frame_equal(df_actuals.sort_index(axis=1), df_expected.sort_index(axis=1))

    def test_evaluate_output_dir_not_exist(self, mock_model_config, questions_file):
        with pytest.raises(EvaluationException) as exc_info:
            evaluate(
                data=questions_file,
                evaluators={"g": GroundednessEvaluator(model_config=mock_model_config)},
                output_path="./not_exist_dir/output.jsonl",
            )

        assert "The output directory './not_exist_dir' does not exist." in exc_info.value.args[0]

    @pytest.mark.parametrize("use_relative_path", [True, False])
    def test_evaluate_output_path(self, evaluate_test_data_jsonl_file, tmpdir, use_relative_path):
        # output_path is a file
        if use_relative_path:
            output_path = os.path.join(tmpdir, "eval_test_results.jsonl")
        else:
            output_path = "eval_test_results.jsonl"

        result = evaluate(
            data=evaluate_test_data_jsonl_file,
            evaluators={"g": F1ScoreEvaluator()},
            output_path=output_path,
        )

        assert result is not None
        assert os.path.exists(output_path)
        assert os.path.isfile(output_path)

        with open(output_path, "r") as f:
            content = f.read()
            data_from_file = json.loads(content)
            assert result["metrics"] == data_from_file["metrics"]

        os.remove(output_path)

        # output_path is a directory
        result = evaluate(
            data=evaluate_test_data_jsonl_file,
            evaluators={"g": F1ScoreEvaluator()},
            output_path=os.path.join(tmpdir),
        )

        with open(os.path.join(tmpdir, DEFAULT_EVALUATION_RESULTS_FILE_NAME), "r") as f:
            content = f.read()
            data_from_file = json.loads(content)
            assert result["metrics"] == data_from_file["metrics"]

    def test_evaluate_with_errors(self):
        """Test evaluate_handle_errors"""
        data = _get_file("yeti_questions.jsonl")
        result = evaluate(data=data, evaluators={"yeti": _yeti_evaluator})
        result_df = pd.DataFrame(result["rows"])
        expected = pd.read_json(data, lines=True)
        expected.rename(columns={"query": "inputs.query", "response": "inputs.response"}, inplace=True)

        expected["outputs.yeti.result"] = expected["inputs.response"].str.len()
        expected.at[0, "outputs.yeti.result"] = math.nan
        expected.at[2, "outputs.yeti.result"] = math.nan
        expected.at[3, "outputs.yeti.result"] = math.nan
        assert_frame_equal(expected, result_df)

    @patch("azure.ai.evaluation._evaluate._evaluate._evaluate")
    def test_evaluate_main_entry_guard(self, mock_evaluate, evaluate_test_data_jsonl_file):
        err_msg = (
            "An attempt has been made to start a new process before the\n        "
            "current process has finished its bootstrapping phase."
        )
        mock_evaluate.side_effect = RuntimeError(err_msg)

        with pytest.raises(EvaluationException) as exc_info:
            evaluate(
                data=evaluate_test_data_jsonl_file,
                evaluators={"f1_score": F1ScoreEvaluator()},
            )

        assert "Please ensure the evaluate API is properly guarded with the '__main__' block" in exc_info.value.args[0]

    def test_get_trace_destination(self, mock_validate_trace_destination, mock_project_scope):
        pf_client = PFClient()
        trace_destination_without_override = pf_client._config.get_trace_destination()

        pf_client = PFClient(
            config={
                "trace.destination": (
                    _trace_destination_from_project_scope(mock_project_scope) if mock_project_scope else None
                )
            }
        )

        trace_destination_with_override = pf_client._config.get_trace_destination()

        assert trace_destination_with_override != trace_destination_without_override
        assert trace_destination_with_override == _trace_destination_from_project_scope(mock_project_scope)

    def test_content_safety_aggregation(self):
        data = {
            # 10 zeroes in a list fully written out
            "content_safety.violence_score": [0, 0, 1, 2, 5, 5, 6, 7, np.nan, None],
            "content_safety.sexual_score": [0, 0, 2, 3, 3, 3, 8, 8, np.nan, None],
            "content_safety.self_harm_score": [0, 0, 0, 0, 1, 1, 1, 1, np.nan, None],
            "content_safety.hate_unfairness_score": [0, 0, 1, 1, 2, 2, 3, 5, 6, 7],
            "content_safety.violence": [
                "low",
                "low",
                "low",
                "low",
                "high",
                "high",
                "high",
                "high",
                "high",
                "high",
            ],  # TODO DETERMINE ACTUAL BASED ON SCORES
            "content_safety.sexual": ["low", "low", "low", "low", "low", "low", "high", "high", "high", "high"],
            "content_safety.self_harm": ["low", "low", "low", "low", "low", "low", "low", "low", "high", "high"],
            "content_safety.hate_unfairness": ["low", "low", "low", "low", "low", "low", "low", "low", "low", "high"],
            "content_safety.violence_reason": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
            "content_safety.sexual_reason": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
            "content_safety.self_harm_reason": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
            "content_safety.hate_unfairness_reason": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
        }
        data_df = pd.DataFrame(data)
        evaluators = {
            "content_safety": ContentSafetyEvaluator,
        }
        aggregation = _aggregate_metrics(data_df, evaluators)

        assert len(aggregation) == 4
        assert aggregation["content_safety.violence_defect_rate"] == 0.5
        assert aggregation["content_safety.sexual_defect_rate"] == 0.25
        assert aggregation["content_safety.self_harm_defect_rate"] == 0.0
        assert aggregation["content_safety.hate_unfairness_defect_rate"] == 0.3

        no_results = _aggregate_metrics(pd.DataFrame({"content_safety.violence_score": [np.nan, None]}), evaluators)
        assert len(no_results) == 0

    def test_label_based_aggregation(self):
        data = {
            "eci.eci_label": [True, True, True, np.nan, None],
            "eci.eci_reasoning": ["a", "b", "c", "d", "e"],
            "protected_material.protected_material_label": [False, False, False, False, True],
            "protected_material.protected_material_reasoning": ["f", "g", "h", "i", "j"],
            "unknown.unaccounted_label": [False, False, False, True, True],
            "unknown.unaccounted_reasoning": ["k", "l", "m", "n", "o"],
        }
        data_df = pd.DataFrame(data)
        evaluators = {
            "eci": ECIEvaluator,
            "protected_material": ProtectedMaterialEvaluator,
        }
        aggregation = _aggregate_metrics(data_df, evaluators)
        # ECI and PM labels should be replaced with defect rates, unaccounted should not
        assert len(aggregation) == 3
        assert "eci.eci_label" not in aggregation
        assert "protected_material.protected_material_label" not in aggregation
        assert aggregation["unknown.unaccounted_label"] == 0.4

        assert aggregation["eci.eci_defect_rate"] == 1.0
        assert aggregation["protected_material.protected_material_defect_rate"] == 0.2
        assert "unaccounted_defect_rate" not in aggregation

        no_results = _aggregate_metrics(pd.DataFrame({"eci.eci_label": [np.nan, None]}), evaluators)
        assert len(no_results) == 0

    def test_other_aggregation(self):
        data = {
            "thing.groundedness_pro_label": [True, False, True, False, np.nan, None],
        }
        data_df = pd.DataFrame(data)
        evaluators = {}
        aggregation = _aggregate_metrics(data_df, evaluators)

        assert len(aggregation) == 1
        assert aggregation["thing.groundedness_pro_passing_rate"] == 0.5

        no_results = _aggregate_metrics(pd.DataFrame({"thing.groundedness_pro_label": [np.nan, None]}), {})
        assert len(no_results) == 0

    def test_general_aggregation(self):
        data = {
            "thing.metric": [1, 2, 3, 4, 5, np.nan, None],
            "thing.reasoning": ["a", "b", "c", "d", "e", "f", "g"],
            "other_thing.other_meteric": [-1, -2, -3, -4, -5, np.nan, None],
            "other_thing.other_reasoning": ["f", "g", "h", "i", "j", "i", "j"],
            "final_thing.final_metric": [False, False, False, True, True, True, False],
            "bad_thing.mixed_metric": [0, 1, False, True, 0.5, True, False],
            "bad_thing.boolean_with_nan": [True, False, True, False, True, False, np.nan],
            "bad_thing.boolean_with_none": [True, False, True, False, True, False, None],
        }
        data_df = pd.DataFrame(data)
        evaluators = {}
        aggregation = _aggregate_metrics(data_df, evaluators)

        assert len(aggregation) == 3
        assert aggregation["thing.metric"] == 3
        assert aggregation["other_thing.other_meteric"] == -3
        assert aggregation["final_thing.final_metric"] == 3 / 7.0
        assert "bad_thing.mixed_metric" not in aggregation
        assert "bad_thing.boolean_with_nan" not in aggregation
        assert "bad_thing.boolean_with_none" not in aggregation

    def test_aggregate_label_defect_metrics_with_nan_in_details(self):
        """Test that NaN/None values in details column are properly ignored during aggregation."""
        data = {
            "evaluator.protected_material_label": [True, False, True, False],
            "evaluator.protected_material_details": [
                {"detail1": 1, "detail2": 0},
                np.nan,  # Failed evaluation
                {"detail1": 0, "detail2": 1},
                None,  # Another failure case
            ],
        }
        df = pd.DataFrame(data)
        
        label_cols, defect_rates = _aggregate_label_defect_metrics(df)
        
        # Should calculate defect rate for label column (all 4 rows)
        assert "evaluator.protected_material_defect_rate" in defect_rates
        assert defect_rates["evaluator.protected_material_defect_rate"] == 0.5
        
        # Should calculate defect rates for detail keys (only from 2 valid dict rows)
        assert "evaluator.protected_material_details.detail1_defect_rate" in defect_rates
        assert "evaluator.protected_material_details.detail2_defect_rate" in defect_rates
        assert defect_rates["evaluator.protected_material_details.detail1_defect_rate"] == 0.5
        assert defect_rates["evaluator.protected_material_details.detail2_defect_rate"] == 0.5

    @pytest.mark.skip(reason="Breaking CI by crashing pytest somehow")
    def test_optional_inputs_with_data(self, questions_file, questions_answers_basic_file):
        from test_evaluators.test_inputs_evaluators import HalfOptionalEval, NoInputEval, NonOptionalEval, OptionalEval

        # All variants work with both keyworded inputs
        results = evaluate(
            data=questions_answers_basic_file,
            evaluators={
                "non": NonOptionalEval(),
                "half": HalfOptionalEval(),
                "opt": OptionalEval(),
                "no": NoInputEval(),
            },
            _use_pf_client=False,
            _use_run_submitter_client=False,
        )  # type: ignore

        first_row = results["rows"][0]
        assert first_row["outputs.non.non_score"] == 0
        assert first_row["outputs.half.half_score"] == 1
        assert first_row["outputs.opt.opt_score"] == 3

        # Variant with no default inputs fails on single input
        with pytest.raises(EvaluationException) as exc_info:
            evaluate(
                data=questions_file,
                evaluators={
                    "non": NonOptionalEval(),
                },
                _use_pf_client=False,
                _use_run_submitter_client=False,
            )  # type: ignore

        expected_message = "Some evaluators are missing required inputs:\n" "- non: ['response']\n"
        assert expected_message in exc_info.value.args[0]

        # Variants with default answer work when only question is inputted
        only_question_results = evaluate(
            data=questions_file,
            evaluators={"half": HalfOptionalEval(), "opt": OptionalEval(), "no": NoInputEval()},
            _use_pf_client=False,
            _use_run_submitter_client=False,
        )  # type: ignore

        first_row_2 = only_question_results["rows"][0]
        assert first_row_2["outputs.half.half_score"] == 0
        assert first_row_2["outputs.opt.opt_score"] == 1

    @pytest.mark.skip(reason="Breaking CI by crashing pytest somehow")
    def test_optional_inputs_with_target(self, questions_file, questions_answers_basic_file):
        from test_evaluators.test_inputs_evaluators import EchoEval

        # Check that target overrides default inputs
        target_answer_results = evaluate(
            data=questions_file,
            target=_new_answer_target,
            evaluators={"echo": EchoEval()},
            _use_pf_client=False,
            _use_run_submitter_client=False,
        )  # type: ignore

        assert target_answer_results["rows"][0]["outputs.echo.echo_query"] == "How long is flight from Earth to LV-426?"
        assert target_answer_results["rows"][0]["outputs.echo.echo_response"] == "new response"

        # Check that target replaces inputs from data (I.E. if both data and target have same output
        # the target output is sent to the evaluator.)
        question_override_results = evaluate(
            data=questions_answers_basic_file,
            target=_question_override_target,
            evaluators={"echo": EchoEval()},
            _use_pf_client=False,
            _use_run_submitter_client=False,
        )  # type: ignore

        assert question_override_results["rows"][0]["outputs.echo.echo_query"] == "new query"
        assert question_override_results["rows"][0]["outputs.echo.echo_response"] == "There is nothing good there."

        # Check that target can replace default and data inputs at the same time.
        double_override_results = evaluate(
            data=questions_answers_basic_file,
            target=_question_answer_override_target,
            evaluators={"echo": EchoEval()},
            _use_pf_client=False,
            _use_run_submitter_client=False,
        )  # type: ignore
        assert double_override_results["rows"][0]["outputs.echo.echo_query"] == "new query"
        assert double_override_results["rows"][0]["outputs.echo.echo_response"] == "new response"

    def test_conversation_aggregation_types(self, evaluate_test_data_conversion_jsonl_file):
        from test_evaluators.test_inputs_evaluators import CountingEval

        counting_eval = CountingEval()
        evaluators = {"count": counting_eval}
        # test default behavior - mean
        results = evaluate(data=evaluate_test_data_conversion_jsonl_file, evaluators=evaluators)
        assert results["rows"][0]["outputs.count.response"] == 1.5  # average of 1 and 2
        assert results["rows"][1]["outputs.count.response"] == 3.5  # average of 3 and 4

        # test maxing
        counting_eval.reset()
        counting_eval._set_conversation_aggregation_type(_AggregationType.MAX)
        results = evaluate(data=evaluate_test_data_conversion_jsonl_file, evaluators=evaluators)
        assert results["rows"][0]["outputs.count.response"] == 2
        assert results["rows"][1]["outputs.count.response"] == 4

        # test minimizing
        counting_eval.reset()
        counting_eval._set_conversation_aggregation_type(_AggregationType.MIN)
        results = evaluate(data=evaluate_test_data_conversion_jsonl_file, evaluators=evaluators)
        assert results["rows"][0]["outputs.count.response"] == 1
        assert results["rows"][1]["outputs.count.response"] == 3

        # test sum
        counting_eval.reset()
        counting_eval._set_conversation_aggregation_type(_AggregationType.SUM)
        results = evaluate(data=evaluate_test_data_conversion_jsonl_file, evaluators=evaluators)
        assert results["rows"][0]["outputs.count.response"] == 3
        assert results["rows"][1]["outputs.count.response"] == 7

        # test custom aggregator
        def custom_aggregator(values):
            return sum(values) + 1

        counting_eval.reset()
        counting_eval._set_conversation_aggregator(custom_aggregator)
        results = evaluate(data=evaluate_test_data_conversion_jsonl_file, evaluators=evaluators)
        assert results["rows"][0]["outputs.count.response"] == 4
        assert results["rows"][1]["outputs.count.response"] == 8

    def test_default_conversation_aggregation_overrides(self):
        fake_project = {"subscription_id": "123", "resource_group_name": "123", "project_name": "123"}
        eval1 = ViolenceEvaluator(None, fake_project)
        eval2 = SexualEvaluator(None, fake_project)
        eval3 = SelfHarmEvaluator(None, fake_project)
        eval4 = HateUnfairnessEvaluator(None, fake_project)
        eval5 = F1ScoreEvaluator()  # Test default
        assert eval1._conversation_aggregation_function == max
        assert eval2._conversation_aggregation_function == max
        assert eval3._conversation_aggregation_function == max
        assert eval4._conversation_aggregation_function == max
        assert eval5._conversation_aggregation_function == list_mean

    def test_conversation_aggregation_type_returns(self):
        fake_project = {"subscription_id": "123", "resource_group_name": "123", "project_name": "123"}
        eval1 = ViolenceEvaluator(None, fake_project)
        # Test builtins
        assert eval1._get_conversation_aggregator_type() == _AggregationType.MAX
        eval1._set_conversation_aggregation_type(_AggregationType.SUM)
        assert eval1._get_conversation_aggregator_type() == _AggregationType.SUM
        eval1._set_conversation_aggregation_type(_AggregationType.MAX)
        assert eval1._get_conversation_aggregator_type() == _AggregationType.MAX
        eval1._set_conversation_aggregation_type(_AggregationType.MIN)
        assert eval1._get_conversation_aggregator_type() == _AggregationType.MIN

        # test custom
        def custom_aggregator(values):
            return sum(values) + 1

        eval1._set_conversation_aggregator(custom_aggregator)
        assert eval1._get_conversation_aggregator_type() == _AggregationType.CUSTOM

    @pytest.mark.parametrize("use_async", ["true", "false"])  # Strings intended
    @pytest.mark.usefixtures("restore_env_vars")
    def test_aggregation_serialization(self, evaluate_test_data_conversion_jsonl_file, use_async):
        # This test exists to ensure that PF doesn't crash when trying to serialize a
        # complex aggregation function.
        from test_evaluators.test_inputs_evaluators import CountingEval

        counting_eval = CountingEval()
        evaluators = {"count": counting_eval}

        def custom_aggregator(values: List[float]) -> float:
            return sum(values) + 1

        os.environ["AI_EVALS_BATCH_USE_ASYNC"] = use_async
        _ = evaluate(data=evaluate_test_data_conversion_jsonl_file, evaluators=evaluators, _use_pf_client=True)
        counting_eval._set_conversation_aggregation_type(_AggregationType.MIN)
        _ = evaluate(data=evaluate_test_data_conversion_jsonl_file, evaluators=evaluators, _use_pf_client=True)
        counting_eval._set_conversation_aggregation_type(_AggregationType.SUM)
        _ = evaluate(data=evaluate_test_data_conversion_jsonl_file, evaluators=evaluators, _use_pf_client=True)
        counting_eval._set_conversation_aggregation_type(_AggregationType.MAX)
        _ = evaluate(data=evaluate_test_data_conversion_jsonl_file, evaluators=evaluators, _use_pf_client=True)
        if use_async == "true":
            counting_eval._set_conversation_aggregator(custom_aggregator)
            _ = evaluate(data=evaluate_test_data_conversion_jsonl_file, evaluators=evaluators, _use_pf_client=True)
        else:
            with pytest.raises(EvaluationException) as exc_info:
                counting_eval._set_conversation_aggregator(custom_aggregator)
                _ = evaluate(data=evaluate_test_data_conversion_jsonl_file, evaluators=evaluators, _use_pf_client=True)
            assert "TestEvaluate.test_aggregation_serialization.<locals>.custom_aggregator" in exc_info.value.args[0]

    def test_unsupported_file_inputs(self, mock_model_config, unsupported_file_type):
        with pytest.raises(EvaluationException) as cm:
            evaluate(
                data=unsupported_file_type,
                evaluators={"groundedness": GroundednessEvaluator(model_config=mock_model_config)},
            )
        assert "Unable to load data from " in cm.value.args[0]
        assert "Supported formats are JSONL and CSV. Detailed error:" in cm.value.args[0]

    def test_malformed_file_inputs(self, model_config, missing_header_csv_file, missing_columns_jsonl_file):
        with pytest.raises(EvaluationException) as exc_info:
            evaluate(
                data=missing_columns_jsonl_file,
                evaluators={"similarity": SimilarityEvaluator(model_config=model_config)},
                fail_on_evaluator_errors=True,
            )

        assert "Either 'conversation' or individual inputs must be provided." in str(exc_info.value)

        with pytest.raises(EvaluationException) as exc_info:
            evaluate(
                data=missing_header_csv_file,
                evaluators={"similarity": SimilarityEvaluator(model_config=model_config)},
                fail_on_evaluator_errors=True,
            )

        assert "Either 'conversation' or individual inputs must be provided." in str(exc_info.value)

    def test_target_failure_error_message(self, questions_file):
        with pytest.raises(EvaluationException) as exc_info:
            evaluate(
                data=questions_file,
                evaluators={"f1_score": F1ScoreEvaluator()},
                target=_target_that_fails,
            )

        assert "Evaluation target failed to produce any results. Please check the logs at " in str(exc_info.value)

    def test_evaluate_korean_characters_result(self, questions_answers_korean_file):
        output_path = "eval_test_results_korean.jsonl"

        result = evaluate(
            data=questions_answers_korean_file,
            evaluators={"g": F1ScoreEvaluator()},
            output_path=output_path,
        )

        assert result is not None

        with open(questions_answers_korean_file, "r", encoding="utf-8") as f:
            first_line = f.readline()
            data_from_file = json.loads(first_line)

        assert result["rows"][0]["inputs.query"] == data_from_file["query"]

        os.remove(output_path)

    def test_name_map_conversion(self):
        test_map = {
            "name1": "property1",
            "name2": "property2",
            "name3": "property3",
        }
        map_dump = json.dumps(test_map)

        # Test basic
        result = _convert_name_map_into_property_entries(test_map)
        assert result[EvaluationRunProperties.NAME_MAP_LENGTH] == 1
        assert result[f"{EvaluationRunProperties.NAME_MAP}_0"] == map_dump

        # Test with splits (dump of test map is 66 characters long)
        result = _convert_name_map_into_property_entries(test_map, segment_length=40)
        assert result[EvaluationRunProperties.NAME_MAP_LENGTH] == 2
        combined_strings = (
            result[f"{EvaluationRunProperties.NAME_MAP}_0"] + result[f"{EvaluationRunProperties.NAME_MAP}_1"]
        )
        # breakpoint()
        assert result[f"{EvaluationRunProperties.NAME_MAP}_0"] == map_dump[0:40]
        assert result[f"{EvaluationRunProperties.NAME_MAP}_1"] == map_dump[40:]
        assert combined_strings == map_dump

        # Test with exact split
        result = _convert_name_map_into_property_entries(test_map, segment_length=22)
        assert result[EvaluationRunProperties.NAME_MAP_LENGTH] == 3
        combined_strings = (
            result[f"{EvaluationRunProperties.NAME_MAP}_0"]
            + result[f"{EvaluationRunProperties.NAME_MAP}_1"]
            + result[f"{EvaluationRunProperties.NAME_MAP}_2"]
        )
        assert result[f"{EvaluationRunProperties.NAME_MAP}_0"] == map_dump[0:22]
        assert result[f"{EvaluationRunProperties.NAME_MAP}_1"] == map_dump[22:44]
        assert result[f"{EvaluationRunProperties.NAME_MAP}_2"] == map_dump[44:]
        assert combined_strings == map_dump

        # Test failure case
        result = _convert_name_map_into_property_entries(test_map, segment_length=10, max_segments=1)
        assert result[EvaluationRunProperties.NAME_MAP_LENGTH] == -1
        assert len(result) == 1

    def test_evaluate_evaluator_only_kwargs_param(self, evaluate_test_data_jsonl_file):
        """Validate that an evaluator with only an **kwargs param receives all input in kwargs."""

        def evaluator(**kwargs):
            return locals()

        result = evaluate(data=evaluate_test_data_jsonl_file, evaluators={"test": evaluator})

        assert len(result["rows"]) == 3

        assert {"query", "response", "ground_truth", "context"}.issubset(result["rows"][0]["outputs.test.kwargs"])
        assert {"query", "response", "ground_truth", "context"}.issubset(result["rows"][1]["outputs.test.kwargs"])
        assert {"query", "response", "ground_truth", "context"}.issubset(result["rows"][2]["outputs.test.kwargs"])

    def test_evaluate_evaluator_kwargs_param(self, evaluate_test_data_jsonl_file):
        """Validate that an evaluator with named parameters and **kwargs obeys python function call semantics."""

        def evaluator(query, response, *, bar=None, **kwargs):
            return locals()

        result = evaluate(data=evaluate_test_data_jsonl_file, evaluators={"test": evaluator})

        assert len(result["rows"]) == 3

        row1_kwargs = result["rows"][0]["outputs.test.kwargs"]
        row2_kwargs = result["rows"][1]["outputs.test.kwargs"]
        row3_kwargs = result["rows"][2]["outputs.test.kwargs"]

        assert {"ground_truth", "context"}.issubset(row1_kwargs), "Unnamed parameters should be in kwargs"
        assert {"query", "response", "bar"}.isdisjoint(row1_kwargs), "Named parameters should not be in kwargs"

        assert {"ground_truth", "context"}.issubset(row2_kwargs), "Unnamed parameters should be in kwargs"
        assert {"query", "response", "bar"}.isdisjoint(row2_kwargs), "Named parameters should not be in kwargs"

        assert {"ground_truth", "context"}.issubset(row3_kwargs), "Unnamed parameters should be in kwargs"
        assert {"query", "response", "bar"}.isdisjoint(row3_kwargs), "Named parameters should not be in kwargs"

    def test_evaluate_evaluator_kwargs_param_column_mapping(self, evaluate_test_data_jsonl_file):
        """Validate that an evaluator with kwargs can receive column mapped values."""

        def evaluator(query, response, *, bar=None, **kwargs):
            return locals()

        result = evaluate(
            data=evaluate_test_data_jsonl_file,
            evaluators={"test": evaluator},
            evaluator_config={
                "default": {
                    "column_mapping": {
                        "query": "${data.query}",
                        "response": "${data.response}",
                        "foo": "${data.context}",
                        "bar": "${data.ground_truth}",
                    }
                }
            },
        )

        assert len(result["rows"]) == 3

        row1_kwargs = result["rows"][0]["outputs.test.kwargs"]
        row2_kwargs = result["rows"][1]["outputs.test.kwargs"]
        row3_kwargs = result["rows"][2]["outputs.test.kwargs"]

        assert {"ground_truth", "context"}.issubset(row1_kwargs), "Unnamed parameters should be in kwargs"
        assert "foo" in row1_kwargs, "Making a column mapping to an unnamed parameter should appear in kwargs"
        assert {"query", "response", "bar"}.isdisjoint(row1_kwargs), "Named parameters should not be in kwargs"

        assert {"ground_truth", "context"}.issubset(row2_kwargs), "Unnamed parameters should be in kwargs"
        assert "foo" in row2_kwargs, "Making a column mapping to an unnamed parameter should appear in kwargs"
        assert {"query", "response", "bar"}.isdisjoint(row2_kwargs), "Named parameters should not be in kwargs"

        assert {"ground_truth", "context"}.issubset(row3_kwargs), "Unnamed parameters should be in kwargs"
        assert "foo" in row3_kwargs, "Making a column mapping to an unnamed parameter should appear in kwargs"
        assert {"query", "response", "bar"}.isdisjoint(row3_kwargs), "Named parameters should not be in kwargs"

    def test_convert_results_to_aoai_evaluation_results(self):
        """Test _convert_results_to_aoai_evaluation_results function with test data"""
        import logging

        # Load test data from the JSON file
        parent = pathlib.Path(__file__).parent.resolve()
        test_data_path = os.path.join(parent, "data", "evaluation_util_convert_old_output_test.jsonl")
        test_input_eval_metadata_path = os.path.join(parent, "data", "evaluation_util_convert_eval_meta_data.json")
        test_input_eval_error_summary_path = os.path.join(parent, "data", "evaluation_util_convert_error_summary.json")
        test_expected_output_path = os.path.join(parent, "data", "evaluation_util_convert_expected_output.json")

        mock_model_config = AzureOpenAIModelConfiguration(
            azure_deployment="test-deployment",
            azure_endpoint="https://test-endpoint.openai.azure.com/",
            api_key="test-api-key",
            api_version="2024-12-01-preview",
        )
        fake_project = {"subscription_id": "123", "resource_group_name": "123", "project_name": "123"}

        evaluators = {
            "labelgrader": AzureOpenAILabelGrader(
                model_config=mock_model_config,
                input=[{"content": "{{item.query}}", "role": "user"}],
                labels=["positive", "negative", "neutral"],
                passing_labels=["neutral"],
                model="gpt-4o-2024-11-20",
                name="labelgrader",
            ),
            "violence": ViolenceEvaluator(None, fake_project),
            "self_harm": SelfHarmEvaluator(None, fake_project),
            "Fluency": FluencyEvaluator(model_config=mock_model_config),
            "ViolenceContentCustomEvaluator": callable(fake_project),
        }

        # Create logger
        logger = logging.getLogger("test_logger")
        # Read and parse the JSONL file (contains multiple JSON objects)
        test_rows = []
        with open(test_data_path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    logger.info(line)
                    test_rows.append(json.loads(line))
        test_eval_input_metadata = {}
        with open(test_input_eval_metadata_path, "r") as f:
            test_eval_input_metadata = json.load(f)
        test_eval_error_summary = {}
        with open(test_input_eval_error_summary_path, "r") as f:
            test_eval_error_summary = json.load(f)

        eval_id = "test_eval_group_123"
        eval_run_id = "test_run_456"
        # Create EvaluationResult structure
        test_results = {"metrics": {"overall_score": 0.75}, "rows": test_rows, "studio_url": "https://test-studio.com"}

        # Test the conversion function
        def run_test():
            _convert_results_to_aoai_evaluation_results(
                results=test_results,
                logger=logger,
                eval_run_id=eval_run_id,
                eval_id=eval_id,
                evaluators=evaluators,
                eval_run_summary=test_eval_error_summary,
                eval_meta_data=test_eval_input_metadata,
            )

        # Run the async function
        run_test()
        converted_results = test_results

        # Verify the structure
        assert "metrics" in converted_results
        assert "rows" in converted_results
        assert "studio_url" in converted_results
        assert "_evaluation_results_list" in converted_results
        assert "_evaluation_summary" in converted_results

        # Normalize timestamp for comparison
        result_list = []
        for item in converted_results["_evaluation_results_list"]:
            item["created_at"] = 1762319309  # Fixed timestamp for testing
            result_list.append(item)
        converted_results["_evaluation_results_list"] = result_list
        converted_results_json = json.loads(f"{json.dumps(converted_results)}")
        expected_results_json = None
        with open(test_expected_output_path, "r") as f:
            expected_results_json = json.load(f)
        assert converted_results_json == expected_results_json

        # Verify metrics preserved
        assert converted_results["metrics"]["overall_score"] == 0.75

        # Verify studio URL preserved
        assert converted_results["studio_url"] == "https://test-studio.com"

        # Verify _evaluation_results_list is same as rows (converted format)
        assert len(converted_results["_evaluation_results_list"]) == len(test_rows)
        assert len(converted_results["_evaluation_results_list"]) == len(converted_results["rows"])

        # Verify conversion structure for each row
        for i, converted_row in enumerate(converted_results["_evaluation_results_list"]):
            # Check RunOutputItem structure
            assert "object" in converted_row
            assert converted_row["object"] == "eval.run.output_item"
            assert "id" in converted_row
            assert "run_id" in converted_row
            assert "eval_id" in converted_row
            assert "created_at" in converted_row
            assert "datasource_item_id" in converted_row
            assert "results" in converted_row
            assert "sample" in converted_row

            # Verify IDs
            assert converted_row["run_id"] == "test_run_456"
            assert converted_row["eval_id"] == "test_eval_group_123"
            assert converted_row["datasource_item_id"] == i

            # Verify results array structure
            assert isinstance(converted_row["results"], list)

            # Check that results contain expected evaluator results
            result_names = [result.get("name") for result in converted_row["results"]]

            # Based on test data, should have violence and labelgrader
            if i < len(test_rows):
                original_row = test_rows[i]
                expected_evaluators = set()
                for key in original_row.keys():
                    if key.startswith("outputs."):
                        parts = key.split(".", 2)
                        if len(parts) >= 2:
                            expected_evaluators.add(parts[1])

                # Verify all expected evaluators are present in results
                for evaluator in expected_evaluators:
                    assert evaluator in result_names

            # Check individual result structure
            for result in converted_row["results"]:
                assert "type" in result
                assert "name" in result
                assert "metric" in result

        # Verify _evaluation_summary structure
        summary = converted_results["_evaluation_summary"]
        assert "result_counts" in summary
        assert "per_model_usage" in summary
        assert "per_testing_criteria_results" in summary

        # Check result counts structure
        result_counts = summary["result_counts"]
        assert "total" in result_counts
        assert "passed" in result_counts
        assert "failed" in result_counts
        assert "errored" in result_counts

        logger.info(result_counts)
        # Verify counts are non-negative integers
        for count_type, count_value in result_counts.items():
            assert isinstance(count_value, int)
            assert count_value >= 0

        # Check per_testing_criteria_results structure
        criteria_results = summary["per_testing_criteria_results"]
        assert isinstance(criteria_results, list)
        logger.info(criteria_results)
        for criteria_result in criteria_results:
            assert "testing_criteria" in criteria_result
            assert "passed" in criteria_result
            assert "failed" in criteria_result
            assert isinstance(criteria_result["passed"], int)
            assert isinstance(criteria_result["failed"], int)

        # Check per_model_usage structure
        model_usage = summary["per_model_usage"]
        assert isinstance(model_usage, list)
        for usage_item in model_usage:
            assert "model_name" in usage_item
            assert "invocation_count" in usage_item
            assert "total_tokens" in usage_item
            assert "prompt_tokens" in usage_item
            assert "completion_tokens" in usage_item
            assert "cached_tokens" in usage_item

        # Test with empty results
        empty_results = {"metrics": {}, "rows": [], "studio_url": None}
        _convert_results_to_aoai_evaluation_results(
            results=empty_results, logger=logger, eval_run_id=eval_run_id, eval_id=eval_id, evaluators=evaluators
        )
        empty_converted = empty_results

        assert len(empty_converted["rows"]) == 0
        assert len(empty_converted["_evaluation_results_list"]) == 0
        assert empty_converted["_evaluation_summary"]["result_counts"]["total"] == 0


@pytest.mark.unittest
class TestTagsInLoggingFunctions:
    """Test tag functionality in logging utility functions."""

    @patch("azure.ai.evaluation._evaluate._utils.LiteMLClient")
    @patch("azure.ai.evaluation._evaluate._eval_run.EvalRun")
    @patch("tempfile.TemporaryDirectory")
    def test_log_metrics_and_instance_results_with_tags(self, mock_tempdir, mock_eval_run, mock_lite_ml_client):
        """Test that tags are properly passed to EvalRun in MLflow logging path."""
        from azure.ai.evaluation._evaluate._utils import _log_metrics_and_instance_results

        # Mock tempfile directory
        mock_tempdir.return_value.__enter__.return_value = "/tmp/mock_tempdir"
        mock_tempdir.return_value.__exit__.return_value = None

        # Mock the management client and workspace info
        mock_client_instance = mock_lite_ml_client.return_value
        mock_workspace_info = type("MockWorkspaceInfo", (), {"ml_flow_tracking_uri": "https://test-tracking-uri"})()
        mock_client_instance.workspace_get_info.return_value = mock_workspace_info

        # Mock EvalRun class attribute
        mock_eval_run.EVALUATION_ARTIFACT = "evaluation_artifact.jsonl"

        # Mock EvalRun context manager
        mock_eval_run_instance = mock_eval_run.return_value.__enter__.return_value
        mock_eval_run_instance.log_artifact = lambda *args, **kwargs: None
        mock_eval_run_instance.write_properties_to_run_history = lambda *args, **kwargs: None
        mock_eval_run_instance.log_metric = lambda *args, **kwargs: None
        mock_eval_run_instance.info = type("MockInfo", (), {"run_id": "test-run-id"})()

        # Mock the file operations
        import builtins

        original_open = builtins.open

        def mock_open(*args, **kwargs):
            if args[0].startswith("/tmp/mock_tempdir"):
                # Return a mock file object that does nothing
                from unittest.mock import MagicMock

                mock_file = MagicMock()
                mock_file.write = lambda x: None
                mock_file.__enter__ = lambda self: mock_file
                mock_file.__exit__ = lambda self, *args: None
                return mock_file
            return original_open(*args, **kwargs)

        with patch("builtins.open", side_effect=mock_open):
            # Test data
            metrics = {"accuracy": 0.8, "f1_score": 0.7}
            instance_results = pd.DataFrame([{"input": "test", "output": "result"}])
            tags = {"experiment": "test-exp", "version": "1.0", "custom_tag": "value"}
            trace_destination = "azureml://subscriptions/test-sub/resourceGroups/test-rg/providers/Microsoft.MachineLearningServices/workspaces/test-ws"

            # Call the function
            result = _log_metrics_and_instance_results(
                metrics=metrics,
                instance_results=instance_results,
                trace_destination=trace_destination,
                run=None,
                evaluation_name="test-evaluation",
                name_map={},
                tags=tags,
            )

            # Verify that EvalRun was called with the correct tags
            mock_eval_run.assert_called_once()
            call_args = mock_eval_run.call_args
            assert call_args[1]["tags"] == tags
            assert call_args[1]["run_name"] == "test-evaluation"

    @patch("azure.ai.evaluation._evaluate._utils.LiteMLClient")
    @patch("azure.ai.evaluation._evaluate._eval_run.EvalRun")
    @patch("tempfile.TemporaryDirectory")
    def test_log_metrics_and_instance_results_with_none_tags(self, mock_tempdir, mock_eval_run, mock_lite_ml_client):
        """Test that None tags are handled properly in MLflow logging path."""
        from azure.ai.evaluation._evaluate._utils import _log_metrics_and_instance_results

        # Mock tempfile directory
        mock_tempdir.return_value.__enter__.return_value = "/tmp/mock_tempdir"
        mock_tempdir.return_value.__exit__.return_value = None

        # Mock the management client and workspace info
        mock_client_instance = mock_lite_ml_client.return_value
        mock_workspace_info = type("MockWorkspaceInfo", (), {"ml_flow_tracking_uri": "https://test-tracking-uri"})()
        mock_client_instance.workspace_get_info.return_value = mock_workspace_info

        # Mock EvalRun class attribute
        mock_eval_run.EVALUATION_ARTIFACT = "evaluation_artifact.jsonl"

        # Mock EvalRun context manager
        mock_eval_run_instance = mock_eval_run.return_value.__enter__.return_value
        mock_eval_run_instance.log_artifact = lambda *args, **kwargs: None
        mock_eval_run_instance.write_properties_to_run_history = lambda *args, **kwargs: None
        mock_eval_run_instance.log_metric = lambda *args, **kwargs: None
        mock_eval_run_instance.info = type("MockInfo", (), {"run_id": "test-run-id"})()

        # Mock the file operations
        import builtins

        original_open = builtins.open

        def mock_open(*args, **kwargs):
            if args[0].startswith("/tmp/mock_tempdir"):
                # Return a mock file object that does nothing
                from unittest.mock import MagicMock

                mock_file = MagicMock()
                mock_file.write = lambda x: None
                mock_file.__enter__ = lambda self: mock_file
                mock_file.__exit__ = lambda self, *args: None
                return mock_file
            return original_open(*args, **kwargs)

        with patch("builtins.open", side_effect=mock_open):
            # Test data
            metrics = {"accuracy": 0.8}
            instance_results = pd.DataFrame([{"input": "test", "output": "result"}])
            trace_destination = "azureml://subscriptions/test-sub/resourceGroups/test-rg/providers/Microsoft.MachineLearningServices/workspaces/test-ws"

            # Call the function with None tags
            result = _log_metrics_and_instance_results(
                metrics=metrics,
                instance_results=instance_results,
                trace_destination=trace_destination,
                run=None,
                evaluation_name="test-evaluation",
                name_map={},
                tags=None,
            )

            # Verify that EvalRun was called with None tags
            mock_eval_run.assert_called_once()
            call_args = mock_eval_run.call_args
            assert call_args[1]["tags"] is None

    def test_log_metrics_and_instance_results_no_trace_destination(self):
        """Test that function returns None when no trace destination is provided."""
        from azure.ai.evaluation._evaluate._utils import _log_metrics_and_instance_results

        # Test data
        metrics = {"accuracy": 0.8}
        instance_results = pd.DataFrame([{"input": "test", "output": "result"}])
        tags = {"test": "tag"}

        # Call the function with no trace destination
        result = _log_metrics_and_instance_results(
            metrics=metrics,
            instance_results=instance_results,
            trace_destination=None,
            run=None,
            evaluation_name="test-evaluation",
            name_map={},
            tags=tags,
        )

        # Should return None and not raise any exceptions
        assert result is None

    @patch("azure.ai.evaluation._azure._token_manager.AzureMLTokenManager")
    @patch("azure.ai.evaluation._common.EvaluationServiceOneDPClient")
    def test_log_metrics_and_instance_results_onedp_with_tags(self, mock_client_class, mock_token_manager):
        """Test that tags are properly passed to OneDP logging path."""
        from azure.ai.evaluation._evaluate._utils import _log_metrics_and_instance_results_onedp

        # Mock the client and its methods
        mock_client = mock_client_class.return_value

        # Mock create_evaluation_result
        mock_create_result = type("MockCreateResult", (), {"id": "test-result-id"})()
        mock_client.create_evaluation_result.return_value = mock_create_result

        # Mock start_evaluation_run
        mock_start_result = type("MockStartResult", (), {"id": "test-run-id"})()
        mock_client.start_evaluation_run.return_value = mock_start_result

        # Mock update_evaluation_run
        mock_update_result = type(
            "MockUpdateResult", (), {"properties": {"AiStudioEvaluationUri": "https://test-uri"}}
        )()
        mock_client.update_evaluation_run.return_value = mock_update_result

        # Test data
        metrics = {"accuracy": 0.8, "f1_score": 0.7}
        instance_results = pd.DataFrame([{"input": "test", "output": "result"}])
        tags = {"experiment": "test-exp", "version": "1.0", "model": "gpt-4"}
        project_url = "https://test-project.cognitiveservices.azure.com/api/projects/test-project"

        # Call the function
        result = _log_metrics_and_instance_results_onedp(
            metrics=metrics,
            instance_results=instance_results,
            project_url=project_url,
            evaluation_name="test-evaluation",
            name_map={},
            tags=tags,
        )

        # Verify that start_evaluation_run was called with tags
        mock_client.start_evaluation_run.assert_called_once()
        call_args = mock_client.start_evaluation_run.call_args
        eval_upload = call_args[1]["evaluation"]
        assert eval_upload.tags == tags

        # Verify return value
        assert result == "https://test-uri"

    @patch("azure.ai.evaluation._azure._token_manager.AzureMLTokenManager")
    @patch("azure.ai.evaluation._common.EvaluationServiceOneDPClient")
    def test_log_metrics_and_instance_results_onedp_with_none_tags(self, mock_client_class, mock_token_manager):
        """Test that None tags are handled properly in OneDP logging path."""
        from azure.ai.evaluation._evaluate._utils import _log_metrics_and_instance_results_onedp

        # Mock the client and its methods
        mock_client = mock_client_class.return_value

        # Mock create_evaluation_result
        mock_create_result = type("MockCreateResult", (), {"id": "test-result-id"})()
        mock_client.create_evaluation_result.return_value = mock_create_result

        # Mock start_evaluation_run
        mock_start_result = type("MockStartResult", (), {"id": "test-run-id"})()
        mock_client.start_evaluation_run.return_value = mock_start_result

        # Mock update_evaluation_run
        mock_update_result = type(
            "MockUpdateResult", (), {"properties": {"AiStudioEvaluationUri": "https://test-uri"}}
        )()
        mock_client.update_evaluation_run.return_value = mock_update_result

        # Test data
        metrics = {"accuracy": 0.8}
        instance_results = pd.DataFrame([{"input": "test", "output": "result"}])
        project_url = "https://test-project.cognitiveservices.azure.com/api/projects/test-project"

        # Call the function with None tags
        result = _log_metrics_and_instance_results_onedp(
            metrics=metrics,
            instance_results=instance_results,
            project_url=project_url,
            evaluation_name="test-evaluation",
            name_map={},
            tags=None,
        )

        # Verify that start_evaluation_run was called with None tags
        mock_client.start_evaluation_run.assert_called_once()
        call_args = mock_client.start_evaluation_run.call_args
        eval_upload = call_args[1]["evaluation"]
        assert eval_upload.tags is None

        # Verify return value
        assert result == "https://test-uri"

    @patch("azure.ai.evaluation._azure._token_manager.AzureMLTokenManager")
    @patch("azure.ai.evaluation._common.EvaluationServiceOneDPClient")
    def test_log_metrics_and_instance_results_onedp_with_empty_tags(self, mock_client_class, mock_token_manager):
        """Test that empty tags dictionary is handled properly in OneDP logging path."""
        from azure.ai.evaluation._evaluate._utils import _log_metrics_and_instance_results_onedp

        # Mock the client and its methods
        mock_client = mock_client_class.return_value

        # Mock create_evaluation_result
        mock_create_result = type("MockCreateResult", (), {"id": "test-result-id"})()
        mock_client.create_evaluation_result.return_value = mock_create_result

        # Mock start_evaluation_run
        mock_start_result = type("MockStartResult", (), {"id": "test-run-id"})()
        mock_client.start_evaluation_run.return_value = mock_start_result

        # Mock update_evaluation_run
        mock_update_result = type(
            "MockUpdateResult", (), {"properties": {"AiStudioEvaluationUri": "https://test-uri"}}
        )()
        mock_client.update_evaluation_run.return_value = mock_update_result

        # Test data
        metrics = {"accuracy": 0.8}
        instance_results = pd.DataFrame([{"input": "test", "output": "result"}])
        project_url = "https://test-project.cognitiveservices.azure.com/api/projects/test-project"
        empty_tags = {}

        # Call the function with empty tags
        result = _log_metrics_and_instance_results_onedp(
            metrics=metrics,
            instance_results=instance_results,
            project_url=project_url,
            evaluation_name="test-evaluation",
            name_map={},
            tags=empty_tags,
        )

        # Verify that start_evaluation_run was called with empty tags
        mock_client.start_evaluation_run.assert_called_once()
        call_args = mock_client.start_evaluation_run.call_args
        eval_upload = call_args[1]["evaluation"]
        assert eval_upload.tags == {}

    @patch("azure.ai.evaluation._azure._token_manager.AzureMLTokenManager")
    @patch("azure.ai.evaluation._common.EvaluationServiceOneDPClient")
    def test_log_metrics_and_instance_results_onedp_no_redundant_tags(self, mock_client_class, mock_token_manager):
        """Test that tags are properly included in properties for sync_evals."""
        from azure.ai.evaluation._evaluate._utils import _log_metrics_and_instance_results_onedp

        # Mock the client and its methods
        mock_client = mock_client_class.return_value

        # Mock create_evaluation_result
        mock_create_result = type("MockCreateResult", (), {"id": "test-result-id"})()
        mock_client.create_evaluation_result.return_value = mock_create_result

        # Mock start_evaluation_run
        mock_start_result = type("MockStartResult", (), {"id": "test-run-id"})()
        mock_client.start_evaluation_run.return_value = mock_start_result

        # Mock update_evaluation_run
        mock_update_result = type(
            "MockUpdateResult", (), {"properties": {"AiStudioEvaluationUri": "https://test-uri"}}
        )()
        mock_client.update_evaluation_run.return_value = mock_update_result

        # Mock data for the test
        metrics = {"accuracy": 0.95}
        instance_results = pd.DataFrame([{"input": "test", "output": "result"}])
        tags = {"tag1": "value1", "tag2": "value2"}

        # Call the function under test
        _log_metrics_and_instance_results_onedp(
            metrics=metrics,
            instance_results=instance_results,
            project_url="https://test-project.cognitiveservices.azure.com/api/projects/test-project",
            evaluation_name="test-evaluation",
            name_map={},
            tags=tags,
        )

        # Verify that start_evaluation_run was called with tags
        mock_client.start_evaluation_run.assert_called_once()
        call_args = mock_client.start_evaluation_run.call_args
        eval_upload = call_args[1]["evaluation"]
        assert eval_upload.tags == tags
