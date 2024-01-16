# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
from typing import Optional

from azure.ai.ml._restclient.v2022_05_01.models import ContainerResourceRequirements
from azure.ai.ml.entities._deployment.container_resource_settings import ResourceSettings
from azure.ai.ml.entities._mixins import RestTranslatableMixin

module_logger = logging.getLogger(__name__)


class ResourceRequirementsSettings(RestTranslatableMixin):
    """Resource requirements settings for a container.

    :param requests: The minimum resource requests for a container.
    :type requests: Optional[~azure.ai.ml.entities.ResourceSettings]
    :param limits: The resource limits for a container.
    :type limits: Optional[~azure.ai.ml.entities.ResourceSettings]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_misc.py
            :start-after: [START resource_requirements_configuration]
            :end-before: [END resource_requirements_configuration]
            :language: python
            :dedent: 8
            :caption: Configuring ResourceRequirementSettings for a Kubernetes deployment.
    """

    def __init__(
        self,
        requests: Optional[ResourceSettings] = None,
        limits: Optional[ResourceSettings] = None,
    ) -> None:
        self.requests = requests
        self.limits = limits

    def _to_rest_object(self) -> ContainerResourceRequirements:
        return ContainerResourceRequirements(
            container_resource_requests=self.requests._to_rest_object() if self.requests else None,
            container_resource_limits=self.limits._to_rest_object() if self.limits else None,
        )

    @classmethod
    def _from_rest_object(  # pylint: disable=arguments-renamed
        cls, settings: ContainerResourceRequirements
    ) -> Optional["ResourceRequirementsSettings"]:
        requests = settings.container_resource_requests
        limits = settings.container_resource_limits
        return (
            ResourceRequirementsSettings(
                requests=ResourceSettings._from_rest_object(requests),
                limits=ResourceSettings._from_rest_object(limits),
            )
            if settings
            else None
        )

    def _merge_with(self, other: Optional["ResourceRequirementsSettings"]) -> None:
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
