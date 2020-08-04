# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint:disable=protected-access
from typing import Optional
from msrest.serialization import UTC
import datetime as dt
import uuid
import json

from ._generated.models._models import StorageBlobCreatedEventData, \
    EventGridEvent as InternalEventGridEvent, \
    CloudEvent as InternalCloudEvent

class CloudEvent(InternalCloudEvent):   #pylint:disable=too-many-instance-attributes
    """Properties of an event published to an Event Grid topic using the CloudEvent 1.0 Schema.

    All required parameters must be populated in order to send to Azure.

    :param source: Required. Identifies the context in which an event happened. The combination of id and source must be 
        unique for each distinct event. If publishing to a domain topic, source must be the domain name.
    :type source: str
    :param data: Event data specific to the event type.
    :type data: object
    :param type: Required. Type of event related to the originating occurrence.
    :type type: str
    :param time: The time (in UTC) the event was generated, in RFC3339 format.
    :type time: ~datetime.datetime
    :param dataschema: Identifies the schema that data adheres to.
    :type dataschema: str
    :param datacontenttype: Content type of data value.
    :type datacontenttype: str
    :param subject: This describes the subject of the event in the context of the event producer
     (identified by source).
    :type subject: str
    :param id: Optional. An identifier for the event. The combination of id and source must be
     unique for each distinct event.
    :type id: str
    """

    _validation = {
        'source': {'required': True},
        'type': {'required': True},
    }

    _attribute_map = {
        'additional_properties': {'key': '', 'type': '{object}'},
        'id': {'key': 'id', 'type': 'str'},
        'source': {'key': 'source', 'type': 'str'},
        'data': {'key': 'data', 'type': 'object'},
        'data_base64': {'key': 'data_base64', 'type': 'bytearray'},
        'type': {'key': 'type', 'type': 'str'},
        'time': {'key': 'time', 'type': 'iso-8601'},
        'specversion': {'key': 'specversion', 'type': 'str'},
        'dataschema': {'key': 'dataschema', 'type': 'str'},
        'datacontenttype': {'key': 'datacontenttype', 'type': 'str'},
        'subject': {'key': 'subject', 'type': 'str'},
    }

    def __init__(self, source, type, **kwargs):
        # type: (Any) -> None
        kwargs["id"] = kwargs.get('id', uuid.uuid4())
        kwargs["source"] = source
        kwargs["type"] = type
        kwargs["time"] = kwargs.get('time', dt.datetime.now(UTC()).isoformat())
        kwargs["specversion"] = "1.0"

        super(CloudEvent, self).__init__(**kwargs)


class EventGridEvent(InternalEventGridEvent):
    """Properties of an event published to an Event Grid topic using the EventGrid Schema.

    Variables are only populated by the server, and will be ignored when sending a request.

    All required parameters must be populated in order to send to Azure.

    :param id: An unique identifier for the event. If not provided, one will be generated for the event.
    :type id: str
    :param topic: The resource path of the event source. If not provided, Event Grid will stamp onto the event.
    :type topic: str
    :param subject: Required. A resource path relative to the topic path.
    :type subject: str
    :param data: Event data specific to the event type.
    :type data: object
    :param event_type: Required. The type of the event that occurred.
    :type event_type: str
    :param event_time: The time (in UTC) of the event. If not provided, it will be the time (in UTC) the event was generated.
    :type event_time: ~datetime.datetime
    :ivar metadata_version: The schema version of the event metadata. If providedj, must match Event Grid Schema exactly.
        If not provided, EventGrid will stamp onto event.
    :vartype metadata_version: str
    :param data_version: The schema version of the data object. If not provided, will be stamped with an empty value.
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

    def __init__(self, subject, event_type, **kwargs):
        # type: (Any) -> None
        kwargs["id"] = kwargs.get('id', uuid.uuid4())
        kwargs["subject"] = subject
        kwargs["event_type"] = event_type
        kwargs["event_time"] = kwargs.get('event_time', dt.datetime.now(UTC()).isoformat())
        kwargs["data"] = kwargs.get('data', None)

        super(EventGridEvent, self).__init__(**kwargs)

class DictMixin(object):

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __contains__(self, key):
        return key in self.__dict__

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.keys())

    def __delitem__(self, key):
        self.__dict__[key] = None

    def __eq__(self, other):
        """Compare objects by comparing all attributes."""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        """Compare objects by comparing all attributes."""
        return not self.__eq__(other)

    def __str__(self):
        return str({k: v for k, v in self.__dict__.items() if not k.startswith('_')})

    def has_key(self, k, **kwargs):
        return k in self.__dict__

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def keys(self, **kwargs):
        return [k for k in self.__dict__ if not k.startswith('_')]

    def values(self, **kwargs):
        return [v for k, v in self.__dict__.items() if not k.startswith('_')]

    def items(self, **kwargs):
        return [(k, v) for k, v in self.__dict__.items() if not k.startswith('_')]

    def get(self, key, default=None, **kwargs):
        if key in self.__dict__:
            return self.__dict__[key]
        return default


class DeserializedEvent():
    """The container for the deserialized event model and mapping of event envelope properties.
        :param dict event: dict
    """
    # class variable
    _event_type_mappings = {'Microsoft.Storage.BlobCreated': StorageBlobCreatedEventData}

    def __init__(self, event):
        # type: (Any) -> None
    #    self._update(*args, **kwargs)
        self._model = None
        self._event_dict = event
    
    def to_json(self):
        return self._event_dict

    def _update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v

    @property
    def model(self):
        # type: () -> Union[CloudEvent, EventGridEvent]
        """
        Returns strongly typed EventGridEvent/CloudEvent object defined by the format of the properties.
        All properties of the model are strongly typed (ie. for an EventGridEvent, event_time property will return a datetime.datetime object).

        model.data: Returns a system event type(StorageBlobCreated, StorageBlobDeleted, etc.). If model.type/model.event_type is not defined in the 
          system registry, returns None.

        :rtype: Union[CloudEvent, EventGridEvent]
        """
        event_type = ""
        if not self._model:
            try:
                if 'specversion' in self._event_dict.keys():
                    self._model = CloudEvent.deserialize(self._event_dict)
                    event_type = self._model.type
                else:
                    self._model = EventGridEvent.deserialize(self._event_dict)
                    event_type = self._model.event_type
            except ValueError:
                print("Event is not correctly formatted CloudEvent or EventGridEvent.")

            self._deserialize_data(event_type)

        return self._model
    
    def _deserialize_data(self, event_type):
        """
        Sets self._model.data to strongly typed event object if event type exists in _event_type_mappings.
        Otherwise, sets self._model.data to None.

        :param str event_type: The event_type of the EventGridEvent object or the type of the CloudEvent object.
        """
        # if system event type defined, set model.data to system event object
        if event_type in DeserializedEvent._event_type_mappings:
            self._model.data = (DeserializedEvent._event_type_mappings[event_type]).deserialize(self._model.data)
        elif isinstance(self._model.data, dict):    # else, if custom event, then model.data is dict and should be set to None
            self._model.data = None
        # else model.data is str/int/etc. and should remain the same
    
class CustomEvent(DictMixin):
    """The wrapper class for a CustomEvent, to be used when publishing events.
       :param dict args: dict
    """

    def __init__(self, *args, **kwargs):
        # type: (Any) -> None
        self._update(*args, **kwargs)

    def _update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            print(k)
            print(v)
            self[k] = v
