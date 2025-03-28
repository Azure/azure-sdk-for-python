from abc import ABC
from typing import TYPE_CHECKING

from ._configuration import DocumentTranslationClientConfiguration, SingleDocumentTranslationClientConfiguration

if TYPE_CHECKING:
    from azure.core import AsyncPipelineClient

    from .._serialization import Deserializer, Serializer


class DocumentTranslationClientMixinABC(ABC):
    """DO NOT use this class. It is for internal typing use only."""

    _client: "AsyncPipelineClient"
    _config: DocumentTranslationClientConfiguration
    _serialize: "Serializer"
    _deserialize: "Deserializer"


class SingleDocumentTranslationClientMixinABC(ABC):
    """DO NOT use this class. It is for internal typing use only."""

    _client: "AsyncPipelineClient"
    _config: SingleDocumentTranslationClientConfiguration
    _serialize: "Serializer"
    _deserialize: "Deserializer"
