from abc import ABC
from typing import TYPE_CHECKING

from ._configuration import (
    DocumentIntelligenceAdministrationClientConfiguration,
    DocumentIntelligenceClientConfiguration,
)

if TYPE_CHECKING:
    from azure.core import AsyncPipelineClient

    from .._serialization import Deserializer, Serializer


class DocumentIntelligenceClientMixinABC(ABC):
    """DO NOT use this class. It is for internal typing use only."""

    _client: "AsyncPipelineClient"
    _config: DocumentIntelligenceClientConfiguration
    _serialize: "Serializer"
    _deserialize: "Deserializer"


class DocumentIntelligenceAdministrationClientMixinABC(ABC):  # pylint: disable=name-too-long
    """DO NOT use this class. It is for internal typing use only."""

    _client: "AsyncPipelineClient"
    _config: DocumentIntelligenceAdministrationClientConfiguration
    _serialize: "Serializer"
    _deserialize: "Deserializer"
