from collections import namedtuple

from azure_devtools.scenario_tests import AzureTestError

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
                 client_kwargs=None):
        super(ResourceGroupPreparer, self).__init__(name_prefix, random_name_length,
                                                    disable_recording=disable_recording,
                                                    playback_fake_resource=playback_fake_resource,
                                                    client_kwargs=client_kwargs)
        self.location = location
        self.parameter_name = parameter_name
        self.parameter_name_for_location = parameter_name_for_location

    def create_resource(self, name, **kwargs):
        if self.is_live:
            self.client = self.create_mgmt_client(ResourceManagementClient)
            self.resource = self.client.resource_groups.create_or_update(
                name, {'location': self.location}
            )
        else:
            self.resource = self.resource or FakeResource(
                name=name,
                id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/"+name
            )
        return {
            self.parameter_name: self.resource,
            self.parameter_name_for_location: self.location,
        }

    def remove_resource(self, name, **kwargs):
        if self.is_live:
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
