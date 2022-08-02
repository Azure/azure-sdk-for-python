import os
import sys
import pytest

from devtools_testutils import AzureTestCase
from azure_devtools.scenario_tests import RecordingProcessor
from azure.core.credentials import AzureKeyCredential
from azure.maps.geolocation import MapsGeolocationClient


# cSpell:disable
class HeaderReplacer(RecordingProcessor):
    def __init__(self):
        self.headers = []

    def register_header(self, header_name, new_val):
        self.headers.append((header_name, new_val))

    def process_request(self, request):
        for header_name, new_val in self.headers:
            for key in request.headers.keys():
                if key.lower() == header_name.lower():
                    request.headers[key] = new_val
                    break
        return request


# cSpell:disable
class AzureMapsGeolocationClientE2ETest(AzureTestCase):
    def __init__(self, *args, **kwargs):
        super(AzureMapsGeolocationClientE2ETest, self).__init__(*args, **kwargs)
        header_replacer = HeaderReplacer()
        header_replacer.register_header("subscription-key", "<RealSubscriptionKey>")
        header_replacer.register_header("x-ms-client-id", "<RealClientId>")
        self.recording_processors.append(header_replacer)

    def setUp(self):
        super(AzureMapsGeolocationClientE2ETest, self).setUp()
        self.client = MapsGeolocationClient(
            client_id=self.get_settings_value('CLIENT_ID'),
            credential=AzureKeyCredential(self.get_settings_value('SUBSCRIPTION_KEY')),
        )
        assert self.client is not None

    @pytest.mark.live_test_only
    def test_get_geolocation(self):
        result = self.client.get_geolocation(ip_address="2001:4898:80e8:b::189")
        assert len(result.results) > 0


if __name__ == "__main__" :
    testArgs = [ "-v" , "-s" ] if len(sys.argv) == 1 else sys.argv[1:]

    pytest.main(args=testArgs)

    print("main() Leave")
