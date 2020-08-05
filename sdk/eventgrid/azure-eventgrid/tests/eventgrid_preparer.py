import functools
import hashlib
import os
from collections import namedtuple

from azure.mgmt.eventgrid import EventGridManagementClient
from azure.mgmt.eventgrid.models import Topic, InputSchema
from azure_devtools.scenario_tests.exceptions import AzureTestError

from devtools_testutils import (
    ResourceGroupPreparer, AzureMgmtPreparer, FakeResource
)

from devtools_testutils.resource_testcase import RESOURCE_GROUP_PARAM

EVENTGRID_TOPIC_PARAM = 'eventgrid_topic'
EVENTGRID_TOPIC_LOCATION = 'westus'
CLOUD_EVENT_SCHEMA = InputSchema.cloud_event_schema_v1_0

# Shared base class for event grid sub-resources that require a RG to exist.
class _EventGridChildResourcePreparer(AzureMgmtPreparer):
    def __init__(self,
                 name_prefix='',
                 resource_group_parameter_name=RESOURCE_GROUP_PARAM,
                 disable_recording=True, playback_fake_resource=None,
                 client_kwargs=None, random_name_enabled=True):
        super(_EventGridChildResourcePreparer, self).__init__(name_prefix, 24,
                                                               random_name_enabled=random_name_enabled,
                                                               disable_recording=disable_recording,
                                                               playback_fake_resource=playback_fake_resource,
                                                               client_kwargs=client_kwargs)
        self.resource_group_parameter_name = resource_group_parameter_name

class EventGridTopicPreparer(_EventGridChildResourcePreparer):
    def __init__(self,
                 name_prefix='',
                 use_cache=False,
                 parameter_name=EVENTGRID_TOPIC_PARAM,
                 parameter_location=EVENTGRID_TOPIC_LOCATION,
                 resource_group_parameter_name=RESOURCE_GROUP_PARAM,
                 disable_recording=True, playback_fake_resource=None,
                 client_kwargs=None, random_name_enabled=True):
        super(EventGridTopicPreparer, self).__init__(name_prefix,
                                                     random_name_enabled=random_name_enabled,
                                                     resource_group_parameter_name=resource_group_parameter_name,
                                                     disable_recording=disable_recording,
                                                     playback_fake_resource=playback_fake_resource,
                                                     client_kwargs=client_kwargs)
        self.parameter_name = parameter_name
        self.parameter_location = parameter_location
        self.name_prefix = name_prefix
        if random_name_enabled:
            self.resource_moniker = self.name_prefix + "egtopic"

    def create_resource(self, name, **kwargs):
        if self.is_live:
            self.client = self.create_mgmt_client(EventGridManagementClient)
            group = self._get_resource_group(**kwargs)

            if self.name_prefix[:5] == "cloud":
                # Create a new topic and verify that it is created successfully
                topic = Topic(location=self.parameter_location, tags=None, input_schema=CLOUD_EVENT_SCHEMA, input_schema_mapping=None)
            else:
                topic = Topic(location=self.parameter_location)
            topic_operation = self.client.topics.create_or_update(
                group.name,
                name,
                topic,
                {}
            )
            self.resource = topic_operation.result()
            key = self.client.topics.list_shared_access_keys(group.name, name)
            self.primary_key = key.key1
        else:
            self.resource = FakeResource(name=name, id=name, location=location)
            self.primary_access_key = "ZmFrZV9hY29jdW50X2tleQ=="    # test key copied from sb_preparer
        return {
            self.parameter_name: self.resource,
            '{}_primary_key'.format(self.parameter_name): self.primary_key,
        }

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            group = self._get_resource_group(**kwargs)
            self.client.topics.delete(group.name, name, polling=False)
    
    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create this service bus child resource service bus a resource group is required. Please add ' \
                       'decorator @{} in front of this service bus preparer.'
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__))
