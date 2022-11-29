# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Dict

from azure.ai.ml._restclient.v2022_10_01_preview.models import AmlCompute as AmlComputeRest
from azure.ai.ml._restclient.v2022_10_01_preview.models import (
    AmlComputeProperties,
    ComputeResource,
    ResourceId,
    ScaleSettings,
    UserAccountCredentials,
)
from azure.ai.ml._schema._utils.utils import get_subnet_str
from azure.ai.ml._schema.compute.aml_compute import AmlComputeSchema
from azure.ai.ml._utils.utils import camel_to_snake, snake_to_pascal, to_iso_duration_format
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, TYPE
from azure.ai.ml.constants._compute import ComputeDefaults, ComputeType
from azure.ai.ml.entities._util import load_from_dict

from azure.ai.ml.entities._credentials import IdentityConfiguration
from .compute import Compute, NetworkSettings


class AmlComputeSshSettings:
    """SSH settings to access a AML compute target."""

    def __init__(
        self,
        *,
        admin_username: str,
        admin_password: str = None,
        ssh_key_value: str = None,
    ):
        """[summary]

        :param admin_username: SSH user name
        :type admin_username: str
        :param admin_password: SSH user password, defaults to None
        :type admin_password: str, optional
        :param ssh_key_value:  Specifies the SSH rsa private key as a string. Use "ssh-keygen -t
            rsa -b 2048" to generate your SSH key pairs. Defaults to None
        :type ssh_key_value: Optional[str], optional
        """
        self.admin_username = admin_username
        self.admin_password = admin_password
        self.ssh_key_value = ssh_key_value

    def _to_user_account_credentials(self) -> UserAccountCredentials:
        return UserAccountCredentials(
            admin_user_name=self.admin_username,
            admin_user_password=self.admin_password,
            admin_user_ssh_public_key=self.ssh_key_value,
        )

    @classmethod
    def _from_user_account_credentials(cls, credentials: UserAccountCredentials) -> "AmlComputeSshSettings":
        return cls(
            admin_username=credentials.admin_user_name,
            admin_password=credentials.admin_user_password,
            ssh_key_value=credentials.admin_user_ssh_public_key,
        )


