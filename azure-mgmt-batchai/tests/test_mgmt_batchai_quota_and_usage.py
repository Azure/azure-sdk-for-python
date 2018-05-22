# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.mgmt.batchai import BatchAIManagementClient
from devtools_testutils import AzureMgmtTestCase

from helpers import create_batchai_client, LOCATION


class JobTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(JobTestCase, self).setUp()
        self.client = create_batchai_client(self)  # type: BatchAIManagementClient

    def test_quota_and_usage(self):
        usages = list(self.client.usage.list(LOCATION))
        self.assertGreater(len(usages), 0)
        for u in usages:
            self.assertIsNotNone(u.name)
            self.assertIsNotNone(u.unit)
