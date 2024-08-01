# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access,too-many-instance-attributes

import logging
import re
import warnings
from typing import Any, Dict, List, Optional

from azure.ai.ml._restclient.v2022_10_01_preview.models import AssignedUser
from azure.ai.ml._restclient.v2023_08_01_preview.models import ComputeInstance as CIRest
from azure.ai.ml._restclient.v2023_08_01_preview.models import ComputeInstanceProperties
from azure.ai.ml._restclient.v2023_08_01_preview.models import ComputeInstanceSshSettings as CiSShSettings
from azure.ai.ml._restclient.v2023_08_01_preview.models import (
    ComputeResource,
    PersonalComputeInstanceSettings,
    ResourceId,
)
from azure.ai.ml._schema._utils.utils import get_subnet_str
from azure.ai.ml._schema.compute.compute_instance import ComputeInstanceSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, TYPE
from azure.ai.ml.constants._compute import ComputeDefaults, ComputeType
from azure.ai.ml.entities._compute.compute import Compute, NetworkSettings
from azure.ai.ml.entities._credentials import IdentityConfiguration
from azure.ai.ml.entities._mixins import DictMixin
from azure.ai.ml.entities._util import load_from_dict

from ._custom_applications import CustomApplications, validate_custom_applications
from ._image_metadata import ImageMetadata
from ._schedule import ComputeSchedules
from ._setup_scripts import SetupScripts

module_logger = logging.getLogger(__name__)


