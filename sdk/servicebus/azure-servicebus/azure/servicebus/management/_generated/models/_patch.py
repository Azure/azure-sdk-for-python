# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, List, Optional, Union, TYPE_CHECKING, Dict

from .. import _serialization
from ._models import RuleFilter

if TYPE_CHECKING:
    from datetime import datetime, timedelta

__all__: List[str] = [
    "CorrelationFilter",
    "KeyObjectValue"
]  # Add all objects you want publicly available to users at this package level


# Re-write to include correct properties type, swagger doesn't allow Union of types in KeyValue
class KeyObjectValue(_serialization.Model):
    """Key Values of custom properties.

    :ivar key:
    :vartype key: str
    :ivar value: Any object.
    :vartype value: JSON
    """

    _attribute_map = {
        "key": {
            "key": "key",
            "type": "str",
            "xml": {
                "name": "Key",
                "ns": "http://schemas.microsoft.com/netservices/2010/10/servicebus/connect"
            },
        },
        "value": {"key": "value", "type": "object"},
    }
    _xml_map = {
        "name": "KeyValueOfObjectType",
        "ns": "http://schemas.microsoft.com/netservices/2010/10/servicebus/connect",
    }

    def __init__(
        self,
        *,
        key: str,
        value: Union[str, int, float, bool, "datetime", "timedelta"],
        **kwargs: Any
    ) -> None:
        """
        :keyword key:
        :paramtype key: str
        :keyword value: Any object.
        :paramtype value: dict[str, str or int or float or bool or datetime or timedelta]
        """
        super().__init__(**kwargs)
        self.key = key
        self.value = value


class CorrelationFilter(RuleFilter):
    """CorrelationFilter.

    All required parameters must be populated in order to send to server.

    :ivar type: Required.
    :vartype type: str
    :ivar correlation_id:
    :vartype correlation_id: str
    :ivar message_id:
    :vartype message_id: str
    :ivar to:
    :vartype to: str
    :ivar reply_to:
    :vartype reply_to: str
    :ivar label:
    :vartype label: str
    :ivar session_id:
    :vartype session_id: str
    :ivar reply_to_session_id:
    :vartype reply_to_session_id: str
    :ivar content_type:
    :vartype content_type: str
    :ivar properties:
    :vartype properties: ~azure.servicebus.management._generated.models.KeyObjectValue
    """

    _validation = {
        "type": {"required": True},
    }

    _attribute_map = {
        "type": {
            "key": "type",
            "type": "str",
            "xml": {
                "attr": True,
                "prefix": "xsi",
                "ns": "http://www.w3.org/2001/XMLSchema-instance"
            },
        },
        "correlation_id": {
            "key": "correlationId",
            "type": "str",
            "xml": {
                "name": "CorrelationId",
                "ns": "http://schemas.microsoft.com/netservices/2010/10/servicebus/connect",
            },
        },
        "message_id": {
            "key": "messageId",
            "type": "str",
            "xml": {
                "name": "MessageId",
                "ns": "http://schemas.microsoft.com/netservices/2010/10/servicebus/connect"
            },
        },
        "to": {
            "key": "to",
            "type": "str",
            "xml": {
                "name": "To",
                "ns": "http://schemas.microsoft.com/netservices/2010/10/servicebus/connect"
            },
        },
        "reply_to": {
            "key": "replyTo",
            "type": "str",
            "xml": {
                "name": "ReplyTo",
                "ns": "http://schemas.microsoft.com/netservices/2010/10/servicebus/connect"
            },
        },
        "label": {
            "key": "label",
            "type": "str",
            "xml": {
                "name": "Label",
                "ns": "http://schemas.microsoft.com/netservices/2010/10/servicebus/connect"
            },
        },
        "session_id": {
            "key": "sessionId",
            "type": "str",
            "xml": {
                "name": "SessionId",
                "ns": "http://schemas.microsoft.com/netservices/2010/10/servicebus/connect"
            },
        },
        "reply_to_session_id": {
            "key": "replyToSessionId",
            "type": "str",
            "xml": {
                "name": "ReplyToSessionId",
                "ns": "http://schemas.microsoft.com/netservices/2010/10/servicebus/connect",
            },
        },
        "content_type": {
            "key": "contentType",
            "type": "str",
            "xml": {
                "name": "ContentType",
                "ns": "http://schemas.microsoft.com/netservices/2010/10/servicebus/connect"
            },
        },
        "properties": {
            "key": "properties",
            "type": "[KeyObjectValue]",
            "xml": {
                "name": "Properties",
                "ns": "http://schemas.microsoft.com/netservices/2010/10/servicebus/connect",
                "wrapped": True,
                "itemsName": "KeyValueOfObjectType",
                "itemsNs": "http://schemas.microsoft.com/netservices/2010/10/servicebus/connect",
            },
        },
    }

    def __init__(
        self,
        *,
        correlation_id: Optional[str] = None,
        message_id: Optional[str] = None,
        to: Optional[str] = None,
        reply_to: Optional[str] = None,
        label: Optional[str] = None,
        session_id: Optional[str] = None,
        reply_to_session_id: Optional[str] = None,
        content_type: Optional[str] = None,
        properties: Optional[List["KeyObjectValue"]] = None,
        **kwargs: Any
    ) -> None:
        """
        :keyword correlation_id:
        :paramtype correlation_id: str
        :keyword message_id:
        :paramtype message_id: str
        :keyword to:
        :paramtype to: str
        :keyword reply_to:
        :paramtype reply_to: str
        :keyword label:
        :paramtype label: str
        :keyword session_id:
        :paramtype session_id: str
        :keyword reply_to_session_id:
        :paramtype reply_to_session_id: str
        :keyword content_type:
        :paramtype content_type: str
        :keyword properties:
        :paramtype properties: ~azure.servicebus.management._generated.models.KeyObjectValue
        """
        super().__init__(**kwargs)
        self.type: str = "CorrelationFilter"
        self.correlation_id = correlation_id
        self.message_id = message_id
        self.to = to
        self.reply_to = reply_to
        self.label = label
        self.session_id = session_id
        self.reply_to_session_id = reply_to_session_id
        self.content_type = content_type
        self.properties = properties


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
