# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
import personalizer_helpers


class TestLogProperties(AzureRecordedTestCase):

    @personalizer_helpers.PersonalizerPreparer()
    @recorded_by_proxy
    def test_delete_log(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_multi_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_multi_slot')
        client = personalizer_helpers.create_personalizer_admin_client(personalizer_endpoint, personalizer_api_key)
        client.delete_logs()
        log_properties = client.get_log_properties()
        date_range = log_properties.get("dateRange")
        if date_range is not None:
            assert "from" in date_range
            assert date_range["from"] is None
            assert "to" in date_range
            assert date_range["to"] is None
