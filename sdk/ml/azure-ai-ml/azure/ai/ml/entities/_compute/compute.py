# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import abstractclassmethod
from os import PathLike
from pathlib import Path
from typing import Dict, Optional, Union

from azure.ai.ml._restclient.v2022_01_01_preview.models import ComputeResource
from azure.ai.ml._utils.utils import dump_yaml_to_file, load_yaml
from azure.ai.ml._schema.compute.compute import ComputeSchema
from azure.ai.ml.constants import (
    BASE_PATH_CONTEXT_KEY,
    PARAMS_OVERRIDE_KEY,
    ComputeType,
    CommonYamlFields,
)
from azure.ai.ml.entities import Resource
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.entities._util import find_type_in_override
from azure.ai.ml._ml_exceptions import ValidationException, ErrorCategory, ErrorTarget


class Compute(Resource, RestTranslatableMixin):
    """Compute resource

    :param type: The type of the compute, possible values are ["amlcompute", "computeinstance", "virtualmachine", "kubernetes"]
    :type type: str
    :param name: Name of the compute
    :type name: str
    :param location: The resource location, defaults to None
    :type location: Optional[str], optional
    :param description: Description of the resource.
    :type description: Optional[str], optional
    :param resource_id: ARM resource id of the underlying compute.
    :type resource_id: str, optional
    """

    def __init__(
        self,
        name: str,
        location: Optional[str] = None,
        description: str = None,
        resource_id: str = None,
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

    @property
    def type(self) -> Optional[str]:
        """The type of the compute, possible values are ["amlcompute", "computeinstance", "virtualmachine", "kubernetes"]

        :return: The type of the compute
        :rtype: Optional[str]
        """
        return self._type

    @property
    def created_on(self) -> Optional[str]:
        """Creation timestamp

        :return: [description]
        :rtype: Optional[str]
        """
        return self._created_on

    @property
    def provisioning_state(self) -> Optional[str]:
        """Provisioning state

        :return: [description]
        :rtype: Optional[str]
        """
        return self._provisioning_state

    @property
    def provisioning_errors(self) -> Optional[str]:
        """Provisioning errors

        :return: [description]
        :rtype: Optional[str]
        """
        return self._provisioning_errors

    def _to_rest_object(self) -> ComputeResource:
        pass

    @classmethod
    def _from_rest_object(cls, rest_obj: ComputeResource) -> "Compute":
        from azure.ai.ml.entities import (
            VirtualMachineCompute,
            AmlCompute,
            ComputeInstance,
            UnsupportedCompute,
            KubernetesCompute,
        )

        mapping = {
            ComputeType.AMLCOMPUTE.lower(): AmlCompute,
            ComputeType.COMPUTEINSTANCE.lower(): ComputeInstance,
            ComputeType.VIRTUALMACHINE.lower(): VirtualMachineCompute,
            ComputeType.KUBERNETES.lower(): KubernetesCompute,
        }
        compute_type = rest_obj.properties.compute_type.lower() if rest_obj.properties.compute_type else None

        class_type = mapping.get(compute_type, None)
        if class_type:
            return class_type._load_from_rest(rest_obj)
        else:
            return UnsupportedCompute._load_from_rest(rest_obj)

    @abstractclassmethod
    def _load_from_rest(cls, rest_obj: ComputeResource) -> "Compute":
        pass

    def _set_full_subnet_name(self, subscription_id: str, rg: str) -> None:
        pass

    def dump(self, path: Union[PathLike, str]) -> None:
        """Dump the compute content into a file in yaml format.

        :param path: Path to a local file as the target, new file will be created, raises exception if the file exists.
        :type path: str
        """

        yaml_serialized = self._to_dict()
        dump_yaml_to_file(path, yaml_serialized, default_flow_style=False)

    def _to_dict(self) -> Dict:
        return ComputeSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    @classmethod
    def load(
        cls,
        path: Union[PathLike, str],
        params_override: list = None,
        **kwargs,
    ) -> "Compute":
        """Construct a compute object from a yaml file.

        :param path: Path to a local file as the source.
        :type path: str
        :param params_override: Fields to overwrite on top of the yaml file. Format is [{"field1": "value1"}, {"field2": "value2"}]
        :type params_override: list
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict

        :return: Loaded compute object.
        :rtype: Compute
        """

        data = load_yaml(path)
        return cls._load(data, path, params_override, **kwargs)

    @classmethod
    def _load(
        cls,
        data: Dict = None,
        yaml_path: Union[PathLike, str] = None,
        params_override: list = None,
        **kwargs,
    ) -> "Compute":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        from azure.ai.ml.entities import VirtualMachineCompute, AmlCompute, ComputeInstance, KubernetesCompute

        type_in_override = find_type_in_override(params_override) if params_override else None
        type = type_in_override or data.get(CommonYamlFields.TYPE, None)  # override takes the priority
        if type:
            if type.lower() == ComputeType.VIRTUALMACHINE:
                return VirtualMachineCompute._load_from_dict(data, context, **kwargs)
            elif type.lower() == ComputeType.AMLCOMPUTE:
                return AmlCompute._load_from_dict(data, context, **kwargs)
            elif type.lower() == ComputeType.COMPUTEINSTANCE:
                return ComputeInstance._load_from_dict(data, context, **kwargs)
            elif type.lower() == ComputeType.KUBERNETES:
                return KubernetesCompute._load_from_dict(data, context, **kwargs)
        msg = f"Unknown compute type: {type}"
        raise ValidationException(
            message=msg,
            target=ErrorTarget.COMPUTE,
            no_personal_data_message=msg,
            error_category=ErrorCategory.USER_ERROR,
        )

    @abstractclassmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs) -> "Compute":
        pass


class NetworkSettings:
    def __init__(
        self,
        *,
        vnet_name: str = None,
        subnet: str = None,
        **kwargs,
    ):
        """Network settings for a compute

        :param vnet_name: The virtual network name, defaults to None
        :type vnet_name: str, optional
        :param subnet: The subnet name, defaults to None
        :type subnet: str, optional
        """
        self.vnet_name = vnet_name
        self.subnet = subnet
        self._public_ip_address = kwargs.pop("public_ip_address", None)
        self._private_ip_address = kwargs.pop("private_ip_address", None)

    @property
    def public_ip_address(self) -> str:
        """Public IP address of the compute instance.

        return: Public IP address.
        rtype: str
        """
        return self._public_ip_address

    @property
    def private_ip_address(self) -> str:
        """Private IP address of the compute instance.

        return: Private IP address.
        rtype: str
        """
        return self._private_ip_address
