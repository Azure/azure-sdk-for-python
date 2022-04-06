# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import azure.mgmt.relay
from devtools_testutils import AzureMgmtRecordedTestCase, ResourceGroupPreparer, recorded_by_proxy


class TestMgmtRelay(AzureMgmtRecordedTestCase):

    def setup_method(self, method):

        self.relay_client = self.create_mgmt_client(
            azure.mgmt.relay.RelayAPI
        )

    @recorded_by_proxy
    def test_operations_list(self):
        # Check the namespace availability
        result = self.relay_client.operations.list()


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()