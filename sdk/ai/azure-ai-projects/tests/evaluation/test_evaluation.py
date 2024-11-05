# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils import recorded_by_proxy


class TestEvaluation(RecordedTestCase):
    @recorded_by_proxy
    def test_evaluation_get(self, **kwargs):
        with self.get_sync_client(**kwargs) as project_client: