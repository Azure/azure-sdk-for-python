from abc import ABC
from typing import TYPE_CHECKING

from ._configuration import DeidentificationClientConfiguration

if TYPE_CHECKING:
    from azure.core import PipelineClient

    from ._serialization import Deserializer, Serializer


class DeidentificationClientMixinABC(ABC):
    """DO NOT use this class. It is for internal typing use only."""

    _client: "PipelineClient"
    _config: DeidentificationClientConfiguration
    _serialize: "Serializer"
    _deserialize: "Deserializer"
