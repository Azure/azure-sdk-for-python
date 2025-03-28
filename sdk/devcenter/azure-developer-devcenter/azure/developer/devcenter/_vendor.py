from abc import ABC
from typing import TYPE_CHECKING

from ._configuration import (
    DeploymentEnvironmentsClientConfiguration,
    DevBoxesClientConfiguration,
    DevCenterClientConfiguration,
)

if TYPE_CHECKING:
    from azure.core import PipelineClient

    from ._serialization import Deserializer, Serializer


class DevCenterClientMixinABC(ABC):
    """DO NOT use this class. It is for internal typing use only."""

    _client: "PipelineClient"
    _config: DevCenterClientConfiguration
    _serialize: "Serializer"
    _deserialize: "Deserializer"


class DevBoxesClientMixinABC(ABC):
    """DO NOT use this class. It is for internal typing use only."""

    _client: "PipelineClient"
    _config: DevBoxesClientConfiguration
    _serialize: "Serializer"
    _deserialize: "Deserializer"


class DeploymentEnvironmentsClientMixinABC(ABC):
    """DO NOT use this class. It is for internal typing use only."""

    _client: "PipelineClient"
    _config: DeploymentEnvironmentsClientConfiguration
    _serialize: "Serializer"
    _deserialize: "Deserializer"
