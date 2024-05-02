# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from pathlib import Path
from typing import Any, Dict, Optional

from azure.ai.ml._restclient.v2022_10_01_preview.models import ComputeResource
from azure.ai.ml._restclient.v2022_10_01_preview.models import VirtualMachine as VMResource
from azure.ai.ml._restclient.v2022_10_01_preview.models import (
    VirtualMachineSchemaProperties,
    VirtualMachineSshCredentials,
)
from azure.ai.ml._schema.compute.virtual_machine_compute import VirtualMachineComputeSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, TYPE, DefaultOpenEncoding
from azure.ai.ml.constants._compute import ComputeType
from azure.ai.ml.entities._compute.compute import Compute
from azure.ai.ml.entities._util import load_from_dict


class VirtualMachineSshSettings:
    """SSH settings for a virtual machine.

    :param admin_username: The admin user name. Defaults to None.
    :type admin_username: str
    :param admin_password: The admin user password. Defaults to None.
        Required if `ssh_private_key_file` is not specified.
    :type admin_password: Optional[str]
    :param ssh_port: The ssh port number. Default is 22.
    :type ssh_port: int
    :param ssh_private_key_file: Path to the file containing the SSH rsa private key.
        Use "ssh-keygen -t rsa -b 2048" to generate your SSH key pairs.
        Required if admin_password is not specified.
    :type ssh_private_key_file: Optional[str]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_compute.py
            :start-after: [START vm_ssh_settings]
            :end-before: [END vm_ssh_settings]
            :language: python
            :dedent: 8
            :caption: Configuring a VirtualMachineSshSettings object.
    """

    def __init__(
        self,
        *,
        admin_username: str,
        admin_password: Optional[str] = None,
        ssh_port: int = 22,
        ssh_private_key_file: Optional[str] = None,
    ) -> None:
        self.admin_username = admin_username
        self.admin_password = admin_password
        self.ssh_port = ssh_port
        self.ssh_private_key_file = ssh_private_key_file


class VirtualMachineCompute(Compute):
    """Virtual Machine Compute resource.

    :param name: Name of the compute resource.
    :type name: str
    :param description: Description of the resource. Defaults to None.
    :type description: Optional[str]
    :param resource_id: ARM resource ID of the underlying compute resource.
    :type resource_id: str
    :param tags: A set of tags. Contains resource tags defined as key/value pairs.
    :type tags: Optional[dict]
    :param ssh_settings: SSH settings. Defaults to None.
    :type ssh_settings: Optional[~azure.ai.ml.entities.VirtualMachineSshSettings]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_compute.py
            :start-after: [START vm_compute]
            :end-before: [END vm_compute]
            :language: python
            :dedent: 8
            :caption: Configuring a VirtualMachineCompute object.
    """

    def __init__(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        resource_id: str,
        tags: Optional[dict] = None,
        ssh_settings: Optional[VirtualMachineSshSettings] = None,
        **kwargs: Any,
    ) -> None:
        kwargs[TYPE] = ComputeType.VIRTUALMACHINE
        self._public_key_data: str = kwargs.pop("public_key_data", None)
        super().__init__(
            name=name,
            location=kwargs.pop("location", None),
            description=description,
            resource_id=resource_id,
            tags=tags,
            **kwargs,
        )
        self.ssh_settings = ssh_settings

    @property
    def public_key_data(self) -> str:
        """Public key data.

        :return: Public key data.
        :rtype: str
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
            tags=rest_obj.tags if rest_obj.tags else None,
            public_key_data=credentials.public_key_data if credentials else None,
            provisioning_state=prop.provisioning_state,
            provisioning_errors=(
                prop.provisioning_errors[0].error.code
                if (prop.provisioning_errors and len(prop.provisioning_errors) > 0)
                else None
            ),
            ssh_settings=ssh_settings_param,
        )
        return response

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        res: dict = VirtualMachineComputeSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, **kwargs: Any) -> "VirtualMachineCompute":
        loaded_data = load_from_dict(VirtualMachineComputeSchema, data, context, **kwargs)
        return VirtualMachineCompute(**loaded_data)

    def _to_rest_object(self) -> ComputeResource:
        ssh_key_value = None
        if self.ssh_settings and self.ssh_settings.ssh_private_key_file:
            ssh_key_value = Path(self.ssh_settings.ssh_private_key_file).read_text(encoding=DefaultOpenEncoding.READ)
        credentials = VirtualMachineSshCredentials(
            username=self.ssh_settings.admin_username if self.ssh_settings else None,
            password=self.ssh_settings.admin_password if self.ssh_settings else None,
            public_key_data=self.public_key_data,
            private_key_data=ssh_key_value,
        )
        if self.ssh_settings is not None:
            properties = VirtualMachineSchemaProperties(
                ssh_port=self.ssh_settings.ssh_port, administrator_account=credentials
            )
        vm_compute = VMResource(
            properties=properties,
            resource_id=self.resource_id,
            description=self.description,
        )
        resource = ComputeResource(name=self.name, location=self.location, tags=self.tags, properties=vm_compute)
        return resource
