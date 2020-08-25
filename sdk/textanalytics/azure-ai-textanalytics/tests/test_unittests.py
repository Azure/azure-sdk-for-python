# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.ai.textanalytics._models import _get_indices
from testcase import TextAnalyticsTest


class TestUnittests(TextAnalyticsTest):

    def test_json_pointer_parsing(self):
        assert [1, 0, 15] == _get_indices("#/documents/1/sentences/0/opinions/15")
