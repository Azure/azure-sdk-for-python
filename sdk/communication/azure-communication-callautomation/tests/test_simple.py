# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from devtools_testutils import AzureMgmtTestCase
from azure.communication.callautomation import CallAutomationClient

class TemplateTest(AzureMgmtTestCase):
    def setUp(self):
        super(TemplateTest, self).setUp()

    def test_case_default(self):
        self.assertEqual(CallAutomationClient.todo_main(), True)
