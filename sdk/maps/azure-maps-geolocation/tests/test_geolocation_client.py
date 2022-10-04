# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
from azure.core.credentials import AccessToken, AzureKeyCredential
from azure.maps.geolocation import GeolocationClient
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from geolocation_preparer import MapsGeolocationPreparer

class TestGeolocationClient(AzureRecordedTestCase):
    def setup_method(self, method):
        self.client = GeolocationClient(
            credential=AzureKeyCredential(os.environ.get('AZURE_SUBSCRIPTION_KEY', "AzureMapsSubscriptionKey"))
        )
        assert self.client is not None

    @MapsGeolocationPreparer()
    @recorded_by_proxy
    def test_get_geolocation(self):
        result = self.client.get_geolocation(ip_address="2001:4898:80e8:b::189")
        assert result is not None
        assert result.iso_code == 'US'