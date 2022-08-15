# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Dict, List, Optional

from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.ai.ml._restclient.v2022_01_01_preview.models import AssignedUser
from azure.ai.ml._restclient.v2022_01_01_preview.models import ComputeInstance as CIRest
from azure.ai.ml._restclient.v2022_01_01_preview.models import ComputeInstanceProperties
from azure.ai.ml._restclient.v2022_01_01_preview.models import ComputeInstanceSshSettings as CiSShSettings
from azure.ai.ml._restclient.v2022_01_01_preview.models import (
    ComputeResource,
    PersonalComputeInstanceSettings,
    ResourceId,
)
from azure.ai.ml._schema._utils.utils import get_subnet_str
from azure.ai.ml._schema.compute.compute_instance import ComputeInstanceSchema
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, TYPE, ComputeDefaults, ComputeType
from azure.ai.ml.entities._compute.compute import Compute, NetworkSettings
from azure.ai.ml.entities._util import load_from_dict

from ._schedule import ComputeSchedules


class ComputeInstanceSshSettings:
    """Credentials for an administrator user account to SSH into the compute
    node.

    Can only be configured if ssh_public_access_enabled is set to true.
    """

    def __init__(
        self,
        *,
        ssh_key_value: str,
        **kwargs,
    ):
        """[summary]

        :param ssh_key_value:  The SSH public key of the administrator user account.
        :type ssh_key_value: str
        """
        self.ssh_key_value = ssh_key_value
        self._ssh_port = kwargs.pop("ssh_port", None)
        self._admin_username = kwargs.pop("admin_username", None)

    @property
    def admin_username(self) -> str:
        """The name of the administrator user account which can be used to SSH
        into nodes.

        return: The name of the administrator user account.
        rtype: str
        """
        return self._admin_username

    @property
    def ssh_port(self) -> str:
        """SSH port.

        return: SSH port.
        rtype: str
        """
        return self._ssh_port


class AssignedUserConfiguration:
    """Settings to create a compute on behalf of another user."""

    def __init__(self, *, user_tenant_id: str, user_object_id: str):
        """[summary]

        :param user_tenant_id: Tenant ID of the user to assign the compute target to.
        :type user_tenant_id: str
        :param user_object_id: Object ID of the user to assign the compute target to.
        :type user_object_id: str
        """
        self.user_tenant_id = user_tenant_id
        self.user_object_id = user_object_id


