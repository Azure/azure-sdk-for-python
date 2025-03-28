from abc import ABC
from typing import TYPE_CHECKING

from ._configuration import MessageTemplateClientConfiguration, NotificationMessagesClientConfiguration

if TYPE_CHECKING:
    from azure.core import AsyncPipelineClient

    from .._serialization import Deserializer, Serializer


class NotificationMessagesClientMixinABC(ABC):
    """DO NOT use this class. It is for internal typing use only."""

    _client: "AsyncPipelineClient"
    _config: NotificationMessagesClientConfiguration
    _serialize: "Serializer"
    _deserialize: "Deserializer"


class MessageTemplateClientMixinABC(ABC):
    """DO NOT use this class. It is for internal typing use only."""

    _client: "AsyncPipelineClient"
    _config: MessageTemplateClientConfiguration
    _serialize: "Serializer"
    _deserialize: "Deserializer"
