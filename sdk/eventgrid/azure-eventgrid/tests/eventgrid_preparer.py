import functools
from devtools_testutils import PowerShellPreparer

from azure.mgmt.eventgrid.models import Topic, InputSchema, JsonInputSchemaMapping, JsonField, JsonFieldWithDefault
from azure_devtools.scenario_tests.exceptions import AzureTestError

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

EventGridPreparer = functools.partial(
    PowerShellPreparer, "eventgrid",
    eventgrid_topic_endpoint="https://fakeresource.westus2-1.eventgrid.azure.net/api/events",
    eventgrid_topic_key="fakekeyfakekeyfakekeyfakekeyfakekeyfakekeyA=",
    eventgrid_domain_endpoint="https://fakeresource.westus2-1.eventgrid.azure.net/api/events",
    eventgrid_domain_key="fakekeyfakekeyfakekeyfakekeyfakekeyfakekeyA=",
    eventgrid_cloud_event_topic_endpoint="https://fakeresource.westus2-1.eventgrid.azure.net/api/events",
    eventgrid_cloud_event_topic_key="fakekeyfakekeyfakekeyfakekeyfakekeyfakekeyA=",
    eventgrid_cloud_event_domain_endpoint="https://fakeresource.westus2-1.eventgrid.azure.net/api/events",
    eventgrid_cloud_event_domain_key="fakekeyfakekeyfakekeyfakekeyfakekeyfakekeyA=",
    eventgrid_custom_event_topic_endpoint="https://fakeresource.westus2-1.eventgrid.azure.net/api/events",
    eventgrid_custom_event_topic_key="fakekeyfakekeyfakekeyfakekeyfakekeyfakekeyA=",
)
