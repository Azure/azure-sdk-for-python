from collections import namedtuple

from azure.mgmt.servicebus import ServiceBusManagementClient

from azure_devtools.scenario_tests.exceptions import AzureTestError

from devtools_testutils import (
    ResourceGroupPreparer, AzureMgmtPreparer, FakeResource
)

from devtools_testutils.resource_testcase import RESOURCE_GROUP_PARAM

# Service Bus Preparer and its shorthand decorator

class ServiceBusNamespacePreparer(AzureMgmtPreparer):
    def __init__(self,
                 name_prefix='',
                 sku='Standard', location='westus',
                 parameter_name='servicebus_namespace',
                 resource_group_parameter_name=RESOURCE_GROUP_PARAM,
                 disable_recording=True, playback_fake_resource=None,
                 client_kwargs=None):
        super(ServiceBusNamespacePreparer, self).__init__(name_prefix, 24,
                                                     disable_recording=disable_recording,
                                                     playback_fake_resource=playback_fake_resource,
                                                     client_kwargs=client_kwargs)
        self.location = location
        self.sku = sku
        self.resource_group_parameter_name = resource_group_parameter_name
        self.parameter_name = parameter_name
        self.service_bus_key = ''

    def create_resource(self, name, **kwargs):
        if self.is_live:
            self.client = self.create_mgmt_client(ServiceBusManagementClient)
            group = self._get_resource_group(**kwargs)
            namespace_async_operation = self.client.namespaces.create_or_update(
                group.name,
                name,
                {
                    'sku': {'name': self.sku},
                    'location': self.location,
                }
            )
            self.resource = namespace_async_operation.result()
            namespace_keys = {
                v.key_name: v.value
                for v in self.client.namespaces.list_keys(group.name, name).keys
            }
            print(namespace_keys)
            self.service_bus_key = namespace_keys['key1']
        else:
            self.resource = FakeResource(name=name, id=name)
            self.service_bus_key = 'ZmFrZV9hY29jdW50X2tleQ=='
        return {
            self.parameter_name: self.resource,
            '{}_key'.format(self.parameter_name): self.service_bus_key,
        }

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            group = self._get_resource_group(**kwargs)
            self.client.namespaces.delete(group.name, name, polling=False)

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create a service bus a resource group is required. Please add ' \
                       'decorator @{} in front of this service bus preparer.'
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__))
