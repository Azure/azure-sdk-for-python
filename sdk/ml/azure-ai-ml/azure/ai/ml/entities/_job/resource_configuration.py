# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import json
from typing import Dict, Any, Optional
from azure.ai.ml.constants import JobComputePropertyFields
from azure.ai.ml._restclient.v2021_10_01.models import ResourceConfiguration as RestResourceConfiguration
from azure.ai.ml.entities._mixins import RestTranslatableMixin, DictMixin


module_logger = logging.getLogger(__name__)


class ResourceConfiguration(RestTranslatableMixin, DictMixin):
    def __init__(
        self, *, instance_count: int = None, instance_type: str = None, properties: Dict[str, Any] = None, **kwargs
    ):
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
                except Exception:
                    pass
        return RestResourceConfiguration(
            instance_count=self.instance_count,
            instance_type=self.instance_type,
            properties=serialized_properties,
        )

    @classmethod
    def _from_rest_object(cls, rest_obj: Optional[RestResourceConfiguration]) -> Optional["ResourceConfiguration"]:
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
