# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import pytest
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.maps.geolocation import MapsGeolocationClient
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from geolocation_preparer import MapsGeolocationPreparer


class TestMapsGeolocationClient(AzureRecordedTestCase):
    def setup_method(self, method):
        self.client = MapsGeolocationClient(
            credential=AzureKeyCredential(os.environ.get("AZURE_SUBSCRIPTION_KEY", "AzureMapsSubscriptionKey"))
        )
        assert self.client is not None

    @MapsGeolocationPreparer()
    @recorded_by_proxy
    def test_get_country_code(self):
        result = self.client.get_country_code(ip_address="2001:4898:80e8:b::189")
        assert result is not None
        assert result.iso_code == "US"

    @MapsGeolocationPreparer()
    @recorded_by_proxy
    def test_wrong_country_code(self):
        with pytest.raises(HttpResponseError):
            self.client.get_country_code(ip_address="123451123123")
