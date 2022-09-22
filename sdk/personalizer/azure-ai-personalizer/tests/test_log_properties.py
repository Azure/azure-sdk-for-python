from devtools_testutils import AzureRecordedTestCase
import helpers

class TestLogProperties(AzureRecordedTestCase):

    @helpers.PersonalizerPreparer()
    def test_delete_log(self, **kwargs):
        personalizer_endpoint = kwargs.pop('personalizer_endpoint_multi_slot')
        personalizer_api_key = kwargs.pop('personalizer_api_key_multi_slot')
        client = helpers.create_personalizer_client(personalizer_endpoint, personalizer_api_key)
        client.log.delete()
        log_properties = client.log.get_properties()
        dateRange = log_properties.get("dateRange")
        if dateRange is not None:
            assert "from" in dateRange
            assert dateRange["from"] is None
            assert "to" in dateRange
            assert dateRange["to"] is None