from collections import namedtuple
import io
import os
import requests
import time

from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.mgmt.keyvault.models import SecretPermissions, KeyPermissions, CertificatePermissions, StoragePermissions, \
    Permissions, Sku, SkuName, AccessPolicyEntry, VaultProperties, VaultCreateOrUpdateParameters

from devtools_testutils import AzureMgmtPreparer, AzureTestError, ResourceGroupPreparer
from devtools_testutils.resource_testcase import RESOURCE_GROUP_PARAM

VAULT_PARAM = 'vault'
FakeVault = namedtuple(
    'FakeVault',
    ['name', 'location', 'properties']
)

DEFAULT_PERMISSIONS = Permissions(keys=[perm.value for perm in KeyPermissions],
                                  secrets=[perm.value for perm in SecretPermissions],
                                  certificates=[perm.value for perm in CertificatePermissions],
                                  storage=[perm.value for perm in StoragePermissions])
DEFAULT_SKU = SkuName.premium.value
CLIENT_OID = '00000000-0000-0000-0000-000000000000'


class KeyVaultPreparer(AzureMgmtPreparer):
    def __init__(self,
                 sku=None,
                 permissions=None,
                 enabled_for_deployment=True,
                 enabled_for_disk_encryption=True,
                 enabled_for_template_deployment=True,
                 enable_soft_delete=None,
                 name_prefix='vault',
                 location='westus',
                 parameter_name=VAULT_PARAM,
                 resource_group_parameter_name=RESOURCE_GROUP_PARAM,
                 disable_recording=True,
                 playback_fake_resource=None,
                 client_kwargs=None):
        super(KeyVaultPreparer, self).__init__(name_prefix, 24,
                                               disable_recording=disable_recording,
                                               playback_fake_resource=playback_fake_resource,
                                               client_kwargs=client_kwargs)
        self.sku = sku or DEFAULT_SKU
        self.permissions = permissions or DEFAULT_PERMISSIONS
        self.enabled_for_deployment = enabled_for_deployment
        self.enabled_for_disk_encryption = enabled_for_disk_encryption
        self.enabled_for_template_deployment = enabled_for_template_deployment
        self.enable_soft_delete = enable_soft_delete
        self.location = location
        self.resource_group_parameter_name = resource_group_parameter_name
        self.parameter_name = parameter_name
        self.creds_parameter = 'credentials'
        self.parameter_name_for_location = 'location'
        self.client_oid = None

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs[self.resource_group_parameter_name]
        except KeyError:
            template = 'To create a key vault a resource group is required. Please add ' \
                       'decorator @{} in front of this storage account preparer.'
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__))


    def create_resource(self, name, **kwargs):
        self.client_oid = self.test_class_instance.set_value_to_scrub('CLIENT_OID', CLIENT_OID)
        group = self._get_resource_group(**kwargs).name

        access_policies = [AccessPolicyEntry(tenant_id=self.test_class_instance.settings.TENANT_ID,
                                             object_id=self.client_oid,
                                             permissions=self.permissions)]
        properties = VaultProperties(tenant_id=self.test_class_instance.settings.TENANT_ID,
                                     sku=Sku(name=self.sku),
                                     access_policies=access_policies,
                                     vault_uri=None,
                                     enabled_for_deployment=self.enabled_for_deployment,
                                     enabled_for_disk_encryption=self.enabled_for_disk_encryption,
                                     enabled_for_template_deployment=self.enabled_for_template_deployment,
                                     enable_soft_delete=self.enable_soft_delete,
                                     enable_purge_protection=None)

        if self.is_live:
            self.client = self.create_mgmt_client(KeyVaultManagementClient)
            parameters = VaultCreateOrUpdateParameters(location=self.location,
                                                       properties=properties)
            self.resource = self.client.vaults.create_or_update(group, name, parameters).result()
        else:
            properties.vault_uri = 'https://{}.vault.azure.net/'.format(name)
            self.resource = FakeVault(name=name, location=self.location, properties=properties)
        return {
            self.parameter_name: self.resource
        }

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            group = self._get_resource_group(**kwargs).name
            self.client.vaults.delete(group, name)
            if self.enable_soft_delete:
                self.client.vaults.purge_deleted(name, self.location).wait()
