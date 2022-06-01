# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List
from azure.ai.ml._restclient.v2022_01_01_preview.models import VirtualMachineSize
from azure.ai.ml._schema.compute.vm_size import VmSizeSchema
from azure.ai.ml.entities import Resource
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from typing import Dict, Union
from os import PathLike
from azure.ai.ml.constants import (
    BASE_PATH_CONTEXT_KEY,
    PARAMS_OVERRIDE_KEY,
    CommonYamlFields,
)


class VmSize(Resource, RestTranslatableMixin):
    """virtual Machine Size"""

    def __init__(
        self,
        name: str = None,
        family: str = None,
        v_cp_us: int = None,
        gpus: int = None,
        os_vhd_size_mb: int = None,
        max_resource_volume_mb: int = None,
        memory_gb: float = None,
        low_priority_capable: bool = None,
        premium_io: bool = None,
        supported_compute_types: List[str] = None,
        **kwargs,
    ):
        """Virtual machine size
        :param name: The name of the virtual machine size.
        :type name: str
        :param family: The family name of the virtual machine size.
        :type family: str
        :param v_cp_us: The number of vCPUs supported by the virtual machine size.
        :type v_cp_us: int
        :param gpus: The number of gPUs supported by the virtual machine size.
        :type gpus: int
        :param os_vhd_size_mb: The OS VHD disk size, in MB, allowed by the virtual machine size.
        :type os_vhd_size_mb: int
        :prarm max_resource_volume_mb: The resource volume size, in MB, allowed by the virtual machine
        size.
        :type max_resource_volume_mb: int
        :param memory_gb: The amount of memory, in GB, supported by the virtual machine size.
        :type memory_gb: float
        :param low_priority_capable: Specifies if the virtual machine size supports low priority VMs.
        :type low_priority_capable: bool
        :param premium_io: Specifies if the virtual machine size supports premium IO.
        :type premium_io: bool
        :param estimated_vm_prices: The estimated price information for using a VM.
        :type estimated_vm_prices: ~azure.mgmt.machinelearningservices.models.EstimatedVMPrices
        :param supported_compute_types: Specifies the compute types supported by the virtual machine
        size.
        :type supported_compute_types: list[str]
        """

        self.name = name
        self.family = family
        self.v_cp_us = v_cp_us
        self.gpus = gpus
        self.os_vhd_size_mb = os_vhd_size_mb
        self.max_resource_volume_mb = max_resource_volume_mb
        self.memory_gb = memory_gb
        self.low_priority_capable = low_priority_capable
        self.premium_io = premium_io
        self.supported_compute_types = ",".join(map(str, supported_compute_types)) if supported_compute_types else None

    @classmethod
    def _from_rest_object(cls, rest_obj: VirtualMachineSize) -> "VmSize":
        result = cls()
        result.__dict__.update(rest_obj.as_dict())
        return result

    def dump(self, path: Union[PathLike, str]) -> None:
        """Dump the virtual machine size content into a file in yaml format.

        :param path: Path to a local file as the target, new file will be created, raises exception if the file exists.
        :type path: str
        """

        yaml_serialized = self._to_dict()
        dump_yaml_to_file(path, yaml_serialized, default_flow_style=False)

    def _to_dict(self) -> Dict:
        return VmSizeSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    @classmethod
    def load(
        cls,
        path: Union[PathLike, str],
        params_override: list = None,
        **kwargs,
    ) -> "VmSize":

        pass
