# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint:disable=protected-access
from typing import Union, Any, Dict
import datetime as dt
import uuid
import json
import six
from msrest.serialization import UTC
from ._generated.models import EventGridEvent as InternalEventGridEvent, CloudEvent as InternalCloudEvent


class EventMixin(object):
    """
    Mixin for the event models comprising of some helper methods.
    """
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


class CloudEvent(EventMixin):   #pylint:disable=too-many-instance-attributes
    """Properties of an event published to an Event Grid topic using the CloudEvent 1.0 Schema.

    All required parameters must be populated in order to send to Azure.
    If data is of binary type, data_base64 can be used alternatively. Note that data and data_base64
    cannot be present at the same time.

    :param source: Required. Identifies the context in which an event happened. The combination of id and source must
     be unique for each distinct event. If publishing to a domain topic, source must be the domain name.
    :type source: str
    :param type: Required. Type of event related to the originating occurrence.
    :type type: str
    :keyword data: Optional. Event data specific to the event type. Only one of the `data` or `data_base64`
     argument must be present. If data is of bytes type, it will be sent as data_base64 in the outgoing request.
    :type data: object
    :keyword time: Optional. The time (in UTC) the event was generated, in RFC3339 format.
    :type time: ~datetime.datetime
    :keyword dataschema: Optional. Identifies the schema that data adheres to.
    :type dataschema: str
    :keyword datacontenttype: Optional. Content type of data value.
    :type datacontenttype: str
    :keyword subject: Optional. This describes the subject of the event in the context of the event producer
     (identified by source).
    :type subject: str
    :keyword specversion: Optional. The version of the CloudEvent spec. Defaults to "1.0"
    :type specversion: str
    :keyword id: Optional. An identifier for the event. The combination of id and source must be
     unique for each distinct event. If not provided, a random UUID will be generated and used.
    :type id: Optional[str]
    :keyword data_base64: Optional. Event data specific to the event type if the data is of bytes type.
     Only data of bytes type is accepted by `data-base64` and only one of the `data` or `data_base64` argument
     must be present.
    :type data_base64: bytes
    :ivar source: Identifies the context in which an event happened. The combination of id and source must
     be unique for each distinct event. If publishing to a domain topic, source must be the domain name.
    :vartype source: str
    :ivar data: Event data specific to the event type.
    :vartype data: object
    :ivar data_base64: Event data specific to the event type if the data is of bytes type.
    :vartype data_base64: bytes
    :ivar type: Type of event related to the originating occurrence.
    :vartype type: str
    :ivar time: The time (in UTC) the event was generated, in RFC3339 format.
    :vartype time: ~datetime.datetime
    :ivar dataschema: Identifies the schema that data adheres to.
    :vartype dataschema: str
    :ivar datacontenttype: Content type of data value.
    :vartype datacontenttype: str
    :ivar subject: This describes the subject of the event in the context of the event producer
     (identified by source).
    :vartype subject: str
    :ivar specversion: Optional. The version of the CloudEvent spec. Defaults to "1.0"
    :vartype specversion: str
    :ivar id: An identifier for the event. The combination of id and source must be
     unique for each distinct event. If not provided, a random UUID will be generated and used.
    :vartype id: Optional[str]
    """
    def __init__(self, source, type, **kwargs): # pylint: disable=redefined-builtin
        # type: (str, str, Any) -> None
        self.source = source
        self.type = type
        self.specversion = kwargs.pop("specversion", "1.0")
        self.id = kwargs.pop("id", str(uuid.uuid4()))
        self.time = kwargs.pop("time", dt.datetime.now(UTC()).isoformat())
        self.data = kwargs.pop("data", None)
        self.datacontenttype = kwargs.pop("datacontenttype", None)
        self.dataschema = kwargs.pop("dataschema", None)
        self.subject = kwargs.pop("subject", None)
        self.data_base64 = kwargs.pop("data_base64", None)
        self.extensions = {}
        self.extensions.update(dict(kwargs.pop('extensions', {})))
        if self.data is not None and self.data_base64 is not None:
            raise ValueError("data and data_base64 cannot be provided at the same time.\
                Use data_base64 only if you are sending bytes, and use data otherwise.")

    @classmethod
    def _from_generated(cls, cloud_event, **kwargs):
        # type: (Union[str, Dict, bytes], Any) -> CloudEvent
        generated = InternalCloudEvent.deserialize(cloud_event)
        if generated.additional_properties:
            extensions = dict(generated.additional_properties)
            kwargs.setdefault('extensions', extensions)
        return cls(
            id=generated.id,
            source=generated.source,
            type=generated.type,
            specversion=generated.specversion,
            data=generated.data or generated.data_base64,
            time=generated.time,
            dataschema=generated.dataschema,
            datacontenttype=generated.datacontenttype,
            subject=generated.subject,
            **kwargs
        )

    def _to_generated(self, **kwargs):
        if isinstance(self.data, six.binary_type):
            data_base64 = self.data
            data = None
        else:
            data = self.data
            data_base64 = None
        return InternalCloudEvent(
            id=self.id,
            source=self.source,
            type=self.type,
            specversion=self.specversion,
            data=data,
            data_base64=self.data_base64 or data_base64,
            time=self.time,
            dataschema=self.dataschema,
            datacontenttype=self.datacontenttype,
            subject=self.subject,
            additional_properties=self.extensions,
            **kwargs
        )


