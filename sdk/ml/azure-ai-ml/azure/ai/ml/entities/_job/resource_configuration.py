# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import logging
from typing import Any, Dict, Optional

from azure.ai.ml._restclient.v2023_04_01_preview.models import ResourceConfiguration as RestResourceConfiguration
from azure.ai.ml.constants._job.job import JobComputePropertyFields
from azure.ai.ml.entities._mixins import DictMixin, RestTranslatableMixin

module_logger = logging.getLogger(__name__)


class ResourceConfiguration(RestTranslatableMixin, DictMixin):
    """Resource configuration for a job.

    This class should not be instantiated directly. Instead, use its subclasses.

    :keyword instance_count: The number of instances to use for the job.
    :paramtype instance_count: Optional[int]
    :keyword instance_type: The type of instance to use for the job.
    :paramtype instance_type: Optional[str]
    :keyword properties: The resource's property dictionary.
    :paramtype properties: Optional[dict[str, Any]]
    """

    def __init__(
        self,  # pylint: disable=unused-argument
        *,
        instance_count: Optional[int] = None,
        instance_type: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> None:
        self.instance_count = instance_count
        self.instance_type = instance_type
        self.properties = {}
        if properties is not None:
            for key, value in properties.items():
                if key == JobComputePropertyFields.AISUPERCOMPUTER:
                    self.properties[JobComputePropertyFields.SINGULARITY.lower()] = value
                else:
                    self.properties[key] = value

    def _to_rest_object(self) -> RestResourceConfiguration:
        serialized_properties = {}
        if self.properties:
            for key, value in self.properties.items():
                try:
                    if (
                        key.lower() == JobComputePropertyFields.SINGULARITY.lower()
                        or key.lower() == JobComputePropertyFields.AISUPERCOMPUTER.lower()
                    ):
                        # Map Singularity -> AISupercomputer in SDK until MFE does mapping
                        key = JobComputePropertyFields.AISUPERCOMPUTER
                    # recursively convert Ordered Dict to dictionary
                    serialized_properties[key] = json.loads(json.dumps(value))
                except Exception:  # pylint: disable=W0718
                    pass
        return RestResourceConfiguration(
            instance_count=self.instance_count,
            instance_type=self.instance_type,
            properties=serialized_properties,
        )

    @classmethod
    def _from_rest_object(  # pylint: disable=arguments-renamed
        cls, rest_obj: Optional[RestResourceConfiguration]
    ) -> Optional["ResourceConfiguration"]:
        if rest_obj is None:
            return None
        return ResourceConfiguration(
            instance_count=rest_obj.instance_count,
            instance_type=rest_obj.instance_type,
            properties=rest_obj.properties,
            deserialize_properties=True,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ResourceConfiguration):
            return NotImplemented
        return self.instance_count == other.instance_count and self.instance_type == other.instance_type

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, ResourceConfiguration):
            return NotImplemented
        return not self.__eq__(other)

    def _merge_with(self, other: "ResourceConfiguration") -> None:
        if other:
            if other.instance_count:
                self.instance_count = other.instance_count
            if other.instance_type:
                self.instance_type = other.instance_type
            if other.properties:
                self.properties = other.properties
