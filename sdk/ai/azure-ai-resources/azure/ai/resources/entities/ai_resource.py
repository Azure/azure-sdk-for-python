# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from typing import Dict, List, Optional

from azure.ai.ml.entities import CustomerManagedKey, WorkspaceHub
from azure.ai.ml.entities._credentials import IdentityConfiguration
from azure.ai.ml.entities._workspace.networking import ManagedNetwork
from azure.ai.ml.entities._workspace_hub.workspace_hub_config import WorkspaceHubConfig


# Effectively a lightweight wrapper around a v2 WorkspaceHub
class AIResource:
    """An AI Resource, which serves as a container for projects and other AI-related objects

    :param name: The name for the AI resource.
    :type name: str
    :param description: The description of the AI resource.
    :type description: Optional[str]
    :param tags: The tags for the AI resource.
    :type tags: Optional[Dict[str, str]]
    :param display_name: The display name for the AI resource.
    :type display_name: Optional[str]
    :param location: The location for the AI resource.
    :type location: Optional[str]
    :param resource_group: The resource group associated with the AI resource.
    :type resource_group: Optional[str]
    :param managed_network: The managed network associated with the AI resource.
    :type managed_network: Optional[~azure.ai.ml.entities._workspace.networking.ManagedNetwork]
    :param storage_account: The storage account associated with the AI resource.
    :type storage_account: Optional[str]
    :param customer_managed_key: The customer managed key associated with the AI resource.
    :type customer_managed_key: Optional[~azure.ai.ml.entities.CustomerManagedKey]
    :param public_network_access: The public network access associated with the AI resource.
    :type public_network_access: Optional[str]
    :param identity: The identity associated with the AI resource.
    :type identity: Optional[~azure.ai.ml.entities.IdentityConfiguration]
    :param container_registry: The container registry associated with the AI resource.
    :type container_registry: Optional[str]
    :param primary_user_assigned_identity: The primary user assigned identity associated with the AI resource.
    :type primary_user_assigned_identity: Optional[str]
    :param default_project_resource_group: The default project's resource group.
    :type default_project_resource_group: Optional[str]
    """
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
        customer_managed_key: Optional[CustomerManagedKey] = None,
        public_network_access: Optional[str] = None,
        identity: Optional[IdentityConfiguration] = None,
        container_registry: Optional[str] = None,
        primary_user_assigned_identity: Optional[str] = None,
        default_project_resource_group: Optional[str] = None,  # Unpacked WorkspaceHubConfig field
        **kwargs,
    ) -> None:

        self._workspace_hub = WorkspaceHub(
            name=name,
            description=description,
            tags=tags,
            display_name=display_name,
            location=location,
            resource_group=resource_group,
            managed_network=managed_network,
            storage_account=storage_account,
            customer_managed_key=customer_managed_key,
            public_network_access=public_network_access,
            identity=identity,
            container_registry=container_registry,
            primary_user_assigned_identity=primary_user_assigned_identity,
            workspace_hub_config=WorkspaceHubConfig(
                additional_workspace_storage_accounts=[],
                default_workspace_resource_group=default_project_resource_group,
            ),
            **kwargs,
        )

    @classmethod
    def _from_v2_workspace_hub(cls, workspace_hub: WorkspaceHub) -> "AIResource":
        """Create a connection from a v2 AML SDK workspace hub. For internal use.

        :param workspace_hub: The workspace connection object to convert into a workspace.
        :type workspace_hub: ~azure.ai.ml.entities.WorkspaceConnection
        :return: The converted AI resource.
        :rtype: ~azure.ai.resources.entities.AIResource
        """
        # It's simpler to create a placeholder resource, then overwrite the internal WC.
        # We don't need to worry about the potentially changing WC fields this way.
        resource = cls(name="a")
        resource._workspace_hub = workspace_hub
        return resource

    @property
    def id(self) -> str:
        """The workspace hub ID. Read-only, set by the backend.

        :return: The workspace hub ID.
        :rtype: str
        """
        return self._workspace_hub.id
    
    @property
    def name(self) -> str:
        """The workspace hub name.

        :return: The workspace hub name.
        :rtype: str
        """
        return self._workspace_hub.name

    @name.setter
    def name(self, value: str):
        """Sets the workspace hub name.

        :param value: The name to assign the workspace hub.
        :type value: str
        """
        if not value:
            return
        self._workspace_hub.name = value

    @property
    def description(self) -> str:
        """The workspace hub description.

        :return: The workspace hub description.
        :rtype: str
        """
        return self._workspace_hub.description

    @description.setter
    def description(self, value: str):
        """Sets the description of the workspace hub.

        :param value: The description to assign the workspace hub.
        :type value: str
        """
        if not value:
            return
        self._workspace_hub.description = value

    @property
    def tags(self) -> Optional[Dict[str, str]]:
        """Tags for the workspace hub.

        :return: The tags of the workspace hub.
        :rtype: str
        """
        return self._workspace_hub.tags

    @tags.setter
    def tags(self, value: Optional[Dict[str, str]]):
        """Sets the tags on the workspace hub.

        :param value: The tags to assign to the workspace hub.
        :type value: str
        """
        if not value:
            return
        self._workspace_hub.tags = value

    @property
    def display_name(self) -> str:
        """The workspace hub's display name.

        :return: The display name of the workspace hub.
        :rtype: str
        """
        return self._workspace_hub.display_name

    @display_name.setter
    def display_name(self, value: str):
        """Sets the display name of the workspace hub.

        :param value: The display name to assign to the workspace hub.
        :type value: str
        """
        if not value:
            return
        self._workspace_hub.display_name = value

    @property
    def location(self) -> str:
        """The workspace hub location.

        :return: The location of the workspace hub.
        :rtype: str
        """
        return self._workspace_hub.location

    @location.setter
    def location(self, value: str):
        """Sets the location of the workspace hub.

        :param value: The location to assign to the workspace hub.
        :type value: str
        """
        if not value:
            return
        self._workspace_hub.location = value

    @property
    def resource_group(self) -> str:
        """The workspace hub's resource group.

        :return: The name of the resource group associated with the workspace hub.
        :rtype: str
        """
        return self._workspace_hub.resource_group

    @resource_group.setter
    def resource_group(self, value: str):
        """Sets the workspace hub's resource group.

        :param value: The name of the resource group to associate with the workspace hub.
        :type value: str
        """
        if not value:
            return
        self._workspace_hub.resource_group = value

    @property
    def managed_network(self) -> Optional[ManagedNetwork]:
        """The managed network to which the workspace hub is connected.

        :return: The name of the managed network associated with the workspace hub.
        :rtype: Optional[~azure.ai.ml.entities._workspace.networking.ManagedNetwork]
        """
        return self._workspace_hub.managed_network

    @managed_network.setter
    def managed_network(self, value: Optional[ManagedNetwork]):
        """Sets the managed network to associate the workspace hub with

        :param value: The name of the managed network to associate the workspace hub with.
        :type value: Optional[~azure.ai.ml.entities._workspace.networking.ManagedNetwork]
        """
        if not value:
            return
        self._workspace_hub.managed_network = value

    @property
    def storage_account(self) -> str:
        """The storage account for the workspace hub.

        :return: The name of the storage account associated with the workspace hub.
        :rtype: str
        """
        return self._workspace_hub.storage_account

    @storage_account.setter
    def storage_account(self, value: str):
        """Sets the storage account for the workspace hub.

        :param value: The name of the storage account to associate with the workspace hub.
        :type value: str
        """
        if not value:
            return
        self._workspace_hub.storage_account = value

    # read only so no setter
    @property
    def existing_workspaces(self) -> List[str]:
        """The existing workspaces related to the workspace hub.

        :return: The names of the existing workspaces related to the workspace hub.
        :rtype: List[str]
        """
        return self._workspace_hub.existing_workspaces

    @property
    def customer_managed_key(self) -> Optional[CustomerManagedKey]:
        """The customer managed key associated with the workspace hub.

        :return: The customer managed key associated with the workspace hub.
        :rtype: Optional[~azure.ai.ml.entities.CustomerManagedKey]
        """
        return self._workspace_hub.customer_managed_key

    @customer_managed_key.setter
    def customer_managed_key(self, value: Optional[CustomerManagedKey]):
        """Sets the customer managed key associated with the workspace hub.

        :param value: The customer managed key to associate with the workspace hub.
        :type value: Optional[~azure.ai.ml.entities.CustomerManagedKey]
        """
        if not value:
            return
        self._workspace_hub.customer_managed_key = value

    @property
    def public_network_access(self) -> str:
        """The public network access to assign to the workspace hub.

        :return: The public network access to assign to the workspace hub.
        :rtype: str
        """
        return self._workspace_hub.public_network_access

    @public_network_access.setter
    def public_network_access(self, value: str):
        """Sets the public network access for the workspace hub.

        :param value: The public network access for the workspace hub
        :type value: str
        """
        if not value:
            return
        self._workspace_hub.public_network_access = value

    @property
    def identity(self) -> Optional[IdentityConfiguration]:
        """The identity associated with the workspace hub.

        :return: The identity associated with the workspace hub.
        :rtype: Optional[~azure.ai.ml.entities.IdentityConfiguration]
        """
        return self._workspace_hub.identity

    @identity.setter
    def identity(self, value: Optional[IdentityConfiguration]):
        """Sets the identity associated with the workspace hub.

        :param value: The identity to associate with the workspace hub.
        :type value: Optional[~azure.ai.ml.entities.IdentityConfiguration]
        """
        if not value:
            return
        self._workspace_hub.identity = value

    @property
    def container_registry(self) -> str:
        """The container registry associated with the workspace hub.

        :return: The container registry associated with the workspace hub.
        :rtype: str
        """
        return self._workspace_hub.container_registry
    
    @container_registry.setter
    def container_registry(self, value: str):
        """Sets the container registry for the workspace hub.

        :param value: The container registry to assign to the resource.
        :type value: str
        """
        if not value:
            return
        self._workspace_hub.container_registry = value

    @property
    def primary_user_assigned_identity(self) -> str:
        """The primary user assigned identity associated with the workspace hub.

        :return: The primary user assigned identity associated with the workspace hub.
        :rtype: str
        """
        return self._workspace_hub.primary_user_assigned_identity

    @primary_user_assigned_identity.setter
    def primary_user_assigned_identity(self, value: str):
        """Sets the primary user assigned identity for the workspace hub.

        :param value: The primary user assigned identity to assign to the resource.
        :type value: str
        """
        if not value:
            return
        self._workspace_hub.primary_user_assigned_identity = value

    # Read only so no setter.
    @property
    def enable_data_isolation(self) -> bool:
        """Whether or not data isolation is enabled for the workspace hub.

        :return: Boolean value indicating whether or not data isolation is enabled for the workspace hub.
        :rtype: bool
        """
        return self._workspace_hub.enable_data_isolation

    @property
    def default_project_resource_group(self) -> str:
        """The default project's resource group.

        :return: The name of the default project's resource group.
        :rtype: str
        """
        return self._workspace_hub.workspace_hub_config.default_workspace_resource_group

    @default_project_resource_group.setter
    def default_project_resource_group(self, value: str):
        """Sets the default project's resource group.

        :param value: The name of the resource group for the default project.
        :type value: str
        """
        if not value:
            return
        self._workspace_hub.workspace_hub_config.default_workspace_resource_group = value
