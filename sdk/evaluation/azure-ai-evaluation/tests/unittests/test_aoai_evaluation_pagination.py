# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, List
from unittest.mock import MagicMock, Mock, patch

import httpx
import pandas as pd
import pytest
from openai import APIStatusError, APITimeoutError

from azure.ai.evaluation import evaluate
from azure.ai.evaluation._evaluate._evaluate_aoai import (
    OAIEvalRunCreationInfo,
    _get_single_run_results,
    _list_output_items_page,
    _wait_for_run_conclusion,
)
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException


class MockOutputItem:
    """Mock class for output items"""

    def __init__(self, id: str, datasource_item_id: int, results: List[dict]):
        self.id = id
        self.datasource_item_id = datasource_item_id
        self.results = results


class MockOutputItemsList:
    """Mock class for paginated results"""

    def __init__(self, data: List[MockOutputItem], has_more: bool = False):
        self.data = data
        self.has_more = has_more


def _mock_openai_client():
    client = Mock()
    client.with_options.return_value = client
    client._calculate_retry_timeout.return_value = 0
    return client


def _api_status_error(status_code, headers=None):
    response = httpx.Response(
        status_code=status_code,
        headers=headers,
        request=httpx.Request("GET", "https://example.test/output_items"),
    )
    return APIStatusError(f"status {status_code}", response=response, body=None)


