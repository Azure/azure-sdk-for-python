from abc import ABC
from typing import TYPE_CHECKING

from ._configuration import EventGridConsumerClientConfiguration, EventGridPublisherClientConfiguration

if TYPE_CHECKING:
    from azure.core import PipelineClient

    from ._serialization import Deserializer, Serializer


class EventGridPublisherClientMixinABC(ABC):
    """DO NOT use this class. It is for internal typing use only."""

    _client: "PipelineClient"
    _config: EventGridPublisherClientConfiguration
    _serialize: "Serializer"
    _deserialize: "Deserializer"


class EventGridConsumerClientMixinABC(ABC):
    """DO NOT use this class. It is for internal typing use only."""

    _client: "PipelineClient"
    _config: EventGridConsumerClientConfiguration
    _serialize: "Serializer"
    _deserialize: "Deserializer"
