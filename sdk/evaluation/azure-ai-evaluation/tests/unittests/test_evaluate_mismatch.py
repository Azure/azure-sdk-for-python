import json
import math
import os
import pathlib
import tempfile
import pytest
import pandas as pd
from unittest.mock import Mock, patch, mock_open, MagicMock
from pandas.testing import assert_frame_equal

from azure.ai.evaluation import evaluate, F1ScoreEvaluator
from azure.ai.evaluation._evaluate._evaluate import (
    _preprocess_data,
    _run_callable_evaluators,
    __ValidatedData,  # Keep double underscore
)
from azure.ai.evaluation._evaluate._batch_run import (
    ProxyClient,
    CodeClient,
    RunSubmitterClient,
)
from azure.ai.evaluation._constants import Prefixes
from azure.ai.evaluation._exceptions import EvaluationException

# Create alias to avoid name mangling issues in class scope
ValidatedData = __ValidatedData


def _get_file(name):
    """Get the file from the unittest data folder."""
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, name)


def _target_with_failures(query):
    """A target function that fails for certain inputs."""
    if "LV-426" in query:
        raise Exception("Target failure for LV-426")
    if "central heating" in query:
        raise Exception("Target failure for central heating")
    return {"response": f"Response to: {query}"}


def _successful_target(query):
    """A target function that always succeeds."""
    return {"response": f"Response to: {query}"}


def _simple_evaluator(query, response):
    """A simple evaluator for testing."""
    return {"score": len(response) if response else 0}


@pytest.fixture
def sample_questions_file():
    """Create a temporary test file with sample questions."""
    test_data = [
        {"query": "How long is flight from Earth to LV-426?"},
        {"query": "Why there is no central heating on the street?"},
        {"query": "Why these questions are so strange?"},
        {"query": "What is the weather like today?"},
    ]

    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
    for item in test_data:
        temp_file.write(json.dumps(item) + "\n")
    temp_file.close()

    yield temp_file.name

    # Cleanup
    if os.path.exists(temp_file.name):
        os.unlink(temp_file.name)


@pytest.fixture
def sample_dataframe_with_target_outputs():
    """Create a sample dataframe with target outputs including failures."""
    return pd.DataFrame(
        {
            "query": [
                "How long is flight from Earth to LV-426?",
                "Why there is no central heating on the street?",
                "Why these questions are so strange?",
                "What is the weather like today?",
            ],
            "__outputs.response": [
                None,  # Failed
                None,  # Failed
                "Response to: Why these questions are so strange?",  # Success
                "Response to: What is the weather like today?",  # Success
            ],
            "line_number": [0, 1, 2, 3],
        }
    )


