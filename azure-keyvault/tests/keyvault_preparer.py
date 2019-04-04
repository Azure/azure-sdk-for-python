from collections import namedtuple
import io
import os
import requests
import time

from azure.keyvault import VaultClient
from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.mgmt.keyvault.models import SecretPermissions, KeyPermissions, CertificatePermissions, StoragePermissions, \
    Permissions, Sku, SkuName, AccessPolicyEntry, VaultProperties, VaultCreateOrUpdateParameters, Vault
from azure_devtools.scenario_tests.preparers import (
    AbstractPreparer,
    SingleValueReplacer,
)
from azure_devtools.scenario_tests.exceptions import AzureTestError

from devtools_testutils import AzureMgmtPreparer, ResourceGroupPreparer, FakeResource
from devtools_testutils.resource_testcase import RESOURCE_GROUP_PARAM

FakeAccount = namedtuple(
    'FakeResource',
    ['name', 'account_endpoint']
)

DEFAULT_PERMISSIONS = Permissions(keys=[perm.value for perm in KeyPermissions],
                                  secrets=[perm.value for perm in SecretPermissions],
                                  certificates=[perm.value for perm in CertificatePermissions],
                                  storage=[perm.value for perm in StoragePermissions])
DEFAULT_SKU = SkuName.premium.value

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
                 parameter_name='vault_client',
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

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs[self.resource_group_parameter_name]
        except KeyError:
            template = 'To create a key vault a resource group is required. Please add ' \
                       'decorator @{} in front of this storage account preparer.'
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__))


    def create_resource(self, name, **kwargs):
        if self.is_live:
            # create a vault with the management client
            group = self._get_resource_group(**kwargs).name
            access_policies = [
                AccessPolicyEntry(tenant_id=self.test_class_instance.settings.TENANT_ID,
                                  object_id=self.test_class_instance.settings.CLIENT_OID,
                                  permissions=self.permissions)
            ]
            properties = VaultProperties(tenant_id=self.test_class_instance.settings.TENANT_ID,
                                        sku=Sku(name=self.sku),
                                        access_policies=access_policies,
                                        vault_uri=None,
                                        enabled_for_deployment=self.enabled_for_deployment,
                                        enabled_for_disk_encryption=self.enabled_for_disk_encryption,
                                        enabled_for_template_deployment=self.enabled_for_template_deployment,
                                        enable_soft_delete=self.enable_soft_delete,
                                        enable_purge_protection=None)
            parameters = VaultCreateOrUpdateParameters(location=self.location, properties=properties)
            self.management_client = self.create_mgmt_client(KeyVaultManagementClient)
            vault = self.management_client.vaults.create_or_update(group, name, parameters).result()
            vault_uri = vault.properties.vault_uri
        else:
            # playback => we need only the uri used in the recording
            vault_uri = 'https://{}.vault.azure.net/'.format(name)

        credentials = self.test_class_instance.settings.get_credentials()
        client = VaultClient(vault_uri, credentials)

        return { self.parameter_name: client }

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            group = self._get_resource_group(**kwargs).name
            self.management_client.vaults.delete(group, name)
            if self.enable_soft_delete:
                self.management_client.vaults.purge_deleted(name, self.location).wait()
