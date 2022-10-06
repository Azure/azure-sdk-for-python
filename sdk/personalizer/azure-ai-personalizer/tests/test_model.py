from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
import personalizer_helpers

class TestModel(AzureRecordedTestCase):

    @personalizer_helpers.PersonalizerPreparer()
    @recorded_by_proxy
    def test_model_import_export(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_single_slot')
        client =  personalizer_helpers.create_personalizer_client(personalizer_endpoint, personalizer_api_key)
        unsigned_model_bytes = client.model.get(signed=False)
        signed_model_bytes = client.model.get(signed=True)
        client.model.import_method(signed_model_bytes)
        new_unsigned_model_bytes = client.model.get(signed=False)
        assert [b for b in unsigned_model_bytes] == [b for b in new_unsigned_model_bytes]
        
