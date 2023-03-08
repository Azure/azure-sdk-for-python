# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import uuid, json, string, random

from testcase import TestPurviewSharing, PurviewSharingPowerShellPreparer
from devtools_testutils import recorded_by_proxy
from azure.core.exceptions import HttpResponseError
from azure.purview.sharing.operations._operations import (
    build_sent_shares_create_or_replace_request,
    build_sent_shares_create_invitation_request,
    build_received_shares_list_detached_request,
    build_received_shares_get_request,
    build_received_shares_delete_request,
    build_received_shares_create_or_replace_request
)

class TestReceivedShares(TestPurviewSharing):

    @PurviewSharingPowerShellPreparer()
    @recorded_by_proxy
    def test_get_all_detached_shares(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)
        sent_share_id = "6eb422c0-ebe0-4e65-a79b-b9348fae9e84"
        sent_share_invitation_id = "0c80bdeb-7801-4220-b32f-fafea6939803"
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
                "expirationDate": "2024-01-01 00:00:00"
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

        list_detached_request = build_received_shares_list_detached_request(orderby="properties/createdAt desc")
        list_detached_response = client.send_request(list_detached_request)

        assert list_detached_response is not None

        list_detached = json.loads(list_detached_response.content)

        assert list_detached is not None
        assert len(list_detached['value']) > 0

        # is the number of items that has shareStatus "Detached" equal to the number of all results
        assert len([x for x in list_detached['value'] if x['properties']['shareStatus'] == "Detached"]) == len(list_detached['value'])
    
    @PurviewSharingPowerShellPreparer()
    @recorded_by_proxy
    def test_get_received_share(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)
        sent_share_id = "63aa0eea-72e8-4741-990e-a69a46de5054"
        sent_share_invitation_id = "149ee1f5-a916-469e-9561-8082f4d47999"
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
                "expirationDate": "2024-01-01 00:00:00"
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

        list_detached_request = build_received_shares_list_detached_request(orderby="properties/createdAt desc")
        list_detached_response = client.send_request(list_detached_request)

        assert list_detached_response is not None

        list_detached = json.loads(list_detached_response.content)

        received_share = list_detached['value'][0]

        get_share_request = build_received_shares_get_request(received_share_id=received_share['id'])
        get_share_response = client.send_request(get_share_request)
        
        retrieved_share = json.loads(get_share_response.content)

        assert retrieved_share is not None
        assert retrieved_share['id'] == received_share['id']

    @PurviewSharingPowerShellPreparer()
    @recorded_by_proxy
    def test_delete_received_share(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)
        sent_share_id = "a179f15e-168a-4534-8eea-5403d0c5cbfc"
        sent_share_invitation_id = "45501fff-f3cb-4713-9db8-9ac69518d279"
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
                "expirationDate": "2024-01-01 00:00:00"
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

        list_detached_request = build_received_shares_list_detached_request(orderby="properties/createdAt desc")
        list_detached_response = client.send_request(list_detached_request)

        assert list_detached_response is not None

        list_detached = json.loads(list_detached_response.content)

        received_share = list_detached['value'][0]

        delete_received_share_request = build_received_shares_delete_request(received_share_id=received_share['id'])
        delete_received_share_response = client.send_request(delete_received_share_request)

        try:
            delete_received_share_response.raise_for_status()
        except HttpResponseError as e:
            print("Exception " + str(e))
            print("Response " + delete_received_share_response.text())

    @PurviewSharingPowerShellPreparer()
    @recorded_by_proxy
    def test_attach_received_share(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)
        sent_share_id = "7c5d17b5-e485-4862-8079-625b6bd25bb0"
        sent_share_invitation_id = "8bad25d9-a8c8-4c96-87a1-dfd70d1c4fb4"
        sent_share = self.prepare_sent_share()

        # cspell:disable-next-line
        consumer_storage_account_resource_id = "/subscriptions/0f3dcfc3-18f8-4099-b381-8353e19d43a7/resourceGroups/faisalaltell/providers/Microsoft.Storage/storageAccounts/ftreceiversan"

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
                "expirationDate": "2024-01-01 00:00:00"
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

        list_detached_request = build_received_shares_list_detached_request(orderby="properties/createdAt desc")
        list_detached_response = client.send_request(list_detached_request)

        assert list_detached_response is not None

        list_detached = json.loads(list_detached_response.content)
        received_share = list_detached['value'][0]

        store_reference = {
            "referenceName": consumer_storage_account_resource_id,
            "type": "ArmResourceReference"
        }

        # cspell:disable
        sink = {
            "properties": {
                "containerName": "containerellxvxonnlukvfzbwhlexfzqfs",
                "folder": "folderpubhxhmiibnxcvqchnbi",
                "mountPath": "mountPathciynxouybsqvfgmcfwtt",
            },
            "storeKind": "AdlsGen2Account",
            "storeReference": store_reference
        }
        # cspell:enable

        received_share['properties']['sink'] = sink

        update_request = build_received_shares_create_or_replace_request(
            received_share['id'],
            content_type="application/json",
            content=json.dumps(received_share))
        
        update_response = client.send_request(update_request)

        assert update_response is not None
        assert update_response.status_code == 201, "Invalid Status Code " + str(update_response.status_code)

        try:
            update_response.raise_for_status()
        except HttpResponseError as e:
            print("Exception " + str(e))
            print("Response " + update_response.text())