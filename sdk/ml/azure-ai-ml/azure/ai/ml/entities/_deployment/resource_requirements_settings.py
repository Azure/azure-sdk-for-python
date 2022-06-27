# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from azure.ai.ml._restclient.v2021_10_01.models import ContainerResourceRequirements
from azure.ai.ml.entities._deployment.container_resource_settings import ResourceSettings
from azure.ai.ml.entities._mixins import RestTranslatableMixin

module_logger = logging.getLogger(__name__)


class ResourceRequirementsSettings(RestTranslatableMixin):
    def __init__(
        self,
        requests: ResourceSettings = None,
        limits: ResourceSettings = None,
    ):
        self.requests = requests
        self.limits = limits

    def _to_rest_object(self) -> ContainerResourceRequirements:
        return ContainerResourceRequirements(
            container_resource_requests=self.requests._to_rest_object() if self.requests else None,
            container_resource_limits=self.limits._to_rest_object() if self.limits else None,
        )

    @classmethod
    def _from_rest_object(cls, settings: ContainerResourceRequirements) -> "ResourceRequirementsSettings":
        requests = settings.container_resource_requests
        limits = settings.container_resource_limits
        return (
            ResourceRequirementsSettings(
                requests=ResourceSettings._from_rest_object(requests), limits=ResourceSettings._from_rest_object(limits)
            )
            if settings
            else None
        )

    def _merge_with(self, other: "ResourceRequirementsSettings") -> None:
        if other:
            if self.requests:
                self.requests._merge_with(other.requests)
            else:
                self.requests = other.requests
            if self.limits:
                self.limits._merge_with(other.limits)
            else:
                self.limits = other.limits

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ResourceRequirementsSettings):
            return NotImplemented
        if not other:
            return False
        # only compare mutable fields
        return self.requests == other.requests and self.limits == other.limits

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
