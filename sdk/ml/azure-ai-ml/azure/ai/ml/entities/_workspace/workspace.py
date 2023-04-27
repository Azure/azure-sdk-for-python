# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-instance-attributes

from os import PathLike
from pathlib import Path
from typing import IO, AnyStr, Dict, Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import ManagedServiceIdentity as RestManagedServiceIdentity
from azure.ai.ml._restclient.v2023_04_01_preview.models import FeatureStoreSettings as RestFeatureStoreSettings
from azure.ai.ml._restclient.v2023_04_01_preview.models import Workspace as RestWorkspace
from azure.ai.ml._restclient.v2023_04_01_preview.models import ManagedNetworkSettings as RestManagedNetwork
from azure.ai.ml._schema.workspace.workspace import WorkspaceSchema
from azure.ai.ml._utils.utils import dump_yaml_to_file, is_private_preview_enabled
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY, WorkspaceResourceConstants
from azure.ai.ml.entities._credentials import IdentityConfiguration
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.entities._util import load_from_dict

from .customer_managed_key import CustomerManagedKey
from .feature_store_settings import FeatureStoreSettings
from .networking import ManagedNetwork


class Workspace(Resource):
    def __init__(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        display_name: Optional[str] = None,
        location: Optional[str] = None,
        resource_group: Optional[str] = None,
        hbi_workspace: bool = False,
        storage_account: Optional[str] = None,
        container_registry: Optional[str] = None,
        key_vault: Optional[str] = None,
        application_insights: Optional[str] = None,
        customer_managed_key: Optional[CustomerManagedKey] = None,
        image_build_compute: Optional[str] = None,
        public_network_access: Optional[str] = None,
        identity: Optional[IdentityConfiguration] = None,
        primary_user_assigned_identity: Optional[str] = None,
        managed_network: Optional[ManagedNetwork] = None,
        enable_data_isolation: bool = False,
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
        :param managed_network: workspace's Managed Network configuration
        :type managed_network: ManagedNetwork
        :param enable_data_isolation: A flag to determine if workspace has data isolation enabled.
            The flag can only be set at the creation phase, it can't be updated.
        :type enable_data_isolation: bool
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict
        """
        self._discovery_url = kwargs.pop("discovery_url", None)
        self._mlflow_tracking_uri = kwargs.pop("mlflow_tracking_uri", None)
        self._kind = kwargs.pop("kind", "default")
        self._feature_store_settings: Optional[FeatureStoreSettings] = kwargs.pop("feature_store_settings", None)
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
        self.managed_network = managed_network
        self.enable_data_isolation = enable_data_isolation

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
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
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

        # TODO: remove this once it is included in API response
        managed_network = None
        if hasattr(rest_obj, "managed_network"):
            if rest_obj.managed_network and isinstance(rest_obj.managed_network, RestManagedNetwork):
                managed_network = ManagedNetwork._from_rest_object(  # pylint: disable=protected-access
                    rest_obj.managed_network
                )

        armid_parts = str(rest_obj.id).split("/")
        group = None if len(armid_parts) < 4 else armid_parts[4]
        identity = None
        if rest_obj.identity and isinstance(rest_obj.identity, RestManagedServiceIdentity):
            identity = IdentityConfiguration._from_workspace_rest_object(  # pylint: disable=protected-access
                rest_obj.identity
            )
        feature_store_settings = None
        if (
            is_private_preview_enabled()
            and rest_obj.feature_store_settings
            and isinstance(rest_obj.feature_store_settings, RestFeatureStoreSettings)
        ):
            feature_store_settings = FeatureStoreSettings._from_rest_object(  # pylint: disable=protected-access
                rest_obj.feature_store_settings
            )
        return Workspace(
            name=rest_obj.name,
            id=rest_obj.id,
            description=rest_obj.description,
            kind=rest_obj.kind.lower() if rest_obj.kind else None,
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
            managed_network=managed_network,
            feature_store_settings=feature_store_settings,
            enable_data_isolation=rest_obj.enable_data_isolation,
        )

    def _to_rest_object(self) -> RestWorkspace:
        feature_store_Settings = None
        if is_private_preview_enabled() and self._feature_store_settings:
            feature_store_Settings = self._feature_store_settings._to_rest_object()  # pylint: disable=protected-access

        return RestWorkspace(
            identity=self.identity._to_workspace_rest_object()  # pylint: disable=protected-access
            if self.identity
            else None,
            location=self.location,
            tags=self.tags,
            description=self.description,
            kind=self._kind,
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
            managed_network=self.managed_network._to_rest_object()  # pylint: disable=protected-access
            if self.managed_network
            else None,  # pylint: disable=protected-access
            feature_store_Settings=feature_store_Settings,
            enable_data_isolation=self.enable_data_isolation,
        )
