# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint:disable=protected-access
import datetime
from copy import deepcopy
from typing import Optional
from dateutil.tz import tzutc
import datetime as dt

#from msrest.serialization import Model

from azure.eventgrid._generated.event_grid_publisher_client.models._models import EventGridEvent as InternalEventGridEvent, \
    CloudEvent as InternalCloudEvent


class CloudEvent(InternalCloudEvent):   #pylint:disable=too-many-instance-attributes
    """Properties of an event published to an Event Grid topic using the CloudEvent 1.0 Schema.

    All required parameters must be populated in order to send to Azure.

    :param id: Required. An identifier for the event. The combination of id and source must be
     unique for each distinct event.
    :type id: str
    :param source: Required. Identifies the context in which an event happened. The combination of
     id and source must be unique for each distinct event.
    :type source: str
    :param data: Event data specific to the event type.
    :type data: object
    :param type: Required. Type of event related to the originating occurrence.
    :type type: str
    :param time: The time (in UTC) the event was generated, in RFC3339 format.
    :type time: ~datetime.datetime
    :param specversion: Required. The version of the CloudEvents specification which the event
     uses.
    :type specversion: str
    :param dataschema: Identifies the schema that data adheres to.
    :type dataschema: str
    :param datacontenttype: Content type of data value.
    :type datacontenttype: str
    :param subject: This describes the subject of the event in the context of the event producer
     (identified by source).
    :type subject: str
    """

    def __init__(
        self,
        **kwargs
    ):
        self.id = kwargs['id']
        self.source = kwargs['source']
        self.data = kwargs.get('data', None)
        self.type = kwargs['type']
        self.time = kwargs.get('time', dt.datetime.now(tzutc()).isoformat())
        self.specversion = kwargs['specversion']
        self.dataschema = kwargs.get('dataschema', None)
        self.datacontenttype = kwargs.get('datacontenttype', None)
        self.subject = kwargs.get('subject', None)

    #@classmethod
    #def from_dict(cls, source):
    #    """
    #    Returns an array of CloudEvent objects given a dict of events following the CloudEvent schema.

    #    :param source: Required. The dict object following the CloudEvent schema.
    #    :type source: dict

    #    :rtype: List[~azure.eventgrid.CloudEvent]
    #    """
    #    events = []
    #    i = 1
    #    for event in source:
    #        try:
    #            events.append(CloudEvent(**event))
    #        except Exception as e:
    #            print("CloudEvent {} in file is incorrectly formatted with error: {}.".format(i, e))

    #    return events

class EventGridEvent(InternalEventGridEvent):
    """Properties of an event published to an Event Grid topic using the EventGrid Schema.

    Variables are only populated by the server, and will be ignored when sending a request.

    All required parameters must be populated in order to send to Azure.

    :param id: Required. An unique identifier for the event.
    :type id: str
    :param topic: The resource path of the event source.
    :type topic: str
    :param subject: Required. A resource path relative to the topic path.
    :type subject: str
    :param data: Required. Event data specific to the event type.
    :type data: object
    :param event_type: Required. The type of the event that occurred.
    :type event_type: str
    :param event_time: Required. The time (in UTC) the event was generated.
    :type event_time: ~datetime.datetime
    :ivar metadata_version: The schema version of the event metadata.
    :vartype metadata_version: str
    :param data_version: Required. The schema version of the data object.
    :type data_version: str
    """

    _validation = {
        'id': {'required': True},
        'subject': {'required': True},
        'data': {'required': True},
        'event_type': {'required': True},
        'event_time': {'required': True},
        'metadata_version': {'readonly': True},
        'data_version': {'required': True},
    }

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'topic': {'key': 'topic', 'type': 'str'},
        'subject': {'key': 'subject', 'type': 'str'},
        'data': {'key': 'data', 'type': 'object'},
        'event_type': {'key': 'eventType', 'type': 'str'},
        'event_time': {'key': 'eventTime', 'type': 'iso-8601'},
        'metadata_version': {'key': 'metadataVersion', 'type': 'str'},
        'data_version': {'key': 'dataVersion', 'type': 'str'},
    }

    def __init__(
        self,
        **kwargs
    ):
        self.id = kwargs['id']
        self.topic = kwargs.get('topic', None)
        self.subject = kwargs['subject']
        self.data = kwargs['data']
        self.event_type = kwargs['event_type']
        self.event_time = kwargs.get('event_time', dt.datetime.now(tzutc()).isoformat())
        self.metadata_version = None
        self.data_version = kwargs['data_version']

    #@classmethod
    #def from_dict(cls, source):
    #    """
    #    Returns an array of EventGridEvent objects given a dict of events following the EventGridEvent schema.

    #    :param source: Required. The dict object following the EventGridEvent schema.
    #    :type source: dict

    #    :rtype: List[~azure.eventgrid.EventGridEvent]
    #    """
    #    events = []
    #    i = 1
    #    for event in source:
    #        try:
    #            events.append(EventGridEvent(**event))
    #        except Exception as e:
    #            print("EventGridEvent {} in file is incorrectly formatted with error: {}.".format(i, e))

    #    return events

