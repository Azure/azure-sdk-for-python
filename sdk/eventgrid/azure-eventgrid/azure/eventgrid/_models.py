# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint:disable=protected-access
from typing import Any, Dict
import datetime as dt
import uuid
from ._messaging_shared import _get_json_content
from ._serialization import AzureCoreNull as NULL, Deserializer

class EventGridEvent(object):
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

    def __init__(self, subject: str, event_type: str, data: Any, data_version: str, **kwargs: Any):

        kwargs.setdefault("id", uuid.uuid4())
        kwargs.setdefault("subject", subject)
        kwargs.setdefault("event_type", event_type)
        kwargs.setdefault("event_time", dt.datetime.now(dt.timezone.utc).isoformat())
        kwargs.setdefault("data", data)
        kwargs.setdefault("data_version", data_version)

        self.id = kwargs.pop("id")
        self.subject = subject
        self.event_type = event_type
        self.event_time = kwargs.pop("event_time")
        self.data = data
        self.data_version = data_version
        self.topic = kwargs.pop("topic", None)
        self.metadata_version = None

    def __repr__(self):
        return "EventGridEvent(subject={}, event_type={}, id={}, event_time={})".format(
            self.subject, self.event_type, self.id, self.event_time
        )[:1024]

    @classmethod
    def from_dict(cls, event: Dict[str, Any]) -> "EventGridEvent":
        """Returns the deserialized EventGridEvent object when a dict is provided.

        :param event: The dict representation of the event which needs to be deserialized.
        :type event: dict
        :rtype: EventGridEvent
        :return: The deserialized EventGridEvent object.
        """
        kwargs: Dict[str, Any] = {}
        event_obj = None

        data = event["data"]
        kwargs["data"] = data if data is not None else NULL

        for item in ["metadata_version", "topic"]:
            if item in event:
                val = event[item]
                kwargs[item] = val if val is not None else NULL

        deserializer = Deserializer()
        if "event_time" in event.keys():
            event_time = deserializer.deserialize_iso(event["event_time"])
            kwargs["event_time"] = event_time if event_time is not None else NULL

        try:
            event_obj = cls(
                id=event["id"],
                subject=event["subject"],
                event_type=event["event_type"],
                data_version=event["data_version"],
                **kwargs,
            )
        except KeyError as err:
            # https://github.com/cloudevents/spec Cloud event spec requires source, type,
            # specversion. We autopopulate everything other than source, type.
            # So we will assume the KeyError is coming from source/type access.
            if all(
                key in event
                for key in (
                    "source",
                    "type",
                )
            ):
                raise ValueError(
                    "The event does not conform to the EventGridEvent type spec."
                    + " The 'subject' and 'event_type' are required."
                ) from err
        return event_obj

    @classmethod
    def from_json(cls, event: Any):
        """
        Returns the deserialized EventGridEvent object when a json payload is provided.
        :param event: The json string that should be converted into a EventGridEvent. This can also be
         a storage QueueMessage, eventhub's EventData or ServiceBusMessage
        :type event: object
        :rtype: EventGridEvent
        :return: An EventGridEvent object.
        :raises ValueError: If the provided JSON is invalid.
        """
        dict_event = _get_json_content(event)
        return cls.from_dict(dict_event)