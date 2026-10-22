# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import pytest
from azure.mgmt.workloadssapvirtualinstance import WorkloadsSapVirtualInstanceMgmtClient
from azure.mgmt.workloadssapvirtualinstance.models import UpdateSAPVirtualInstanceRequest
from azure.mgmt.msi import ManagedServiceIdentityClient
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = "eastus"
SAP_VIRTUAL_INSTANCE_NAME = "S08"


@pytest.mark.skip("hard to test")
@pytest.mark.skipif(os.getenv("AZURE_TEST_RUN_LIVE") not in ("true", "yes"), reason="only run live test")
class TestMgmtWorkloadsSapVirtualInstance(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.mgmt_client = self.create_mgmt_client(WorkloadsSapVirtualInstanceMgmtClient)
        self.msi_client = self.create_mgmt_client(ManagedServiceIdentityClient)
        self.authorization_client = self.create_mgmt_client(AuthorizationManagementClient)
        self.network_client = self.create_mgmt_client(NetworkManagementClient)
        self.ssh_client = self.create_mgmt_client(ComputeManagementClient)

    def create_user_assigned_identity(self, group_name, location, identity_name):
        user_assigned_identity_creation = self.msi_client.user_assigned_identities.create_or_update(
            group_name, identity_name, {"location": location}
        )
        return (user_assigned_identity_creation.id, user_assigned_identity_creation.principal_id)

    def create_role_assignment_for_identity(self, subscription, group_name, principal_id):
        role_definition_creation = self.authorization_client.role_definitions.create_or_update(
            scope=f"/subscriptions/{subscription}/resourceGroups/{group_name}",
            role_definition_id="66666666-6666-6666-6666-666666666666",
            role_definition={
                "properties": {
                    "roleName": "saprole",
                    "assignableScopes": [f"/subscriptions/{subscription}/resourceGroups/{group_name}"],
                    "permissions": [{"actions": ["*"]}],
                }
            },
        )

        self.authorization_client.role_assignments.create(
            scope=f"/subscriptions/{subscription}/resourceGroups/{group_name}",
            role_assignment_name="66666666-6666-6666-6666-666666666666",
            parameters={
                "properties": {
                    "principalId": principal_id,
                    "principalType": "ServicePrincipal",
                    "roleDefinitionId": role_definition_creation.id,
                }
            },
        )

    def delete_role_assignment(self, subscription, group_name):
        self.authorization_client.role_assignments.delete(
            scope=f"/subscriptions/{subscription}/resourceGroups/{group_name}",
            role_assignment_name="66666666-6666-6666-6666-666666666666",
        )

    def create_virtual_network(self, group_name, location, network_name, subnet_name):
        virtual_network_creation = self.network_client.virtual_networks.begin_create_or_update(
            group_name, network_name, {"location": location, "address_space": {"address_prefixes": ["10.0.0.0/16"]}}
        ).result()

        subnet_creation = self.network_client.subnets.begin_create_or_update(
            group_name, virtual_network_creation.name, subnet_name, {"address_prefix": "10.0.0.0/24"}
        ).result()
        return subnet_creation.id

    def create_ssh_key_pair(self, group_name, location, ssh_public_key_name):
        ssh_public_key_creation = self.ssh_client.ssh_public_keys.create(
            group_name, ssh_public_key_name, {"location": location}
        )

        ssh_key_pair_creation = self.ssh_client.ssh_public_keys.generate_key_pair(
            group_name,
            ssh_public_key_creation.name,
        )
        return (ssh_key_pair_creation.public_key, ssh_key_pair_creation.private_key)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_sap_virtual_instance(self, resource_group):
        SUBSCRIPTION_ID = self.get_settings_value("SUBSCRIPTION_ID")
        IDENTITY_NAME = self.get_resource_name("sapidentity")
        NETWORK_NAME = self.get_resource_name("sapnetwork")
        SUBNET_NAME = self.get_resource_name("sapsubnet")
        SSH_PUBLIC_KEY_NAME = self.get_resource_name("sapsshpublickey")

        identity_resource_id, identity_principal_id = self.create_user_assigned_identity(
            resource_group.name, AZURE_LOCATION, IDENTITY_NAME
        )
        self.create_role_assignment_for_identity(SUBSCRIPTION_ID, resource_group.name, identity_principal_id)
        subnet_id = self.create_virtual_network(resource_group.name, AZURE_LOCATION, NETWORK_NAME, SUBNET_NAME)
        ssh_public_key, ssh_private_key = self.create_ssh_key_pair(
            resource_group.name, AZURE_LOCATION, SSH_PUBLIC_KEY_NAME
        )

        BODY = {
            "tags": {},
            "location": AZURE_LOCATION,
            "identity": {"type": "UserAssigned", "userAssignedIdentities": {identity_resource_id: {}}},
            "properties": {
                "environment": "NonProd",
                "sapProduct": "S4HANA",
                "managedResourcesNetworkAccessType": "Public",
                "configuration": {
                    "configurationType": "DeploymentWithOSConfig",
                    "appLocation": "eastus",
                    "infrastructureConfiguration": {
                        "deploymentType": "SingleServer",
                        "subnetId": subnet_id,
                        "virtualMachineConfiguration": {
                            "vmSize": "Standard_E32ds_v4",
                            "imageReference": {
                                "sku": "gen2",
                                "publisher": "SUSE",
                                "version": "latest",
                                "offer": "sles-sap-12-sp5",
                            },
                            "osProfile": {
                                "adminUsername": "saptest",
                                "osConfiguration": {
                                    "osType": "Linux",
                                    "disablePasswordAuthentication": True,
                                    "sshKeyPair": {"publicKey": ssh_public_key, "privateKey": ssh_private_key},
                                },
                            },
                        },
                        "appResourceGroup": resource_group.name,
                    },
                    "osSapConfiguration": {"sapFqdn": "xyz.test.com"},
                },
            },
        }
        create_result = self.mgmt_client.sap_virtual_instances.begin_create(
            resource_group.name, SAP_VIRTUAL_INSTANCE_NAME, BODY
        ).result()
        assert create_result.properties.configuration.configuration_type == "DeploymentWithOSConfig"

        dict = {"key1": "val1"}
        updateBody = UpdateSAPVirtualInstanceRequest(tags=dict)
        result = self.mgmt_client.sap_virtual_instances.begin_update(
            resource_group.name, SAP_VIRTUAL_INSTANCE_NAME, updateBody
        ).result()

        self.delete_role_assignment(SUBSCRIPTION_ID, resource_group.name)