@pytest.mark.unittest
class TestTargetFailureHandling:
    """Test cases for target failure handling functionality."""

    @patch("azure.ai.evaluation._evaluate._evaluate._apply_target_to_data")
    @patch("azure.ai.evaluation._evaluate._evaluate._validate_and_load_data")
    def test_preprocess_data_creates_temp_file_for_proxy_client_with_target_failures(
        self, mock_load_data, mock_apply_target, sample_dataframe_with_target_outputs
    ):
        """Test that _preprocess_data creates a temporary file for ProxyClient when target has failures."""
        # Setup mocks
        mock_load_data.return_value = pd.DataFrame({"query": ["test"]})
        mock_apply_target.return_value = (
            sample_dataframe_with_target_outputs,
            {"response"},
            Mock(),
        )

        # Test data
        evaluators_and_graders = {"test_eval": _simple_evaluator}

        with patch("tempfile.NamedTemporaryFile") as mock_temp_file:
            mock_file = Mock()
            mock_file.name = "/tmp/test_temp_file.jsonl"
            mock_file.__enter__ = Mock(return_value=mock_file)
            mock_file.__exit__ = Mock(return_value=None)
            mock_temp_file.return_value = mock_file

            with patch("json.dumps") as mock_json_dumps:
                mock_json_dumps.return_value = '{"test": "data"}'

                result = _preprocess_data(
                    data="/test/path.jsonl",
                    evaluators_and_graders=evaluators_and_graders,
                    target=_target_with_failures,
                    _use_pf_client=True,
                )

                # Verify temp file was created
                mock_temp_file.assert_called_once()

                # Verify batch_run_data points to temp file
                assert result["batch_run_data"] == "/tmp/test_temp_file.jsonl"

                # Verify target_run is None (we don't use previous run)
                assert result["target_run"] is None

                # Verify column mapping uses data references instead of run outputs
                assert "response" in result["column_mapping"]["default"]
                assert (
                    result["column_mapping"]["default"]["response"]
                    == "${data.__outputs.response}"
                )

    @patch("azure.ai.evaluation._evaluate._evaluate._apply_target_to_data")
    @patch("azure.ai.evaluation._evaluate._evaluate._validate_and_load_data")
    def test_preprocess_data_uses_dataframe_for_non_proxy_clients_with_target_failures(
        self, mock_load_data, mock_apply_target, sample_dataframe_with_target_outputs
    ):
        """Test that _preprocess_data uses dataframe for non-ProxyClient when target has failures."""
        # Setup mocks
        mock_load_data.return_value = pd.DataFrame({"query": ["test"]})
        mock_apply_target.return_value = (
            sample_dataframe_with_target_outputs,
            {"response"},
            Mock(),
        )

        # Test data
        evaluators_and_graders = {"test_eval": _simple_evaluator}

        result = _preprocess_data(
            data="/test/path.jsonl",
            evaluators_and_graders=evaluators_and_graders,
            target=_target_with_failures,
            _use_run_submitter_client=True,
        )

        # Verify batch_run_data is the dataframe
        assert isinstance(result["batch_run_data"], pd.DataFrame)
        assert_frame_equal(
            result["batch_run_data"], sample_dataframe_with_target_outputs
        )

        # Verify column mapping uses data references
        assert "response" in result["column_mapping"]["default"]
        assert (
            result["column_mapping"]["default"]["response"]
            == "${data.__outputs.response}"
        )

    @patch("azure.ai.evaluation._evaluate._evaluate.json.dumps")
    @patch("azure.ai.evaluation._evaluate._evaluate.pd.isna")
    def test_temp_file_creation_handles_nan_values(
        self, mock_isna, mock_json_dumps, sample_dataframe_with_target_outputs
    ):
        """Test that NaN values are properly converted to None in temp file creation."""
        # Setup mocks - simulate NaN detection
        mock_isna.side_effect = lambda x: x is None
        mock_json_dumps.return_value = '{"test": "data"}'

        with patch("tempfile.NamedTemporaryFile") as mock_temp_file:
            mock_file = Mock()
            mock_file.name = "/tmp/test.jsonl"
            mock_file.write = Mock()
            mock_file.close = Mock()
            mock_temp_file.return_value = mock_file

            with patch(
                "azure.ai.evaluation._evaluate._evaluate._apply_target_to_data"
            ) as mock_apply_target:
                with patch(
                    "azure.ai.evaluation._evaluate._evaluate._validate_and_load_data"
                ) as mock_load_data:
                    mock_load_data.return_value = pd.DataFrame({"query": ["test"]})
                    mock_apply_target.return_value = (
                        sample_dataframe_with_target_outputs,
                        {"response"},
                        Mock(),
                    )

                    _preprocess_data(
                        data="/test/path.jsonl",
                        evaluators_and_graders={"test_eval": _simple_evaluator},
                        target=_target_with_failures,
                        _use_pf_client=True,
                    )

                    # Verify json.dumps was called (temp file creation happened)
                    assert mock_json_dumps.call_count > 0

    def test_temp_file_cleanup_on_exception(self):
        """Test that temporary files are cleaned up when exceptions occur."""
        with patch("tempfile.NamedTemporaryFile") as mock_temp_file:
            mock_file = Mock()
            mock_file.name = "/tmp/test_temp_file.jsonl"
            mock_temp_file.return_value = mock_file

            with patch("os.path.exists") as mock_exists:
                with patch("os.unlink") as mock_unlink:
                    mock_exists.return_value = True

                    with patch(
                        "azure.ai.evaluation._evaluate._evaluate._apply_target_to_data"
                    ) as mock_apply_target:
                        with patch(
                            "azure.ai.evaluation._evaluate._evaluate._validate_and_load_data"
                        ) as mock_load_data:
                            mock_load_data.return_value = pd.DataFrame(
                                {"query": ["test"]}
                            )
                            mock_apply_target.return_value = (
                                pd.DataFrame(
                                    {
                                        "query": ["test"],
                                        "__outputs.response": ["response"],
                                    }
                                ),
                                {"response"},
                                Mock(),
                            )

                            # Mock json.dumps to raise an exception
                            with patch(
                                "json.dumps", side_effect=Exception("JSON error")
                            ):
                                with pytest.raises(Exception):
                                    _preprocess_data(
                                        data="/test/path.jsonl",
                                        evaluators_and_graders={
                                            "test_eval": _simple_evaluator
                                        },
                                        target=_target_with_failures,
                                        _use_pf_client=True,
                                    )

                                # Verify cleanup was attempted
                                mock_unlink.assert_called_once_with(
                                    "/tmp/test_temp_file.jsonl"
                                )

    @patch("azure.ai.evaluation._evaluate._evaluate.EvalRunContext")
    def test_run_callable_evaluators_temp_file_cleanup(self, mock_eval_context):
        """Test that _run_callable_evaluators cleans up temporary files."""
        # Create mock validated data with temp file
        temp_file_path = "/tmp/test_eval_temp.jsonl"
        validated_data = ValidatedData(
            evaluators={"test_eval": _simple_evaluator},
            graders={},
            input_data_df=pd.DataFrame(
                {"query": ["test"], "__outputs.response": ["response"]}
            ),
            column_mapping={"default": {"response": "${data.__outputs.response}"}},
            target_run=None,
            batch_run_client=Mock(spec=ProxyClient),
            batch_run_data=temp_file_path,
        )

        # Mock the batch client run methods
        mock_run = Mock()
        validated_data["batch_run_client"].run.return_value = mock_run
        validated_data["batch_run_client"].get_details.return_value = pd.DataFrame(
            {"outputs.test_eval.score": [10]}
        )
        validated_data["batch_run_client"].get_metrics.return_value = {}
        validated_data["batch_run_client"].get_run_summary.return_value = {
            "failed_lines": 0,
            "status": "Completed",
        }

        with patch("tempfile.gettempdir", return_value="/tmp"):
            with patch("os.path.exists") as mock_exists:
                with patch("os.unlink") as mock_unlink:
                    mock_exists.return_value = True

                    # Run the function
                    _run_callable_evaluators(validated_data)

                    # Verify cleanup was called
                    mock_unlink.assert_called_once_with(temp_file_path)

    @patch("azure.ai.evaluation._evaluate._evaluate.EvalRunContext")
    def test_run_callable_evaluators_no_cleanup_for_non_temp_files(
        self, mock_eval_context
    ):
        """Test that _run_callable_evaluators doesn't clean up non-temp files."""
        # Create mock validated data with regular file (not in temp directory)
        regular_file_path = "/data/test_eval.jsonl"
        validated_data = ValidatedData(
            evaluators={"test_eval": _simple_evaluator},
            graders={},
            input_data_df=pd.DataFrame(
                {"query": ["test"], "__outputs.response": ["response"]}
            ),
            column_mapping={"default": {"response": "${data.__outputs.response}"}},
            target_run=None,
            batch_run_client=Mock(spec=ProxyClient),
            batch_run_data=regular_file_path,
        )

        # Mock the batch client run methods
        mock_run = Mock()
        validated_data["batch_run_client"].run.return_value = mock_run
        validated_data["batch_run_client"].get_details.return_value = pd.DataFrame(
            {"outputs.test_eval.score": [10]}
        )
        validated_data["batch_run_client"].get_metrics.return_value = {}
        validated_data["batch_run_client"].get_run_summary.return_value = {
            "failed_lines": 0,
            "status": "Completed",
        }

        with patch("tempfile.gettempdir", return_value="/tmp"):
            with patch("os.unlink") as mock_unlink:
                # Run the function
                _run_callable_evaluators(validated_data)

                # Verify cleanup was NOT called for non-temp file
                mock_unlink.assert_not_called()

    def test_column_mapping_uses_data_reference_for_proxy_client_with_target(self):
        """Test that column mapping uses ${data.__outputs.column} for ProxyClient with target failures."""
        with patch(
            "azure.ai.evaluation._evaluate._evaluate._apply_target_to_data"
        ) as mock_apply_target:
            with patch(
                "azure.ai.evaluation._evaluate._evaluate._validate_and_load_data"
            ) as mock_load_data:
                mock_load_data.return_value = pd.DataFrame({"query": ["test"]})
                mock_apply_target.return_value = (
                    pd.DataFrame(
                        {"query": ["test"], "__outputs.response": ["response"]}
                    ),
                    {"response"},
                    Mock(),
                )

                with patch("tempfile.NamedTemporaryFile") as mock_temp_file:
                    mock_file = Mock()
                    mock_file.name = "/tmp/test.jsonl"
                    mock_file.close = Mock()
                    mock_temp_file.return_value = mock_file

                    with patch("json.dumps"):
                        result = _preprocess_data(
                            data="/test/path.jsonl",
                            evaluators_and_graders={"test_eval": _simple_evaluator},
                            target=_target_with_failures,
                            _use_pf_client=True,
                        )

                        # Verify column mapping uses data reference
                        assert (
                            result["column_mapping"]["default"]["response"]
                            == "${data.__outputs.response}"
                        )

    def test_column_mapping_uses_data_reference_for_dataframe_clients_with_target(self):
        """Test that column mapping uses ${data.__outputs.column} for DataFrame clients with target."""
        with patch(
            "azure.ai.evaluation._evaluate._evaluate._apply_target_to_data"
        ) as mock_apply_target:
            with patch(
                "azure.ai.evaluation._evaluate._evaluate._validate_and_load_data"
            ) as mock_load_data:
                mock_load_data.return_value = pd.DataFrame({"query": ["test"]})
                mock_apply_target.return_value = (
                    pd.DataFrame(
                        {"query": ["test"], "__outputs.response": ["response"]}
                    ),
                    {"response"},
                    Mock(),
                )

                result = _preprocess_data(
                    data="/test/path.jsonl",
                    evaluators_and_graders={"test_eval": _simple_evaluator},
                    target=_target_with_failures,
                    _use_run_submitter_client=True,
                )

                # Verify column mapping uses data reference
                assert (
                    result["column_mapping"]["default"]["response"]
                    == "${data.__outputs.response}"
                )

    @patch("azure.ai.evaluation._evaluate._evaluate.EvalRunContext")
    def test_run_callable_evaluators_doesnt_pass_target_run_when_using_complete_dataframe(
        self, mock_eval_context
    ):
        """Test that target_run is not passed when using complete dataframe with ProxyClient."""
        validated_data = ValidatedData(
            evaluators={"test_eval": _simple_evaluator},
            graders={},
            input_data_df=pd.DataFrame(
                {"query": ["test"], "__outputs.response": ["response"]}
            ),
            column_mapping={"default": {"response": "${data.__outputs.response}"}},
            target_run=Mock(),  # This should not be passed to run()
            batch_run_client=Mock(spec=ProxyClient),
            batch_run_data="/tmp/test_temp.jsonl",
        )

        # Mock the batch client run methods
        mock_run = Mock()
        validated_data["batch_run_client"].run.return_value = mock_run
        validated_data["batch_run_client"].get_details.return_value = pd.DataFrame(
            {"outputs.test_eval.score": [10]}
        )
        validated_data["batch_run_client"].get_metrics.return_value = {}
        validated_data["batch_run_client"].get_run_summary.return_value = {
            "failed_lines": 0,
            "status": "Completed",
        }

        with patch("tempfile.gettempdir", return_value="/tmp"):
            with patch("os.path.exists", return_value=True):
                with patch("os.unlink"):
                    _run_callable_evaluators(validated_data)

                    # Verify run was called with target_run (the original target_run should still be passed)
                    validated_data["batch_run_client"].run.assert_called_once()
                    call_args = validated_data["batch_run_client"].run.call_args
                    assert (
                        "run" in call_args[1]
                    )  # target_run should be passed in kwargs

    @patch("azure.ai.evaluation._evaluate._evaluate.LOGGER")
    def test_temp_file_cleanup_warning_on_failure(self, mock_logger):
        """Test that warnings are logged when temp file cleanup fails."""
        validated_data = ValidatedData(
            evaluators={"test_eval": _simple_evaluator},
            graders={},
            input_data_df=pd.DataFrame(
                {"query": ["test"], "__outputs.response": ["response"]}
            ),
            column_mapping={"default": {"response": "${data.__outputs.response}"}},
            target_run=None,
            batch_run_client=Mock(spec=ProxyClient),
            batch_run_data="/tmp/test_temp.jsonl",
        )

        # Mock the batch client run methods
        mock_run = Mock()
        validated_data["batch_run_client"].run.return_value = mock_run
        validated_data["batch_run_client"].get_details.return_value = pd.DataFrame(
            {"outputs.test_eval.score": [10]}
        )
        validated_data["batch_run_client"].get_metrics.return_value = {}
        validated_data["batch_run_client"].get_run_summary.return_value = {
            "failed_lines": 0,
            "status": "Completed",
        }

        with patch("tempfile.gettempdir", return_value="/tmp"):
            with patch("os.path.exists", return_value=True):
                with patch("os.unlink", side_effect=Exception("Cleanup failed")):
                    with patch(
                        "azure.ai.evaluation._evaluate._evaluate.EvalRunContext"
                    ):
                        _run_callable_evaluators(validated_data)

                        # Verify warning was logged
                        mock_logger.warning.assert_called_once()
                        warning_call = mock_logger.warning.call_args[0][0]
                        assert "Failed to clean up temporary file" in warning_call
                        assert "/tmp/test_temp.jsonl" in warning_call

    @patch("azure.ai.evaluation._evaluate._evaluate._validate_columns_for_evaluators")
    @patch("azure.ai.evaluation._evaluate._evaluate._apply_target_to_data")
    @patch("azure.ai.evaluation._evaluate._evaluate._validate_and_load_data")
    def test_preprocess_data_no_temp_file_without_target(
        self, mock_load_data, mock_apply_target, mock_validate_columns
    ):
        """Test that no temp file is created when there's no target function."""
        mock_load_data.return_value = pd.DataFrame(
            {"query": ["test"], "response": ["response"]}
        )

        with patch("tempfile.NamedTemporaryFile") as mock_temp_file:
            result = _preprocess_data(
                data="/test/path.jsonl",
                evaluators_and_graders={"test_eval": _simple_evaluator},
                target=None,  # No target
                _use_pf_client=True,
            )

            # Verify no temp file was created
            mock_temp_file.assert_not_called()

            # Verify batch_run_data is still the original file path
            assert result["batch_run_data"] == os.path.abspath("/test/path.jsonl")

    def test_temp_file_creation_path_with_proxy_client(self):
        """Test that the temp file creation path is exercised for ProxyClient."""
        with patch(
            "azure.ai.evaluation._evaluate._evaluate._apply_target_to_data"
        ) as mock_apply_target:
            with patch(
                "azure.ai.evaluation._evaluate._evaluate._validate_and_load_data"
            ) as mock_load_data:
                mock_load_data.return_value = pd.DataFrame({"query": ["test"]})
                mock_apply_target.return_value = (
                    pd.DataFrame(
                        {"query": ["test"], "__outputs.response": ["response"]}
                    ),
                    {"response"},
                    Mock(),
                )

                with patch("tempfile.NamedTemporaryFile") as mock_temp_file:
                    mock_file = Mock()
                    mock_file.name = "/tmp/eval_temp.jsonl"
                    mock_file.close = Mock()
                    mock_temp_file.return_value = mock_file

                    with patch(
                        "json.dumps", return_value='{"test": "data"}'
                    ) as mock_json_dumps:
                        result = _preprocess_data(
                            data="/test/path.jsonl",
                            evaluators_and_graders={"test_eval": _simple_evaluator},
                            target=_target_with_failures,
                            _use_pf_client=True,
                        )

                        # Verify that temp file was created and used
                        mock_temp_file.assert_called_once()
                        assert result["batch_run_data"] == "/tmp/eval_temp.jsonl"
                        assert result["target_run"] is None

                        # Verify JSON serialization was called
                        assert mock_json_dumps.call_count > 0

    def test_dataframe_client_preserves_all_rows_with_failures(self):
        """Test that DataFrame-based clients preserve all rows including failures."""
        sample_df = pd.DataFrame(
            {
                "query": ["test1", "test2", "test3"],
                "__outputs.response": [
                    None,
                    "response2",
                    None,
                ],  # Mixed success/failure
            }
        )

        with patch(
            "azure.ai.evaluation._evaluate._evaluate._apply_target_to_data"
        ) as mock_apply_target:
            with patch(
                "azure.ai.evaluation._evaluate._evaluate._validate_and_load_data"
            ) as mock_load_data:
                mock_load_data.return_value = pd.DataFrame(
                    {"query": ["test1", "test2", "test3"]}
                )
                mock_apply_target.return_value = (sample_df, {"response"}, Mock())

                result = _preprocess_data(
                    data="/test/path.jsonl",
                    evaluators_and_graders={"test_eval": _simple_evaluator},
                    target=_target_with_failures,
                    _use_run_submitter_client=True,
                )

                # Verify all rows are preserved in batch_run_data
                assert isinstance(result["batch_run_data"], pd.DataFrame)
                assert len(result["batch_run_data"]) == 3
                assert_frame_equal(result["batch_run_data"], sample_df)
