# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-instance-attributes

from os import PathLike
from pathlib import Path
from typing import IO, AnyStr, Dict, Union

from azure.ai.ml._restclient.v2022_10_01_preview.models import ManagedServiceIdentity as RestManagedServiceIdentity
from azure.ai.ml._restclient.v2022_10_01_preview.models import Workspace as RestWorkspace
from azure.ai.ml._schema.workspace.workspace import WorkspaceSchema
from azure.ai.ml._utils.utils import dump_yaml_to_file
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY, WorkspaceResourceConstants
from azure.ai.ml.entities._credentials import IdentityConfiguration
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.entities._util import load_from_dict

from .customer_managed_key import CustomerManagedKey


class Workspace(Resource):
    def __init__(
        self,
        *,
        name: str,
        description: str = None,
        tags: Dict[str, str] = None,
        display_name: str = None,
        location: str = None,
        resource_group: str = None,
        hbi_workspace: bool = False,
        storage_account: str = None,
        container_registry: str = None,
        key_vault: str = None,
        application_insights: str = None,
        customer_managed_key: CustomerManagedKey = None,
        image_build_compute: str = None,
        public_network_access: str = None,
        identity: IdentityConfiguration = None,
        primary_user_assigned_identity: str = None,
        **kwargs,
    ):

        """Azure ML workspace.

        :param name: Name of the workspace.
        :type name: str
        :param description: Description of the workspace.
        :type description: str
        :param tags: Tags of the workspace.
        :type tags: dict
        :param display_name: Display name for the workspace. This is non-unique within the resource group.
        :type display_name: str
        :param location: The location to create the workspace in.
            If not specified, the same location as the resource group will be used.
        :type location: str
        :param resource_group: Name of resource group to create the workspace in.
        :type resource_group: str
        :param hbi_workspace: Whether the customer data is of high business impact (HBI),
            containing sensitive business information.
            For more information, see
            https://docs.microsoft.com/azure/machine-learning/concept-data-encryption#encryption-at-rest.
        :type hbi_workspace: bool
        :param storage_account: The resource ID of an existing storage account to use instead of creating a new one.
        :type storage_account: str
        :param container_registry: The resource ID of an existing container registry
            to use instead of creating a new one.
        :type container_registry: str
        :param key_vault: The resource ID of an existing key vault to use instead of creating a new one.
        :type key_vault: str
        :param application_insights: The resource ID of an existing application insights
            to use instead of creating a new one.
        :type application_insights: str
        :param customer_managed_key: Key vault details for encrypting data with customer-managed keys.
            If not specified, Microsoft-managed keys will be used by default.
        :type customer_managed_key: CustomerManagedKey
        :param image_build_compute: The name of the compute target to use for building environment
            Docker images with the container registry is behind a VNet.
        :type image_build_compute: str
        :param public_network_access: Whether to allow public endpoint connectivity
            when a workspace is private link enabled.
        :type public_network_access: str
        :param identity: workspace's Managed Identity (user assigned, or system assigned)
        :type identity: IdentityConfiguration
        :param primary_user_assigned_identity: The workspace's primary user assigned identity
        :type primary_user_assigned_identity: str
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict
        """
        self._discovery_url = kwargs.pop("discovery_url", None)
        self._mlflow_tracking_uri = kwargs.pop("mlflow_tracking_uri", None)
        super().__init__(name=name, description=description, tags=tags, **kwargs)

        self.display_name = display_name
        self.location = location
        self.resource_group = resource_group
        self.hbi_workspace = hbi_workspace
        self.storage_account = storage_account
        self.container_registry = container_registry
        self.key_vault = key_vault
        self.application_insights = application_insights
        self.customer_managed_key = customer_managed_key
        self.image_build_compute = image_build_compute
        self.public_network_access = public_network_access
        self.identity = identity
        self.primary_user_assigned_identity = primary_user_assigned_identity

    @property
    def discovery_url(self) -> str:
        """Backend service base URLs for the workspace.

        :return: Backend service URLs of the workspace
        :rtype: str
        """
        return self._discovery_url

    @property
    def mlflow_tracking_uri(self) -> str:
        """MLflow tracking uri for the workspace.

        :return: Returns mlflow tracking uri of the workspace.
        :rtype: str
        """
        return self._mlflow_tracking_uri

    def dump(self, dest: Union[str, PathLike, IO[AnyStr]], **kwargs) -> None:
        """Dump the workspace spec into a file in yaml format.

        :param dest: The destination to receive this workspace's spec.
            Must be either a path to a local file, or an already-open file stream.
            If dest is a file path, a new file will be created,
            and an exception is raised if the file exists.
            If dest is an open file, the file will be written to directly,
            and an exception will be raised if the file is not writable.
        :type dest: Union[PathLike, str, IO[AnyStr]]
        """
        path = kwargs.pop("path", None)
        yaml_serialized = self._to_dict()
        dump_yaml_to_file(dest, yaml_serialized, default_flow_style=False, path=path, **kwargs)

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        return WorkspaceSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    @classmethod
    def _load(
        cls,
        data: Dict = None,
        yaml_path: Union[PathLike, str] = None,
        params_override: list = None,
        **kwargs,
    ) -> "Workspace":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        loaded_schema = load_from_dict(WorkspaceSchema, data, context, **kwargs)
        return Workspace(**loaded_schema)

    @classmethod
    def _from_rest_object(cls, rest_obj: RestWorkspace) -> "Workspace":

        if not rest_obj:
            return None
        customer_managed_key = (
            CustomerManagedKey(
                key_vault=rest_obj.encryption.key_vault_properties.key_vault_arm_id,
                key_uri=rest_obj.encryption.key_vault_properties.key_identifier,
            )
            if rest_obj.encryption
            and rest_obj.encryption.status == WorkspaceResourceConstants.ENCRYPTION_STATUS_ENABLED
            else None
        )

        # TODO: Remove attribute check once Oct API version is out
        mlflow_tracking_uri = None
        if hasattr(rest_obj, "ml_flow_tracking_uri"):
            mlflow_tracking_uri = rest_obj.ml_flow_tracking_uri

        armid_parts = str(rest_obj.id).split("/")
        group = None if len(armid_parts) < 4 else armid_parts[4]
        identity = None
        if rest_obj.identity and isinstance(rest_obj.identity, RestManagedServiceIdentity):
            identity = IdentityConfiguration._from_workspace_rest_object(rest_obj.identity) # pylint: disable=protected-access
        return Workspace(
            name=rest_obj.name,
            id=rest_obj.id,
            description=rest_obj.description,
            tags=rest_obj.tags,
            location=rest_obj.location,
            resource_group=group,
            display_name=rest_obj.friendly_name,
            discovery_url=rest_obj.discovery_url,
            hbi_workspace=rest_obj.hbi_workspace,
            storage_account=rest_obj.storage_account,
            container_registry=rest_obj.container_registry,
            key_vault=rest_obj.key_vault,
            application_insights=rest_obj.application_insights,
            customer_managed_key=customer_managed_key,
            image_build_compute=rest_obj.image_build_compute,
            public_network_access=rest_obj.public_network_access,
            mlflow_tracking_uri=mlflow_tracking_uri,
            identity=identity,
            primary_user_assigned_identity=rest_obj.primary_user_assigned_identity,
        )

    def _to_rest_object(self) -> RestWorkspace:
        return RestWorkspace(
            # pylint: disable=protected-access
            identity=self.identity._to_workspace_rest_object() if self.identity else None,
            location=self.location,
            tags=self.tags,
            description=self.description,
            friendly_name=self.display_name,
            key_vault=self.key_vault,
            application_insights=self.application_insights,
            container_registry=self.container_registry,
            storage_account=self.storage_account,
            discovery_url=self.discovery_url,
            hbi_workspace=self.hbi_workspace,
            image_build_compute=self.image_build_compute,
            public_network_access=self.public_network_access,
            primary_user_assigned_identity=self.primary_user_assigned_identity,
        )
