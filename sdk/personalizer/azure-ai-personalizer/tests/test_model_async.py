import pytest
from devtools_testutils import AzureTestCase
import personalizer_helpers
import personalizer_helpers_async


class TestModelAsync(AzureTestCase):

    @personalizer_helpers.PersonalizerPreparer()
    @pytest.mark.asyncio
    @pytest.mark.skip('Get model is returning bad request')
    async def test_model_import_export(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_single_slot')
        client = personalizer_helpers_async.create_async_personalizer_client(personalizer_endpoint, personalizer_api_key)
        unsigned_model_bytes = await client.model.get(signed=False)
        signed_model_bytes = await client.model.get(signed=True)
        await client.model.import_method(signed_model_bytes)
        new_unsigned_model_bytes = await client.model.get(signed=False)
        assert [b async for b in unsigned_model_bytes] == [b async for b in new_unsigned_model_bytes]
        
