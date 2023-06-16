# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import json
from uuid import uuid4

from testcase import TestPurviewSharing, PurviewSharingPowerShellPreparer
from devtools_testutils import recorded_by_proxy
from azure.purview.sharing.operations._operations import (
    build_share_resources_list_request,
    build_sent_shares_create_or_replace_request
)

class TestShareResources(TestPurviewSharing):
    @PurviewSharingPowerShellPreparer()
    @recorded_by_proxy
    def test_list_share_resources(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)
        sent_share_id = uuid4()
        sent_share = self.prepare_sent_share()

        request = build_sent_shares_create_or_replace_request(
            sent_share_id,
            content_type="application/json",
            content=json.dumps(sent_share))
        
        response = client.send_request(request)
        
        assert response is not None
        assert response.status_code == 201, "Invalid Status Code " + str(response.status_code)
        assert response.content is not None

        created_sent_share = json.loads(response.content)

        assert created_sent_share is not None
        assert created_sent_share['id'] == str(sent_share_id)

        list_request = build_share_resources_list_request(
            filter="properties/storeKind eq 'AdlsGen2Account'",
            orderby="properties/createdAt desc")
        
        list_response = client.send_request(list_request)

        assert list_response is not None
        assert list_response.content is not None
         
        list = json.loads(list_response.content)['value']

        assert len(list) > 0, "Invalid number of share resources " + str(len(list))
        assert all(x["storeKind"] == "AdlsGen2Account" for x in list)

