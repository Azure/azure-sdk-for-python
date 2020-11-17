# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from collections import namedtuple
import functools
import os
import datetime
import time
from functools import partial

from devtools_testutils import AzureMgmtPreparer
from azure_devtools.scenario_tests.exceptions import AzureTestError
from devtools_testutils import ResourceGroupPreparer


FakeResource = namedtuple(
    'FakeResource',
    ['name', 'id', 'host_name']
)

class DigitalTwinsRGPreparer(ResourceGroupPreparer):

    def create_resource(self, name, **kwargs):
        if self.is_live and 'AZURE_DIGITAL_TWINS_HOSTNAME' in os.environ:
            self.resource = self.resource or FakeResource(
                name=name,
                id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/"+name,
                host_name=None
            )
            return {
                self.parameter_name: self.resource,
                self.parameter_name_for_location: self.location,
            }
        return super(DigitalTwinsRGPreparer, self).create_resource(name, **kwargs)

    def remove_resource(self, name, **kwargs):
        if 'AZURE_DIGITAL_TWINS_HOSTNAME' not in os.environ:
            return super(DigitalTwinsRGPreparer, self).remove_resource(name, **kwargs)


class DigitalTwinsPreparer(AzureMgmtPreparer):
    def __init__(self, name_prefix='',
                    use_cache=False,
                    random_name_length=50,
                    location='westus',
                    parameter_name='digitaltwin',
                    resource_group_parameter_name='resource_group',
                    disable_recording=True,
                    playback_fake_resource=None,
                    client_kwargs=None,
                    random_name_enabled=True):
        super(DigitalTwinsPreparer, self).__init__(
            name_prefix,
            random_name_length,
            playback_fake_resource=playback_fake_resource,
            disable_recording=disable_recording,
            client_kwargs=client_kwargs,
            random_name_enabled=random_name_enabled
        )
        self.location = location
        self.resource_group_parameter_name = resource_group_parameter_name
        self.parameter_name = parameter_name
        self.resource_moniker = self.name_prefix
        self.use_cache = use_cache
        if random_name_enabled:
            self.resource_moniker += "digitaltwinsname"
        self.set_cache(use_cache, None, location)

    def create_resource(self, name, **kwargs):
        if self.is_live:
            if 'AZURE_DIGITAL_TWINS_HOSTNAME' in os.environ:
                host_name=os.environ['AZURE_DIGITAL_TWINS_HOSTNAME']
                name = host_name.split('.')[0]
                self.resource = FakeResource(name=name, id=name, host_name=host_name)
                self.test_class_instance.scrubber.register_name_pair(
                    name,
                    self.resource_moniker
                )
            else:
                # We have to import here due to a bug in the mgmt SDK
                from azure.mgmt.digitaltwins import AzureDigitalTwinsManagementClient
                self.client = self.create_mgmt_client(AzureDigitalTwinsManagementClient)
                group = self._get_resource_group(**kwargs)

                result = self.client.digital_twins.create_or_update(group.name, name, self.location)
                self.resource = result.result()
                self.id = self.resource.id
                self.test_class_instance.scrubber.register_name_pair(
                    name,
                    self.resource_moniker
                )
        else:
            self.resource = FakeResource(
                name=name,
                id=name,
                host_name= self.resource_moniker + ".api.wcus.digitaltwins.azure.net")

        return {self.parameter_name: self.resource}

    def remove_resource(self, name, **kwargs):
        if self.is_live and 'AZURE_DIGITAL_TWINS_HOSTNAME' not in os.environ:
            group = self._get_resource_group(**kwargs)
            self.client.digital_twins.delete(group.name, name, polling=False)

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create a Digital Twin, a resource group is required. Please add ' \
                       'decorator @{} in front of this preparer.'
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__))


CachedDigitalTwinsRGPreparer = functools.partial(DigitalTwinsRGPreparer, use_cache=True)
CachedDigitalTwinsPreparer = functools.partial(DigitalTwinsPreparer, use_cache=True)
