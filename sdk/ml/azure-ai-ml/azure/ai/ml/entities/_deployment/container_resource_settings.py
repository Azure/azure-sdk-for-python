# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging

from azure.ai.ml._restclient.v2021_10_01.models import ContainerResourceSettings
from azure.ai.ml.entities._mixins import RestTranslatableMixin

module_logger = logging.getLogger(__name__)


class ResourceSettings(RestTranslatableMixin):
    def __init__(self, cpu: str = None, memory: str = None, gpu: str = None):
        self.cpu = cpu
        self.memory = memory
        self.gpu = gpu

    def _to_rest_object(self) -> ContainerResourceSettings:
        return ContainerResourceSettings(cpu=self.cpu, memory=self.memory, gpu=self.gpu)

    @classmethod
    def _from_rest_object(cls, settings: ContainerResourceSettings) -> "ResourceSettings":

        return (
            ResourceSettings(
                cpu=settings.cpu,
                memory=settings.memory,
                gpu=settings.gpu,
            )
            if settings
            else None
        )

    def _merge_with(self, other: "ResourceSettings") -> None:
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
