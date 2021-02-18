# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools

from azure.mgmt.cosmosdb import CosmosDBManagementClient
from azure.mgmt.storage.models import StorageAccount, Endpoints
from azure.mgmt.cosmosdb.models import (
    DatabaseAccountCreateUpdateParameters,
    Capability,
    CreateUpdateOptions
)

from azure_devtools.scenario_tests.exceptions import AzureTestError

from devtools_testutils import AzureMgmtPreparer, ResourceGroupPreparer, FakeResource

FakeCosmosAccount = FakeResource
RESOURCE_GROUP_PARAM = 'resource_group'

# Cosmos Account Preparer and its shorthand decorator

class CosmosAccountPreparer(AzureMgmtPreparer):
    def __init__(
        self,
        name_prefix='',
        sku='Standard_LRS',
        location='westus',
        kind='StorageV2',
        parameter_name='cosmos_account',
        resource_group_parameter_name=RESOURCE_GROUP_PARAM,
        disable_recording=True,
        playback_fake_resource=None,
        client_kwargs=None,
        random_name_enabled=True,
        use_cache=False
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
        self.cosmos_key = ''
        self.cosmos_account_name = ''
        self.primary_endpoint = ''
        self.resource_moniker = self.name_prefix
        self.set_cache(use_cache, sku, location, name_prefix)
        if random_name_enabled:
            self.resource_moniker += "cosmosname"

    def create_resource(self, name, **kwargs):
        if self.is_live:
            capabilities = Capability(name='EnableTable')
            db_params = DatabaseAccountCreateUpdateParameters(
                capabilities=[capabilities],
                locations=[{'location_name': self.location}],
                location=self.location,
            )

            self.client = self.create_mgmt_client(CosmosDBManagementClient)
            group = self._get_resource_group(**kwargs)
            cosmos_async_operation = self.client.database_accounts.begin_create_or_update(
                group.name,
                name,
                db_params
            )
            self.resource = cosmos_async_operation.result()

            cosmos_keys = self.client.database_accounts.list_keys(
                group.name,
                name
            )
            self.cosmos_key = cosmos_keys.primary_master_key
            self.cosmos_account_name = name

            self.test_class_instance.scrubber.register_name_pair(
                name,
                self.resource_moniker
            )
            self.primary_endpoint = 'https://{}.table.cosmos.azure.com:443/'.format(name)
        else:
            self.resource = StorageAccount(
                location=self.location
            )
            self.resource.name = name
            self.resource.id = name
            self.primary_endpoint = 'https://{}.table.cosmos.azure.com:443/'.format(name)
            self.cosmos_key = 'ZmFrZV9hY29jdW50X2tleQ=='
            self.cosmos_account_name = name
        return {
            self.parameter_name: self.resource,
            '{}_key'.format(self.parameter_name): self.cosmos_key,
            '{}_cs'.format(self.parameter_name): ";".join([
                "DefaultEndpointsProtocol=https",
                "AccountName={}".format(self.cosmos_account_name),
                "AccountKey={}".format(self.cosmos_key),
                "TableEndpoint={}".format(self.primary_endpoint)
            ])
        }

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            group = self._get_resource_group(**kwargs)
            self.client.database_accounts.delete(group.name, name, polling=False)

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create a cosmos instance a resource group is required. Please add ' \
                       'decorator @{} in front of this cosmos account preparer.'
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__))

CachedCosmosAccountPreparer = functools.partial(CosmosAccountPreparer, use_cache=True, random_name_enabled=True)