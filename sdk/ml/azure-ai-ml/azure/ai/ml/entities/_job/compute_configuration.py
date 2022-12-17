# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import logging
from typing import Any, Dict, Optional

from azure.ai.ml._restclient.v2020_09_01_dataplanepreview.models import ComputeConfiguration as RestComputeConfiguration
from azure.ai.ml.constants._common import LOCAL_COMPUTE_TARGET
from azure.ai.ml.constants._job.job import JobComputePropertyFields
from azure.ai.ml.entities._mixins import DictMixin, RestTranslatableMixin

module_logger = logging.getLogger(__name__)


class ComputeConfiguration(RestTranslatableMixin, DictMixin):
    def __init__(
        self,
        *,
        target: Optional[str] = None,
        instance_count: Optional[int] = None,
        is_local: Optional[bool] = None,
        instance_type: Optional[str] = None,
        location: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        deserialize_properties: bool = False,
    ):
        self.instance_count = instance_count
        self.target = target or LOCAL_COMPUTE_TARGET
        self.is_local = is_local or self.target == LOCAL_COMPUTE_TARGET
        self.instance_type = instance_type
        self.location = location
        self.properties = properties
        if deserialize_properties and properties:
            for key, value in self.properties.items():
                try:
                    self.properties[key] = json.loads(value)
                except Exception:  # pylint: disable=broad-except
                    # keep serialized string if load fails
                    pass

    def _to_rest_object(self) -> RestComputeConfiguration:
        if self.properties:
            serialized_properties = {}
            for key, value in self.properties.items():
                try:
                    if key.lower() == JobComputePropertyFields.SINGULARITY.lower():
                        # Map Singularity -> AISupercomputer in SDK until MFE does mapping
                        key = JobComputePropertyFields.AISUPERCOMPUTER
                    # Ensure keymatch is case invariant
                    elif key.lower() == JobComputePropertyFields.AISUPERCOMPUTER.lower():
                        key = JobComputePropertyFields.AISUPERCOMPUTER
                    serialized_properties[key] = json.dumps(value)
                except Exception:  # pylint: disable=broad-except
                    pass
        else:
            serialized_properties = None
        return RestComputeConfiguration(
            target=self.target if not self.is_local else None,
            is_local=self.is_local,
            instance_count=self.instance_count,
            instance_type=self.instance_type,
            location=self.location,
            properties=serialized_properties,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestComputeConfiguration) -> "ComputeConfiguration":
        return ComputeConfiguration(
            target=obj.target,
            is_local=obj.is_local,
            instance_count=obj.instance_count,
            location=obj.location,
            instance_type=obj.instance_type,
            properties=obj.properties,
            deserialize_properties=True,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ComputeConfiguration):
            return NotImplemented
        return (
            self.instance_count == other.instance_count
            and self.target == other.target
            and self.is_local == other.is_local
            and self.location == other.location
            and self.instance_type == other.instance_type
        )

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, ComputeConfiguration):
            return NotImplemented
        return not self.__eq__(other)
