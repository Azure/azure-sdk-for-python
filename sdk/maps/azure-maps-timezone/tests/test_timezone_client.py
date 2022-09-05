# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from azure.maps.timezone import MapsTimezoneClient
from timezone_preparer import TimezonePreparer

class TestTimezoneClient(AzureRecordedTestCase):
    def setUp(self):
        super(TimezoneClientTest, self).setUp()
        self.client = self.create_basic_client(MapsTimezoneClient)

    @TimezonePreparer()
    @recorded_by_proxy
    def test_get_timezone_by_id(self, **kwargs):
        timezone = self.client.get_timezone_by_id()
        self.assertEqual(template_main(), True)
