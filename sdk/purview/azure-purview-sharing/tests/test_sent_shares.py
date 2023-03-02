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
        sent_share_id = uuid.uuid4()
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
        sent_share_id = uuid.uuid4()
        sent_share_invitation_id = uuid.uuid4()
        sent_share = self.prepare_sent_share()

        request = build_sent_shares_create_or_replace_request(
            sent_share_id,
            content_type="application/json",
            content=json.dumps(sent_share))
        
        response = client.send_request(request)

        assert response is not None
        assert response.status_code == 201, "Invalid Status Code " + str(response.status_code)

        consumerEmail = "consumer@contoso.com"
        today=date.today()

        invitation = {
            "invitationKind": "User",
            "properties": {
                "targetEmail": consumerEmail,
                "notify": "true",
                "expirationDate": date(today.year+1,today.month,today.day).strftime("%Y-%m-%d") + " 00:00:00"
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
        sent_share_id = uuid.uuid4()
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
        sent_share_id = uuid.uuid4()
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
        sent_share_id = uuid.uuid4()
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
        sent_share_id = uuid.uuid4()
        sent_share_invitation_id = uuid.uuid4()
        sent_share = self.prepare_sent_share()
        
        request = build_sent_shares_create_or_replace_request(
            sent_share_id,
            content_type="application/json",
            content=json.dumps(sent_share))
        
        response = client.send_request(request)

        assert response is not None
        assert response.status_code == 201, "Invalid Status Code " + str(response.status_code)

        targetActiverDirectoryId = "72f988bf-86f1-41af-91ab-2d7cd011db47"
        targetObjectId = "fc010728-94f6-4e9c-be3c-c08687414bd4"

        sent_share_invitation = {
            "invitationKind": "Service",
            "properties": {
                "targetActiveDirectoryId": targetActiverDirectoryId,
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
        assert invitation_response.status_code == 201, "Invalid status code"
        assert invitation_response.content is not None

        created_invitation = json.loads(invitation_response.content)

        assert created_invitation['id'] == str(sent_share_invitation_id)
        assert created_invitation['properties']['targetActiveDirectoryId'] == targetActiverDirectoryId
        assert created_invitation['properties']['targetObjectId'] == targetObjectId

    @PurviewSharingPowerShellPreparer()
    @recorded_by_proxy
    def test_get_sent_share_service_invitation(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)
        sent_share_id = uuid.uuid4()
        sent_share_invitation_id = uuid.uuid4()
        sent_share = self.prepare_sent_share()

        request = build_sent_shares_create_or_replace_request(
            sent_share_id,
            content_type="application/json",
            content=json.dumps(sent_share))
        
        response = client.send_request(request)

        assert response is not None
        assert response.status_code == 201, "Invalid Status Code " + str(response.status_code)

        targetActiverDirectoryId = "72f988bf-86f1-41af-91ab-2d7cd011db47"
        targetObjectId = "fc010728-94f6-4e9c-be3c-c08687414bd4"

        sent_share_invitation = {
            "invitationKind": "Service",
            "properties": {
                "targetActiveDirectoryId": targetActiverDirectoryId,
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
        assert invitation_response.status_code == 201, "Invalid status code"
        assert invitation_response.content is not None

        created_invitation = json.loads(invitation_response.content)

        assert created_invitation['id'] == str(sent_share_invitation_id)
        assert created_invitation['properties']['targetActiveDirectoryId'] == targetActiverDirectoryId
        assert created_invitation['properties']['targetObjectId'] == targetObjectId

        get_request = build_sent_shares_get_invitation_request(
            sent_share_id=sent_share_id,
            sent_share_invitation_id=sent_share_invitation_id,
            content=json.dumps(sent_share_invitation))
        
        get_response = client.send_request(get_request)

        assert get_response is not None
        assert get_response.status_code == 200, "Invalid status code"

        retrieved_invitation = json.loads(get_response.content)

        assert retrieved_invitation['id'] == str(sent_share_invitation_id)
        assert retrieved_invitation['properties']['targetActiveDirectoryId'] == targetActiverDirectoryId
        assert retrieved_invitation['properties']['targetObjectId'] == targetObjectId

    @PurviewSharingPowerShellPreparer()
    @recorded_by_proxy
    def test_get_all_sent_share_service_invitation(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)
        sent_share_id = uuid.uuid4()
        sent_share_invitation_id = uuid.uuid4()
        sent_share = self.prepare_sent_share()

        request = build_sent_shares_create_or_replace_request(
            sent_share_id,
            content_type="application/json",
            content=json.dumps(sent_share))
        
        response = client.send_request(request)

        assert response is not None
        assert response.status_code == 201, "Invalid Status Code " + str(response.status_code)

        targetActiverDirectoryId = "72f988bf-86f1-41af-91ab-2d7cd011db47"
        targetObjectId = "fc010728-94f6-4e9c-be3c-c08687414bd4"

        sent_share_invitation = {
            "invitationKind": "Service",
            "properties": {
                "targetActiveDirectoryId": targetActiverDirectoryId,
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
        assert invitation_response.status_code == 201, "Invalid status code"
        assert invitation_response.content is not None

        created_invitation = json.loads(invitation_response.content)

        assert created_invitation['id'] == str(sent_share_invitation_id)
        assert created_invitation['properties']['targetActiveDirectoryId'] == targetActiverDirectoryId
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
        sent_share_id = uuid.uuid4()
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