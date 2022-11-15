# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
import personalizer_helpers

class TestModel(AzureRecordedTestCase):

    @personalizer_helpers.PersonalizerPreparer()
    @recorded_by_proxy
    def test_model_import_export(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_single_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_single_slot')
        client = personalizer_helpers.create_personalizer_admin_client(personalizer_endpoint, personalizer_api_key)
        unsigned_model_bytes = client.export_model(signed=False)
        signed_model_bytes = client.export_model(signed=True)
        client.import_model(signed_model_bytes)
        new_unsigned_model_bytes = client.export_model(signed=False)
        assert [b for b in unsigned_model_bytes] == [b for b in new_unsigned_model_bytes]
        
