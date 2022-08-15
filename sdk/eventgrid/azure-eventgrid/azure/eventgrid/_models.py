# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint:disable=protected-access
from typing import Any, cast
import datetime as dt
import uuid
from msrest.serialization import UTC
from ._messaging_shared import _get_json_content
from ._generated.models import (
    EventGridEvent as InternalEventGridEvent,
)


class EventGridEvent(InternalEventGridEvent):
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
    :keyword topic: The resource path of the event source. If not provided, Event Grid will
     stamp onto the event. This is required when sending event(s) to a domain.
    :paramtype topic: Optional[str]
    :keyword metadata_version: The schema version of the event metadata. If provided,
     must match Event Grid Schema exactly. If not provided, EventGrid will stamp onto event.
    :paramtype metadata_version: Optional[str]
    :keyword id: An identifier for the event. In not provided, a random UUID will be generated and used.
    :paramtype id: Optional[str]
    :keyword event_time: The time (in UTC) of the event. If not provided,
     it will be the time (in UTC) the event was generated.
    :paramtype event_time: Optional[~datetime.datetime]
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
    :vartype id: str
    :ivar event_time: The time (in UTC) of the event. If not provided,
     it will be the time (in UTC) the event was generated.
    :vartype event_time: ~datetime.datetime
    """

    _validation = {
        "id": {"required": True},
        "subject": {"required": True},
        "data": {"required": True},
        "event_type": {"required": True},
        "event_time": {"required": True},
        "metadata_version": {"readonly": True},
        "data_version": {"required": True},
    }

    _attribute_map = {
        "id": {"key": "id", "type": "str"},
        "topic": {"key": "topic", "type": "str"},
        "subject": {"key": "subject", "type": "str"},
        "data": {"key": "data", "type": "object"},
        "event_type": {"key": "eventType", "type": "str"},
        "event_time": {"key": "eventTime", "type": "iso-8601"},
        "metadata_version": {"key": "metadataVersion", "type": "str"},
        "data_version": {"key": "dataVersion", "type": "str"},
    }

    def __init__(self, subject, event_type, data, data_version, **kwargs):
        # type: (str, str, object, str, Any) -> None
        kwargs.setdefault("id", uuid.uuid4())
        kwargs.setdefault("subject", subject)
        kwargs.setdefault("event_type", event_type)
        kwargs.setdefault("event_time", dt.datetime.now(UTC()).isoformat())
        kwargs.setdefault("data", data)
        kwargs.setdefault("data_version", data_version)

        super(EventGridEvent, self).__init__(**kwargs)

    def __repr__(self):
        return "EventGridEvent(subject={}, event_type={}, id={}, event_time={})".format(
            self.subject, self.event_type, self.id, self.event_time
        )[:1024]

    @classmethod
    def from_json(cls, event):
        # type: (Any) -> EventGridEvent
        """
        Returns the deserialized EventGridEvent object when a json payload is provided.
        :param event: The json string that should be converted into a EventGridEvent. This can also be
         a storage QueueMessage, eventhub's EventData or ServiceBusMessage
        :type event: object
        :rtype: EventGridEvent
        :raises ValueError: If the provided JSON is invalid.
        """
        dict_event = _get_json_content(event)
        return cast(EventGridEvent, EventGridEvent.from_dict(dict_event))