class TestAOAIPagination:
    """Test pagination functionality in AOAI evaluation results"""

    @pytest.mark.parametrize(
        "evaluate_kwargs, expected_page_size",
        [
            ({}, 100),
            ({"aoai_output_items_page_size": 3}, 3),
        ],
    )
    def test_evaluate_propagates_page_size_to_every_native_grader_run(self, evaluate_kwargs, expected_page_size):
        clients = [_mock_openai_client(), _mock_openai_client()]
        input_data = pd.DataFrame([{"query": "hi"}])
        run_info = [
            OAIEvalRunCreationInfo(
                client=clients[0],
                eval_group_id="group-1",
                eval_run_id="run-1",
                grader_name_map={"grader-1": "first_grader"},
                expected_rows=1,
            ),
            OAIEvalRunCreationInfo(
                client=clients[1],
                eval_group_id="group-2",
                eval_run_id="run-2",
                grader_name_map={"grader-2": "second_grader"},
                expected_rows=1,
            ),
        ]
        completed_runs = []
        for grader_id in ("grader-1", "grader-2"):
            completed_run = Mock()
            completed_run.status = "completed"
            completed_run.per_testing_criteria_results = [Mock(testing_criteria=grader_id, passed=1, failed=0)]
            completed_runs.append(completed_run)

        clients[0].evals.runs.output_items.list.return_value = MockOutputItemsList(
            data=[
                MockOutputItem(
                    id="item-0",
                    datasource_item_id=0,
                    results=[{"name": "grader-1", "passed": True, "score": 0.9}],
                )
            ]
        )
        clients[1].evals.runs.output_items.list.return_value = MockOutputItemsList(
            data=[
                MockOutputItem(
                    id="item-0",
                    datasource_item_id=0,
                    results=[{"name": "grader-2", "passed": True, "score": 0.8}],
                )
            ]
        )

        with patch(
            "azure.ai.evaluation._evaluate._evaluate._preprocess_data",
            return_value={
                "column_mapping": {},
                "evaluators": {},
                "graders": {"first_grader": object(), "second_grader": object()},
                "input_data_df": input_data,
                "target_run": None,
                "batch_run_client": None,
                "batch_run_data": None,
            },
        ), patch(
            "azure.ai.evaluation._evaluate._evaluate._begin_aoai_evaluation",
            return_value=run_info,
        ), patch(
            "azure.ai.evaluation._evaluate._evaluate_aoai._wait_for_run_conclusion",
            side_effect=completed_runs,
        ), patch(
            "azure.ai.evaluation._evaluate._evaluate._map_names_to_builtins",
            return_value={},
        ):
            result = evaluate(data="unused.jsonl", evaluators={"grader": object()}, **evaluate_kwargs)

        assert len(result["rows"]) == 1
        assert result["metrics"] == {"first_grader.pass_rate": 1.0, "second_grader.pass_rate": 1.0}
        for client in clients:
            client.with_options.assert_called_once_with(max_retries=0)
            client.evals.runs.output_items.list.assert_called_once()
            assert client.evals.runs.output_items.list.call_args.kwargs["limit"] == expected_page_size

    @pytest.mark.parametrize("invalid_page_size", [True, False, "3", 3.0, 3.5, 0, -1, 101])
    def test_evaluate_rejects_invalid_page_size_before_any_evaluation_work(self, invalid_page_size):
        with patch("azure.ai.evaluation._evaluate._evaluate._preprocess_data") as mock_preprocess, patch(
            "azure.ai.evaluation._evaluate._evaluate.UserAgentSingleton.add_useragent_product"
        ) as mock_add_user_agent:
            with pytest.raises(EvaluationException) as exc_info:
                evaluate(
                    data="unused.jsonl",
                    evaluators={},
                    aoai_output_items_page_size=invalid_page_size,
                    user_agent="custom/1",
                )

        mock_preprocess.assert_not_called()
        mock_add_user_agent.assert_not_called()
        assert exc_info.value.blame == ErrorBlame.USER_ERROR
        assert exc_info.value.category == ErrorCategory.INVALID_VALUE
        assert exc_info.value.target == ErrorTarget.EVALUATE
        assert "'aoai_output_items_page_size' must be an integer between 1 and 100" in str(exc_info.value)

    def test_single_page_results(self):
        """Test handling of single page results (no pagination needed)"""
        # Mock client and run info
        mock_client = _mock_openai_client()
        run_info = OAIEvalRunCreationInfo(
            client=mock_client,
            eval_group_id="test-group",
            eval_run_id="test-run",
            grader_name_map={"grader-1": "test_grader"},
            expected_rows=10,
        )

        # Mock the wait_for_run_conclusion response
        mock_run_results = Mock()
        mock_run_results.status = "completed"
        mock_run_results.per_testing_criteria_results = [Mock(testing_criteria="grader-1", passed=8, failed=2)]

        # Mock single page of results
        mock_output_items = [
            MockOutputItem(
                id=f"item-{i}",
                datasource_item_id=i,
                results=[
                    {
                        "name": "grader-1",
                        "passed": i % 2 == 0,
                        "score": 0.8 if i % 2 == 0 else 0.2,
                        "sample": f"Sample {i}",
                    }
                ],
            )
            for i in range(10)
        ]

        mock_list_response = MockOutputItemsList(data=mock_output_items, has_more=False)
        mock_client.evals.runs.output_items.list.return_value = mock_list_response

        with patch(
            "azure.ai.evaluation._evaluate._evaluate_aoai._wait_for_run_conclusion", return_value=mock_run_results
        ):
            df, metrics = _get_single_run_results(run_info)

        # Verify results
        assert len(df) == 10
        assert "outputs.test_grader.passed" in df.columns
        assert "outputs.test_grader.score" in df.columns
        assert metrics["test_grader.pass_rate"] == 0.8

        # Verify list was called once (no pagination)
        assert mock_client.evals.runs.output_items.list.call_count == 1

    def test_multi_page_results(self):
        """Test handling of multi-page results with pagination"""
        mock_client = _mock_openai_client()
        run_info = OAIEvalRunCreationInfo(
            client=mock_client,
            eval_group_id="test-group",
            eval_run_id="test-run",
            grader_name_map={"grader-1": "test_grader"},
            expected_rows=250,
        )

        # Mock run results
        mock_run_results = Mock()
        mock_run_results.status = "completed"
        mock_run_results.per_testing_criteria_results = [Mock(testing_criteria="grader-1", passed=80, failed=20)]

        # Create 3 pages of results
        page1_items = [
            MockOutputItem(
                id=f"item-{i}",
                datasource_item_id=i,
                results=[{"name": "grader-1", "passed": True, "score": 0.9, "sample": f"Sample {i}"}],
            )
            for i in range(100)
        ]

        page2_items = [
            MockOutputItem(
                id=f"item-{i}",
                datasource_item_id=i,
                results=[{"name": "grader-1", "passed": True, "score": 0.85, "sample": f"Sample {i}"}],
            )
            for i in range(100, 200)
        ]

        page3_items = [
            MockOutputItem(
                id=f"item-{i}",
                datasource_item_id=i,
                results=[{"name": "grader-1", "passed": False, "score": 0.3, "sample": f"Sample {i}"}],
            )
            for i in range(200, 250)
        ]

        # Mock paginated responses
        responses = [
            MockOutputItemsList(data=page1_items, has_more=True),
            MockOutputItemsList(data=page2_items, has_more=True),
            MockOutputItemsList(data=page3_items, has_more=False),
        ]

        mock_client.evals.runs.output_items.list.side_effect = responses

        with patch(
            "azure.ai.evaluation._evaluate._evaluate_aoai._wait_for_run_conclusion", return_value=mock_run_results
        ):
            df, metrics = _get_single_run_results(run_info)

        # Verify all results were collected
        assert len(df) == 250
        assert mock_client.evals.runs.output_items.list.call_count == 3

        # Verify pagination parameters
        calls = mock_client.evals.runs.output_items.list.call_args_list
        assert calls[0][1]["eval_id"] == "test-group"
        assert calls[0][1]["run_id"] == "test-run"
        assert calls[0][1]["limit"] == 100
        assert "after" not in calls[0][1]

        assert calls[1][1]["after"] == "item-99"  # Last item ID from page 1
        assert calls[2][1]["after"] == "item-199"  # Last item ID from page 2

    def test_empty_page_handling(self):
        """Test handling of empty pages in pagination"""
        mock_client = _mock_openai_client()
        run_info = OAIEvalRunCreationInfo(
            client=mock_client,
            eval_group_id="test-group",
            eval_run_id="test-run",
            grader_name_map={"grader-1": "test_grader"},
            expected_rows=5,
        )

        mock_run_results = Mock()
        mock_run_results.status = "completed"
        mock_run_results.per_testing_criteria_results = [Mock(testing_criteria="grader-1", passed=5, failed=0)]

        # First page has data, second page is empty but has_more=True, third page breaks loop
        responses = [
            MockOutputItemsList(
                data=[
                    MockOutputItem(
                        id=f"item-{i}",
                        datasource_item_id=i,
                        results=[{"name": "grader-1", "passed": True, "score": 1.0}],
                    )
                    for i in range(5)
                ],
                has_more=True,
            ),
            MockOutputItemsList(data=[], has_more=True),  # Empty page
            MockOutputItemsList(data=[], has_more=False),
        ]

        mock_client.evals.runs.output_items.list.side_effect = responses

        with patch(
            "azure.ai.evaluation._evaluate._evaluate_aoai._wait_for_run_conclusion", return_value=mock_run_results
        ):
            df, metrics = _get_single_run_results(run_info)

        assert len(df) == 5
        assert metrics["test_grader.pass_rate"] == 1.0

    def test_result_ordering_preservation(self):
        """Test that results maintain proper ordering after pagination"""
        mock_client = _mock_openai_client()
        run_info = OAIEvalRunCreationInfo(
            client=mock_client,
            eval_group_id="test-group",
            eval_run_id="test-run",
            grader_name_map={"grader-1": "test_grader"},
            expected_rows=10,
        )

        mock_run_results = Mock()
        mock_run_results.status = "completed"
        mock_run_results.per_testing_criteria_results = [Mock(testing_criteria="grader-1", passed=20, failed=0)]

        # Create results in non-sequential order across pages, covering ids 0..9 exactly
        page1_items = [
            MockOutputItem(
                id=f"item-{i}",
                datasource_item_id=i,  # was i * 2
                results=[{"name": "grader-1", "passed": True, "score": i}],
            )
            for i in [5, 3, 8, 1, 9]
        ]

        page2_items = [
            MockOutputItem(
                id=f"item-{i}",
                datasource_item_id=i,  # was i * 2
                results=[{"name": "grader-1", "passed": True, "score": i}],
            )
            for i in [2, 7, 4, 6, 0]
        ]

        responses = [
            MockOutputItemsList(data=page1_items, has_more=True),
            MockOutputItemsList(data=page2_items, has_more=False),
        ]

        mock_client.evals.runs.output_items.list.side_effect = responses

        with patch(
            "azure.ai.evaluation._evaluate._evaluate_aoai._wait_for_run_conclusion", return_value=mock_run_results
        ):
            df, metrics = _get_single_run_results(run_info)

        # Verify results are sorted by datasource_item_id (0..9)
        scores = df["outputs.test_grader.score"].tolist()
        expected_scores = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        assert scores == expected_scores

    def test_configured_page_size_fetches_all_results_and_final_partial_page(self):
        mock_client = _mock_openai_client()
        run_info = OAIEvalRunCreationInfo(
            client=mock_client,
            eval_group_id="test-group",
            eval_run_id="test-run",
            grader_name_map={"grader-1": "friendly_grader"},
            expected_rows=160,
        )
        mock_run_results = Mock()
        mock_run_results.status = "completed"
        mock_run_results.per_testing_criteria_results = [Mock(testing_criteria="grader-1", passed=120, failed=40)]
        output_items = [
            MockOutputItem(
                id=f"item-{position}",
                datasource_item_id=position,
                results=[{"name": "grader-1", "passed": position < 120, "score": position}],
            )
            for position in range(160)
        ]

        def list_output_items(**kwargs):
            after = kwargs.get("after")
            start = int(after.removeprefix("item-")) + 1 if after else 0
            end = min(start + kwargs["limit"], len(output_items))
            return MockOutputItemsList(data=output_items[start:end], has_more=end < len(output_items))

        mock_client.evals.runs.output_items.list.side_effect = list_output_items

        with patch(
            "azure.ai.evaluation._evaluate._evaluate_aoai._wait_for_run_conclusion",
            return_value=mock_run_results,
        ):
            df, metrics = _get_single_run_results(run_info, aoai_output_items_page_size=3)

        assert mock_client.evals.runs.output_items.list.call_count == 54
        assert len(df) == 160
        assert df["outputs.friendly_grader.score"].tolist() == list(range(160))
        assert metrics == {"friendly_grader.pass_rate": 0.75}
        calls = mock_client.evals.runs.output_items.list.call_args_list
        assert "after" not in calls[0].kwargs
        assert calls[1].kwargs["after"] == "item-2"
        assert calls[-1].kwargs["after"] == "item-158"
        assert all(call_.kwargs["limit"] == 3 for call_ in calls)

    @pytest.mark.parametrize(
        "initial_page_size, expected_attempt_sizes",
        [
            (100, [100, 50, 25]),
            (50, [50, 25, 13]),
        ],
    )
    @patch("azure.ai.evaluation._evaluate._evaluate_aoai.sleep")
    def test_timeout_retries_reduce_page_size(self, mock_sleep, initial_page_size, expected_attempt_sizes):
        mock_client = _mock_openai_client()
        request = httpx.Request("GET", "https://example.test/output_items")
        mock_client.evals.runs.output_items.list.side_effect = [
            APITimeoutError(request=request),
            APITimeoutError(request=request),
            MockOutputItemsList(data=[]),
        ]

        _, final_page_size = _list_output_items_page(mock_client, {"after": "cursor-1"}, initial_page_size)

        assert final_page_size == expected_attempt_sizes[-1]
        assert [
            call_.kwargs["limit"] for call_ in mock_client.evals.runs.output_items.list.call_args_list
        ] == expected_attempt_sizes
        assert all(
            call_.kwargs["after"] == "cursor-1" for call_ in mock_client.evals.runs.output_items.list.call_args_list
        )
        assert [call_.args[0] for call_ in mock_client._calculate_retry_timeout.call_args_list] == [2, 1]
        assert mock_sleep.call_count == 2

    @patch("azure.ai.evaluation._evaluate._evaluate_aoai.sleep")
    def test_minimum_page_size_retries_no_more_than_three_attempts(self, mock_sleep):
        mock_client = _mock_openai_client()
        request = httpx.Request("GET", "https://example.test/output_items")
        mock_client.evals.runs.output_items.list.side_effect = APITimeoutError(request=request)

        with pytest.raises(APITimeoutError):
            _list_output_items_page(mock_client, {"after": "cursor-1"}, 1)

        assert [call_.kwargs["limit"] for call_ in mock_client.evals.runs.output_items.list.call_args_list] == [1, 1, 1]
        assert mock_sleep.call_count == 2

    @pytest.mark.parametrize("status_code", [408, 504])
    @patch("azure.ai.evaluation._evaluate._evaluate_aoai.sleep")
    def test_http_timeout_status_reduces_page_size(self, mock_sleep, status_code):
        mock_client = _mock_openai_client()
        mock_client._should_retry.return_value = True
        mock_client.evals.runs.output_items.list.side_effect = [
            _api_status_error(status_code),
            MockOutputItemsList(data=[]),
        ]

        _, final_page_size = _list_output_items_page(mock_client, {"after": "cursor-1"}, 25)

        assert final_page_size == 13
        assert [call_.kwargs["limit"] for call_ in mock_client.evals.runs.output_items.list.call_args_list] == [25, 13]
        mock_sleep.assert_called_once()

    @patch("azure.ai.evaluation._evaluate._evaluate_aoai.sleep")
    def test_reduced_page_size_carries_forward_and_collects_all_results_once(self, mock_sleep):
        mock_client = _mock_openai_client()
        run_info = OAIEvalRunCreationInfo(
            client=mock_client,
            eval_group_id="test-group",
            eval_run_id="test-run",
            grader_name_map={"grader-1": "test_grader"},
            expected_rows=160,
        )
        mock_run_results = Mock()
        mock_run_results.status = "completed"
        mock_run_results.per_testing_criteria_results = [Mock(testing_criteria="grader-1", passed=160, failed=0)]
        output_items = [
            MockOutputItem(
                id=f"item-{position}",
                datasource_item_id=position,
                results=[{"name": "grader-1", "passed": True, "score": position}],
            )
            for position in range(160)
        ]
        request = httpx.Request("GET", "https://example.test/output_items")
        call_count = 0

        def list_output_items(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise APITimeoutError(request=request)
            if call_count == 3:
                raise _api_status_error(504)

            after = kwargs.get("after")
            start = int(after.removeprefix("item-")) + 1 if after else 0
            end = min(start + kwargs["limit"], len(output_items))
            return MockOutputItemsList(data=output_items[start:end], has_more=end < len(output_items))

        mock_client._should_retry.return_value = True
        mock_client.evals.runs.output_items.list.side_effect = list_output_items

        with patch(
            "azure.ai.evaluation._evaluate._evaluate_aoai._wait_for_run_conclusion",
            return_value=mock_run_results,
        ):
            df, metrics = _get_single_run_results(run_info, aoai_output_items_page_size=100)

        calls = mock_client.evals.runs.output_items.list.call_args_list
        assert [call_.kwargs["limit"] for call_ in calls] == [100, 50, 50, 25, 25, 25, 25, 25]
        assert "after" not in calls[0].kwargs
        assert "after" not in calls[1].kwargs
        assert calls[2].kwargs["after"] == "item-49"
        assert calls[3].kwargs["after"] == "item-49"
        assert calls[4].kwargs["after"] == "item-74"
        assert len(df) == 160
        assert df["outputs.test_grader.score"].tolist() == list(range(160))
        assert metrics == {"test_grader.pass_rate": 1.0}
        assert mock_sleep.call_count == 2

    @patch("azure.ai.evaluation._evaluate._evaluate_aoai.sleep")
    def test_later_page_retry_exhaustion_propagates_without_partial_result(self, mock_sleep):
        mock_client = _mock_openai_client()
        run_info = OAIEvalRunCreationInfo(
            client=mock_client,
            eval_group_id="test-group",
            eval_run_id="test-run",
            grader_name_map={"grader-1": "test_grader"},
            expected_rows=100,
        )
        mock_run_results = Mock()
        mock_run_results.status = "completed"
        mock_run_results.per_testing_criteria_results = [Mock(testing_criteria="grader-1", passed=100, failed=0)]
        first_page = MockOutputItemsList(
            data=[
                MockOutputItem(
                    id=f"item-{i}",
                    datasource_item_id=i,
                    results=[{"name": "grader-1", "passed": True, "score": i}],
                )
                for i in range(50)
            ],
            has_more=True,
        )
        request = httpx.Request("GET", "https://example.test/output_items")
        final_error = APITimeoutError(request=request)
        mock_client.evals.runs.output_items.list.side_effect = [
            first_page,
            APITimeoutError(request=request),
            APITimeoutError(request=request),
            final_error,
        ]

        with patch(
            "azure.ai.evaluation._evaluate._evaluate_aoai._wait_for_run_conclusion",
            return_value=mock_run_results,
        ):
            with pytest.raises(APITimeoutError) as exc_info:
                _get_single_run_results(run_info, aoai_output_items_page_size=50)

        assert exc_info.value is final_error
        calls = mock_client.evals.runs.output_items.list.call_args_list
        assert [call_.kwargs["limit"] for call_ in calls] == [50, 50, 25, 13]
        assert all(call_.kwargs.get("after") == "item-49" for call_ in calls[1:])
        assert mock_sleep.call_count == 2

    @patch("azure.ai.evaluation._evaluate._evaluate_aoai.sleep")
    def test_other_retryable_status_preserves_page_size_and_backoff_headers(self, mock_sleep):
        mock_client = _mock_openai_client()
        run_info = OAIEvalRunCreationInfo(
            client=mock_client,
            eval_group_id="test-group",
            eval_run_id="test-run",
            grader_name_map={"grader-1": "test_grader"},
            expected_rows=1,
        )
        mock_run_results = Mock()
        mock_run_results.status = "completed"
        mock_run_results.per_testing_criteria_results = [Mock(testing_criteria="grader-1", passed=1, failed=0)]
        retryable_error = _api_status_error(503, headers={"Retry-After": "4", "x-should-retry": "true"})
        mock_client._should_retry.return_value = True
        mock_client._calculate_retry_timeout.return_value = 4.0
        mock_client.evals.runs.output_items.list.side_effect = [
            retryable_error,
            MockOutputItemsList(
                data=[
                    MockOutputItem(
                        id="item-0",
                        datasource_item_id=0,
                        results=[{"name": "grader-1", "passed": True, "score": 1}],
                    )
                ]
            ),
        ]

        with patch(
            "azure.ai.evaluation._evaluate._evaluate_aoai._wait_for_run_conclusion",
            return_value=mock_run_results,
        ):
            df, _ = _get_single_run_results(run_info, aoai_output_items_page_size=50)

        assert len(df) == 1
        assert [call_.kwargs["limit"] for call_ in mock_client.evals.runs.output_items.list.call_args_list] == [50, 50]
        mock_client._should_retry.assert_called_once_with(retryable_error.response)
        assert mock_client._calculate_retry_timeout.call_args.args[2] == retryable_error.response.headers
        mock_sleep.assert_called_once_with(4.0)

    @patch("azure.ai.evaluation._evaluate._evaluate_aoai.sleep")
    def test_non_retryable_status_propagates_immediately(self, mock_sleep):
        mock_client = _mock_openai_client()
        non_retryable_error = _api_status_error(503, headers={"x-should-retry": "false"})
        mock_client._should_retry.return_value = False
        mock_client.evals.runs.output_items.list.side_effect = non_retryable_error

        with pytest.raises(APIStatusError) as exc_info:
            _list_output_items_page(mock_client, {"after": "cursor-1"}, 50)

        assert exc_info.value is non_retryable_error
        mock_client.evals.runs.output_items.list.assert_called_once_with(after="cursor-1", limit=50)
        mock_client._calculate_retry_timeout.assert_not_called()
        mock_sleep.assert_not_called()

    def test_output_items_fetch_disables_client_retries_without_mutating_shared_client(self):
        shared_client = Mock()
        output_items_client = Mock()
        shared_client.with_options.return_value = output_items_client
        run_info = OAIEvalRunCreationInfo(
            client=shared_client,
            eval_group_id="test-group",
            eval_run_id="test-run",
            grader_name_map={"grader-1": "test_grader"},
            expected_rows=1,
        )
        mock_run_results = Mock()
        mock_run_results.status = "completed"
        mock_run_results.per_testing_criteria_results = [Mock(testing_criteria="grader-1", passed=1, failed=0)]
        output_items_client.evals.runs.output_items.list.return_value = MockOutputItemsList(
            data=[
                MockOutputItem(
                    id="item-0",
                    datasource_item_id=0,
                    results=[{"name": "grader-1", "passed": True, "score": 1}],
                )
            ]
        )

        with patch(
            "azure.ai.evaluation._evaluate._evaluate_aoai._wait_for_run_conclusion",
            return_value=mock_run_results,
        ) as mock_wait:
            _get_single_run_results(run_info)

        mock_wait.assert_called_once_with(shared_client, "test-group", "test-run")
        shared_client.with_options.assert_called_once_with(max_retries=0)
        shared_client.evals.runs.output_items.list.assert_not_called()
        output_items_client.evals.runs.output_items.list.assert_called_once()
        shared_client.close.assert_not_called()
        output_items_client.close.assert_not_called()
