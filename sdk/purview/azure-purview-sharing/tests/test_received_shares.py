# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
from uuid import uuid4

from testcase import TestPurviewSharing, PurviewSharingPowerShellPreparer
from devtools_testutils import recorded_by_proxy
from azure.core.exceptions import HttpResponseError
from azure.purview.sharing.operations._operations import (
    build_sent_shares_create_or_replace_request,
    build_sent_shares_create_invitation_request,
    build_received_shares_list_detached_request,
    build_received_shares_get_request,
    build_received_shares_delete_request,
    build_received_shares_create_or_replace_request,
    build_received_shares_list_attached_request
)

class TestReceivedShares(TestPurviewSharing):

    @PurviewSharingPowerShellPreparer()
    @recorded_by_proxy
    def test_get_all_detached_shares(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)
        sent_share_id = "4556ccb7-5d6a-45d4-8568-e1faa236e037" # uuid4()
        sent_share_invitation_id = "554696cf-ddc7-46c0-b915-45face229cd3" # uuid4()
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

        list_detached_request = build_received_shares_list_detached_request(order_by="properties/createdAt desc")
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
        sent_share_id = "34ede054-d6fc-49a1-a4e2-996433ed4b53" #uuid4()
        sent_share_invitation_id = "b8307b9f-db8d-4023-b406-2e7f9f6d88c5" #uuid4()
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

        list_detached_request = build_received_shares_list_detached_request(order_by="properties/createdAt desc")
        list_detached_response = client.send_request(list_detached_request)

        assert list_detached_response is not None

        list_detached = json.loads(list_detached_response.content)

        received_share = list_detached['value'][0]

        get_share_request = build_received_shares_get_request(received_share_id=received_share['id'])
        get_share_response = client.send_request(get_share_request)
        
        retrieved_share = json.loads(get_share_response.content)
        print(retrieved_share)
        assert retrieved_share is not None
        assert retrieved_share['id'] == received_share['id']

    @PurviewSharingPowerShellPreparer()
    @recorded_by_proxy
    def test_delete_received_share(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)
        sent_share_id = "2a7268a0-85d9-4c13-ba7b-a25ebba5faf3" #uuid4()
        sent_share_invitation_id = "9a672068-d620-4492-9e20-3f686f768f29" #uuid4()
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

        list_detached_request = build_received_shares_list_detached_request(order_by="properties/createdAt desc")
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
        sent_share_id = "b9d374c2-30d7-4e91-a750-a53238002652" # uuid4()
        sent_share_invitation_id = "242f81b5-fe36-402b-9a27-5d2af7f33308" #uuid4()
        sent_share = self.prepare_sent_share()

        # cspell:disable-next-line
        consumer_storage_account_resource_id = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/fakeResourceGroup/providers/Microsoft.Storage/storageAccounts/fakeStorageAccountR"

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

        list_detached_request = build_received_shares_list_detached_request(order_by="properties/createdAt desc")
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

    ###     ###
    ### NEW ###
    ###     ###
    @PurviewSharingPowerShellPreparer()
    @recorded_by_proxy
    def test_get_all_attached_shares(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)
        sent_share_id = "6143851f-930b-4050-a437-00b6bfbf2b4e" #uuid4()
        sent_share_invitation_id = "4430cf68-61db-4e05-af7b-297bad6d362b" #uuid4()
        sent_share = self.prepare_sent_share()

        # cspell:disable-next-line
        consumer_storage_account_resource_id = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/fakeResourceGroup/providers/Microsoft.Storage/storageAccounts/fakeStorageAccountR"

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

        list_detached_request = build_received_shares_list_detached_request(order_by="properties/createdAt desc")
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

        list_attached_request = build_received_shares_list_attached_request(
            reference_name=consumer_storage_account_resource_id,
            order_by="properties/createdAt desc")
        list_attached_response = client.send_request(list_attached_request)

        assert list_attached_response is not None

        list_attached = json.loads(list_attached_response.content)

        assert list_attached is not None
        assert len(list_attached['value']) > 0
        # is the number of items that has shareStatus "Attached" equal to the number of all results
        assert len([x for x in list_attached['value'] if x['properties']['shareStatus'] == "Attached"]) == len(list_attached['value'])