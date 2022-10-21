# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
import platform
import functools
from testcase import TextAnalyticsTest, TextAnalyticsPreparer
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
            categories=["Health", "Politics", "Music", "Sports"]
        )
