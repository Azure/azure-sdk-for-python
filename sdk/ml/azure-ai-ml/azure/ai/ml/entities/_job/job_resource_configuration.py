# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import logging
from typing import Any, Dict, Optional

from azure.ai.ml._restclient.v2022_10_01_preview.models import JobResourceConfiguration as RestJobResourceConfiguration
from azure.ai.ml.constants._job.job import JobComputePropertyFields
from azure.ai.ml.entities._mixins import DictMixin, RestTranslatableMixin
from azure.ai.ml.entities._util import convert_ordered_dict_to_dict

module_logger = logging.getLogger(__name__)


class BaseProperty(dict):
    """Base class for entity classes to be used as value of JobResourceConfiguration.properties."""

    def __init__(self, **kwargs: Any):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __setattr__(self, key: str, value: Any) -> None:
        if key.startswith("_"):
            super().__setattr__(key, value)
        else:
            self[key] = value

    def __getattr__(self, key: str) -> Any:
        if key.startswith("_"):
            super().__getattribute__(key)
        else:
            return self[key]

    def __repr__(self) -> str:
        return json.dumps(self.as_dict())

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, dict):
            return self.as_dict() == other
        if isinstance(other, BaseProperty):
            return self.as_dict() == other.as_dict()
        return False

    def as_dict(self) -> Dict[str, Any]:
        """Return a dict representation of the object."""
        return self._to_dict(self)

    @classmethod
    def _to_dict(cls, obj: Any) -> Any:
        if isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                if value is None:
                    continue
                if isinstance(value, dict):
                    result[key] = cls._to_dict(value)
                else:
                    result[key] = value
            return result
        return obj


class Properties(BaseProperty):
    # pre-defined properties are case-insensitive
    # Map Singularity -> AISupercomputer in SDK until MFE does mapping
    _KEY_MAPPING = {
        JobComputePropertyFields.AISUPERCOMPUTER.lower(): JobComputePropertyFields.AISUPERCOMPUTER,
        JobComputePropertyFields.SINGULARITY.lower(): JobComputePropertyFields.AISUPERCOMPUTER,
        JobComputePropertyFields.ITP.lower(): JobComputePropertyFields.ITP,
        JobComputePropertyFields.TARGET_SELECTOR.lower(): JobComputePropertyFields.TARGET_SELECTOR,
    }

    def as_dict(self) -> Dict[str, Any]:
        result = {}
        for key, value in super().as_dict().items():
            if key.lower() in self._KEY_MAPPING:
                key = self._KEY_MAPPING[key.lower()]
            result[key] = value
        # recursively convert Ordered Dict to dictionary
        return convert_ordered_dict_to_dict(result)


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
    ):  # pylint: disable=unused-argument
        self.instance_count = instance_count
        self.instance_type = instance_type
        self.shm_size = shm_size
        self.docker_args = docker_args
        self._properties = None
        self.properties = properties

    @property
    def properties(self) -> Properties:
        return self._properties

    @properties.setter
    def properties(self, properties: Dict[str, Any]):
        if properties is None:
            self._properties = Properties()
        elif isinstance(properties, dict):
            self._properties = Properties(**properties)
        else:
            raise TypeError("properties must be a dict.")

    def _to_rest_object(self) -> RestJobResourceConfiguration:
        return RestJobResourceConfiguration(
            instance_count=self.instance_count,
            instance_type=self.instance_type,
            properties=self.properties.as_dict(),
            docker_args=self.docker_args,
            shm_size=self.shm_size,
        )

    @classmethod
    def _from_rest_object(cls, obj: Optional[RestJobResourceConfiguration]) -> Optional["JobResourceConfiguration"]:
        if obj is None:
            return None
        return JobResourceConfiguration(
            instance_count=obj.instance_count,
            instance_type=obj.instance_type,
            properties=obj.properties,
            docker_args=obj.docker_args,
            shm_size=obj.shm_size,
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
