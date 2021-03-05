# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from collections import namedtuple
import functools
import os
import uuid

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
                    location='westcentralus',
                    parameter_name='digitaltwin',
                    role_assignment_name='Azure Digital Twins Data Owner',
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
        self.role_name = role_assignment_name
        if random_name_enabled:
            self.resource_moniker += "digitaltwinsname"
        self.set_cache(use_cache, None, location)

    def create_resource(self, name, **kwargs):
        if self.is_live:
            if os.environ.get('AZURE_DIGITAL_TWINS_HOSTNAME'):
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
                self._add_role_assignment(group)
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
    
    def _add_role_assignment(self, resource_group):
        from azure.mgmt.authorization import AuthorizationManagementClient
        role_client = self.create_mgmt_client(AuthorizationManagementClient)
        sp_id = os.environ.get('AZURE_CLIENT_ID')
        if not sp_id:
            raise ValueError("Cannot assign role to DigitalTwins with AZURE_CLIENT_ID.")

        roles = list(role_client.role_definitions.list(
            resource_group.id,
            filter="roleName eq '{}'".format(self.role_name)
        ))
        assert len(roles) == 1
        dt_role = roles[0]

        role_client.role_assignments.create(
            self.id,
            uuid.uuid4(), # Role assignment random name
            {
                'role_definition_id': dt_role.id,
                'principal_id': sp_id
            }
        )


CachedDigitalTwinsRGPreparer = functools.partial(DigitalTwinsRGPreparer, use_cache=True)
CachedDigitalTwinsPreparer = functools.partial(DigitalTwinsPreparer, use_cache=True)
