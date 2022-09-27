import pytest
from devtools_testutils import AzureRecordedTestCase
import helpers


class TestEventAsync(AzureRecordedTestCase):

    @helpers.PersonalizerPreparer()
    @pytest.mark.asyncio
    async def test_reward(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_single_slot')
        client = helpers.create_async_personalizer_client(personalizer_endpoint, personalizer_api_key)
        await client.events.reward("myeventid", {"value": 1.0})

    @helpers.PersonalizerPreparer()
    @pytest.mark.asyncio
    async def test_activate(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_single_slot')
        client = helpers.create_async_personalizer_client(personalizer_endpoint, personalizer_api_key)
        await client.events.activate("myeventid")
