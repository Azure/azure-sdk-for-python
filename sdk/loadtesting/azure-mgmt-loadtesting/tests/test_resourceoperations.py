# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import unittest
import os
from azure.mgmt.loadtesting import LoadTestMgmtClient
from azure.mgmt.loadtesting.models import (
    LoadTestResource,
    LoadTestResourcePatchRequestBody,
    ManagedServiceIdentity,
    UserAssignedIdentity,
    EncryptionProperties,
    EncryptionPropertiesIdentity,
)
from azure.mgmt.msi import ManagedServiceIdentityClient
from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.keyvault.keys import KeyClient
from devtools_testutils import (
    AzureMgmtRecordedTestCase,
    recorded_by_proxy,
    ResourceGroupPreparer,
)
from mgmt_test_helper import create_key, create_key_vault, create_managed_identity

DEFAULT_SANITIZER = "00000000-0000-0000-0000-000000000000"


@pytest.mark.live_test_only
class TestResourceOperations(AzureMgmtRecordedTestCase):
    AZURE_LOCATION = "westus2"

    def setup_method(self, method):
        self.loadtestservice_client = self.create_mgmt_client(LoadTestMgmtClient)
        self.msi_client = self.create_mgmt_client(ManagedServiceIdentityClient)
        self.akv_client = self.create_mgmt_client(KeyVaultManagementClient)
        self.credential = self.get_credential(KeyClient)
        self.tenant_id = (
            os.environ.get("AZURE_TENANT_ID", None)
            if self.is_live
            else DEFAULT_SANITIZER
        )
        self.object_id = (
            os.environ.get("CLIENT_OID", None) if self.is_live else DEFAULT_SANITIZER
        )

    @ResourceGroupPreparer(name_prefix="altpysdk")
    @recorded_by_proxy
    def test_load_test_resource_operations(self, resource_group):

        self.msi1 = create_managed_identity(
            self.msi_client,
            resource_group.name + "mi1",
            resource_group.name,
            self.AZURE_LOCATION,
        )
        self.msi2 = create_managed_identity(
            self.msi_client,
            resource_group.name + "mi2",
            resource_group.name,
            self.AZURE_LOCATION,
        )
        self.akv = create_key_vault(
            self.akv_client,
            resource_group.name + "akv",
            resource_group.name,
            self.AZURE_LOCATION,
            self.msi1,
            self.tenant_id,
            self.object_id,
        )

        self.key = create_key(self.akv, self.credential, resource_group.name + "key")

        # Create a load test resource
        loadtestresource_create_payload = LoadTestResource(
            location=self.AZURE_LOCATION,
            identity=ManagedServiceIdentity(
                type="SystemAssigned,UserAssigned",
                user_assigned_identities={
                    self.msi1.id: UserAssignedIdentity(),
                    self.msi2.id: UserAssignedIdentity(),
                },
            ),
            encryption=EncryptionProperties(
                identity=EncryptionPropertiesIdentity(
                    type="UserAssigned", resource_id=self.msi1.id
                ),
                key_url=self.key.id,
            ),
        )

        # Create a load test resource create begin - returns a poller
        loadtest_resource_poller = (
            self.loadtestservice_client.load_tests.begin_create_or_update(
                resource_group.name,
                resource_group.name + "resource",
                loadtestresource_create_payload,
            )
        )

        # Get the result of the poller
        loadtest_resource = loadtest_resource_poller.result()

        # Assert the result of the poller
        assert loadtest_resource
        assert loadtest_resource.id
        assert loadtest_resource.name == resource_group.name + "resource"
        assert loadtest_resource.location == self.AZURE_LOCATION
        assert loadtest_resource.identity
        assert loadtest_resource.identity.type == "SystemAssigned, UserAssigned"
        assert len(loadtest_resource.identity.user_assigned_identities) == 2
        assert loadtest_resource.encryption
        assert loadtest_resource.encryption.key_url == self.key.id
        assert loadtest_resource.encryption.identity
        assert loadtest_resource.encryption.identity.type == "UserAssigned"
        assert loadtest_resource.encryption.identity.resource_id == self.msi1.id

        # # Get the load test resource
        loadtest_resource_get = self.loadtestservice_client.load_tests.get(
            resource_group.name, resource_group.name + "resource"
        )

        # # Assert the result of the get operation
        assert loadtest_resource_get
        assert loadtest_resource_get.id
        assert loadtest_resource_get.name == resource_group.name + "resource"
        assert loadtest_resource_get.location == self.AZURE_LOCATION
        assert loadtest_resource_get.identity
        assert loadtest_resource_get.identity.type == "SystemAssigned, UserAssigned"
        assert len(loadtest_resource_get.identity.user_assigned_identities) == 2
        assert loadtest_resource_get.encryption
        assert loadtest_resource_get.encryption.key_url == self.key.id
        assert loadtest_resource_get.encryption.identity
        assert loadtest_resource_get.encryption.identity.type == "UserAssigned"
        assert loadtest_resource_get.encryption.identity.resource_id == self.msi1.id

        # Update the load test resource
        loadtestresourcePatchdata = LoadTestResourcePatchRequestBody(
            identity=ManagedServiceIdentity(
                type="SystemAssigned,UserAssigned",
                user_assigned_identities={self.msi2.id: None},
            ),
        )

        # load test resource update begin - returns a poller
        loadtest_resource_patch_poller = (
            self.loadtestservice_client.load_tests.begin_update(
                resource_group.name,
                resource_group.name + "resource",
                loadtestresourcePatchdata,
            )
        )

        # Get the result of the poller
        loadtest_resource_patch_response = loadtest_resource_patch_poller.result()

        # Assert the result of the poller
        assert loadtest_resource_patch_response
        assert loadtest_resource_patch_response.id
        assert loadtest_resource_patch_response.name == resource_group.name + "resource"
        assert loadtest_resource_patch_response.location == self.AZURE_LOCATION
        assert loadtest_resource_patch_response.identity
        assert (
            loadtest_resource_patch_response.identity.type
            == "SystemAssigned, UserAssigned"
        )
        assert (
            len(loadtest_resource_patch_response.identity.user_assigned_identities) == 1
        )
        assert loadtest_resource_patch_response.encryption
        assert loadtest_resource_patch_response.encryption.key_url == self.key.id
        assert loadtest_resource_patch_response.encryption.identity
        assert (
            loadtest_resource_patch_response.encryption.identity.type == "UserAssigned"
        )
        assert (
            loadtest_resource_patch_response.encryption.identity.resource_id
            == self.msi1.id
        )

        # Delete the load test resource - returns a poller
        loadtest_resource_delete_poller = (
            self.loadtestservice_client.load_tests.begin_delete(
                resource_group.name, resource_group.name + "resource"
            )
        )


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
