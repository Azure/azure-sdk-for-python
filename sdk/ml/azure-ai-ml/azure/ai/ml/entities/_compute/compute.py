# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from abc import abstractclassmethod
from os import PathLike
from pathlib import Path
from typing import IO, AnyStr, Dict, Optional, Union

from azure.ai.ml._restclient.v2022_10_01_preview.models import ComputeResource
from azure.ai.ml._schema.compute.compute import ComputeSchema
from azure.ai.ml._utils.utils import dump_yaml_to_file
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY, CommonYamlFields
from azure.ai.ml.constants._compute import ComputeType
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.entities._util import find_type_in_override
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException


class Compute(Resource, RestTranslatableMixin):
    """Compute resource.

    :param type: The type of the compute, possible values are
        ["amlcompute", "computeinstance", "virtualmachine", "kubernetes", "synapsespark"]
    :type type: str
    :param name: Name of the compute
    :type name: str
    :param location: The resource location, defaults to workspace location.
    :type location: Optional[str], optional
    :param description: Description of the resource.
    :type description: Optional[str], optional
    :param resource_id: ARM resource id of the underlying compute.
    :type resource_id: str, optional
    :param tags: A set of tags. Contains resource tags defined as key/value pairs.
    :type tags: Optional[dict[str, str]]
    """

    def __init__(
        self,
        name: str,
        location: Optional[str] = None,
        description: Optional[str] = None,
        resource_id: Optional[str] = None,
        tags: Optional[dict] = None,
        **kwargs,
    ):
        self._type = kwargs.pop("type", None)
        if self._type:
            self._type = self._type.lower()

        self._created_on = kwargs.pop("created_on", None)
        self._provisioning_state = kwargs.pop("provisioning_state", None)
        self._provisioning_errors = kwargs.pop("provisioning_errors", None)

        super().__init__(name=name, description=description, **kwargs)
        self.resource_id = resource_id
        self.location = location
        self.tags = tags

    @property
    def type(self) -> Optional[str]:
        """The type of the compute, possible values are ["amlcompute", "computeinstance", "virtualmachine",
        "kubernetes", "synapsespark"]

        :return: The type of the compute
        :rtype: Optional[str]
        """
        return self._type

    @property
    def created_on(self) -> Optional[str]:
        """Creation timestamp.

        :return: [description]
        :rtype: Optional[str]
        """
        return self._created_on

    @property
    def provisioning_state(self) -> Optional[str]:
        """Provisioning state.

        :return: [description]
        :rtype: Optional[str]
        """
        return self._provisioning_state

    @property
    def provisioning_errors(self) -> Optional[str]:
        """Provisioning errors.

        :return: [description]
        :rtype: Optional[str]
        """
        return self._provisioning_errors

    def _to_rest_object(self) -> ComputeResource:
        pass

    @classmethod
    def _from_rest_object(cls, obj: ComputeResource) -> "Compute":
        from azure.ai.ml.entities import (
            AmlCompute,
            ComputeInstance,
            KubernetesCompute,
            SynapseSparkCompute,
            UnsupportedCompute,
            VirtualMachineCompute,
        )

        mapping = {
            ComputeType.AMLCOMPUTE.lower(): AmlCompute,
            ComputeType.COMPUTEINSTANCE.lower(): ComputeInstance,
            ComputeType.VIRTUALMACHINE.lower(): VirtualMachineCompute,
            ComputeType.KUBERNETES.lower(): KubernetesCompute,
            ComputeType.SYNAPSESPARK.lower(): SynapseSparkCompute,
        }
        compute_type = obj.properties.compute_type.lower() if obj.properties.compute_type else None

        class_type = mapping.get(compute_type, None)
        if class_type:
            return class_type._load_from_rest(obj)
        return UnsupportedCompute._load_from_rest(obj)

    @abstractclassmethod
    def _load_from_rest(cls, rest_obj: ComputeResource) -> "Compute":
        pass

    def _set_full_subnet_name(self, subscription_id: str, rg: str) -> None:
        pass

    def dump(self, dest: Union[str, PathLike, IO[AnyStr]], **kwargs) -> None:
        """Dump the compute content into a file in yaml format.

        :param dest: The destination to receive this compute's content.
            Must be either a path to a local file, or an already-open file stream.
            If dest is a file path, a new file will be created,
            and an exception is raised if the file exists.
            If dest is an open file, the file will be written to directly,
            and an exception will be raised if the file is not writable.'.
        :type dest: Union[PathLike, str, IO[AnyStr]]
        """
        path = kwargs.pop("path", None)
        yaml_serialized = self._to_dict()
        dump_yaml_to_file(dest, yaml_serialized, default_flow_style=False, path=path, **kwargs)

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return ComputeSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs,
    ) -> "Compute":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        from azure.ai.ml.entities import (
            AmlCompute,
            ComputeInstance,
            KubernetesCompute,
            SynapseSparkCompute,
            VirtualMachineCompute,
        )

        type_in_override = find_type_in_override(params_override) if params_override else None
        compute_type = type_in_override or data.get(CommonYamlFields.TYPE, None)  # override takes the priority
        if compute_type:
            if compute_type.lower() == ComputeType.VIRTUALMACHINE:
                return VirtualMachineCompute._load_from_dict(data, context, **kwargs)
            if compute_type.lower() == ComputeType.AMLCOMPUTE:
                return AmlCompute._load_from_dict(data, context, **kwargs)
            if compute_type.lower() == ComputeType.COMPUTEINSTANCE:
                return ComputeInstance._load_from_dict(data, context, **kwargs)
            if compute_type.lower() == ComputeType.KUBERNETES:
                return KubernetesCompute._load_from_dict(data, context, **kwargs)
            if compute_type.lower() == ComputeType.SYNAPSESPARK:
                return SynapseSparkCompute._load_from_dict(data, context, **kwargs)
        msg = f"Unknown compute type: {compute_type}"
        raise ValidationException(
            message=msg,
            target=ErrorTarget.COMPUTE,
            no_personal_data_message=msg,
            error_category=ErrorCategory.USER_ERROR,
        )

    @abstractclassmethod
    def _load_from_dict(cls, data: Dict, context: Dict, **kwargs) -> "Compute":
        pass
