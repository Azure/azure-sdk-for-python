from collections import namedtuple
import os

import azure.mgmt.keyvault
import azure.mgmt.batch

from azure_devtools.scenario_tests.preparers import (
    AbstractPreparer,
    SingleValueReplacer,
)
from azure_devtools.scenario_tests.exceptions import AzureTestError

from devtools_testutils import AzureMgmtPreparer, ResourceGroupPreparer, FakeResource
from devtools_testutils.resource_testcase import RESOURCE_GROUP_PARAM


class KeyVaultPreparer(AzureMgmtPreparer):
    def __init__(self,
                 name_prefix='batch',
                 location='westus',
                 parameter_name='keyvault',
                 resource_group_parameter_name=RESOURCE_GROUP_PARAM,
                 disable_recording=True, playback_fake_resource=None,
                 client_kwargs=None):
        super(KeyVaultPreparer, self).__init__(name_prefix, 24,
                                               disable_recording=disable_recording,
                                               playback_fake_resource=playback_fake_resource,
                                               client_kwargs=client_kwargs,
                                               random_name_enabled=True)
        self.location = location
        self.resource_group_parameter_name = resource_group_parameter_name
        self.parameter_name = parameter_name
        self.parameter_name_for_location='location'

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create a keyvault a resource group is required. Please add ' \
                       'decorator @{} in front of this storage account preparer.'
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__))

    def create_resource(self, name, **kwargs):
        name = name.replace('_', '-')
        #raise Exception(name)
        if self.is_live:
            TENANT_ID = os.environ.get("AZURE_TENANT_ID", None)
            CLIENT_OID = os.environ.get("CLIENT_OID", None)
            self.client = self.create_mgmt_client(
                azure.mgmt.keyvault.KeyVaultManagementClient)
            group = self._get_resource_group(**kwargs)
            self.resource = self.client.vaults.begin_create_or_update(
                group.name,
                name,
                {
                    'location': self.location,
                    'properties': {
                        'sku': {
                            'name': 'standard',
                            'family': 'A'
                        },
                        # 'tenant_id': "72f988bf-86f1-41af-91ab-2d7cd011db47",
                        'tenant_id': TENANT_ID,
                        'enabled_for_deployment': True,
                        'enabled_for_disk_encryption': True,
                        'enabled_for_template_deployment': True,
                        'access_policies': [ {
                            # 'tenant_id': "72f988bf-86f1-41af-91ab-2d7cd011db47",
                            'tenant_id': TENANT_ID,
                            # 'object_id': "f520d84c-3fd3-4cc8-88d4-2ed25b00d27a",
                            'object_id': CLIENT_OID,
                            'permissions': {
                                'keys': ['all'],
                                'secrets': ['all']
                            }
                        }]
                    }
                }
            )
        else:
            self.resource = FakeResource(name=name, id=name)
        return {
            self.parameter_name: self.resource,
        }

    def remove_resource(self, name, **kwargs):
        name = name.replace('_', '-')
        if self.is_live:
            group = self._get_resource_group(**kwargs)
            self.client.vaults.delete(group.name, name)


class SimpleBatchPreparer(AzureMgmtPreparer):
    def __init__(self,
                 name_prefix='batch11',
                 location='westus',
                 parameter_name='batch_account',
                 resource_group_parameter_name=RESOURCE_GROUP_PARAM,
                 disable_recording=True, playback_fake_resource=None,
                 client_kwargs=None):
        super(SimpleBatchPreparer, self).__init__(name_prefix, 24,
                                                  disable_recording=disable_recording,
                                                  playback_fake_resource=playback_fake_resource,
                                                  client_kwargs=client_kwargs)
        self.location = location
        self.resource_group_parameter_name = resource_group_parameter_name
        self.parameter_name = parameter_name
        self.parameter_name_for_location='location'

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create a batch account a resource group is required. Please add ' \
                       'decorator @{} in front of this storage account preparer.'
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__))

    def create_resource(self, name, **kwargs):
        if self.is_live:
            self.client = self.create_mgmt_client(
                azure.mgmt.batch.BatchManagementClient)
            group = self._get_resource_group(**kwargs)
            batch_account = azure.mgmt.batch.models.BatchAccountCreateParameters(
                location=self.location,
            )
            account_setup = self.client.batch_account.begin_create(
                group.name,
                name,
                batch_account)
            self.resource = account_setup.result()
        else:
            self.resource = FakeResource(name=name, id=name)
        return {
            self.parameter_name: self.resource,
        }

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            group = self._get_resource_group(**kwargs)
            deleting = self.client.batch_account.begin_delete(group.name, name)
            try:
                deleting.wait()
            except:
                pass
