import azure.mgmt.datalake.analytics.account

import unittest

from devtools_testutils import (
    AzureMgmtRecordedTestCase, ResourceGroupPreparer, recorded_by_proxy
)


class TestMgmtDatalake(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(
            azure.mgmt.datalake.analytics.account.DataLakeAnalyticsAccountManagementClient
        )

    @recorded_by_proxy
    def test_generate_recommendations(self):

        response = self.client.operations.list()

        assert response


if __name__ == '__main__':
    unittest.main()
