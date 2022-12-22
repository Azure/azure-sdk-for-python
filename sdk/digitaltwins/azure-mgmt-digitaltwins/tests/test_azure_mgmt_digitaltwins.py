# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
from azure.mgmt.digitaltwins import AzureDigitalTwinsManagementClient
from azure.mgmt.msi import ManagedServiceIdentityClient
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, ResourceGroupPreparer, recorded_by_proxy

import functools
import pytest
import unittest
import random
import string

AZURE_LOCATION = 'westus2'

class TestDigitalTwin(AzureMgmtRecordedTestCase):

    def setup_method(self, method):
        self.client = self.create_mgmt_client(AzureDigitalTwinsManagementClient)
        self.msi_client = self.create_mgmt_client(ManagedServiceIdentityClient)
    
    @recorded_by_proxy
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_create_digital_twin_with_identity(self, resource_group):
        SUBSCRIPTION_ID = self.get_settings_value("SUBSCRIPTION_ID")
        RESOURCE_GROUP_NAME = resource_group.name
        RESOURCE_NAME = self.get_resource_name("digitalTwin")

        # Setup Digital Twin
        self.create_digital_twins_and_validate(resource_group_name = RESOURCE_GROUP_NAME, resource_name = RESOURCE_NAME)

        # Cleanup
        self.client.digital_twins.begin_delete(resource_group_name = RESOURCE_GROUP_NAME, resource_name = RESOURCE_NAME).result()

    @recorded_by_proxy
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_create_endpoint_with_identity(self, resource_group):
        SUBSCRIPTION_ID = self.get_settings_value("SUBSCRIPTION_ID")
        RESOURCE_GROUP_NAME = resource_group.name
        RESOURCE_NAME = self.get_resource_name("digitalTwin")

        # Setup Digital Twin
        msi_id = self.create_digital_twins_and_validate(resource_group_name = RESOURCE_GROUP_NAME, resource_name = RESOURCE_NAME)

        # Create endpoint
        ENDPOINT_NAME = self.get_resource_name("endpoint")
        ENDPOINT_BODY = { 
            "properties": {
                "endpointType": "ServiceBus",
                "authenticationType": "IdentityBased",
                "endpointUri": "sb://mysb.servicebus.windows.net/",
                "entityPath": "abcabc",
                "identity": {
                    "type": "UserAssigned",
                    "userAssignedIdentity": msi_id
                }
            }
        }

        result = self.client.digital_twins_endpoint.begin_create_or_update(resource_group_name = RESOURCE_GROUP_NAME, resource_name = RESOURCE_NAME, endpoint_name = ENDPOINT_NAME, endpoint_description = ENDPOINT_BODY)
        result = result.result()
        assert result.name == ENDPOINT_NAME
        assert result.properties.identity is not None

        # Cleanup
        self.client.digital_twins_endpoint.begin_delete(resource_group_name = RESOURCE_GROUP_NAME, resource_name = RESOURCE_NAME, endpoint_name = ENDPOINT_NAME).result()
        self.client.digital_twins.begin_delete(resource_group_name = RESOURCE_GROUP_NAME, resource_name = RESOURCE_NAME).result()

    @recorded_by_proxy
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_create_tsdbconnection_with_identity(self, resource_group):
        SUBSCRIPTION_ID = self.get_settings_value("SUBSCRIPTION_ID")
        RESOURCE_GROUP_NAME = resource_group.name
        RESOURCE_NAME = self.get_resource_name("digitalTwin")

        # Setup Digital Twin
        msi_id = self.create_digital_twins_and_validate(resource_group_name = RESOURCE_GROUP_NAME, resource_name = RESOURCE_NAME)

        # Create TSDB connection
        TSDB_CONNECTION_NAME = self.get_resource_name("tsdbConnection")
        TSDB_CONNECTION_BODY = { 
            "properties": {
                "connectionType":"AzureDataExplorer",
                "adxEndpointUri":"https://testclusterZikfikxz.eastus.kusto.windows.net",
                "adxDatabaseName":"myDatabase",
                "eventHubEndpointUri":"sb://mysb.servicebus.windows.net/",
                "eventHubEntityPath":"abcabc", 
                "adxResourceId":"subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/testResourceGroup/providers/Microsoft.Kusto/clusters/testclusterZikfikxz", 
                "eventHubNamespaceResourceId":"subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/testResourceGroup/providers/Microsoft.EventHub/namespaces/myEH",
                "identity": {
                    "type": "UserAssigned",
                    "userAssignedIdentity": msi_id
                }
            }
        }

        # Setting polling to false since payload contains fake data
        result = self.client.time_series_database_connections.begin_create_or_update(resource_group_name = RESOURCE_GROUP_NAME, resource_name = RESOURCE_NAME, time_series_database_connection_name = TSDB_CONNECTION_NAME, time_series_database_connection_description = TSDB_CONNECTION_BODY, polling = False)
        result = result.result()
        assert result.name == TSDB_CONNECTION_NAME
        assert result.properties.identity is not None

        # Cleanup
        self.client.time_series_database_connections.begin_delete(resource_group_name = RESOURCE_GROUP_NAME, resource_name = RESOURCE_NAME, time_series_database_connection_name = TSDB_CONNECTION_NAME).result()
        self.client.digital_twins.begin_delete(resource_group_name = RESOURCE_GROUP_NAME, resource_name = RESOURCE_NAME).result()

    def create_digital_twins_and_validate(self, resource_group_name, resource_name):
        # Setup User Assigned Identity
        identity_name = self.get_resource_name("identityResource")
        if self.is_live:
            msi = self.msi_client.user_assigned_identities.create_or_update(resource_group_name, identity_name, {"location": AZURE_LOCATION})
            msi_id = msi.id    
        else:
            msi_id = f"/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/rgname/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identity_name}"

        # Create digital twin with UserAssigned
        BODY = {
            "location": AZURE_LOCATION,
            "identity": {
                "type": "UserAssigned",
                "userAssignedIdentities": {
                    msi_id: {}
                }
            }
        }
        result = self.client.digital_twins.begin_create_or_update(resource_group_name = resource_group_name, resource_name = resource_name, digital_twins_create = BODY)
        result = result.result()
        assert result.name == resource_name
        assert result.identity is not None

        return msi_id