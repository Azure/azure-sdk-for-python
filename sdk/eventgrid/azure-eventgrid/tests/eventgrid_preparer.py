import functools
import hashlib
import os
from collections import namedtuple

from azure.mgmt.eventgrid import EventGridManagementClient
from azure.mgmt.eventgrid.models import Topic, InputSchema, JsonInputSchemaMapping, JsonField, JsonFieldWithDefault
from azure_devtools.scenario_tests.exceptions import AzureTestError

from devtools_testutils import (
    ResourceGroupPreparer, AzureMgmtPreparer, FakeResource
)

from devtools_testutils.resource_testcase import RESOURCE_GROUP_PARAM

EVENTGRID_TOPIC_PARAM = 'eventgrid_topic'
EVENTGRID_TOPIC_LOCATION = 'westus'
CLOUD_EVENT_SCHEMA = InputSchema.cloud_event_schema_v1_0
CUSTOM_EVENT_SCHEMA = InputSchema.custom_event_schema
ID_JSON_FIELD = JsonField(source_field='customId')
TOPIC_JSON_FIELD = JsonField(source_field='customTopic')
EVENT_TIME_JSON_FIELD = JsonField(source_field='customEventTime')
EVENT_TYPE_JSON_FIELD_WITH_DEFAULT = JsonFieldWithDefault(source_field='customEventType', default_value='')
SUBJECT_JSON_FIELD_WITH_DEFAULT = JsonFieldWithDefault(source_field='customSubject', default_value='')
DATA_VERSION_JSON_FIELD_WITH_DEFAULT = JsonFieldWithDefault(source_field='customDataVersion', default_value='')
CUSTOM_JSON_INPUT_SCHEMA_MAPPING = JsonInputSchemaMapping(id=ID_JSON_FIELD, topic=TOPIC_JSON_FIELD, event_time=EVENT_TIME_JSON_FIELD, event_type=EVENT_TYPE_JSON_FIELD_WITH_DEFAULT, subject=SUBJECT_JSON_FIELD_WITH_DEFAULT, data_version=DATA_VERSION_JSON_FIELD_WITH_DEFAULT)


class EventGridTopicPreparer(AzureMgmtPreparer):
    def __init__(self,
                 name_prefix='',
                 use_cache=False,
                 parameter_location=EVENTGRID_TOPIC_LOCATION,
                 parameter_name=EVENTGRID_TOPIC_PARAM,
                 resource_group_parameter_name=RESOURCE_GROUP_PARAM,
                 disable_recording=True, playback_fake_resource=None,
                 client_kwargs=None, random_name_enabled=True):
        super(EventGridTopicPreparer, self).__init__(name_prefix, random_name_length=24,
                                                     random_name_enabled=random_name_enabled,
                                                     disable_recording=disable_recording,
                                                     playback_fake_resource=playback_fake_resource,
                                                     client_kwargs=client_kwargs)
        self.resource_group_parameter_name = resource_group_parameter_name
        self.parameter_name = parameter_name
        self.parameter_location = parameter_location
        self.name_prefix = name_prefix
        if random_name_enabled:
            self.resource_moniker = self.name_prefix + "egtopic"
        
        self.set_cache(use_cache, name_prefix)

    def create_resource(self, name, **kwargs):
        if self.is_live:
            self.client = self.create_mgmt_client(EventGridManagementClient)
            group = self._get_resource_group(**kwargs)

            if self.name_prefix.startswith("cloud"):
                # Create a new topic and verify that it is created successfully
                topic = Topic(location=self.parameter_location, tags=None, input_schema=CLOUD_EVENT_SCHEMA, input_schema_mapping=None)
            elif self.name_prefix.startswith("custom"):
                # Create a new topic and verify that it is created successfully
                topic = Topic(location=self.parameter_location, tags=None, input_schema=CUSTOM_EVENT_SCHEMA, input_schema_mapping=CUSTOM_JSON_INPUT_SCHEMA_MAPPING)
            else:
                topic = Topic(location=self.parameter_location)
            topic_operation = self.client.topics.begin_create_or_update(
                group.name,
                name,
                topic,
            )
            self.resource = topic_operation.result()
            key = self.client.topics.list_shared_access_keys(group.name, name)
            self.primary_key = key.key1
            self.endpoint = self.resource.endpoint
        else:
            self.resource = FakeResource(name=name, id=name)
            self.primary_key = "ZmFrZV9hY29jdW50X2tleQ=="    # test key copied from sb_preparer
            self.endpoint = "https://{}.westus-1.eventgrid.azure.net/api/events".format(name)
        return {
            self.parameter_name: self.resource,
            '{}_primary_key'.format(self.parameter_name): self.primary_key,
            '{}_endpoint'.format(self.parameter_name): self.endpoint,
        }

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            group = self._get_resource_group(**kwargs)
            self.client.topics.begin_delete(group.name, name, polling=False)

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create this event grid topic resource, a resource group is required. Please add ' \
                       'decorator @{} in front of this event grid topic preparer.'
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__))

CachedEventGridTopicPreparer = functools.partial(EventGridTopicPreparer, use_cache=True)
