# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
import random

from string import ascii_letters

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

try:
    from azure.mgmt.keyvault.models import SkuFamily
except ImportError:
    pass

from azure_devtools.scenario_tests.exceptions import (
    AzureTestError,
    NameInUseError,
    ReservedResourceNameError,
)

from . import AzureMgmtPreparer, ResourceGroupPreparer
from .resource_testcase import RESOURCE_GROUP_PARAM


DEFAULT_PERMISSIONS = Permissions(
    keys=[perm.value for perm in KeyPermissions],
    secrets=[perm.value for perm in SecretPermissions],
    certificates=[perm.value for perm in CertificatePermissions],
    storage=[perm.value for perm in StoragePermissions],
)
DEFAULT_SKU = SkuName.premium.value
CLIENT_OID = "00000000-0000-0000-0000-000000000000"


class KeyVaultPreparer(AzureMgmtPreparer):
    def __init__(
        self,
        name_prefix=random.choice(ascii_letters).lower(),
        sku=DEFAULT_SKU,
        permissions=DEFAULT_PERMISSIONS,
        enabled_for_deployment=True,
        enabled_for_disk_encryption=True,
        enabled_for_template_deployment=True,
        enable_soft_delete=None,
        location="westus",
        parameter_name="vault_uri",
        resource_group_parameter_name=RESOURCE_GROUP_PARAM,
        disable_recording=True,
        playback_fake_resource=None,
        client_kwargs=None,
        random_name_enabled=True,
    ):
        super(KeyVaultPreparer, self).__init__(
            name_prefix,
            24,
            disable_recording=disable_recording,
            playback_fake_resource=playback_fake_resource,
            client_kwargs=client_kwargs,
            random_name_enabled=random_name_enabled,
        )
        self.location = location
        self.sku = sku
        self.permissions = permissions
        self.enabled_for_deployment = enabled_for_deployment
        self.enabled_for_disk_encryption = enabled_for_disk_encryption
        self.enabled_for_template_deployment = enabled_for_template_deployment
        self.enable_soft_delete = enable_soft_delete
        self.resource_group_parameter_name = resource_group_parameter_name
        self.parameter_name = parameter_name
        if random_name_enabled:
            self.resource_moniker = "vaultname"
        self.client_oid = None

    def create_resource(self, name, **kwargs):
        self.client_oid = self.test_class_instance.set_value_to_scrub(
            "CLIENT_OID", CLIENT_OID
        )
        if self.is_live:
            group = self._get_resource_group(**kwargs).name
            access_policies = [
                AccessPolicyEntry(
                    tenant_id=self.test_class_instance.get_settings_value("TENANT_ID"),
                    object_id=self.client_oid,
                    permissions=self.permissions,
                )
            ]
            properties = VaultProperties(
                tenant_id=self.test_class_instance.get_settings_value("TENANT_ID"),
                sku=Sku(name=self.sku, family=SkuFamily.A)
                if SkuFamily
                else Sku(name=self.sku),
                access_policies=access_policies,
                vault_uri=None,
                enabled_for_deployment=self.enabled_for_deployment,
                enabled_for_disk_encryption=self.enabled_for_disk_encryption,
                enabled_for_template_deployment=self.enabled_for_template_deployment,
                enable_soft_delete=self.enable_soft_delete,
                enable_purge_protection=None,
            )
            parameters = VaultCreateOrUpdateParameters(
                location=self.location, properties=properties
            )
            self.client = self.create_mgmt_client(KeyVaultManagementClient)

            # ARM may return not found at first even though the resource group has been created
            retries = 4
            for i in range(retries):
                try:
                    vault = self.client.vaults.begin_create_or_update(
                        group, name, parameters
                    ).result()
                    break
                except Exception as ex:
                    if "VaultAlreadyExists" in str(ex):
                        raise NameInUseError(name)
                    if "ReservedResourceName" in str(ex):
                        raise ReservedResourceNameError(name)
                    if "ResourceGroupNotFound" not in str(ex) or i == retries - 1:
                        raise
                    time.sleep(3)
            self.test_class_instance.scrubber.register_name_pair(
                name, self.resource_moniker
            )
            vault_uri = vault.properties.vault_uri
        else:
            # playback => we need only the uri used in the recording
            vault_uri = "https://{}.vault.azure.net/".format(name)
        return {self.parameter_name: vault_uri}

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            group = self._get_resource_group(**kwargs).name
            self.client.vaults.delete(group, name)
            if self.enable_soft_delete:
                self.client.vaults.purge_deleted(name, self.location).wait()

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs[self.resource_group_parameter_name]
        except KeyError:
            template = (
                "To create a key vault a resource group is required. Please add "
                "decorator @{} in front of this storage account preparer."
            )
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__))