class EventBatch:
    """A batch of events.

    Sending events in a batch is more performant than sending individual events.
    EventBatch helps you create the maximum allowed size batch of either `EventGridEvent` or `CloudEvent` to improve sending performance.

    Use the `add` method to add events until the maximum batch size limit in bytes has been reached -
    at which point a `ValueError` will be raised.
    Use the `publish_events` method of :class:`EventGridPublisherClient<azure.eventgrid.EventGridPublisherClient>`
    for sending.

    **Please use the create_batch method of EventGridPublisherClient
    to create an EventBatch object instead of instantiating an EventBatch object directly.**

    :param int max_size_in_bytes: The maximum size of bytes data that an EventDataBatch object can hold.
    """

    def __init__(self, max_size_in_bytes=None):
        # type: (Optional[int], Optional[str], Optional[Union[str, bytes]]) -> None
        return
        self._max_size_in_bytes = max_size_in_bytes #or constants.MAX_MESSAGE_LENGTH_BYTES
        self._event_list = []#BatchMessage(data=[], multi_messages=False, properties=None)

        self._size = 0#self.message.gather()[0].get_message_encoded_size()
        self._count = 0

    def __repr__(self):
        # type: () -> str
        batch_repr = "max_size_in_bytes={}, event_count={}".format(
            self._max_size_in_bytes, self._count
        )
        return "EventBatch({})".format(batch_repr)

    def __len__(self):
        return self._count

    def _load_events(self, events):
        for event_data in events:
            try:
                self.add(event_data)
            except ValueError:
                raise ValueError("The combined size of EventData collection exceeds the Event Hub frame size limit. "
                                 "Please send a smaller collection of EventData, or use EventDataBatch, "
                                 "which is guaranteed to be under the frame size limit")

    @property
    def size_in_bytes(self):
        # type: () -> int
        """The combined size of the events in the batch, in bytes.

        :rtype: int
        """
        return self._size

    def add(self, event, **kwargs):
        # type: (EventGridEvent, CloudEvent) -> None
        """Try to add an EventGridEvent/CloudEvent to the batch.

        The total size of an added event is the sum of its body, properties, etc.
        If this added size results in the batch exceeding the maximum batch size, a `ValueError` will
        be raised.

        :param event: The EventData to add to the batch.
        :type event: models.EventGridEvent or models.CloudEvent
        :rtype: None
        :raise: :class:`ValueError`, when exceeding the size limit.
        """
        pass
    
class EventContainer(dict):
    """The container for the event model and mapping event envelope properties.
    """
    # class variable
    #_event_type_mappings = {}

    def __init__(self, *args, **kwargs):
        # type: (Union[CloudEvent, EventGridEvent], Any) -> None
        self._update(*args, **kwargs)
    
    def __getitem__(self, key):
        return dict.__getitem__(self, key)
    
    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)

    #def __repr__(self):
    #    dictrepr = dict.__repr__(self)
    #    return '%s(%s)' % (type(self).__name__, dictrepr)

    def _update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v

    @property
    def model(self):  # aka: as_model(), why not do lazy loading here?, why is transparency needed
        # type: () -> List[Any]
        """A specific event type object is returned based on the "event type" and "data" fields specified in the event.

        :rtype: Union[BlobStorageCreated, BlobStorageDeleted, FileCreated, ...]
        """
        
        pass
    