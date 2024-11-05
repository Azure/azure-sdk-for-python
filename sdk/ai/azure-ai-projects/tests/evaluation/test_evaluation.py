# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy
from azure.ai.projects.models import Evaluation, Dataset, EvaluatorConfiguration, ConnectionTy


class TestEvaluation(RecordedTestCase):
    @recorded_by_proxy
    def test_evaluation_create(self, project_client):
