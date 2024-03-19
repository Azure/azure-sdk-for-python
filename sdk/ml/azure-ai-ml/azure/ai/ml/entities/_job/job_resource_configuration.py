# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import logging
from typing import Any, Dict, List, Optional, Union, cast

from azure.ai.ml._restclient.v2023_04_01_preview.models import JobResourceConfiguration as RestJobResourceConfiguration
from azure.ai.ml.constants._job.job import JobComputePropertyFields
from azure.ai.ml.entities._mixins import DictMixin, RestTranslatableMixin
from azure.ai.ml.entities._util import convert_ordered_dict_to_dict

module_logger = logging.getLogger(__name__)


class BaseProperty(dict):
    """Base class for entity classes to be used as value of JobResourceConfiguration.properties."""

    def __init__(self, **kwargs: Any) -> None:
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
            return None

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
        res: dict = self._to_dict(self)
        return res

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
        return cast(dict, convert_ordered_dict_to_dict(result))


class JobResourceConfiguration(RestTranslatableMixin, DictMixin):
    """Job resource configuration class, inherited and extended functionalities from ResourceConfiguration.

    :keyword locations: A list of locations where the job can run.
    :paramtype locations: Optional[List[str]]
    :keyword instance_count: The number of instances or nodes used by the compute target.
    :paramtype instance_count: Optional[int]
    :keyword instance_type: The type of VM to be used, as supported by the compute target.
    :paramtype instance_type: Optional[str]
    :keyword properties: A dictionary of properties for the job.
    :paramtype properties: Optional[dict[str, Any]]
    :keyword docker_args: Extra arguments to pass to the Docker run command. This would override any
        parameters that have already been set by the system, or in this section. This parameter is only
        supported for Azure ML compute types.
    :paramtype docker_args: Optional[str]
    :keyword shm_size: The size of the docker container's shared memory block. This should be in the
        format of (number)(unit) where the number has to be greater than 0 and the unit can be one of
        b(bytes), k(kilobytes), m(megabytes), or g(gigabytes).
    :paramtype shm_size: Optional[str]
    :keyword max_instance_count: The maximum number of instances or nodes used by the compute target.
    :paramtype max_instance_count: Optional[int]
    :keyword kwargs: A dictionary of additional configuration parameters.
    :paramtype kwargs: dict

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_command_configurations.py
            :start-after: [START command_job_resource_configuration]
            :end-before: [END command_job_resource_configuration]
            :language: python
            :dedent: 8
            :caption: Configuring a CommandJob with a JobResourceConfiguration.
    """

    def __init__(
        self,  # pylint: disable=unused-argument
        *,
        locations: Optional[List[str]] = None,
        instance_count: Optional[int] = None,
        instance_type: Optional[Union[str, List]] = None,
        properties: Optional[Union[Properties, Dict]] = None,
        docker_args: Optional[str] = None,
        shm_size: Optional[str] = None,
        max_instance_count: Optional[int] = None,
        **kwargs: Any
    ) -> None:
        self.locations = locations
        self.instance_count = instance_count
        self.instance_type = instance_type
        self.shm_size = shm_size
        self.max_instance_count = max_instance_count
        self.docker_args = docker_args
        self._properties = None
        self.properties = properties

    @property
    def properties(self) -> Optional[Union[Properties, Dict]]:
        """The properties of the job.

        :rtype: ~azure.ai.ml.entities._job.job_resource_configuration.Properties
        """
        return self._properties

    @properties.setter
    def properties(self, properties: Dict[str, Any]) -> None:
        """Sets the properties of the job.

        :param properties: A dictionary of properties for the job.
        :type properties: Dict[str, Any]
        :raises TypeError: Raised if properties is not a dictionary type.
        """
        if properties is None:
            self._properties = Properties()
        elif isinstance(properties, dict):
            self._properties = Properties(**properties)
        else:
            raise TypeError("properties must be a dict.")

    def _to_rest_object(self) -> RestJobResourceConfiguration:
        return RestJobResourceConfiguration(
            locations=self.locations,
            instance_count=self.instance_count,
            instance_type=self.instance_type,
            max_instance_count=self.max_instance_count,
            properties=self.properties.as_dict() if isinstance(self.properties, Properties) else None,
            docker_args=self.docker_args,
            shm_size=self.shm_size,
        )

    @classmethod
    def _from_rest_object(cls, obj: Optional[RestJobResourceConfiguration]) -> Optional["JobResourceConfiguration"]:
        if obj is None:
            return None
        if isinstance(obj, dict):
            return cls(**obj)
        return JobResourceConfiguration(
            locations=obj.locations,
            instance_count=obj.instance_count,
            instance_type=obj.instance_type,
            max_instance_count=obj.max_instance_count if hasattr(obj, "max_instance_count") else None,
            properties=obj.properties,
            docker_args=obj.docker_args,
            shm_size=obj.shm_size,
            deserialize_properties=True,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, JobResourceConfiguration):
            return NotImplemented
        return (
            self.locations == other.locations
            and self.instance_count == other.instance_count
            and self.instance_type == other.instance_type
            and self.max_instance_count == other.max_instance_count
            and self.docker_args == other.docker_args
            and self.shm_size == other.shm_size
        )

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, JobResourceConfiguration):
            return NotImplemented
        return not self.__eq__(other)

    def _merge_with(self, other: "JobResourceConfiguration") -> None:
        if other:
            if other.locations:
                self.locations = other.locations
            if other.instance_count:
                self.instance_count = other.instance_count
            if other.instance_type:
                self.instance_type = other.instance_type
            if other.max_instance_count:
                self.max_instance_count = other.max_instance_count
            if other.properties:
                self.properties = other.properties
            if other.docker_args:
                self.docker_args = other.docker_args
            if other.shm_size:
                self.shm_size = other.shm_size
