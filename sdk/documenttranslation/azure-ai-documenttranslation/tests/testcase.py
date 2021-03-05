# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from devtools_testutils import (
    AzureTestCase,
)

from azure_devtools.scenario_tests import (
    ReplayableTest
)


class DocumentTranslationTest(AzureTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + ['Ocp-Apim-Subscription-Key']

    def __init__(self, method_name):
        super(DocumentTranslationTest, self).__init__(method_name)
        self.vcr.match_on = ["path", "method", "query"]

