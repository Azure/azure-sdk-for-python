from abc import ABC
from typing import TYPE_CHECKING

from ._configuration import BlocklistClientConfiguration, ContentSafetyClientConfiguration

if TYPE_CHECKING:
    from azure.core import AsyncPipelineClient

    from .._serialization import Deserializer, Serializer


class ContentSafetyClientMixinABC(ABC):
    """DO NOT use this class. It is for internal typing use only."""

    _client: "AsyncPipelineClient"
    _config: ContentSafetyClientConfiguration
    _serialize: "Serializer"
    _deserialize: "Deserializer"


class BlocklistClientMixinABC(ABC):
    """DO NOT use this class. It is for internal typing use only."""

    _client: "AsyncPipelineClient"
    _config: BlocklistClientConfiguration
    _serialize: "Serializer"
    _deserialize: "Deserializer"
