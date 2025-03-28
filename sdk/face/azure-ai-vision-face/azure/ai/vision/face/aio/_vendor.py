from abc import ABC
from typing import TYPE_CHECKING

from ._configuration import FaceClientConfiguration, FaceSessionClientConfiguration

if TYPE_CHECKING:
    from azure.core import AsyncPipelineClient

    from .._serialization import Deserializer, Serializer


class FaceClientMixinABC(ABC):
    """DO NOT use this class. It is for internal typing use only."""

    _client: "AsyncPipelineClient"
    _config: FaceClientConfiguration
    _serialize: "Serializer"
    _deserialize: "Deserializer"


class FaceSessionClientMixinABC(ABC):
    """DO NOT use this class. It is for internal typing use only."""

    _client: "AsyncPipelineClient"
    _config: FaceSessionClientConfiguration
    _serialize: "Serializer"
    _deserialize: "Deserializer"
