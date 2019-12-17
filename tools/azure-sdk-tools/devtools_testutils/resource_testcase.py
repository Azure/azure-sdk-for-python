from collections import namedtuple
import os

from azure_devtools.scenario_tests import AzureTestError, ReservedResourceNameError

from azure.common.exceptions import CloudError
from azure.mgmt.resource import ResourceManagementClient

from . import AzureMgmtPreparer


RESOURCE_GROUP_PARAM = 'resource_group'


FakeResource = namedtuple(
    'FakeResource',
    ['name', 'id']
)


class ResourceGroupPreparer(AzureMgmtPreparer):
    def __init__(self, name_prefix='',
                 random_name_length=75,
                 parameter_name=RESOURCE_GROUP_PARAM,
                 parameter_name_for_location='location', location='westus',
                 disable_recording=True, playback_fake_resource=None,
                 client_kwargs=None,
                 random_name_enabled=False):
        super(ResourceGroupPreparer, self).__init__(name_prefix, random_name_length,
                                                    disable_recording=disable_recording,
                                                    playback_fake_resource=playback_fake_resource,
                                                    client_kwargs=client_kwargs,
                                                    random_name_enabled=random_name_enabled)
        self.location = location
        self.parameter_name = parameter_name
        self.parameter_name_for_location = parameter_name_for_location
        env_value = os.environ.get("AZURE_RESOURCEGROUP_NAME", None)
        self._need_creation = True
        if env_value:
            self.resource_random_name = env_value
            self._need_creation = False
        if self.random_name_enabled:
            self.resource_moniker = self.name_prefix + "rgname"

    def create_resource(self, name, **kwargs):
        if self.is_live and self._need_creation:
            self.client = self.create_mgmt_client(ResourceManagementClient)
            try:
                self.resource = self.client.resource_groups.create_or_update(
                    name, {'location': self.location}
                )
            except Exception as ex:
                if "ReservedResourceName" in str(ex):
                    raise ReservedResourceNameError(name)
                raise
        else:
            self.resource = self.resource or FakeResource(
                name=name,
                id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/"+name
            )
        if name != self.moniker:
            self.test_class_instance.scrubber.register_name_pair(
                name,
                self.moniker
            )
        return {
            self.parameter_name: self.resource,
            self.parameter_name_for_location: self.location,
        }

    def remove_resource(self, name, **kwargs):
        if self.is_live and self._need_creation:
            try:
                if 'wait_timeout' in kwargs:
                    azure_poller = self.client.resource_groups.delete(name)
                    azure_poller.wait(kwargs.get('wait_timeout'))
                    if azure_poller.done():
                        return
                    raise AzureTestError('Timed out waiting for resource group to be deleted.')
                else:
                    self.client.resource_groups.delete(name, polling=False)
            except CloudError:
                pass
