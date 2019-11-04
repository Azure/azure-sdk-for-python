# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
import hashlib
import os

try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock

from azure.core.credentials import AccessToken
from azure.identity import EnvironmentCredential

from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.mgmt.keyvault.models import (
    SecretPermissions,
    KeyPermissions,
    CertificatePermissions,
    StoragePermissions,
    Permissions,
    Sku,
    SkuName,
    AccessPolicyEntry,
    VaultProperties,
    VaultCreateOrUpdateParameters,
)
from azure_devtools.scenario_tests.exceptions import AzureTestError

from devtools_testutils import AzureMgmtPreparer, ResourceGroupPreparer
from devtools_testutils.resource_testcase import RESOURCE_GROUP_PARAM

from keys_vault_client import VaultClient


DEFAULT_PERMISSIONS = Permissions(
    keys=[perm.value for perm in KeyPermissions],
    secrets=[perm.value for perm in SecretPermissions],
    certificates=[perm.value for perm in CertificatePermissions],
    storage=[perm.value for perm in StoragePermissions],
)
DEFAULT_SKU = SkuName.premium.value
CLIENT_OID = "00000000-0000-0000-0000-000000000000"


class VaultClientPreparer(AzureMgmtPreparer):
    def __init__(
        self,
        sku=None,
        permissions=None,
        enabled_for_deployment=True,
        enabled_for_disk_encryption=True,
        enabled_for_template_deployment=True,
        enable_soft_delete=None,
        name_prefix="vault",
        location="westus",
        parameter_name="vault_client",
        resource_group_parameter_name=RESOURCE_GROUP_PARAM,
        disable_recording=True,
        playback_fake_resource=None,
        client_kwargs=None,
    ):
        # incorporate md5 hashing of run identifier into key vault name for uniqueness
        name_prefix += hashlib.md5(os.environ['RUN_IDENTIFIER'].encode()).hexdigest()[-10:]

        super(VaultClientPreparer, self).__init__(
            name_prefix,
            24,
            disable_recording=disable_recording,
            playback_fake_resource=playback_fake_resource,
            client_kwargs=client_kwargs,
        )
        self.sku = sku or DEFAULT_SKU
        self.permissions = permissions or DEFAULT_PERMISSIONS
        self.enabled_for_deployment = enabled_for_deployment
        self.enabled_for_disk_encryption = enabled_for_disk_encryption
        self.enabled_for_template_deployment = enabled_for_template_deployment
        self.enable_soft_delete = enable_soft_delete
        self.location = location
        self.resource_group_parameter_name = resource_group_parameter_name
        self.parameter_name = parameter_name
        self.creds_parameter = "credentials"
        self.parameter_name_for_location = "location"
        self.client_oid = None

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs[self.resource_group_parameter_name]
        except KeyError:
            template = (
                "To create a key vault a resource group is required. Please add "
                "decorator @{} in front of this storage account preparer."
            )
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__))

    def create_resource(self, name, **kwargs):
        self.client_oid = self.test_class_instance.set_value_to_scrub("CLIENT_OID", CLIENT_OID)
        if self.is_live:
            # create a vault with the management client
            group = self._get_resource_group(**kwargs).name
            access_policies = [
                AccessPolicyEntry(
                    tenant_id=self.test_class_instance.get_settings_value('TENANT_ID'),
                    object_id=self.client_oid,
                    permissions=self.permissions,
                )
            ]
            properties = VaultProperties(
                tenant_id=self.test_class_instance.get_settings_value('TENANT_ID'),
                sku=Sku(name=self.sku),
                access_policies=access_policies,
                vault_uri=None,
                enabled_for_deployment=self.enabled_for_deployment,
                enabled_for_disk_encryption=self.enabled_for_disk_encryption,
                enabled_for_template_deployment=self.enabled_for_template_deployment,
                enable_soft_delete=self.enable_soft_delete,
                enable_purge_protection=None,
            )
            parameters = VaultCreateOrUpdateParameters(location=self.location, properties=properties)

            self.management_client = self.create_mgmt_client(KeyVaultManagementClient)

            # ARM may return not found at first even though the resource group has been created
            retries = 4
            for i in range(retries):
                try:
                    vault = self.management_client.vaults.create_or_update(group, name, parameters).result()
                except Exception as ex:
                    if "ResourceGroupNotFound" not in str(ex) or i == retries - 1:
                        raise
                    time.sleep(3)
            vault_uri = vault.properties.vault_uri
        else:
            # playback => we need only the uri used in the recording
            vault_uri = "https://{}.vault.azure.net/".format(name)

        client = self.create_vault_client(vault_uri)

        return {self.parameter_name: client}

    def create_vault_client(self, vault_uri):
        if self.is_live:
            credential = EnvironmentCredential()
        else:
            credential = Mock(get_token=lambda _: AccessToken("fake-token", 0))
        return VaultClient(vault_uri, credential, **self.client_kwargs)

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            group = self._get_resource_group(**kwargs).name
            self.management_client.vaults.delete(group, name)
            if self.enable_soft_delete:
                self.management_client.vaults.purge_deleted(name, self.location).wait()
