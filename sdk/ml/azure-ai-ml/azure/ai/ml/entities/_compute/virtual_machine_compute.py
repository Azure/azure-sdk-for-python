# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from pathlib import Path
from typing import Dict, Optional

from azure.ai.ml._restclient.v2022_10_01_preview.models import ComputeResource
from azure.ai.ml._restclient.v2022_10_01_preview.models import VirtualMachine as VMResource
from azure.ai.ml._restclient.v2022_10_01_preview.models import (
    VirtualMachineSchemaProperties,
    VirtualMachineSshCredentials,
)
from azure.ai.ml._schema.compute.virtual_machine_compute import VirtualMachineComputeSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, TYPE
from azure.ai.ml.constants._compute import ComputeType
from azure.ai.ml.entities._compute.compute import Compute
from azure.ai.ml.entities._util import load_from_dict


class VirtualMachineSshSettings:
    def __init__(
        self,
        *,
        admin_username: str,
        admin_password: str = None,
        ssh_port: int = 22,
        ssh_private_key_file: str = None,
    ):
        """SSH settings for a virtual machine.

        :param admin_username:  Describes the admin user name., defaults to None.
        :type admin_username: str, required
        :param admin_password: Describes the admin user password.
            Defaults to None. Required if ssh_private_key_file is not specified.
        :type admin_password: str, optional
        :param ssh_port: The ssh port number. Default is 22.
        :type ssh_port: str, optional
        :param ssh_private_key_file: Specifies the file containing SSH rsa private key.
            Use "ssh-keygen -t rsa -b 2048" to generate your SSH key pairs.
            Required if admin_password is not specified.
        :type ssh_private_key_file: str, optional
        """
        self.admin_username = admin_username
        self.admin_password = admin_password
        self.ssh_port = ssh_port
        self.ssh_private_key_file = ssh_private_key_file


class VirtualMachineCompute(Compute):
    """Virtual Machine Compute resource.

    :param name: Name of the compute
    :type name: str
    :param description: Description of the resource.
    :type description: Optional[str], optional
    :param resource_id: ARM resource id of the underlying compute
    :type resource_id: str
    :param ssh_settings: SSH settings.
    :type ssh_settings: VirtualMachineSshSettings, optional
    """

    def __init__(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        resource_id: str,
        ssh_settings: VirtualMachineSshSettings = None,
        **kwargs,
    ):
        kwargs[TYPE] = ComputeType.VIRTUALMACHINE
        self._public_key_data = kwargs.pop("public_key_data", None)
        super().__init__(
            name=name,
            location=kwargs.pop("location", None),
            description=description,
            resource_id=resource_id,
            **kwargs,
        )
        self.ssh_settings = ssh_settings

    @property
    def public_key_data(self) -> str:
        """Public key data.

        return: Public key data.
        rtype: str
        """
        return self._public_key_data

    @classmethod
    def _load_from_rest(cls, rest_obj: ComputeResource) -> "VirtualMachineCompute":
        prop = rest_obj.properties
        credentials = prop.properties.administrator_account if prop.properties else None
        ssh_settings_param = None
        if credentials or (prop.properties and prop.properties.ssh_port):
            ssh_settings_param = VirtualMachineSshSettings(
                admin_username=credentials.username if credentials else None,
                admin_password=credentials.password if credentials else None,
                ssh_port=prop.properties.ssh_port if prop.properties else None,
            )
        response = VirtualMachineCompute(
            name=rest_obj.name,
            id=rest_obj.id,
            description=prop.description,
            location=rest_obj.location,
            resource_id=prop.resource_id,
            public_key_data=credentials.public_key_data if credentials else None,
            provisioning_state=prop.provisioning_state,
            provisioning_errors=prop.provisioning_errors[0].error.code
            if (prop.provisioning_errors and len(prop.provisioning_errors) > 0)
            else None,
            ssh_settings=ssh_settings_param,
        )
        return response

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return VirtualMachineComputeSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, **kwargs) -> "VirtualMachineCompute":
        loaded_data = load_from_dict(VirtualMachineComputeSchema, data, context, **kwargs)
        return VirtualMachineCompute(**loaded_data)

    def _to_rest_object(self) -> ComputeResource:
        ssh_key_value = None
        if self.ssh_settings and self.ssh_settings.ssh_private_key_file:
            ssh_key_value = Path(self.ssh_settings.ssh_private_key_file).read_text()
        credentials = VirtualMachineSshCredentials(
            username=self.ssh_settings.admin_username if self.ssh_settings else None,
            password=self.ssh_settings.admin_password if self.ssh_settings else None,
            public_key_data=self.public_key_data,
            private_key_data=ssh_key_value,
        )
        properties = VirtualMachineSchemaProperties(
            ssh_port=self.ssh_settings.ssh_port,
            administrator_account=credentials
        )
        vm_compute = VMResource(
            properties=properties,
            resource_id=self.resource_id,
            description=self.description,
        )
        resource = ComputeResource(name=self.name, location=self.location, properties=vm_compute)
        return resource
