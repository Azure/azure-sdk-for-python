# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-instance-attributes,protected-access
from typing import Any, Dict, List, Optional

from azure.ai.ml._restclient.v2024_07_01_preview.models import (
    Workspace as RestWorkspace,
    WorkspaceHubConfig as RestWorkspaceHubConfig,
)
from azure.ai.ml._schema.workspace import HubSchema
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.constants._common import WorkspaceKind
from azure.ai.ml.entities import CustomerManagedKey, Workspace
from azure.ai.ml.entities._credentials import IdentityConfiguration
from azure.ai.ml.entities._workspace.networking import ManagedNetwork


@experimental
class Hub(Workspace):
    """A Hub is a special type of workspace that acts as a parent and resource container for lightweight child
    workspaces called projects. Resources like the hub's storage account, key vault,
    and container registry are shared by all child projects.

    As a type of workspace, hub management is controlled by an MLClient's workspace operations.

    :param name: Name of the hub.
    :type name: str
    :param description: Description of the hub.
    :type description: str
    :param tags: Tags of the hub.
    :type tags: dict
    :param display_name: Display name for the hub. This is non-unique within the resource group.
    :type display_name: str
    :param location: The location to create the hub in.
        If not specified, the same location as the resource group will be used.
    :type location: str
    :param resource_group: Name of resource group to create the hub in.
    :type resource_group: str
    :param managed_network: Hub's Managed Network configuration
    :type managed_network: ~azure.ai.ml.entities.ManagedNetwork
    :param storage_account: The resource ID of an existing storage account to use instead of creating a new one.
    :type storage_account: str
    :param key_vault: The resource ID of an existing key vault to use instead of creating a new one.
    :type key_vault: str
    :param container_registry: The resource ID of an existing container registry
        to use instead of creating a new one.
    :type container_registry: str
    :param customer_managed_key: Key vault details for encrypting data with customer-managed keys.
        If not specified, Microsoft-managed keys will be used by default.
    :type customer_managed_key: ~azure.ai.ml.entities.CustomerManagedKey
    :param image_build_compute: The name of the compute target to use for building environment.
        Docker images with the container registry is behind a VNet.
    :type image_build_compute: str
    :param public_network_access: Whether to allow public endpoint connectivity.
        when a workspace is private link enabled.
    :type public_network_access: str
    :param identity: The hub's Managed Identity (user assigned, or system assigned).
    :type identity: ~azure.ai.ml.entities.IdentityConfiguration
    :param primary_user_assigned_identity: The hub's primary user assigned identity.
    :type primary_user_assigned_identity: str
    :param enable_data_isolation: A flag to determine if workspace has data isolation enabled.
        The flag can only be set at the creation phase, it can't be updated.
    :type enable_data_isolation: bool
    :param default_resource_group: The resource group that will be used by projects
        created under this hub if no resource group is specified.
    :type default_resource_group: str
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict

    .. literalinclude:: ../samples/ml_samples_workspace.py
            :start-after: [START workspace_hub]
            :end-before: [END workspace_hub]
            :language: python
            :dedent: 8
            :caption: Creating a Hub object.
    """

    # The field 'additional_workspace_storage_accounts' exists in the API but is currently unused.

    def __init__(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        display_name: Optional[str] = None,
        location: Optional[str] = None,
        resource_group: Optional[str] = None,
        managed_network: Optional[ManagedNetwork] = None,
        storage_account: Optional[str] = None,
        key_vault: Optional[str] = None,
        container_registry: Optional[str] = None,
        customer_managed_key: Optional[CustomerManagedKey] = None,
        public_network_access: Optional[str] = None,
        identity: Optional[IdentityConfiguration] = None,
        primary_user_assigned_identity: Optional[str] = None,
        enable_data_isolation: bool = False,
        default_resource_group: Optional[str] = None,
        associated_workspaces: Optional[List[str]] = None,  # hidden input for rest->client conversions.
        **kwargs: Any,
    ):
        self._workspace_id = kwargs.pop("workspace_id", "")
        # Ensure user can't overwrite/double input kind.
        kwargs.pop("kind", None)
        super().__init__(
            name=name,
            description=description,
            tags=tags,
            kind=WorkspaceKind.HUB,
            display_name=display_name,
            location=location,
            storage_account=storage_account,
            key_vault=key_vault,
            container_registry=container_registry,
            resource_group=resource_group,
            customer_managed_key=customer_managed_key,
            public_network_access=public_network_access,
            identity=identity,
            primary_user_assigned_identity=primary_user_assigned_identity,
            managed_network=managed_network,
            enable_data_isolation=enable_data_isolation,
            **kwargs,
        )
        self._default_resource_group = default_resource_group
        self._associated_workspaces = associated_workspaces

    @classmethod
    def _get_schema_class(cls):
        return HubSchema

    @classmethod
    def _from_rest_object(cls, rest_obj: RestWorkspace, v2_service_context: Optional[object] = None) -> Optional["Hub"]:
        if not rest_obj:
            return None

        workspace_object = Workspace._from_rest_object(rest_obj, v2_service_context)

        default_resource_group = None

        if hasattr(rest_obj, "workspace_hub_config"):
            if rest_obj.workspace_hub_config and isinstance(rest_obj.workspace_hub_config, RestWorkspaceHubConfig):
                default_resource_group = rest_obj.workspace_hub_config.default_workspace_resource_group

        if workspace_object is not None:
            return Hub(
                name=workspace_object.name if workspace_object.name is not None else "",
                description=workspace_object.description,
                tags=workspace_object.tags,
                display_name=workspace_object.display_name,
                location=workspace_object.location,
                resource_group=workspace_object.resource_group,
                managed_network=workspace_object.managed_network,
                customer_managed_key=workspace_object.customer_managed_key,
                public_network_access=workspace_object.public_network_access,
                identity=workspace_object.identity,
                primary_user_assigned_identity=workspace_object.primary_user_assigned_identity,
                storage_account=rest_obj.storage_account,
                key_vault=rest_obj.key_vault,
                container_registry=rest_obj.container_registry,
                workspace_id=rest_obj.workspace_id,
                enable_data_isolation=rest_obj.enable_data_isolation,
                default_resource_group=default_resource_group,
                associated_workspaces=rest_obj.associated_workspaces if rest_obj.associated_workspaces else [],
                id=rest_obj.id,
            )
        return None

    # Helper function to deal with sub-rest object conversion.
    def _hub_values_to_rest_object(self) -> RestWorkspaceHubConfig:
        additional_workspace_storage_accounts = None
        default_resource_group = None
        if hasattr(self, "additional_workspace_storage_accounts"):
            additional_workspace_storage_accounts = None
        if hasattr(self, "default_resource_group"):
            default_resource_group = None
        return RestWorkspaceHubConfig(
            additional_workspace_storage_accounts=additional_workspace_storage_accounts,
            default_workspace_resource_group=default_resource_group,
        )

    def _to_rest_object(self) -> RestWorkspace:
        restWorkspace = super()._to_rest_object()
        restWorkspace.workspace_hub_config = self._hub_values_to_rest_object()
        return restWorkspace

    @property
    def default_resource_group(self) -> Optional[str]:
        """The default resource group for this hub and its children.

        :return: The resource group.
        :rtype: Optional[str]
        """
        return self._default_resource_group

    @default_resource_group.setter
    def default_resource_group(self, value: str):
        """Set the default resource group for child projects of this hub.

        :param value: The new resource group.
        :type value: str
        """
        if not value:
            return
        self._default_resource_group = value

    # No setter, read-only
    @property
    def associated_workspaces(self) -> Optional[List[str]]:
        """The workspaces associated with the hub.

        :return: The resource group.
        :rtype:  Optional[List[str]]
        """
        return self._associated_workspaces
