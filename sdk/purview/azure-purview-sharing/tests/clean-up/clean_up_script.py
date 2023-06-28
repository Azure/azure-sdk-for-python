# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import json
from uuid import uuid4

# from devtools_testutils import recorded_by_proxy
from testcase import TestPurviewSharing, PurviewSharingPowerShellPreparer
from azure.core.exceptions import HttpResponseError
from azure.purview.sharing.operations._operations import (
    build_sent_shares_create_or_replace_request,
    build_sent_shares_delete_request,
)

class CleanUpScripts(TestPurviewSharing):
    # @recorded_by_proxy
    @PurviewSharingPowerShellPreparer()
    def clean_up_all_sent_shares(self, purviewsharing_endpoint):
        """
        This script is meant to clean up all sent shares created by the tests
        """
        client = self.create_client(endpoint=purviewsharing_endpoint)
        # sent_share_id = "d857d382-b535-4b6e-bb5a-db59c42ed333" # uuid4()
        # sent_share = self.prepare_sent_share()

        # request = build_sent_shares_create_or_replace_request(
        #     sent_share_id,
        #     content_type="application/json",
        #     content=json.dumps(sent_share))
        
        # response = client.send_request(request)

        # assert response is not None
        # assert response.status_code == 201, "Invalid Status Code " + str(response.status_code)

        ### Get list of all sent shares
        #### go through list and delete by id??

        delete_request = build_sent_shares_delete_request(sent_share_id=sent_share_id)
        delete_response = client.send_request(delete_request)

        assert delete_response is not None
        assert delete_response.status_code == 202, "Invalid Status Code " + str(response.status_code)

        try:
            delete_response.raise_for_status()
        except HttpResponseError as e:
            print("Exception " + str(e))
            print("Response " + delete_response.text())