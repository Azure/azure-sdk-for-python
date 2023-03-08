# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import uuid, json

from datetime import date
from testcase import TestPurviewSharing, PurviewSharingPowerShellPreparer
from devtools_testutils import recorded_by_proxy
from azure.core.exceptions import HttpResponseError
from azure.purview.sharing.operations._operations import (
    build_sent_shares_create_or_replace_request,
    build_sent_shares_create_invitation_request,
    build_sent_shares_get_request,
    build_sent_shares_list_request,
    build_sent_shares_delete_request,
    build_sent_shares_get_invitation_request,
    build_sent_shares_list_invitations_request
)

class TestSentShares(TestPurviewSharing):
    
    @PurviewSharingPowerShellPreparer()
    @recorded_by_proxy
    def test_create_sent_share(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)
        sent_share_id = "16e39ad5-007c-493a-8acb-c8c6b483b989"
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
        sent_share_id = "9765bd0c-e91b-4e64-a84c-4726532c0fc5"
        sent_share_invitation_id = "899274a4-c5b9-4753-9b03-7a62a2b3e73a"
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
        sent_share_id = "a424360f-c966-4183-9c9f-a38b984fbac7"
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
        sent_share_id = "7687b479-0f21-4a13-8316-a1198f5c1d5b"
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
        sent_share_id = "362bfbad-3d86-41eb-95c7-61eec7eb4b61"
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
        sent_share_id = "f78cbff1-faa8-4541-96cc-db9f7cf1c316"
        sent_share_invitation_id = "7733b4aa-02e0-4d32-b4ef-3f5bef527a74"
        sent_share = self.prepare_sent_share()
        
        request = build_sent_shares_create_or_replace_request(
            sent_share_id,
            content_type="application/json",
            content=json.dumps(sent_share))
        
        response = client.send_request(request)

        assert response is not None
        assert response.status_code == 201, "Invalid Status Code 1 " + str(response.status_code)

        targetActiveDirectoryId = "72f988bf-86f1-41af-91ab-2d7cd011db47"
        targetObjectId = "fc010728-94f6-4e9c-be3c-c08687414bd4"

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
    def test_get_sent_share_service_invitation(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)
        sent_share_id = "718ec0b3-ea73-4f29-9c0d-3cd1798044b1"
        sent_share_invitation_id = "51b62bad-43ab-423f-9c7f-5ffd56a42b70"
        sent_share = self.prepare_sent_share()

        request = build_sent_shares_create_or_replace_request(
            sent_share_id,
            content_type="application/json",
            content=json.dumps(sent_share))
        
        response = client.send_request(request)

        assert response is not None
        assert response.status_code == 201, "Invalid Status Code " + str(response.status_code)

        targetActiveDirectoryId = "72f988bf-86f1-41af-91ab-2d7cd011db47"
        targetObjectId = "fc010728-94f6-4e9c-be3c-c08687414bd4"

        invitation_request = build_sent_shares_create_invitation_request(
            sent_share_id=sent_share_id,
            sent_share_invitation_id=sent_share_invitation_id)
        
        invitation_response = client.send_request(invitation_request)

        assert invitation_response is not None
        assert invitation_response.status_code == 201, "Invalid status code " + str(invitation_response.status_code)
        assert invitation_response.content is not None

        created_invitation = json.loads(invitation_response.content)

        assert created_invitation['id'] == str(sent_share_invitation_id)
        assert created_invitation['properties']['targetActiveDirectoryId'] == targetActiveDirectoryId
        assert created_invitation['properties']['targetObjectId'] == targetObjectId

        get_request = build_sent_shares_get_invitation_request(
            sent_share_id=sent_share_id,
            sent_share_invitation_id=sent_share_invitation_id)
        
        get_response = client.send_request(get_request)

        assert get_response is not None
        assert get_response.status_code == 200, "Invalid status code " + str(get_response.status_code)

        retrieved_invitation = json.loads(get_response.content)

        assert retrieved_invitation['id'] == str(sent_share_invitation_id)
        assert retrieved_invitation['properties']['targetActiveDirectoryId'] == targetActiveDirectoryId
        assert retrieved_invitation['properties']['targetObjectId'] == targetObjectId

    @PurviewSharingPowerShellPreparer()
    @recorded_by_proxy
    def test_get_all_sent_share_service_invitation(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)
        sent_share_id = "477ab96b-ffda-4e45-821f-9fc60dc15da4"
        sent_share_invitation_id = "cf0e1028-718d-43ee-a487-949bdd4d4499"
        sent_share = self.prepare_sent_share()

        request = build_sent_shares_create_or_replace_request(
            sent_share_id,
            content_type="application/json",
            content=json.dumps(sent_share))
        
        response = client.send_request(request)

        assert response is not None
        assert response.status_code == 201, "Invalid Status Code " + str(response.status_code)

        targetActiveDirectoryId = "72f988bf-86f1-41af-91ab-2d7cd011db47"
        targetObjectId = "fc010728-94f6-4e9c-be3c-c08687414bd4"

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
        assert invitation_response.status_code == 201, "Invalid status code " + str(invitation_response.status_code)
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
        sent_share_id = "46a8100f-5c37-4ce5-af87-3f45d9b015bf"
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