class EventGridEvent(InternalEventGridEvent, EventMixin):
    """Properties of an event published to an Event Grid topic using the EventGrid Schema.

    Variables are only populated by the server, and will be ignored when sending a request.

    All required parameters must be populated in order to send to Azure.

    :param subject: Required. A resource path relative to the topic path.
    :type subject: str
    :param event_type: Required. The type of the event that occurred.
    :type event_type: str
    :param data: Required. Event data specific to the event type.
    :type data: object
    :param data_version: Required. The schema version of the data object.
     If not provided, will be stamped with an empty value.
    :type data_version: str
    :keyword topic: Optional. The resource path of the event source. If not provided, Event Grid will
     stamp onto the event.
    :type topic: str
    :keyword metadata_version: Optional. The schema version of the event metadata. If provided,
     must match Event Grid Schema exactly. If not provided, EventGrid will stamp onto event.
    :type metadata_version: str
    :keyword id: Optional. An identifier for the event. In not provided, a random UUID will be generated and used.
    :type id: Optional[str]
    :keyword event_time: Optional.The time (in UTC) of the event. If not provided,
     it will be the time (in UTC) the event was generated.
    :type event_time: Optional[~datetime.datetime]
    :ivar subject: A resource path relative to the topic path.
    :vartype subject: str
    :ivar event_type: The type of the event that occurred.
    :vartype event_type: str
    :ivar data: Event data specific to the event type.
    :vartype data: object
    :ivar data_version: The schema version of the data object.
     If not provided, will be stamped with an empty value.
    :vartype data_version: str
    :ivar topic: The resource path of the event source. If not provided, Event Grid will stamp onto the event.
    :vartype topic: str
    :ivar metadata_version: The schema version of the event metadata. If provided, must match Event Grid Schema exactly.
     If not provided, EventGrid will stamp onto event.
    :vartype metadata_version: str
    :ivar id: An identifier for the event. In not provided, a random UUID will be generated and used.
    :vartype id: Optional[str]
    :ivar event_time: The time (in UTC) of the event. If not provided,
     it will be the time (in UTC) the event was generated.
    :vartype event_time: Optional[~datetime.datetime]
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

    def __init__(self, subject, event_type, data, data_version, **kwargs):
        # type: (str, str, object, str, Any) -> None
        kwargs.setdefault('id', uuid.uuid4())
        kwargs.setdefault('subject', subject)
        kwargs.setdefault("event_type", event_type)
        kwargs.setdefault('event_time', dt.datetime.now(UTC()).isoformat())
        kwargs.setdefault('data', data)
        kwargs.setdefault('data_version', data_version)

        super(EventGridEvent, self).__init__(**kwargs)
