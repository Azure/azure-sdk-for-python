# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List, Any
from unittest.mock import Mock, MagicMock, patch

import httpx
import pandas as pd
import pytest
from openai import APIStatusError, APITimeoutError, OpenAI

from azure.ai.evaluation._evaluate._evaluate_aoai import (
    _get_single_run_results,
    OAIEvalRunCreationInfo,
    _wait_for_run_conclusion,
)
from azure.ai.evaluation._exceptions import EvaluationException


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


class TestAOAIPagination:
    """Test pagination functionality in AOAI evaluation results"""

    def test_single_page_results(self):
        """Test handling of single page results (no pagination needed)"""
        # Mock client and run info
        mock_client = Mock()
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
        mock_client = Mock()
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
        mock_run_results.per_testing_criteria_results = [Mock(testing_criteria="grader-1", passed=200, failed=50)]

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
        assert df["outputs.test_grader.sample"].tolist() == [f"Sample {i}" for i in range(250)]
        assert df["outputs.test_grader.score"].tolist() == [0.9] * 100 + [0.85] * 100 + [0.3] * 50
        assert metrics == {"test_grader.pass_rate": 0.8}
        assert mock_client.evals.runs.output_items.list.call_count == 3
        mock_client.with_options.assert_not_called()

        # Verify pagination parameters
        calls = mock_client.evals.runs.output_items.list.call_args_list
        assert calls[0][1]["eval_id"] == "test-group"
        assert calls[0][1]["run_id"] == "test-run"
        assert all(call.kwargs["limit"] == 100 for call in calls)
        assert "after" not in calls[0][1]

        assert calls[1][1]["after"] == "item-99"  # Last item ID from page 1
        assert calls[2][1]["after"] == "item-199"  # Last item ID from page 2

    @pytest.mark.parametrize("failure", ["timeout", 408, 504])
    def test_later_page_failure_uses_client_retries_without_reducing_page_size(self, failure):
        requests = []

        def handle_request(request):
            requests.append(request)
            if len(requests) == 1:
                return httpx.Response(
                    200,
                    json={
                        "object": "list",
                        "data": [
                            {
                                "id": "item-0",
                                "datasource_item_id": 0,
                                "results": [{"name": "grader-1", "passed": True, "score": 1.0}],
                            }
                        ],
                        "has_more": True,
                    },
                )
            if failure == "timeout":
                raise httpx.ReadTimeout("output-items timeout", request=request)
            return httpx.Response(failure, json={"error": {"message": "output-items timeout"}})

        with OpenAI(
            api_key="test-key",
            base_url="https://example.test/v1",
            max_retries=1,
            http_client=httpx.Client(transport=httpx.MockTransport(handle_request)),
        ) as client:
            run_info = OAIEvalRunCreationInfo(
                client=client,
                eval_group_id="test-group",
                eval_run_id="test-run",
                grader_name_map={"grader-1": "test_grader"},
                expected_rows=2,
            )
            completed_run = Mock(
                status="completed",
                per_testing_criteria_results=[Mock(testing_criteria="grader-1", passed=2, failed=0)],
            )
            with patch(
                "azure.ai.evaluation._evaluate._evaluate_aoai._wait_for_run_conclusion",
                return_value=completed_run,
            ), patch("openai._base_client.time.sleep"), pytest.raises(
                APITimeoutError if failure == "timeout" else APIStatusError
            ):
                _get_single_run_results(run_info)
            assert client.max_retries == 1

        assert len(requests) == 3
        assert all(request.url.params["limit"] == "100" for request in requests)
        assert "after" not in requests[0].url.params
        assert all(request.url.params["after"] == "item-0" for request in requests[1:])

    def test_empty_page_handling(self):
        """Test handling of empty pages in pagination"""
        mock_client = Mock()
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
        mock_client = Mock()
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
