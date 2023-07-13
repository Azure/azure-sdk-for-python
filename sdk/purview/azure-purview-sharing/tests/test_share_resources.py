# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import json

from testcase import TestPurviewSharing, PurviewSharingPowerShellPreparer
from devtools_testutils import recorded_by_proxy
from azure.purview.sharing.operations._operations import (
    build_share_resources_list_request,
)

class TestShareResources(TestPurviewSharing):
    @PurviewSharingPowerShellPreparer()
    @recorded_by_proxy
    def test_list_share_resources(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)

        list_request = build_share_resources_list_request(
            filter="properties/storeKind eq 'AdlsGen2Account'",
            order_by="properties/createdAt desc")
        
        list_response = client.send_request(list_request)

        assert list_response is not None
        assert list_response.content is not None
         
        list = json.loads(list_response.content)['value']

        assert len(list) > 0, "Invalid number of share resources " + str(len(list))
        assert all(x["storeKind"] == "AdlsGen2Account" for x in list)

