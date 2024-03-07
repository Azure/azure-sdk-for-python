# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=arguments-renamed

import logging
from typing import Optional

from azure.ai.ml._restclient.v2022_05_01.models import ContainerResourceSettings
from azure.ai.ml.entities._mixins import RestTranslatableMixin

module_logger = logging.getLogger(__name__)


class ResourceSettings(RestTranslatableMixin):
    """Resource settings for a container.

    This class uses Kubernetes Resource unit formats. For more information, see
    https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/.

    :param cpu: The CPU resource settings for a container.
    :type cpu: Optional[str]
    :param memory: The memory resource settings for a container.
    :type memory: Optional[str]
    :param gpu: The GPU resource settings for a container.
    :type gpu: Optional[str]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_misc.py
            :start-after: [START resource_requirements_configuration]
            :end-before: [END resource_requirements_configuration]
            :language: python
            :dedent: 8
            :caption: Configuring ResourceSettings for a Kubernetes deployment.
    """

    def __init__(self, cpu: Optional[str] = None, memory: Optional[str] = None, gpu: Optional[str] = None) -> None:
        self.cpu = cpu
        self.memory = memory
        self.gpu = gpu

    def _to_rest_object(self) -> ContainerResourceSettings:
        return ContainerResourceSettings(cpu=self.cpu, memory=self.memory, gpu=self.gpu)

    @classmethod
    def _from_rest_object(cls, settings: ContainerResourceSettings) -> Optional["ResourceSettings"]:
        return (
            ResourceSettings(
                cpu=settings.cpu,
                memory=settings.memory,
                gpu=settings.gpu,
            )
            if settings
            else None
        )

    def _merge_with(self, other: Optional["ResourceSettings"]) -> None:
        if other:
            self.cpu = other.cpu or self.cpu
            self.memory = other.memory or self.memory
            self.gpu = other.gpu or self.gpu

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ResourceSettings):
            return NotImplemented
        if not other:
            return False
        # only compare mutable fields
        return self.cpu == other.cpu and self.memory == other.memory and self.gpu == other.gpu

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
