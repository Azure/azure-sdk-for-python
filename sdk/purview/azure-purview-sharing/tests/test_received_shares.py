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
        sent_share_id = "44a61a1f-c550-4c85-b8e3-f6f83fee489d" # uuid4()
        sent_share_invitation_id = "a713dfaf-70ac-4c48-80dd-33916a342d64" # uuid4()
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
        sent_share_id = "87bf306d-db22-4f57-a6e5-084245e386fd" # uuid4()
        sent_share_invitation_id = "40de4e40-fd85-4024-99b3-c09cead6896a" # uuid4()
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
        print(retrieved_share)
        assert retrieved_share is not None
        assert retrieved_share['id'] == received_share['id']

    @PurviewSharingPowerShellPreparer()
    @recorded_by_proxy
    def test_delete_received_share(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)
        sent_share_id = "50c5e9f2-8fc0-484b-96ab-1011401ec0b5" # uuid4()
        sent_share_invitation_id = "c3c31c43-95b9-406e-a9b7-cf21c41d80bb" # uuid4()
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
        sent_share_id = "0ea7e339-3790-47d5-8dbb-8c9415676f87" # uuid4()
        sent_share_invitation_id = "752d25fc-bad1-4e36-b28a-bcd6ddb02ee9" # uuid4()
        sent_share = self.prepare_sent_share()

        # cspell:disable-next-line
        consumer_storage_account_resource_id = "/subscriptions/0f3dcfc3-18f8-4099-b381-8353e19d43a7/resourceGroups/faisalaltell/providers/Microsoft.Storage/storageAccounts/bbfaisalr1"

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

    ###     ###
    ### NEW ###
    ###     ###
    @PurviewSharingPowerShellPreparer()
    @recorded_by_proxy
    def test_get_all_attached_shares(self, purviewsharing_endpoint):
        client = self.create_client(endpoint=purviewsharing_endpoint)
        sent_share_id = "d92b66fd-5458-4db3-878d-c3b79c3ed8ca" # uuid4()
        sent_share_invitation_id = "9898c18c-7848-4747-93de-9ffa1f4a79bf" # uuid4()
        sent_share = self.prepare_sent_share()

        # cspell:disable-next-line
        consumer_storage_account_resource_id = "/subscriptions/0f3dcfc3-18f8-4099-b381-8353e19d43a7/resourceGroups/faisalaltell/providers/Microsoft.Storage/storageAccounts/bbfaisalr1"

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

        list_attached_request = build_received_shares_list_attached_request(
            reference_name=consumer_storage_account_resource_id,
            orderby="properties/createdAt desc")
        list_attached_response = client.send_request(list_attached_request)

        assert list_attached_response is not None

        list_attached = json.loads(list_attached_response.content)

        assert list_attached is not None
        assert len(list_attached['value']) > 0
        # is the number of items that has shareStatus "Attached" equal to the number of all results
        assert len([x for x in list_attached['value'] if x['properties']['shareStatus'] == "Attached"]) == len(list_attached['value'])