import asyncio
from unittest.mock import Mock

from azure.core.credentials import AccessToken
from devtools_testutils import AzureMgmtTestCase
from devtools_testutils.fake_credentials_async import AsyncFakeCredential

class AzureMgmtAsyncTestCase(AzureMgmtTestCase):

    def setUp(self):
        super(AzureMgmtAsyncTestCase, self).setUp()

    @property
    def event_loop(self):
        return asyncio.get_event_loop()

    def create_mgmt_aio_client(self, client, **kwargs):
        if self.is_live:
            from azure.identity.aio import DefaultAzureCredential
            credential = DefaultAzureCredential()
        else:
            credential = AsyncFakeCredential()
        return client(
            credential=credential,
            subscription_id=self.settings.SUBSCRIPTION_ID
        )

    def to_list(self, ait):
        async def lst():
            result = []
            async for item in ait:
                result.append(item)
            return result
        return self.event_loop.run_until_complete(lst())
