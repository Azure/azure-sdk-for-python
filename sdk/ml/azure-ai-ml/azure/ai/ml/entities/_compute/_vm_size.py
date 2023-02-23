# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from os import PathLike
from typing import IO, AnyStr, Dict, List, Optional, Union

from azure.ai.ml._restclient.v2022_10_01_preview.models import VirtualMachineSize
from azure.ai.ml._schema.compute.vm_size import VmSizeSchema
from azure.ai.ml._utils.utils import dump_yaml_to_file
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class VmSize(RestTranslatableMixin):
    """virtual Machine Size."""

    def __init__(
        self,
        name: Optional[str] = None,
        family: Optional[str] = None,
        v_cp_us: Optional[int] = None,
        gpus: Optional[int] = None,
        os_vhd_size_mb: Optional[int] = None,
        max_resource_volume_mb: Optional[int] = None,
        memory_gb: Optional[float] = None,
        low_priority_capable: Optional[bool] = None,
        premium_io: Optional[bool] = None,
        supported_compute_types: Optional[List[str]] = None,
    ):
        """Virtual machine size.

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
        :param max_resource_volume_mb: The resource volume size, in MB, allowed by the virtual machine
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
    def _from_rest_object(cls, obj: VirtualMachineSize) -> "VmSize":
        result = cls()
        result.__dict__.update(obj.as_dict())
        return result

    def dump(self, dest: Union[str, PathLike, IO[AnyStr]], **kwargs) -> None:
        """Dump the virtual machine size content into a file in yaml format.

        :param dest: The destination to receive this virtual machine size's content.
            Must be either a path to a local file, or an already-open file stream.
            If dest is a file path, a new file will be created,
            and an exception is raised if the file exists.
            If dest is an open file, the file will be written to directly,
            and an exception will be raised if the file is not writable.
        :type dest: Union[PathLike, str, IO[AnyStr]]
        """

        path = kwargs.pop("path", None)
        yaml_serialized = self._to_dict()
        dump_yaml_to_file(dest, yaml_serialized, default_flow_style=False, path=path, **kwargs)

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return VmSizeSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    @classmethod
    def _load(
        cls,
        path: Union[PathLike, str],
        params_override: Optional[list] = None,
        **kwargs,
    ) -> "VmSize":
        pass
