# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from typing import Dict, Optional

from azure.ai.ml.entities import CustomerManagedKey, WorkspaceHub
from azure.ai.ml.entities._credentials import IdentityConfiguration
from azure.ai.ml.entities._workspace.networking import ManagedNetwork
from azure.ai.ml.entities._workspace_hub.workspace_hub_config import WorkspaceHubConfig


# Effectively a lightweight wrapper around a v2 WorkspaceHub
class AIResource:
    """An AI Resource, which serves as a container for projects and other AI-related objects"""

    # TODO full docstring
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
        primary_user_assigned_identity: Optional[str] = None,
        default_project_resource_group: Optional[str] = None,  # Unpacked WorkspaceHubConfig field
        **kwargs,
    ):
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
        """The read-only id of the resource. Set by the backend.

        :return: ID of the resource.
        :rtype: str
        """
        return self._workspace_hub.id
    
    @property
    def name(self) -> str:
        """The name of the resource.

        :return: Name of the resource.
        :rtype: str
        """
        return self._workspace_hub.name

    @name.setter
    def name(self, value: str):
        """Set the name of the resource.

        :param value: The new type to assign to the resource.
        :type value: str
        """
        if not value:
            return
        self._workspace_hub.name = value

    @property
    def description(self) -> str:
        """The description of the resource.

        :return: Name of the resource.
        :rtype: str
        """
        return self._workspace_hub.description

    @description.setter
    def description(self, value: str):
        """Set the description of the resource.

        :param value: The new type to assign to the resource.
        :type value: str
        """
        if not value:
            return
        self._workspace_hub.description = value

    @property
    def tags(self) -> str:
        """The tags of the resource.

        :return: Name of the resource.
        :rtype: str
        """
        return self._workspace_hub.tags

    @tags.setter
    def tags(self, value: str):
        """Set the tags of the resource.

        :param value: The new type to assign to the resource.
        :type value: str
        """
        if not value:
            return
        self._workspace_hub.tags = value

    @property
    def display_name(self) -> str:
        """The display_name of the resource.

        :return: Name of the resource.
        :rtype: str
        """
        return self._workspace_hub.display_name

    @display_name.setter
    def display_name(self, value: str):
        """Set the display_name of the resource.

        :param value: The new type to assign to the resource.
        :type value: str
        """
        if not value:
            return
        self._workspace_hub.display_name = value

    @property
    def location(self) -> str:
        """The location of the resource.

        :return: Name of the resource.
        :rtype: str
        """
        return self._workspace_hub.location

    @location.setter
    def location(self, value: str):
        """Set the location of the resource.

        :param value: The new type to assign to the resource.
        :type value: str
        """
        if not value:
            return
        self._workspace_hub.location = value

    @property
    def resource_group(self) -> str:
        """The resource_group of the resource.

        :return: Name of the resource.
        :rtype: str
        """
        return self._workspace_hub.resource_group

    @resource_group.setter
    def resource_group(self, value: str):
        """Set the resource_group of the resource.

        :param value: The new type to assign to the resource.
        :type value: str
        """
        if not value:
            return
        self._workspace_hub.resource_group = value

    @property
    def managed_network(self) -> str:
        """The managed_network of the resource.

        :return: Name of the resource.
        :rtype: str
        """
        return self._workspace_hub.managed_network

    @managed_network.setter
    def managed_network(self, value: str):
        """Set the managed_network of the resource.

        :param value: The new type to assign to the resource.
        :type value: str
        """
        if not value:
            return
        self._workspace_hub.managed_network = value

    @property
    def storage_account(self) -> str:
        """The storage_account of the resource.

        :return: Name of the resource.
        :rtype: str
        """
        return self._workspace_hub.storage_account

    @storage_account.setter
    def storage_account(self, value: str):
        """Set the storage_account of the resource.

        :param value: The new type to assign to the resource.
        :type value: str
        """
        if not value:
            return
        self._workspace_hub.storage_account = value

    # read only so no setter
    @property
    def existing_workspaces(self) -> str:
        """The existing_workspaces of the resource.

        :return: Name of the resource.
        :rtype: str
        """
        return self._workspace_hub.existing_workspaces

    @property
    def customer_managed_key(self) -> str:
        """The customer_managed_key of the resource.

        :return: Name of the resource.
        :rtype: str
        """
        return self._workspace_hub.customer_managed_key

    @customer_managed_key.setter
    def customer_managed_key(self, value: str):
        """Set the customer_managed_key of the resource.

        :param value: The new type to assign to the resource.
        :type value: str
        """
        if not value:
            return
        self._workspace_hub.customer_managed_key = value

    @property
    def public_network_access(self) -> str:
        """The public_network_access of the resource.

        :return: Name of the resource.
        :rtype: str
        """
        return self._workspace_hub.public_network_access

    @public_network_access.setter
    def public_network_access(self, value: str):
        """Set the public_network_access of the resource.

        :param value: The new type to assign to the resource.
        :type value: str
        """
        if not value:
            return
        self._workspace_hub.public_network_access = value

    @property
    def identity(self) -> str:
        """The identity of the resource.

        :return: Name of the resource.
        :rtype: str
        """
        return self._workspace_hub.identity

    @identity.setter
    def identity(self, value: str):
        """Set the identity of the resource.

        :param value: The new type to assign to the resource.
        :type value: str
        """
        if not value:
            return
        self._workspace_hub.identity = value

    @property
    def primary_user_assigned_identity(self) -> str:
        """The primary_user_assigned_identity of the resource.

        :return: Name of the resource.
        :rtype: str
        """
        return self._workspace_hub.primary_user_assigned_identity

    @primary_user_assigned_identity.setter
    def primary_user_assigned_identity(self, value: str):
        """Set the primary_user_assigned_identity of the resource.

        :param value: The new type to assign to the resource.
        :type value: str
        """
        if not value:
            return
        self._workspace_hub.primary_user_assigned_identity = value

    # Read only so no setter.
    @property
    def enable_data_isolation(self) -> str:
        """The enable_data_isolation of the resource.

        :return: Name of the resource.
        :rtype: str
        """
        return self._workspace_hub.enable_data_isolation

    @property
    def default_project_resource_group(self) -> str:
        """The default_project_resource_group of the resource.

        :return: Name of the resource.
        :rtype: str
        """
        return self._workspace_hub.workspace_hub_config.default_workspace_resource_group

    @default_project_resource_group.setter
    def default_project_resource_group(self, value: str):
        """Set the default_project_resource_group of the resource.

        :param value: The new type to assign to the resource.
        :type value: str
        """
        if not value:
            return
        self._workspace_hub.workspace_hub_config.default_workspace_resource_group = value
