from abc import ABC
from typing import TYPE_CHECKING

from ._configuration import ImageAnalysisClientConfiguration

if TYPE_CHECKING:
    from azure.core import PipelineClient

    from ._serialization import Deserializer, Serializer


class ImageAnalysisClientMixinABC(ABC):
    """DO NOT use this class. It is for internal typing use only."""

    _client: "PipelineClient"
    _config: ImageAnalysisClientConfiguration
    _serialize: "Serializer"
    _deserialize: "Deserializer"