class AmlCompute(Compute):
    """Aml Compute resource.

    :param name: Name of the compute
    :type name: str
    :param description: Description of the resource.
    :type description: str, optional
    :param size: Compute Size, defaults to None.
    :type size: str, optional
    :param ssh_settings: SSH settings to access the AzureML compute cluster.
    :type ssh_settings: AmlComputeSshSettings, optional
    :param network_settings: Virtual network settings for the AzureML compute cluster.
    :type network_settings: NetworkSettings, optional
    :param idle_time_before_scale_down: Node Idle Time before scaling down amlCompute. Defaults to None.
    :type idle_time_before_scale_down: int, optional
    :param identity:  The identity configuration, identities that are associated with the compute cluster.
    :type identity: IdentityConfiguration, optional
    :param tier: Virtual Machine tier. Possible values include: "Dedicated", "LowPriority". Defaults to None.
    :type tier: str, optional
    :param min_instances: Minimum number of instances. Defaults to None.
    :type min_instances: int, optional
    :param max_instances: Maximum number of instances. Defaults to None.
    :type max_instances: int, optional
    :param ssh_public_access_enabled: State of the public SSH port. Possible values are:
     False - Indicates that the public ssh port is closed on all nodes of the cluster. True -
     Indicates that the public ssh port is open on all nodes of the cluster. None -
     Indicates that the public ssh port is closed on all nodes of the cluster if VNet is defined,
     else is open all public nodes. It can be default only during cluster creation time, after
     creation it will be either True or False. Possible values include: True, False, None. Default value: None.
     :type ssh_public_access_enabled: bool, optional
    """

    def __init__(
        self,
        *,
        name: str,
        description: str = None,
        size: str = None,
        ssh_public_access_enabled: bool = None,
        ssh_settings: AmlComputeSshSettings = None,
        min_instances: int = None,
        max_instances: int = None,
        network_settings: NetworkSettings = None,
        idle_time_before_scale_down: int = None,
        identity: IdentityConfiguration = None,
        tier: str = None,
        **kwargs,
    ):
        kwargs[TYPE] = ComputeType.AMLCOMPUTE
        super().__init__(
            name=name,
            description=description,
            location=kwargs.pop("location", None),
            **kwargs,
        )
        self.size = size
        self.min_instances = min_instances or 0
        self.max_instances = max_instances or 1
        self.idle_time_before_scale_down = idle_time_before_scale_down
        self.identity = identity
        self.ssh_public_access_enabled = ssh_public_access_enabled
        self.ssh_settings = ssh_settings
        self.network_settings = network_settings
        self.tier = tier
        self.subnet = None

    @classmethod
    def _load_from_rest(cls, rest_obj: ComputeResource) -> "AmlCompute":
        prop = rest_obj.properties

        network_settings = None
        if prop.properties.subnet or (prop.properties.enable_node_public_ip is not None):
            network_settings = NetworkSettings(
                subnet=prop.properties.subnet.id if prop.properties.subnet else None,
            )

        ssh_settings = (
            AmlComputeSshSettings._from_user_account_credentials(prop.properties.user_account_credentials)
            if prop.properties.user_account_credentials
            else None
        )

        response = AmlCompute(
            name=rest_obj.name,
            id=rest_obj.id,
            description=prop.description,
            location=rest_obj.location,
            provisioning_state=prop.provisioning_state,
            provisioning_errors=prop.provisioning_errors[0].error.code
            if (prop.provisioning_errors and len(prop.provisioning_errors) > 0)
            else None,
            size=prop.properties.vm_size,
            tier=camel_to_snake(prop.properties.vm_priority),
            min_instances=prop.properties.scale_settings.min_node_count if prop.properties.scale_settings else None,
            max_instances=prop.properties.scale_settings.max_node_count if prop.properties.scale_settings else None,
            network_settings=network_settings or None,
            ssh_settings=ssh_settings,
            ssh_public_access_enabled=(prop.properties.remote_login_port_public_access == "Enabled"),
            idle_time_before_scale_down=prop.properties.scale_settings.node_idle_time_before_scale_down.total_seconds()
            if prop.properties.scale_settings and prop.properties.scale_settings.node_idle_time_before_scale_down
            else None,
            identity=IdentityConfiguration._from_compute_rest_object(rest_obj.identity) if rest_obj.identity else None,
            created_on=prop.additional_properties.get("createdOn", None),
        )
        return response

    def _set_full_subnet_name(self, subscription_id: str, rg: str) -> None:
        if self.network_settings:
            self.subnet = get_subnet_str(
                self.network_settings.vnet_name,
                self.network_settings.subnet,
                subscription_id,
                rg,
            )

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return AmlComputeSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, **kwargs) -> "AmlCompute":
        loaded_data = load_from_dict(AmlComputeSchema, data, context, **kwargs)
        return AmlCompute(**loaded_data)

    def _to_rest_object(self) -> ComputeResource:
        if self.network_settings and self.network_settings.subnet:
            subnet_resource = ResourceId(id=self.subnet)
        else:
            subnet_resource = None

        # Scale settings is required when creating an AzureML compute cluster
        scale_settings = ScaleSettings(
            max_node_count=self.max_instances,
            min_node_count=self.min_instances,
            node_idle_time_before_scale_down=to_iso_duration_format(int(self.idle_time_before_scale_down))
            if self.idle_time_before_scale_down
            else None,
        )
        remote_login_public_access = "Enabled"
        if self.ssh_public_access_enabled is not None:
            remote_login_public_access = "Enabled" if self.ssh_public_access_enabled else "Disabled"
        else:
            remote_login_public_access = "NotSpecified"
        aml_prop = AmlComputeProperties(
            vm_size=self.size if self.size else ComputeDefaults.VMSIZE,
            vm_priority=snake_to_pascal(self.tier),
            user_account_credentials=self.ssh_settings._to_user_account_credentials() if self.ssh_settings else None,
            scale_settings=scale_settings,
            subnet=subnet_resource,
            remote_login_port_public_access=remote_login_public_access,
        )

        aml_comp = AmlComputeRest(description=self.description, compute_type=self.type, properties=aml_prop)
        return ComputeResource(
            location=self.location,
            properties=aml_comp,
            identity=(self.identity._to_compute_rest_object() if self.identity else None),
        )
