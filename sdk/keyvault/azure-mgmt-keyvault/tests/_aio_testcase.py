import asyncio
from unittest.mock import Mock

from azure.core.credentials import AccessToken
from azure_devtools.scenario_tests.patches import mock_in_unit_test
from devtools_testutils import AzureMgmtTestCase


def skip_sleep(unit_test):
    async def immediate_return(_):
        return

    return mock_in_unit_test(unit_test, "asyncio.sleep", immediate_return)


class AzureMgmtAsyncTestCase(AzureMgmtTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.replay_patches.append(skip_sleep)

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
            credential = Mock(get_token=asyncio.coroutine(lambda _: AccessToken("fake-token", 0)))
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
