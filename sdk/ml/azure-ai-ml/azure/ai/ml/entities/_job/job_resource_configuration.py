# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import logging
from typing import Any, Dict, Optional

from azure.ai.ml._restclient.v2022_06_01_preview.models import JobResourceConfiguration as RestJobResourceConfiguration
from azure.ai.ml.constants._job.job import JobComputePropertyFields
from azure.ai.ml.entities._mixins import DictMixin, RestTranslatableMixin

module_logger = logging.getLogger(__name__)


class JobResourceConfiguration(RestTranslatableMixin, DictMixin):
    """Class for job resource, inherited and extended functionalities from ResourceConfiguration.

    :param instance_count: Optional number of instances or nodes used by the compute target.
    :type instance_count: int
    :param instance_type: Optional type of VM used as supported by the compute target.
    :type instance_type: str
    :param properties: Additional properties bag.
    :type properties: Dict[str, Any]
    :param docker_args: Extra arguments to pass to the Docker run command. This would override any
     parameters that have already been set by the system, or in this section. This parameter is only
     supported for Azure ML compute types.
    :type docker_args: str
    :param shm_size: Size of the docker container's shared memory block. This should be in the
     format of (number)(unit) where number as to be greater than 0 and the unit can be one of
     b(bytes), k(kilobytes), m(megabytes), or g(gigabytes).
    :type shm_size: str
    """

    def __init__(
        self,
        *,
        instance_count: int = None,
        instance_type: str = None,
        properties: Dict[str, Any] = None,
        docker_args: str = None,
        shm_size: str = None,
        **kwargs
    ):
        self.instance_count = instance_count
        self.instance_type = instance_type
        self.shm_size = shm_size
        self.docker_args = docker_args
        self.properties = {}
        if properties is not None:
            for key, value in properties.items():
                if key == JobComputePropertyFields.AISUPERCOMPUTER:
                    self.properties[JobComputePropertyFields.SINGULARITY.lower()] = value
                else:
                    self.properties[key] = value

    def _to_rest_object(self) -> RestJobResourceConfiguration:
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
        return RestJobResourceConfiguration(
            instance_count=self.instance_count,
            instance_type=self.instance_type,
            properties=serialized_properties,
            docker_args=self.docker_args,
            shm_size=self.shm_size,
        )

    @classmethod
    def _from_rest_object(
        cls, rest_obj: Optional[RestJobResourceConfiguration]
    ) -> Optional["JobResourceConfiguration"]:
        if rest_obj is None:
            return None
        return JobResourceConfiguration(
            instance_count=rest_obj.instance_count,
            instance_type=rest_obj.instance_type,
            properties=rest_obj.properties,
            docker_args=rest_obj.docker_args,
            shm_size=rest_obj.shm_size,
            deserialize_properties=True,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, JobResourceConfiguration):
            return NotImplemented
        return (
            self.instance_count == other.instance_count
            and self.instance_type == other.instance_type
            and self.docker_args == other.docker_args
            and self.shm_size == other.shm_size
        )

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, JobResourceConfiguration):
            return NotImplemented
        return not self.__eq__(other)

    def _merge_with(self, other: "JobResourceConfiguration") -> None:
        if other:
            if other.instance_count:
                self.instance_count = other.instance_count
            if other.instance_type:
                self.instance_type = other.instance_type
            if other.properties:
                self.properties = other.properties
            if other.docker_args:
                self.docker_args = other.docker_args
            if other.shm_size:
                self.shm_size = other.shm_size
