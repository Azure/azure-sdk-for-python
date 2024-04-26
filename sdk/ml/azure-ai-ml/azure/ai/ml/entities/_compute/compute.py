# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from abc import abstractmethod
from os import PathLike
from pathlib import Path
from typing import IO, Any, AnyStr, Dict, Optional, Union, cast

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
    """Base class for compute resources.

    This class should not be instantiated directly. Instead, use one of its subclasses.

    :param type: The compute type. Accepted values are "amlcompute", "computeinstance",
        "virtualmachine", "kubernetes", and "synapsespark".
    :type type: str
    :param name: Name of the compute resource.
    :type name: str
    :param location: The resource location. Defaults to workspace location.
    :type location: Optional[str]
    :param description: Description of the resource. Defaults to None.
    :type description: Optional[str]
    :param resource_id: ARM resource id of the underlying compute. Defaults to None.
    :type resource_id: Optional[str]
    :param tags: A set of tags. Contains resource tags defined as key/value pairs.
    :type tags: Optional[dict[str, str]]
    """

    def __init__(
        self,
        name: str,
        location: Optional[str] = None,
        description: Optional[str] = None,
        resource_id: Optional[str] = None,
        tags: Optional[Dict] = None,
        **kwargs: Any,
    ) -> None:
        self._type: Optional[str] = kwargs.pop("type", None)
        if self._type:
            self._type = self._type.lower()

        self._created_on: Optional[str] = kwargs.pop("created_on", None)
        self._provisioning_state: Optional[str] = kwargs.pop("provisioning_state", None)
        self._provisioning_errors: Optional[str] = kwargs.pop("provisioning_errors", None)

        super().__init__(name=name, description=description, **kwargs)
        self.resource_id = resource_id
        self.location = location
        self.tags = tags

    @property
    def type(self) -> Optional[str]:
        """The compute type.

        :return: The compute type.
        :rtype: Optional[str]
        """
        return self._type

    @property
    def created_on(self) -> Optional[str]:
        """The compute resource creation timestamp.

        :return: The compute resource creation timestamp.
        :rtype: Optional[str]
        """
        return self._created_on

    @property
    def provisioning_state(self) -> Optional[str]:
        """The compute resource's provisioning state.

        :return: The compute resource's provisioning state.
        :rtype: Optional[str]
        """
        return self._provisioning_state

    @property
    def provisioning_errors(self) -> Optional[str]:
        """The compute resource provisioning errors.

        :return: The compute resource provisioning errors.
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

        class_type = cast(
            Optional[Union[AmlCompute, ComputeInstance, VirtualMachineCompute, KubernetesCompute, SynapseSparkCompute]],
            mapping.get(compute_type, None),
        )
        if class_type:
            return class_type._load_from_rest(obj)
        _unsupported_from_rest: Compute = UnsupportedCompute._load_from_rest(obj)
        return _unsupported_from_rest

    @classmethod
    @abstractmethod
    def _load_from_rest(cls, rest_obj: ComputeResource) -> "Compute":
        pass

    def _set_full_subnet_name(self, subscription_id: str, rg: str) -> None:
        pass

    def dump(self, dest: Union[str, PathLike, IO[AnyStr]], **kwargs: Any) -> None:
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
        res: dict = ComputeSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs: Any,
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
                _vm_load_from_dict: Compute = VirtualMachineCompute._load_from_dict(data, context, **kwargs)
                return _vm_load_from_dict
            if compute_type.lower() == ComputeType.AMLCOMPUTE:
                _aml_load_from_dict: Compute = AmlCompute._load_from_dict(data, context, **kwargs)
                return _aml_load_from_dict
            if compute_type.lower() == ComputeType.COMPUTEINSTANCE:
                _compute_instance_load_from_dict: Compute = ComputeInstance._load_from_dict(data, context, **kwargs)
                return _compute_instance_load_from_dict
            if compute_type.lower() == ComputeType.KUBERNETES:
                _kub_load_from_dict: Compute = KubernetesCompute._load_from_dict(data, context, **kwargs)
                return _kub_load_from_dict
            if compute_type.lower() == ComputeType.SYNAPSESPARK:
                _synapse_spark_load_from_dict: Compute = SynapseSparkCompute._load_from_dict(data, context, **kwargs)
                return _synapse_spark_load_from_dict
        msg = f"Unknown compute type: {compute_type}"
        raise ValidationException(
            message=msg,
            target=ErrorTarget.COMPUTE,
            no_personal_data_message=msg,
            error_category=ErrorCategory.USER_ERROR,
        )

    @classmethod
    @abstractmethod
    def _load_from_dict(cls, data: Dict, context: Dict, **kwargs: Any) -> "Compute":
        pass


class NetworkSettings:
    """Network settings for a compute resource. If the workspace and VNet are in different resource groups,
    please provide the full URI for subnet and leave vnet_name as None.

    :param vnet_name: The virtual network name.
    :type vnet_name: Optional[str]
    :param subnet: The subnet name.
    :type subnet: Optional[str]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_compute.py
            :start-after: [START network_settings]
            :end-before: [END network_settings]
            :language: python
            :dedent: 8
            :caption: Configuring NetworkSettings for an AmlCompute object.
    """

    def __init__(
        self,
        *,
        vnet_name: Optional[str] = None,
        subnet: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.vnet_name = vnet_name
        self.subnet = subnet
        self._public_ip_address: str = kwargs.pop("public_ip_address", None)
        self._private_ip_address: str = kwargs.pop("private_ip_address", None)

    @property
    def public_ip_address(self) -> str:
        """Public IP address of the compute instance.

        :return: Public IP address.
        :rtype: str
        """
        return self._public_ip_address

    @property
    def private_ip_address(self) -> str:
        """Private IP address of the compute instance.

        :return: Private IP address.
        :rtype: str
        """
        return self._private_ip_address
