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
    build_sent_shares_delete_invitation_request,
    build_sent_shares_list_invitations_request,
    build_sent_shares_get_invitation_request
)

class TestSentShares(TestPurviewSharing):
    @PurviewSharingPowerShellPreparer()
    @recorded_by_proxy
    def test_create_sent_share(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)
        sent_share_id = "541fd873-afa4-4d41-8b67-70d2302154c4" # uuid4()
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
        sent_share_id = "37061299-7990-4edd-b14c-2edf02edf162" # uuid4()
        sent_share_invitation_id = "f3275be4-b54d-4620-bf50-ec478f8c12a6" #uuid4()
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
        sent_share_id = "41211a38-0125-45a0-b748-b6008cf107c7" # uuid4()
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
        sent_share_id = "25fb1b10-8131-4610-84c4-181236fdd062" # uuid4()
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
            order_by="properties/createdAt desc")
        
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
        sent_share_id = "d857d382-b535-4b6e-bb5a-db59c42ed333" # uuid4()
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
        sent_share_id = "c0a51c4e-6951-4fb6-a501-98034ab5b741" # uuid4()
        sent_share_invitation_id = "840faa15-db43-46b5-9de0-842c0aa2db35" # uuid4()
        sent_share = self.prepare_sent_share()
        
        request = build_sent_shares_create_or_replace_request(
            sent_share_id,
            content_type="application/json",
            content=json.dumps(sent_share))
        
        response = client.send_request(request)

        assert response is not None
        assert response.status_code == 201, "Invalid Status Code 1 " + str(response.status_code)

        targetActiveDirectoryId = "b73a405f-f2e4-40f9-a606-5562778074c6" # uuid4()
        targetObjectId = "7cbeb37b-95ea-4a7a-8cb3-becc797b3b8d" # uuid4()

        invitation = {
            "invitationKind": "Service",
            "properties": {
                "targetActiveDirectoryId": str(targetActiveDirectoryId),
                "targetObjectId": str(targetObjectId)
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
        assert created_invitation['properties']['targetActiveDirectoryId'] == str(targetActiveDirectoryId)
        assert created_invitation['properties']['targetObjectId'] == str(targetObjectId)

    @PurviewSharingPowerShellPreparer()
    @recorded_by_proxy
    def test_get_all_sent_share_service_invitation(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)
        sent_share_id = "df189706-d347-4659-b7d9-62f8b7b974d2" # uuid4()
        sent_share_invitation_id = "2d423d1e-b1b1-4b33-9960-2fd2dd3fe90c" #uuid4()
        sent_share = self.prepare_sent_share()

        request = build_sent_shares_create_or_replace_request(
            sent_share_id,
            content_type="application/json",
            content=json.dumps(sent_share))
        
        response = client.send_request(request)

        assert response is not None
        assert response.status_code == 201, "Invalid Status Code 1 " + str(response.status_code)

        targetActiveDirectoryId = "2a040521-5776-4569-a788-bc9b66160f6b" # uuid4()
        targetObjectId = "e86fe185-1f23-4518-ab7b-e887cca44933" #uuid4()

        sent_share_invitation = {
            "invitationKind": "Service",
            "properties": {
                "targetActiveDirectoryId": str(targetActiveDirectoryId),
                "targetObjectId": str(targetObjectId)
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
        assert created_invitation['properties']['targetActiveDirectoryId'] == str(targetActiveDirectoryId)
        assert created_invitation['properties']['targetObjectId'] == str(targetObjectId)

        list_request = build_sent_shares_list_invitations_request(sent_share_id=sent_share_id)
        list_response = client.send_request(list_request)

        assert list_response is not None
        assert list_response.content is not None
         
        list = json.loads(list_response.content)['value']
        assert len([x for x in list if x['id'] == str(sent_share_invitation_id)]) == 1
    ###     ###
    ### NEW ###
    ###     ###
    @PurviewSharingPowerShellPreparer()
    @recorded_by_proxy
    def test_delete_sent_share_service_invitation(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)
        sent_share_id = "03a166c3-f68d-41fe-9af1-83f5dcc8b83e" # uuid4()
        sent_share_invitation_id = "0bea71cd-428b-4989-91e9-92f19b9e165c" # uuid4()
        sent_share = self.prepare_sent_share()

        request = build_sent_shares_create_or_replace_request(
            sent_share_id,
            content_type="application/json",
            content=json.dumps(sent_share))

        response = client.send_request(request)

        assert response is not None
        assert response.status_code == 201, "Invalid Status Code " + str(response.status_code)

        targetActiveDirectoryId = "746a6b35-6571-4688-9e52-d29451add6ed" # uuid4()
        targetObjectId = "fb5b839c-1401-4a58-b956-2d42f5641039" #uuid4()

        sent_share_invitation = {
            "invitationKind": "Service",
            "properties": {
                "targetActiveDirectoryId": str(targetActiveDirectoryId),
                "targetObjectId": str(targetObjectId)
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

        delete_request = build_sent_shares_delete_invitation_request(
            sent_share_id=sent_share_id, 
            sent_share_invitation_id=sent_share_invitation_id)
        
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
    def test_get_sent_share_invitation(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)
        sent_share_id = "1a82d02a-033c-4624-b8f2-243c0df06a9b" # uuid4()
        sent_share_invitation_id = "23006055-336a-437d-9808-3793af9fc6a8" # uuid4()
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

        