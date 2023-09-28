# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-instance-attributes,protected-access


from os import PathLike
from pathlib import Path
from typing import Dict, List, Optional, Union

from azure.ai.ml._restclient.v2023_06_01_preview.models import Workspace as RestWorkspace
from azure.ai.ml._restclient.v2023_06_01_preview.models import WorkspaceHubConfig as RestWorkspaceHubConfig

from azure.ai.ml._schema._workspace_hub.workspace_hub import WorkspaceHubSchema
from azure.ai.ml.entities._workspace_hub.workspace_hub_config import WorkspaceHubConfig
from azure.ai.ml.entities._credentials import IdentityConfiguration
from azure.ai.ml.entities._workspace.networking import ManagedNetwork
from azure.ai.ml.entities import Workspace, CustomerManagedKey
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
from azure.ai.ml._utils._experimental import experimental

from ._constants import WORKSPACE_HUB_KIND


@experimental
class WorkspaceHub(Workspace):
    """WorkspaceHub.

    :param name: Name of the WorkspaceHub.
    :type name: str
    :param description: Description of the WorkspaceHub.
    :type description: str
    :param tags: Tags of the WorkspaceHub.
    :type tags: dict
    :param display_name: Display name for the WorkspaceHub. This is non-unique within the resource group.
    :type display_name: str
    :param location: The location to create the WorkspaceHub in.
        If not specified, the same location as the resource group will be used.
    :type location: str
    :param resource_group: Name of resource group to create the WorkspaceHub in.
    :type resource_group: str
    :param managed_network: WorkspaceHub's Managed Network configuration
    :type managed_network: ~azure.ai.ml.entities.ManagedNetwork
    :param storage_account: The resource ID of an existing storage account to use instead of creating a new one.
    :type storage_account: str
    :param key_vault: The resource ID of an existing key vault to use instead of creating a new one.
    :type key_vault: str
    :param container_registry: The resource ID of an existing container registry
        to use instead of creating a new one.
    :type container_registry: str
    :param existing_workspaces: List of existing workspaces to convert to use this workspaceHub's shared resources.
    :type existing_workspaces: List[str]
    :param customer_managed_key: Key vault details for encrypting data with customer-managed keys.
        If not specified, Microsoft-managed keys will be used by default.
    :type customer_managed_key: ~azure.ai.ml.entities.CustomerManagedKey
    :param image_build_compute: The name of the compute target to use for building environment
        Docker images with the container registry is behind a VNet.
    :type public_network_access: str
    :param identity: workspaceHub's Managed Identity (user assigned, or system assigned)
    :type identity: ~azure.ai.ml.entities.IdentityConfiguration
    :param primary_user_assigned_identity: The workspaceHub's primary user assigned identity
    :type primary_user_assigned_identity: str
    :param enable_data_isolation: A flag to determine if workspace has data isolation enabled.
        The flag can only be set at the creation phase, it can't be updated.
    :type enable_data_isolation: bool
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict

    .. literalinclude:: ../samples/ml_samples_workspace.py
            :start-after: [START workspace_hub]
            :end-before: [END workspace_hub]
            :language: python
            :dedent: 8
            :caption: Creating a WorkspaceHub object.
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
        key_vault: Optional[str] = None,
        container_registry: Optional[str] = None,
        existing_workspaces: Optional[List[str]] = None,
        customer_managed_key: Optional[CustomerManagedKey] = None,
        public_network_access: Optional[str] = None,
        identity: Optional[IdentityConfiguration] = None,
        primary_user_assigned_identity: Optional[str] = None,
        enable_data_isolation: bool = False,
        workspace_hub_config: Optional[WorkspaceHubConfig] = None,
        **kwargs,
    ):
        self._workspace_id = kwargs.pop("workspace_id", "")
        super().__init__(
            name=name,
            description=description,
            tags=tags,
            kind=WORKSPACE_HUB_KIND,
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
        self.existing_workspaces = existing_workspaces
        self.workspace_hub_config = workspace_hub_config
        self.associated_workspaces = None

    @classmethod
    def _from_rest_object(cls, rest_obj: RestWorkspace) -> "WorkspaceHub":
        if not rest_obj:
            return None

        workspace_object = Workspace._from_rest_object(rest_obj)

        workspace_hub_config = None
        if hasattr(rest_obj, "workspace_hub_config"):
            if rest_obj.workspace_hub_config and isinstance(rest_obj.workspace_hub_config, RestWorkspaceHubConfig):
                workspace_hub_config = WorkspaceHubConfig._from_rest_object(  # pylint: disable=protected-access
                    rest_obj.workspace_hub_config
                )

        workspacehub_object = WorkspaceHub(
            name=workspace_object.name,
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
            existing_workspaces=rest_obj.existing_workspaces,
            workspace_id=rest_obj.workspace_id,
            enable_data_isolation=rest_obj.enable_data_isolation,
            workspace_hub_config=workspace_hub_config,
            id=rest_obj.id,
        )
        workspacehub_object.set_associated_workspaces(rest_obj.associated_workspaces)
        return workspacehub_object

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs,
    ) -> "WorkspaceHub":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        loaded_schema = load_from_dict(WorkspaceHubSchema, data, context, **kwargs)
        return WorkspaceHub(**loaded_schema)

    def set_associated_workspaces(self, value: List[str]):
        """Sets the workspaces associated with the hub, not meant for use by the user.

        :param value: List of workspace ARM ids.
        :type value: List[str]
        """
        self.associated_workspaces = value

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return WorkspaceHubSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    def _to_rest_object(self) -> RestWorkspace:
        restWorkspace = super()._to_rest_object()
        restWorkspace.workspace_hub_config = (self.workspace_hub_config,)
        restWorkspace.existing_workspaces = (self.existing_workspaces,)
        return restWorkspace
