import asyncio
from unittest.mock import Mock

from azure.core.credentials import AccessToken
from devtools_testutils import AzureMgmtTestCase

class AzureMgmtAsyncTestCase(AzureMgmtTestCase):

    def setUp(self):
        super(AzureMgmtAsyncTestCase, self).setUp()

    @property
    def event_loop(self):
        return asyncio.get_event_loop()

    def mock_completed_future(self, result=None):
        future = asyncio.Future()
        future.set_result = result
        return future

    def create_mgmt_aio_client(self, client, **kwargs):
        if self.is_live:
            from azure.identity.aio import DefaultAzureCredential
            credential = DefaultAzureCredential()
        else:
            credential = Mock(get_token=lambda _: self.mock_completed_future(AccessToken("fake-token", 0)))
        return client(
            credential=credential,
            subscription_id=self.settings.SUBSCRIPTION_ID
        )
    
    def mock_completed_future(self, result=None):
        future = asyncio.Future()
        future.set_result = result
        return future

    def to_list(self, ait):
        async def lst():
            result = []
            async for item in ait:
                result.append(item)
            return result
        return self.event_loop.run_until_complete(lst())
