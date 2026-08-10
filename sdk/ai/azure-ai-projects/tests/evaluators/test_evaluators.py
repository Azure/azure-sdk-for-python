# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for sync evaluator generation pollers."""

from unittest.mock import MagicMock

from azure.ai.projects.models import EvaluatorGenerationLROPoller
from azure.ai.projects.operations._patch_evaluators import BetaEvaluatorsOperations


def test_begin_create_generation_job_exposes_job_id():
    """The sync create operation exposes its job ID without SDK polling."""
    operation = BetaEvaluatorsOperations.__new__(BetaEvaluatorsOperations)
    operation._client = MagicMock()  # pylint: disable=protected-access
    operation._config = MagicMock(polling_interval=0)  # pylint: disable=protected-access
    operation._serialize = MagicMock()  # pylint: disable=protected-access
    operation._serialize.url.return_value = "https://example.test"  # pylint: disable=protected-access
    operation._deserialize = MagicMock()  # pylint: disable=protected-access

    initial_response = MagicMock()
    initial_response.http_response.json.return_value = {"id": "evaluator-job-sync"}
    operation._create_generation_job_initial = MagicMock(  # pylint: disable=protected-access
        return_value=initial_response
    )

    poller = operation.begin_create_generation_job(job={}, polling=False)

    assert isinstance(poller, EvaluatorGenerationLROPoller)
    assert poller.details["job_id"] == "evaluator-job-sync"