class ComputeInstanceSshSettings:
    """Credentials for an administrator user account to SSH into the compute node.

    Can only be configured if `ssh_public_access_enabled` is set to true on compute
    resource.

    :param ssh_key_value: The SSH public key of the administrator user account.
    :type ssh_key_value: Optional[str]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_compute.py
            :start-after: [START compute_instance_ssh_settings]
            :end-before: [END compute_instance_ssh_settings]
            :language: python
            :dedent: 8
            :caption: Configuring ComputeInstanceSshSettings object.
    """

    def __init__(
        self,
        *,
        ssh_key_value: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.ssh_key_value = ssh_key_value
        self._ssh_port: str = kwargs.pop("ssh_port", None)
        self._admin_username: str = kwargs.pop("admin_username", None)

    @property
    def admin_username(self) -> str:
        """The name of the administrator user account which can be used to SSH into nodes.

        :return: The name of the administrator user account.
        :rtype: str
        """
        return self._admin_username

    @property
    def ssh_port(self) -> str:
        """SSH port.

        :return: SSH port.
        :rtype: str
        """
        return self._ssh_port


class AssignedUserConfiguration(DictMixin):
    """Settings to create a compute resource on behalf of another user.

    :param user_tenant_id: Tenant ID of the user to assign the compute target to.
    :type user_tenant_id: str
    :param user_object_id: Object ID of the user to assign the compute target to.
    :type user_object_id: str

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_compute.py
            :start-after: [START assigned_user_configuration]
            :end-before: [END assigned_user_configuration]
            :language: python
            :dedent: 8
            :caption: Creating an AssignedUserConfiguration.
    """

    def __init__(self, *, user_tenant_id: str, user_object_id: str) -> None:
        self.user_tenant_id = user_tenant_id
        self.user_object_id = user_object_id


class ComputeInstance(Compute):
    """Compute Instance resource.

    :param name: Name of the compute.
    :type name: str
    :param location: The resource location.
    :type location: Optional[str]
    :param description: Description of the resource.
    :type description: Optional[str]
    :param size: Compute size.
    :type size: Optional[str]
    :param tags: A set of tags. Contains resource tags defined as key/value pairs.
    :type tags: Optional[dict[str, str]]
    :param create_on_behalf_of: Configuration to create resource on behalf of another user. Defaults to None.
    :type create_on_behalf_of: Optional[~azure.ai.ml.entities.AssignedUserConfiguration]
    :ivar state: State of the resource.
    :type state: Optional[str]
    :ivar last_operation: The last operation.
    :type last_operation: Optional[Dict[str, str]]
    :ivar applications: Applications associated with the compute instance.
    :type applications: Optional[List[Dict[str, str]]]
    :param network_settings: Network settings for the compute instance.
    :type network_settings: Optional[~azure.ai.ml.entities.NetworkSettings]
    :param ssh_settings: SSH settings for the compute instance.
    :type ssh_settings: Optional[~azure.ai.ml.entities.ComputeInstanceSshSettings]
    :param ssh_public_access_enabled: State of the public SSH port. Defaults to None.
        Possible values are:

        * False - Indicates that the public ssh port is closed on all nodes of the cluster.
        * True - Indicates that the public ssh port is open on all nodes of the cluster.
        * None -Indicates that the public ssh port is closed on all nodes of the cluster if VNet is defined,
            else is open all public nodes. It can be default only during cluster creation time, after
            creation it will be either True or False.

    :type ssh_public_access_enabled: Optional[bool]
    :param schedules: Compute instance schedules. Defaults to None.
    :type schedules: Optional[~azure.ai.ml.entities.ComputeSchedules]
    :param identity: The identities that are associated with the compute cluster.
    :type identity: ~azure.ai.ml.entities.IdentityConfiguration
    :param idle_time_before_shutdown: Deprecated. Use the `idle_time_before_shutdown_minutes` parameter instead.
        Stops compute instance after user defined period of inactivity.
        Time is defined in ISO8601 format. Minimum is 15 minutes, maximum is 3 days.
    :type idle_time_before_shutdown: Optional[str]
    :param idle_time_before_shutdown_minutes: Stops compute instance after a user defined period of
        inactivity in minutes. Minimum is 15 minutes, maximum is 3 days.
    :type idle_time_before_shutdown_minutes: Optional[int]
    :param enable_node_public_ip: Enable or disable node public IP address provisioning. Defaults to True.
        Possible values are:

            * True - Indicates that the compute nodes will have public IPs provisioned.
            * False - Indicates that the compute nodes will have a private endpoint and no public IPs.

    :type enable_node_public_ip: Optional[bool]
    :param setup_scripts: Details of customized scripts to execute for setting up the cluster.
    :type setup_scripts: Optional[~azure.ai.ml.entities.SetupScripts]
    :param custom_applications: List of custom applications and their endpoints for the compute instance.
    :type custom_applications: Optional[List[~azure.ai.ml.entities.CustomApplications]]
    :param enable_sso: Enable or disable single sign-on. Defaults to True.
    :type enable_sso: bool
    :param enable_root_access: Enable or disable root access. Defaults to True.
    :type enable_root_access: bool
    :param release_quota_on_stop: Release quota on stop for the compute instance. Defaults to False.
    :type release_quota_on_stop: bool
    :param enable_os_patching: Enable or disable OS patching for the compute instance. Defaults to False.
    :type enable_os_patching: bool

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_compute.py
            :start-after: [START compute_instance]
            :end-before: [END compute_instance]
            :language: python
            :dedent: 8
            :caption: Creating a ComputeInstance object.
    """

    def __init__(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        size: Optional[str] = None,
        tags: Optional[dict] = None,
        ssh_public_access_enabled: Optional[bool] = None,
        create_on_behalf_of: Optional[AssignedUserConfiguration] = None,
        network_settings: Optional[NetworkSettings] = None,
        ssh_settings: Optional[ComputeInstanceSshSettings] = None,
        schedules: Optional[ComputeSchedules] = None,
        identity: Optional[IdentityConfiguration] = None,
        idle_time_before_shutdown: Optional[str] = None,
        idle_time_before_shutdown_minutes: Optional[int] = None,
        setup_scripts: Optional[SetupScripts] = None,
        enable_node_public_ip: bool = True,
        custom_applications: Optional[List[CustomApplications]] = None,
        enable_sso: bool = True,
        enable_root_access: bool = True,
        release_quota_on_stop: bool = False,
        enable_os_patching: bool = False,
        **kwargs: Any,
    ) -> None:
        kwargs[TYPE] = ComputeType.COMPUTEINSTANCE
        self._state: str = kwargs.pop("state", None)
        self._last_operation: dict = kwargs.pop("last_operation", None)
        self._os_image_metadata: ImageMetadata = kwargs.pop("os_image_metadata", None)
        self._services: list = kwargs.pop("services", None)
        super().__init__(
            name=name,
            location=kwargs.pop("location", None),
            resource_id=kwargs.pop("resource_id", None),
            description=description,
            tags=tags,
            **kwargs,
        )
        self.size = size
        self.ssh_public_access_enabled = ssh_public_access_enabled
        self.create_on_behalf_of = create_on_behalf_of
        self.network_settings = network_settings
        self.ssh_settings = ssh_settings
        self.schedules = schedules
        self.identity = identity
        self.idle_time_before_shutdown = idle_time_before_shutdown
        self.idle_time_before_shutdown_minutes = idle_time_before_shutdown_minutes
        self.setup_scripts = setup_scripts
        self.enable_node_public_ip = enable_node_public_ip
        self.enable_sso = enable_sso
        self.enable_root_access = enable_root_access
        self.release_quota_on_stop = release_quota_on_stop
        self.enable_os_patching = enable_os_patching
        self.custom_applications = custom_applications
        self.subnet = None

    @property
    def services(self) -> List[Dict[str, str]]:
        """The compute instance's services.

        :return: The compute instance's services.
        :rtype: List[Dict[str, str]]
        """
        return self._services

    @property
    def last_operation(self) -> Dict[str, str]:
        """The last operation.

        :return: The last operation.
        :rtype: str
        """
        return self._last_operation

    @property
    def state(self) -> str:
        """The state of the compute.

        :return: The state of the compute.
        :rtype: str
        """
        return self._state

    @property
    def os_image_metadata(self) -> ImageMetadata:
        """Metadata about the operating system image for this compute instance.

        :return: Operating system image metadata.
        :rtype: ~azure.ai.ml.entities.ImageMetadata
        """
        return self._os_image_metadata

    def _to_rest_object(self) -> ComputeResource:
        if self.network_settings and self.network_settings.subnet:
            subnet_resource = ResourceId(id=self.subnet)
        else:
            subnet_resource = None

        ssh_settings = None
        if self.ssh_public_access_enabled is not None or self.ssh_settings is not None:
            ssh_settings = CiSShSettings()
            ssh_settings.ssh_public_access = "Enabled" if self.ssh_public_access_enabled else "Disabled"
            ssh_settings.admin_public_key = (
                self.ssh_settings.ssh_key_value if self.ssh_settings and self.ssh_settings.ssh_key_value else None
            )

        personal_compute_instance_settings = None
        if self.create_on_behalf_of:
            personal_compute_instance_settings = PersonalComputeInstanceSettings(
                assigned_user=AssignedUser(
                    object_id=self.create_on_behalf_of.user_object_id,
                    tenant_id=self.create_on_behalf_of.user_tenant_id,
                )
            )

        idle_time_before_shutdown = None
        if self.idle_time_before_shutdown_minutes:
            idle_time_before_shutdown = f"PT{self.idle_time_before_shutdown_minutes}M"
        elif self.idle_time_before_shutdown:
            warnings.warn(
                """ The property 'idle_time_before_shutdown' is deprecated.
                Please use'idle_time_before_shutdown_minutes' instead.""",
                DeprecationWarning,
            )
            idle_time_before_shutdown = self.idle_time_before_shutdown

        compute_instance_prop = ComputeInstanceProperties(
            vm_size=self.size if self.size else ComputeDefaults.VMSIZE,
            subnet=subnet_resource,
            ssh_settings=ssh_settings,
            personal_compute_instance_settings=personal_compute_instance_settings,
            idle_time_before_shutdown=idle_time_before_shutdown,
            enable_node_public_ip=self.enable_node_public_ip,
            enable_sso=self.enable_sso,
            enable_root_access=self.enable_root_access,
            release_quota_on_stop=self.release_quota_on_stop,
            enable_os_patching=self.enable_os_patching,
        )
        compute_instance_prop.schedules = self.schedules._to_rest_object() if self.schedules else None
        compute_instance_prop.setup_scripts = self.setup_scripts._to_rest_object() if self.setup_scripts else None
        if self.custom_applications:
            validate_custom_applications(self.custom_applications)
            compute_instance_prop.custom_services = []
            for app in self.custom_applications:
                compute_instance_prop.custom_services.append(app._to_rest_object())
        compute_instance = CIRest(
            description=self.description,
            compute_type=self.type,
            properties=compute_instance_prop,
        )
        return ComputeResource(
            location=self.location,
            properties=compute_instance,
            identity=(self.identity._to_compute_rest_object() if self.identity else None),
            tags=self.tags,
        )

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        res: dict = ComputeInstanceSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res

    def _set_full_subnet_name(self, subscription_id: str, rg: str) -> None:
        if self.network_settings and (self.network_settings.vnet_name or self.network_settings.subnet):
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
                public_ip_address=(
                    prop.properties.connectivity_endpoints.public_ip_address
                    if prop.properties.connectivity_endpoints
                    and prop.properties.connectivity_endpoints.public_ip_address
                    else None
                ),
                private_ip_address=(
                    prop.properties.connectivity_endpoints.private_ip_address
                    if prop.properties.connectivity_endpoints
                    and prop.properties.connectivity_endpoints.private_ip_address
                    else None
                ),
            )
        os_image_metadata = None
        if prop.properties and prop.properties.os_image_metadata:
            metadata = prop.properties.os_image_metadata
            os_image_metadata = ImageMetadata(
                is_latest_os_image_version=(
                    metadata.is_latest_os_image_version if metadata.is_latest_os_image_version is not None else None
                ),
                current_image_version=metadata.current_image_version if metadata.current_image_version else None,
                latest_image_version=metadata.latest_image_version if metadata.latest_image_version else None,
            )

        idle_time_before_shutdown = None
        idle_time_before_shutdown_minutes = None
        idle_time_before_shutdown_pattern = r"PT([0-9]+)M"
        if prop.properties and prop.properties.idle_time_before_shutdown:
            idle_time_before_shutdown = prop.properties.idle_time_before_shutdown
            idle_time_match = re.match(
                pattern=idle_time_before_shutdown_pattern,
                string=idle_time_before_shutdown,
            )
            idle_time_before_shutdown_minutes = int(idle_time_match[1]) if idle_time_match else None
        custom_applications = None
        if prop.properties and prop.properties.custom_services:
            custom_applications = []
            for app in prop.properties.custom_services:
                custom_applications.append(CustomApplications._from_rest_object(app))
        response = ComputeInstance(
            name=rest_obj.name,
            id=rest_obj.id,
            description=prop.description,
            location=rest_obj.location,
            resource_id=prop.resource_id,
            tags=rest_obj.tags if rest_obj.tags else None,
            provisioning_state=prop.provisioning_state,
            provisioning_errors=(
                prop.provisioning_errors[0].error.code
                if (prop.provisioning_errors and len(prop.provisioning_errors) > 0)
                else None
            ),
            size=prop.properties.vm_size if prop.properties else None,
            state=prop.properties.state if prop.properties else None,
            last_operation=(
                prop.properties.last_operation.as_dict() if prop.properties and prop.properties.last_operation else None
            ),
            services=(
                [app.as_dict() for app in prop.properties.applications]
                if prop.properties and prop.properties.applications
                else None
            ),
            created_on=(
                rest_obj.properties.created_on.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
                if rest_obj.properties and rest_obj.properties.created_on is not None
                else None
            ),
            create_on_behalf_of=create_on_behalf_of,
            network_settings=network_settings,
            ssh_settings=ssh_settings,
            ssh_public_access_enabled=(
                _ssh_public_access_to_bool(prop.properties.ssh_settings.ssh_public_access)
                if (prop.properties and prop.properties.ssh_settings and prop.properties.ssh_settings.ssh_public_access)
                else None
            ),
            schedules=(
                ComputeSchedules._from_rest_object(prop.properties.schedules)
                if prop.properties and prop.properties.schedules and prop.properties.schedules.compute_start_stop
                else None
            ),
            identity=IdentityConfiguration._from_compute_rest_object(rest_obj.identity) if rest_obj.identity else None,
            setup_scripts=(
                SetupScripts._from_rest_object(prop.properties.setup_scripts)
                if prop.properties and prop.properties.setup_scripts
                else None
            ),
            idle_time_before_shutdown=idle_time_before_shutdown,
            idle_time_before_shutdown_minutes=idle_time_before_shutdown_minutes,
            os_image_metadata=os_image_metadata,
            enable_node_public_ip=(
                prop.properties.enable_node_public_ip
                if (prop.properties and prop.properties.enable_node_public_ip is not None)
                else True
            ),
            custom_applications=custom_applications,
            enable_sso=(
                prop.properties.enable_sso if (prop.properties and prop.properties.enable_sso is not None) else True
            ),
            enable_root_access=(
                prop.properties.enable_root_access
                if (prop.properties and prop.properties.enable_root_access is not None)
                else True
            ),
            release_quota_on_stop=(
                prop.properties.release_quota_on_stop
                if (prop.properties and prop.properties.release_quota_on_stop is not None)
                else False
            ),
            enable_os_patching=(
                prop.properties.enable_os_patching
                if (prop.properties and prop.properties.enable_os_patching is not None)
                else False
            ),
        )
        return response

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, **kwargs: Any) -> "ComputeInstance":
        loaded_data = load_from_dict(ComputeInstanceSchema, data, context, **kwargs)
        return ComputeInstance(**loaded_data)


def _ssh_public_access_to_bool(value: str) -> Optional[bool]:
    if value.lower() == "disabled":
        return False
    if value.lower() == "enabled":
        return True
    return None
