#--------------------------------------------------------------------------
import unittest

import azure.mgmt.redis
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy

AZURE_LOCATION ='eastus'

class TestMgmtSubscription(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.redis.RedisManagementClient
        )

    @recorded_by_proxy
    def test_redis_list(self):
        result = self.mgmt_client.redis.list_by_subscription()
        assert list(result) is not None


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()