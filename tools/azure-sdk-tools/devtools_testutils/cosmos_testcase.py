# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from collections import namedtuple
import os

from azure.mgmt.cosmosdb import CosmosDBManagementClient
from azure.mgmt.storage.models import StorageAccount, Endpoints

from azure_devtools.scenario_tests.preparers import (
    AbstractPreparer,
    SingleValueReplacer,
)
from azure_devtools.scenario_tests.exceptions import AzureTestError

from . import AzureMgmtPreparer, ResourceGroupPreparer, FakeResource
from .resource_testcase import RESOURCE_GROUP_PARAM


FakeStorageAccount = FakeResource

# Cosmos Account Preparer and its shorthand decorator

class CosmosAccountPreparer(AzureMgmtPreparer):
    def __init(
        self,
        name_prefix='',
        sku='Standard_LRS',
        location='westus',
        kind='StorageV2',
        parameter_name='storage_account',
        resource_group_parameter_name=RESOURCE_GROUP_PARAM,
        disable_recording=True,
        playback_fake_resource=None,
        client_kwargs=None,
        random_name_enabled=False
    ):
        super(CosmosAccountPreparer, self).__init__(
            name_prefix,
            24,
            disable_recording=disable_recording,
            playback_fake_resource=playback_fake_resource,
            client_kwargs=client_kwargs,
            random_name_enabled=random_name_enabled
        )
        self.location = location
        self.sku = sku
        self.kind = kind
        self.resource_group_parameter_name = resource_group_parameter_name
        self.parameter_name = parameter_name
        self.storage_key = ''
        self.resource_moniker = self.name_prefix
        if random_name_enabled:
            self.resource_moniker += "cosmosname"

    def create_resource(self, name, **kwargs):
        if self.is_live:
            self.client = self.create_mgmt_client(CosmosManagementClient)
            group = self._get_resource_group(**kwargs)
            cosmos_async_operation = self.client.database_accounts.create_or_update(
                group.name,
                name,
                {
                    'sku': {'name': self.sku},
                    'locations': [{
                        self.location,
                    }],
                    # 'kind': self.kind,
                    # 'enable_https_traffic_only': True,
                }
            )
            self.resource = cosmos_async_operation.result()
            storage_keys = {
                v.key_name: v.value
                for v in self.client.storage_accounts.list_keys(group.name, name).keys
            }
            self.storage_key = storage_keys['key1']

            self.test_class_instance.scrubber.register_name_pair(
                name,
                self.resource_moniker
            )
        else:
            self.resource = StorageAccount(
                location=self.location,
            )
            self.resource.name = name
            self.resource.id = name
        return {
            self.parameter_name: self.resource,
            '{}_key'.format(self.parameter_name): self.storage_key,
            '{}_cs'.format(self.parameter_name): ";".join([
                "DefaultEndpointsProtocol=https",
                "AccountName={}".format(name),
                "AccountKey={}".format(self.storage_key),
            ])
        }

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            group = self._get_resource_group(**kwargs)
            self.client.storage_accounts.delete(group.name, name, polling=False)

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create a storage account a resource group is required. Please add ' \
                       'decorator @{} in front of this storage account preparer.'
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__))
