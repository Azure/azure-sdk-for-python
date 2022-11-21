# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import platform
import functools
from testcase import TextAnalyticsTest, TextAnalyticsPreparer, is_public_cloud
from testcase import TextAnalyticsClientPreparer as _TextAnalyticsClientPreparer
from devtools_testutils import recorded_by_proxy
from azure.ai.textanalytics import (
    DynamicClassificationResult,
    TextAnalyticsClient,
    ClassificationType,
)

# pre-apply the client_cls positional argument so it needn't be explicitly passed below
TextAnalyticsClientPreparer = functools.partial(_TextAnalyticsClientPreparer, TextAnalyticsClient)


class TestDynamicClassification(TextAnalyticsTest):

    @pytest.mark.skipif(not is_public_cloud(), reason='Usgov and China Cloud are not supported')
    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_dynamic_classification(self, client):
        documents = [
            "The WHO is issuing a warning about Monkey Pox.",
            "Mo Salah plays in Liverpool FC in England.",
        ]
        result = client.dynamic_classification(
            documents,
            categories=["Health", "Politics", "Music", "Sports"],
            show_stats=True
        )
        for res in result:
            assert res.id
            assert res.statistics
            for classification in res.classifications:
                assert classification.category
                assert classification.confidence_score is not None

    @pytest.mark.skipif(not is_public_cloud(), reason='Usgov and China Cloud are not supported')
    @TextAnalyticsPreparer()
    @TextAnalyticsClientPreparer()
    @recorded_by_proxy
    def test_dynamic_classification_single(self, client):
        documents = [
            "The WHO is issuing a warning about Monkey Pox.",
            "Mo Salah plays in Liverpool FC in England.",
        ]
        result = client.dynamic_classification(
            documents,
            categories=["Health", "Politics", "Music", "Sports"],
            classification_type="single"
        )
        for res in result:
            assert res.id
            assert len(res.classifications) == 1
            assert res.classifications[0].category
            assert res.classifications[0].confidence_score is not None
