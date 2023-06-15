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
from azure.core.exceptions import HttpResponseError
from azure.purview.sharing.operations._operations import (
    build_sent_shares_create_or_replace_request,
    build_sent_shares_create_invitation_request,
    build_sent_shares_get_request,
    build_sent_shares_list_request,
    build_sent_shares_delete_request,
    build_sent_shares_list_invitations_request,
    build_sent_shares_get_invitation_request
)

class TestSentShares(TestPurviewSharing):
    
    @PurviewSharingPowerShellPreparer()
    @recorded_by_proxy
    def test_create_sent_share(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)
        sent_share_id = "85e57d9e-9f5c-4304-bfe5-973627039bf8"
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

    @PurviewSharingPowerShellPreparer()
    @recorded_by_proxy
    def test_create_sent_share_user_invitation(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)
        sent_share_id = "087fa116-287d-4dd3-894d-0b635aaff683"
        sent_share_invitation_id = "8cea274b-bd71-4c60-9865-08df5780aa11"
        sent_share = self.prepare_sent_share()

        request = build_sent_shares_create_or_replace_request(
            sent_share_id,
            content_type="application/json",
            content=json.dumps(sent_share))
        
        response = client.send_request(request)

        assert response is not None
        assert response.status_code == 201, "Invalid Status Code " + str(response.status_code)

        consumerEmail = "consumer@contoso.com"

        invitation = {
            "invitationKind": "User",
            "properties": {
                "targetEmail": consumerEmail,
                "notify": "true",
                "expirationDate": "2024-03-02 00:00:00"
            }
        }

        invitation_request = build_sent_shares_create_invitation_request(
            sent_share_id=sent_share_id,
            sent_share_invitation_id=sent_share_invitation_id,
            content_type="application/json",
            content=json.dumps(invitation))
        
        invitation_response = client.send_request(invitation_request)

        assert invitation_response is not None
        assert invitation_response.status_code == 201, "Invalid Status Code " + str(invitation_response.status_code)
        assert invitation_response.content is not None

        created_invitation = json.loads(invitation_response.content)

        assert created_invitation['id'] == str(sent_share_invitation_id)
        assert created_invitation['properties']['targetEmail'] == consumerEmail

    @PurviewSharingPowerShellPreparer()
    @recorded_by_proxy
    def test_get_sent_share(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)
        sent_share_id = "3f55ca37-78a5-4641-a6ab-14b4249ec5c5"
        sent_share = self.prepare_sent_share()

        request = build_sent_shares_create_or_replace_request(
            sent_share_id,
            content_type="application/json",
            content=json.dumps(sent_share))
        
        response = client.send_request(request)

        assert response is not None
        assert response.status_code == 201, "Invalid Status Code " + str(response.status_code)

        get_request = build_sent_shares_get_request(sent_share_id=sent_share_id)
        get_response = client.send_request(get_request)

        assert get_response is not None
        assert get_response.content is not None

        retrieved_sent_share = json.loads(get_response.content)

        assert retrieved_sent_share['id'] == str(sent_share_id)

    @PurviewSharingPowerShellPreparer()
    @recorded_by_proxy
    def test_get_all_sent_shares(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)
        sent_share_id = "08c1b2a2-880c-4db7-9afe-140683fd1aed"
        sent_share = self.prepare_sent_share()

        request = build_sent_shares_create_or_replace_request(
            sent_share_id,
            content_type="application/json",
            content=json.dumps(sent_share))
        
        response = client.send_request(request)

        assert response is not None
        assert response.status_code == 201, "Invalid Status Code " + str(response.status_code)

        list_request = build_sent_shares_list_request(
            reference_name=sent_share["properties"]["artifact"]["storeReference"]["referenceName"],
            orderby="properties/createdAt desc")
        
        list_response = client.send_request(list_request)

        assert list_response is not None
        assert list_response.content is not None
         
        list = json.loads(list_response.content)['value']

        assert len(list) > 0, "Invalid number of shares " + str(len(list))
        assert len([x for x in list if x["id"] == str(sent_share_id)]) == 1

    @PurviewSharingPowerShellPreparer()
    @recorded_by_proxy
    def test_delete_sent_share(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)
        sent_share_id = "9550f86d-dc04-4c85-9ff0-db8978cd728e"
        sent_share = self.prepare_sent_share()

        request = build_sent_shares_create_or_replace_request(
            sent_share_id,
            content_type="application/json",
            content=json.dumps(sent_share))
        
        response = client.send_request(request)

        assert response is not None
        assert response.status_code == 201, "Invalid Status Code " + str(response.status_code)

        delete_request = build_sent_shares_delete_request(sent_share_id=sent_share_id)
        delete_response = client.send_request(delete_request)

        assert delete_response is not None
        assert delete_response.status_code == 202, "Invalid Status Code " + str(response.status_code)

        try:
            delete_response.raise_for_status()
        except HttpResponseError as e:
            print("Exception " + str(e))
            print("Response " + delete_response.text())

    @PurviewSharingPowerShellPreparer()
    @recorded_by_proxy
    def test_create_sent_share_service_invitation(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)
        sent_share_id = "f638f1e7-f9e8-4a96-9c2b-cb07cd1caa11"
        sent_share_invitation_id = "bb85371e-7360-43ef-a0d1-65e4058253b7"
        sent_share = self.prepare_sent_share()
        
        request = build_sent_shares_create_or_replace_request(
            sent_share_id,
            content_type="application/json",
            content=json.dumps(sent_share))
        
        response = client.send_request(request)

        assert response is not None
        assert response.status_code == 201, "Invalid Status Code 1 " + str(response.status_code)

        targetActiveDirectoryId = "bc02d987-c010-4e4e-95d1-4bab99ed0ac2"
        targetObjectId = "28b46e20-9847-4d41-8bae-28e17a76d3de"

        invitation = {
            "invitationKind": "Service",
            "properties": {
                "targetActiveDirectoryId": targetActiveDirectoryId,
                "targetObjectId": targetObjectId
            }
        }

        invitation_request = build_sent_shares_create_invitation_request(
            sent_share_id=sent_share_id,
            sent_share_invitation_id=sent_share_invitation_id,
            content_type="application/json",
            content=json.dumps(invitation))
        
        invitation_response = client.send_request(invitation_request)

        assert invitation_response is not None
        assert invitation_response.status_code == 201, "Invalid status code 2 " + str(invitation_response.status_code)
        assert invitation_response.content is not None

        created_invitation = json.loads(invitation_response.content)

        assert created_invitation['id'] == str(sent_share_invitation_id)
        assert created_invitation['properties']['targetActiveDirectoryId'] == targetActiveDirectoryId
        assert created_invitation['properties']['targetObjectId'] == targetObjectId

    @PurviewSharingPowerShellPreparer()
    @recorded_by_proxy
    def test_get_all_sent_share_service_invitation(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)
        sent_share_id = "7eb8ba5b-e550-46c4-b877-097835d0cc80"
        sent_share_invitation_id = "623fe4bf-d2cb-4b9f-9243-abe16b65d8a8"
        sent_share = self.prepare_sent_share()

        request = build_sent_shares_create_or_replace_request(
            sent_share_id,
            content_type="application/json",
            content=json.dumps(sent_share))
        
        response = client.send_request(request)

        assert response is not None
        assert response.status_code == 201, "Invalid Status Code 1 " + str(response.status_code)

        targetActiveDirectoryId = "19513734-8215-4190-bd7e-ff6cbed36fbe"
        targetObjectId = "ebf435a4-3f8d-4ed1-843b-e598e2916a3e"

        sent_share_invitation = {
            "invitationKind": "Service",
            "properties": {
                "targetActiveDirectoryId": targetActiveDirectoryId,
                "targetObjectId": targetObjectId
            }
        }

        invitation_request = build_sent_shares_create_invitation_request(
            sent_share_id=sent_share_id,
            sent_share_invitation_id=sent_share_invitation_id,
            content_type="application/json",
            content=json.dumps(sent_share_invitation))
        
        invitation_response = client.send_request(invitation_request)

        assert invitation_response is not None
        assert invitation_response.status_code == 201, "Invalid status code 2 " + str(invitation_response.status_code)
        assert invitation_response.content is not None

        created_invitation = json.loads(invitation_response.content)

        assert created_invitation['id'] == str(sent_share_invitation_id)
        assert created_invitation['properties']['targetActiveDirectoryId'] == targetActiveDirectoryId
        assert created_invitation['properties']['targetObjectId'] == targetObjectId

        list_request = build_sent_shares_list_invitations_request(sent_share_id=sent_share_id)
        list_response = client.send_request(list_request)

        assert list_response is not None
        assert list_response.content is not None
         
        list = json.loads(list_response.content)['value']
        assert len([x for x in list if x['id'] == str(sent_share_invitation_id)]) == 1

    @PurviewSharingPowerShellPreparer()
    @recorded_by_proxy
    def test_delete_sent_share_service_invitation(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)
        sent_share_id = "17253ebb-2a2b-48da-8c9f-fa99c699d6c4"
        sent_share = self.prepare_sent_share()

        request = build_sent_shares_create_or_replace_request(
            sent_share_id,
            content_type="application/json",
            content=json.dumps(sent_share))

        response = client.send_request(request)

        assert response is not None
        assert response.status_code == 201, "Invalid Status Code " + str(response.status_code)

        delete_request = build_sent_shares_delete_request(sent_share_id=sent_share_id)
        delete_response = client.send_request(delete_request)

        assert delete_response is not None
        assert delete_response.status_code == 202, "Invalid Status Code " + str(response.status_code)

        try:
            delete_response.raise_for_status()
        except HttpResponseError as e:
            print("Exception " + str(e))
            print("Response " + delete_response.text())
    ###     ###
    ### NEW ###
    ###     ###
    @PurviewSharingPowerShellPreparer()
    @recorded_by_proxy
    def test_get_sent_share_invitation(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)
        sent_share_id = uuid4()
        sent_share_invitation_id = uuid4()
        sent_share = self.prepare_sent_share()

        request = build_sent_shares_create_or_replace_request(
            sent_share_id,
            content_type="application/json",
            content=json.dumps(sent_share))
        
        response = client.send_request(request)

        assert response is not None
        assert response.status_code == 201, "Invalid Status Code " + str(response.status_code)

        consumerEmail = "consumer@contoso.com"

        invitation = {
            "invitationKind": "User",
            "properties": {
                "targetEmail": consumerEmail,
                "notify": "true",
                "expirationDate": "2024-03-02 00:00:00"
            }
        }

        invitation_request = build_sent_shares_create_invitation_request(
            sent_share_id=sent_share_id,
            sent_share_invitation_id=sent_share_invitation_id,
            content_type="application/json",
            content=json.dumps(invitation))
        
        invitation_response = client.send_request(invitation_request)

        assert invitation_response is not None
        assert invitation_response.status_code == 201, "Invalid Status Code " + str(invitation_response.status_code)
        assert invitation_response.content is not None

        created_invitation = json.loads(invitation_response.content)

        assert created_invitation['id'] == str(sent_share_invitation_id)
        assert created_invitation['properties']['targetEmail'] == consumerEmail

        get_request = build_sent_shares_get_invitation_request(sent_share_id=sent_share_id, sent_share_invitation_id=sent_share_invitation_id)
        get_response = client.send_request(get_request)

        assert get_response is not None
        assert get_response.content is not None
         
        retrieved_sent_share_invitation = json.loads(get_response.content)

        assert retrieved_sent_share_invitation['id'] == str(sent_share_invitation_id)

        