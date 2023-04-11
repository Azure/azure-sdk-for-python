# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-instance-attributes,protected-access


from os import PathLike
from pathlib import Path
from typing import Dict, List, Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import Workspace as RestWorkspace

from azure.ai.ml._schema._hub.hub import HubSchema
from azure.ai.ml.entities._credentials import IdentityConfiguration
from azure.ai.ml.entities._workspace.networking import ManagedNetwork
from azure.ai.ml.entities import Workspace, CustomerManagedKey
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY

from ._constants import HUB_KIND

class WorkspaceHub(Workspace):
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
        storage_accounts: Optional[List[str]] = None,
        key_vaults: Optional[List[str]] = None,
        container_registries: Optional[List[str]] = None,
        existing_workspaces: Optional[List[str]] = None,
        customer_managed_key: Optional[CustomerManagedKey] = None,
        public_network_access: Optional[str] = None,
        identity: Optional[IdentityConfiguration] = None,
        primary_user_assigned_identity: Optional[str] = None,
        **kwargs,
    ):

        """WorkspaceHub.

        :param name: Name of the feature store.
        :type name: str
        :param description: Description of the feature store.
        :type description: str
        :param tags: Tags of the feature store.
        :type tags: dict
        :param display_name: Display name for the feature store. This is non-unique within the resource group.
        :type display_name: str
        :param location: The location to create the feature store in.
            If not specified, the same location as the resource group will be used.
        :type location: str
        :param resource_group: Name of resource group to create the feature store in.
        :type resource_group: str
        :param managed_network: workspace's Managed Network configuration
        :type managed_network: ManagedNetwork
        :param storage_accounts: List of storage accounts used by Hub
        :type storage_accounts: List[str]
        :param key_vaults: List of key vaults used by Hub
        :key_vaults: List[str]
        :param container_registries: List of container registries used by Hub
        :type container_registries: List[str]
        :param existing_workspaces: List of existing workspaces used by Hub to do convert
        :type existing_workspaces: List[str]
        :param customer_managed_key: Key vault details for encrypting data with customer-managed keys.
            If not specified, Microsoft-managed keys will be used by default.
        :type customer_managed_key: CustomerManagedKey
        :param image_build_compute: The name of the compute target to use for building environment
            Docker images with the container registry is behind a VNet.
        :type public_network_access: str
        :param identity: workspace's Managed Identity (user assigned, or system assigned)
        :type identity: IdentityConfiguration
        :param primary_user_assigned_identity: The workspace's primary user assigned identity
        :type primary_user_assigned_identity: str
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict
        """

        self._workspace_id = kwargs.pop("workspace_id", "")
        super().__init__(
            name=name,
            description=description,
            tags=tags,
            kind=HUB_KIND,
            display_name=display_name,
            location=location,
            resource_group=resource_group,
            customer_managed_key=customer_managed_key,
            public_network_access=public_network_access,
            identity=identity,
            primary_user_assigned_identity=primary_user_assigned_identity,
            managed_network=managed_network,
            storage_accounts=storage_accounts,
            container_registries=container_registries,
            key_vaults=key_vaults,
            existing_workspaces=existing_workspaces,
            **kwargs,
        )

    @classmethod
    def _from_rest_object(cls, rest_obj: RestWorkspace) -> "WorkspaceHub":
        if not rest_obj:
            return None

        workspace_object = Workspace._from_rest_object(rest_obj)

        return WorkspaceHub(
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
            storage_accounts=workspace_object.storage_accounts,
            key_vaults=workspace_object.key_vaults,
            container_registries=workspace_object.container_registries,
            existing_workspaces=workspace_object.existing_workspaces,
            workspace_id=rest_obj.workspace_id,
            id=rest_obj.id,
        )

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
        loaded_schema = load_from_dict(HubSchema, data, context, **kwargs)
        return WorkspaceHub(**loaded_schema)

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return HubSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