class ComputeInstance(Compute):
    """Compute Instance resource.

    :param name: Name of the compute
    :type name: str
    :param location: The resource location, defaults to None
    :type location: Optional[str], optional
    :param description: Description of the resource.
    :type description: Optional[str], optional
    :param size: Compute Size, defaults to None
    :type size: Optional[str], optional
    :param create_on_behalf_of: defaults to None
    :type create_on_behalf_of: Optional[AssignedUserConfiguration], optional
    :ivar state: defaults to None
    :type state: Optional[str], optional
    :ivar last_operation: defaults to None
    :type last_operation: Optional[Dict[str, str]], optional
    :ivar applications: defaults to None
    :type applications: Optional[List[Dict[str, str]]], optional
    :param network_settings: defaults to None
    :type network_settings: Optional[NetworkSettings], optional
    :param ssh_settings: defaults to None
    :type ssh_settings: Optional[ComputeInstanceSshSettings], optional
    :param ssh_public_access_enabled: State of the public SSH port. Possible values are: ["False", "True", "None"]
        False - Indicates that the public ssh port is closed on all nodes of the cluster.
        True - Indicates that the public ssh port is open on all nodes of the cluster.
        None -Indicates that the public ssh port is closed on all nodes of the cluster if VNet is defined,
        else is open all public nodes. It can be default only during cluster creation time, after
        creation it will be either True or False. Possible values include: True, False, None.
        Default value: None.

    :type ssh_public_access_enabled: Optional[bool], optional
    :param schedules: Compute instance schedules, defaults to None
    :type schedules: Optional[ComputeSchedules], optional
    """

    def __init__(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        size: Optional[str] = None,
        ssh_public_access_enabled: Optional[bool] = None,
        create_on_behalf_of: Optional[AssignedUserConfiguration] = None,
        network_settings: Optional[NetworkSettings] = None,
        ssh_settings: Optional[ComputeInstanceSshSettings] = None,
        schedules: Optional[ComputeSchedules] = None,
        **kwargs,
    ):
        kwargs[TYPE] = ComputeType.COMPUTEINSTANCE
        self._state = kwargs.pop("state", None)
        self._last_operation = kwargs.pop("last_operation", None)
        self._services = kwargs.pop("services", None)
        super().__init__(
            name=name,
            location=kwargs.pop("location", None),
            resource_id=kwargs.pop("resource_id", None),
            description=description,
            **kwargs,
        )
        self.size = size
        self.ssh_public_access_enabled = ssh_public_access_enabled
        self.create_on_behalf_of = create_on_behalf_of
        self.network_settings = network_settings
        self.ssh_settings = ssh_settings
        self.schedules = schedules

    @property
    def services(self) -> List[Dict[str, str]]:
        """

        return: The services for the compute instance.
        rtype: List[Dict[str, str]]
        """
        return self._services

    @property
    def last_operation(self) -> Dict[str, str]:
        """The last operation.

        return: The last operation.
        rtype: str
        """
        return self._last_operation

    @property
    def state(self) -> str:
        """The state of the compute.

        return: The state of the compute.
        rtype: str
        """
        return self._state

    @staticmethod
    def _ssh_public_access_to_bool(value: str) -> bool:
        if value.lower() == "disabled":
            return False
        elif value.lower() == "enabled":
            return True
        else:
            return None

    def _to_rest_object(self) -> ComputeResource:
        if self.network_settings and self.network_settings.subnet:
            subnet_resource = ResourceId(id=self.subnet)
        else:
            subnet_resource = None
        if self.ssh_public_access_enabled and not (self.ssh_settings and self.ssh_settings.ssh_key_value):
            msg = "ssh_key_value is required when ssh_public_access_enabled = True."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.COMPUTE,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        ssh_settings = None
        if self.ssh_settings and self.ssh_settings.ssh_key_value:
            ssh_settings = CiSShSettings(
                admin_public_key=self.ssh_settings.ssh_key_value,
            )
            if self.ssh_public_access_enabled is not None:
                ssh_settings.ssh_public_access = "Enabled" if self.ssh_public_access_enabled else "Disabled"
            else:
                ssh_settings.ssh_public_access = "NotSpecified"
        personal_compute_instance_settings = None
        if self.create_on_behalf_of:
            personal_compute_instance_settings = PersonalComputeInstanceSettings(
                assigned_user=AssignedUser(
                    object_id=self.create_on_behalf_of.user_object_id,
                    tenant_id=self.create_on_behalf_of.user_tenant_id,
                )
            )

        compute_instance_prop = ComputeInstanceProperties(
            vm_size=self.size if self.size else ComputeDefaults.VMSIZE,
            subnet=subnet_resource,
            ssh_settings=ssh_settings,
            personal_compute_instance_settings=personal_compute_instance_settings,
            schedules=self.schedules._to_rest_object() if self.schedules else None,
        )
        compute_instance = CIRest(
            description=self.description,
            compute_type=self.type,
            properties=compute_instance_prop,
        )
        return ComputeResource(location=self.location, properties=compute_instance)

    def _to_dict(self) -> Dict:
        return ComputeInstanceSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    def _set_full_subnet_name(self, subscription_id: str, rg: str) -> None:
        if self.network_settings:
            self.subnet = get_subnet_str(
                self.network_settings.vnet_name,
                self.network_settings.subnet,
                subscription_id,
                rg,
            )

    @classmethod
    def _load_from_rest(cls, rest_obj: ComputeResource) -> "ComputeInstance":
        prop = rest_obj.properties
        create_on_behalf_of = None
        if prop.properties and prop.properties.personal_compute_instance_settings:
            create_on_behalf_of = AssignedUserConfiguration(
                user_tenant_id=prop.properties.personal_compute_instance_settings.assigned_user.tenant_id,
                user_object_id=prop.properties.personal_compute_instance_settings.assigned_user.object_id,
            )
        ssh_settings = None
        if prop.properties and prop.properties.ssh_settings:
            ssh_settings = ComputeInstanceSshSettings(
                ssh_key_value=prop.properties.ssh_settings.admin_public_key,
                ssh_port=prop.properties.ssh_settings.ssh_port,
                admin_username=prop.properties.ssh_settings.admin_user_name,
            )

        network_settings = None
        if prop.properties and (
            prop.properties.subnet
            or (
                prop.properties.connectivity_endpoints
                and (
                    prop.properties.connectivity_endpoints.private_ip_address
                    or prop.properties.connectivity_endpoints.public_ip_address
                )
            )
        ):
            network_settings = NetworkSettings(
                subnet=prop.properties.subnet.id if prop.properties.subnet else None,
                public_ip_address=prop.properties.connectivity_endpoints.public_ip_address
                if prop.properties.connectivity_endpoints and prop.properties.connectivity_endpoints.public_ip_address
                else None,
                private_ip_address=prop.properties.connectivity_endpoints.private_ip_address
                if prop.properties.connectivity_endpoints and prop.properties.connectivity_endpoints.private_ip_address
                else None,
            )

        response = ComputeInstance(
            name=rest_obj.name,
            id=rest_obj.id,
            description=prop.description,
            location=rest_obj.location,
            resource_id=prop.resource_id,
            provisioning_state=prop.provisioning_state,
            provisioning_errors=prop.provisioning_errors[0].error.code
            if (prop.provisioning_errors and len(prop.provisioning_errors) > 0)
            else None,
            size=prop.properties.vm_size if prop.properties else None,
            state=prop.properties.state if prop.properties else None,
            last_operation=prop.properties.last_operation.as_dict()
            if prop.properties and prop.properties.last_operation
            else None,
            services=[app.as_dict() for app in prop.properties.applications]
            if prop.properties and prop.properties.applications
            else None,
            created_on=prop.additional_properties.get("createdOn", None),
            create_on_behalf_of=create_on_behalf_of,
            network_settings=network_settings,
            ssh_settings=ssh_settings,
            ssh_public_access_enabled=cls._ssh_public_access_to_bool(prop.properties.ssh_settings.ssh_public_access)
            if (prop.properties and prop.properties.ssh_settings and prop.properties.ssh_settings.ssh_public_access)
            else None,
            schedules=ComputeSchedules._from_rest_object(prop.properties.schedules)
            if prop.properties and prop.properties.schedules and prop.properties.schedules.compute_start_stop
            else None,
        )
        return response

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, **kwargs) -> "ComputeInstance":
        loaded_data = load_from_dict(ComputeInstanceSchema, data, context, **kwargs)
        return ComputeInstance(**loaded_data)
