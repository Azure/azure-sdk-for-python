# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import uuid
from  base64 import b64decode
from datetime import datetime

try:
    from datetime import timezone
    TZ_UTC = timezone.utc  # type: ignore
except ImportError:
    from azure.core._utils import _FixedOffset
    TZ_UTC = _FixedOffset(0) # type: ignore

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Any, Dict

__all__ = ["CloudEvent"]


class CloudEvent(object):   #pylint:disable=too-many-instance-attributes
    """Properties of the CloudEvent 1.0 Schema.
    All required parameters must be populated in order to send to Azure.
    If data is of binary type, data_base64 can be used alternatively. Note that data and data_base64
    cannot be present at the same time.
    :param source: Required. Identifies the context in which an event happened. The combination of id and source must
     be unique for each distinct event. If publishing to a domain topic, source must be the domain name.
    :type source: str
    :param type: Required. Type of event related to the originating occurrence.
    :type type: str
    :keyword data: Optional. Event data specific to the event type. If data is of bytes type, it will be sent
     as data_base64 in the outgoing request.
    :type data: object
    :keyword time: Optional. The time (in UTC) the event was generated, in RFC3339 format.
    :type time: str
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
    :keyword extensions: Optional. A CloudEvent MAY include any number of additional context attributes
     with distinct names represented as key - value pairs. Each extension must be alphanumeric, lower cased
     and must not exceed the length of 20 characters.
    :type extensions: Optional[dict]
    :ivar source: Identifies the context in which an event happened. The combination of id and source must
     be unique for each distinct event. If publishing to a domain topic, source must be the domain name.
    :vartype source: str
    :ivar data: Event data specific to the event type.
    :vartype data: object
    :ivar type: Type of event related to the originating occurrence.
    :vartype type: str
    :ivar time: The time (in UTC) the event was generated, in RFC3339 format.
    :vartype time: str
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
    :vartype id: str
    :ivar extensions: A CloudEvent MAY include any number of additional context attributes
     with distinct names represented as key - value pairs. Each extension must be alphanumeric, lower cased
     and must not exceed the length of 20 characters.
    :vartype extensions: dict
    """
    def __init__(self, source, type, **kwargs): # pylint: disable=redefined-builtin
        # type: (str, str, Any) -> None
        self.source = source
        self.type = type
        self.specversion = kwargs.pop("specversion", "1.0")
        self.id = kwargs.pop("id", str(uuid.uuid4()))
        self.time = kwargs.pop("time", datetime.now(TZ_UTC).isoformat())
        self.datacontenttype = kwargs.pop("datacontenttype", None)
        self.dataschema = kwargs.pop("dataschema", None)
        self.subject = kwargs.pop("subject", None)
        self.extensions = {}
        self.extensions.update(dict(kwargs.pop('extensions', {})))
        self.data = kwargs.pop("data", None)

    def __repr__(self):
        return (
            "CloudEvent(source={}, type={}, specversion={}, id={}, time={})".format(
                self.source,
                self.type,
                self.specversion,
                self.id,
                self.time
            )[:1024]
        )

    @classmethod
    def from_dict(cls, event, **kwargs):
        # type: (Dict, Any) -> CloudEvent
        """
        Returns the deserialized CloudEvent object when a dict is provided.
        :param event: The dict representation of the event which needs to be deserialized.
        :type event: dict
        :rtype: CloudEvent
        """
        data = event.pop("data", None)
        data_base64 = event.pop("data_base64", None)
        if data and data_base64:
            raise ValueError("Invalid input. Only one of data and data_base64 must be present.")
        return cls(
            id=event.pop("id", None),
            source=event.pop("source", None),
            type=event.pop("type", None),
            specversion=event.pop("specversion", None),
            data=data or b64decode(data_base64),
            time=event.pop("time", None),
            dataschema=event.pop("dataschema", None),
            datacontenttype=event.pop("datacontenttype", None),
            subject=event.pop("subject", None),
            extensions=event,
            **kwargs
        )
