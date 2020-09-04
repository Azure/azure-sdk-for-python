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
import six
from ._generated import models
from ._generated.models import StorageBlobCreatedEventData, \
    EventGridEvent as InternalEventGridEvent, \
    CloudEvent as InternalCloudEvent
from ._shared.mixins import DictMixin
from ._event_mappings import _event_mappings


class EventMixin(object):
    """
    Mixin for the event models comprising of some helper methods.
    """
    @staticmethod
    def _deserialize_data(event, event_type):
        """
        Sets the data of the desrialized event to strongly typed event object if event type exists in _event_mappings.
        Otherwise, sets it to None.

        :param str event_type: The event_type of the EventGridEvent object or the type of the CloudEvent object.
        """
        # if system event type defined, set event.data to system event object
        try:
            event.data = (_event_mappings[event_type]).deserialize(event.data)
        except KeyError: # else, if custom event, then event.data is dict and should be set to None
            event.data = None

    @staticmethod
    def _from_json(event, encode):
        """
        Load the event into the json
        :param dict eventgrid_event: The event to be deserialized.
        :type eventgrid_event: Union[str, dict, bytes]
        :param str encode: The encoding to be used. Defaults to 'utf-8'
        """
        if isinstance(event, six.binary_type):
            event = json.loads(event.decode(encode))
        elif isinstance(event, six.string_types):
            event = json.loads(event)
        return event


class CloudEvent(InternalCloudEvent, EventMixin):   #pylint:disable=too-many-instance-attributes
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
    :type id: Optional[str]
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
        # type: (str, str, Any) -> None
        kwargs.setdefault('id', uuid.uuid4())
        kwargs.setdefault("source", source)
        kwargs.setdefault("type", type)
        kwargs.setdefault("time", dt.datetime.now(UTC()).isoformat())
        kwargs.setdefault("specversion", "1.0")

        super(CloudEvent, self).__init__(**kwargs)


class EventGridEvent(InternalEventGridEvent, EventMixin):
    """Properties of an event published to an Event Grid topic using the EventGrid Schema.

    Variables are only populated by the server, and will be ignored when sending a request.

    All required parameters must be populated in order to send to Azure.

    :param topic: The resource path of the event source. If not provided, Event Grid will stamp onto the event.
    :type topic: str
    :param subject: Required. A resource path relative to the topic path.
    :type subject: str
    :param data: Event data specific to the event type.
    :type data: object
    :param event_type: Required. The type of the event that occurred.
    :type event_type: str
    :ivar metadata_version: The schema version of the event metadata. If provided, must match Event Grid Schema exactly.
        If not provided, EventGrid will stamp onto event.
    :vartype metadata_version: str
    :param data_version: The schema version of the data object. If not provided, will be stamped with an empty value.
    :type data_version: str
    :param id: Optional. An identifier for the event. The combination of id and source must be
     unique for each distinct event.
    :type id: Optional[str]
    :param event_time: Optional.The time (in UTC) of the event. If not provided, it will be the time (in UTC) the event was generated.
    :type event_time: Optional[~datetime.datetime]
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
        # type: (str, str, Any) -> None
        kwargs.setdefault('id', uuid.uuid4())
        kwargs.setdefault('subject', subject)
        kwargs.setdefault("event_type", event_type)
        kwargs.setdefault('event_time', dt.datetime.now(UTC()).isoformat())
        kwargs.setdefault('data', None)

        super(EventGridEvent, self).__init__(**kwargs)


class CustomEvent(DictMixin):
    """The wrapper class for a CustomEvent, to be used when publishing events.
       :param dict args: dict
    """

    def __init__(self, *args, **kwargs):
        # type: (Any, Any) -> None
        self._update(*args, **kwargs)

    def _update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v
