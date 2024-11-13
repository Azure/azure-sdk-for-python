# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-instance-attributes,protected-access


from os import PathLike
from pathlib import Path
from typing import Any, Dict, Optional, Union

from azure.ai.ml._restclient.v2024_07_01_preview.models import Workspace as RestWorkspace
from azure.ai.ml._schema._feature_store.feature_store_schema import FeatureStoreSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
from azure.ai.ml.entities._credentials import IdentityConfiguration, ManagedIdentityConfiguration
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.entities._workspace.compute_runtime import ComputeRuntime
from azure.ai.ml.entities._workspace.customer_managed_key import CustomerManagedKey
from azure.ai.ml.entities._workspace.feature_store_settings import FeatureStoreSettings
from azure.ai.ml.entities._workspace.networking import ManagedNetwork
from azure.ai.ml.entities._workspace.workspace import Workspace
from azure.ai.ml.constants._common import WorkspaceKind
from ._constants import DEFAULT_SPARK_RUNTIME_VERSION
from .materialization_store import MaterializationStore


class FeatureStore(Workspace):
    """Feature Store

    :param name: The name of the feature store.
    :type name: str
    :param compute_runtime: The compute runtime of the feature store. Defaults to None.
    :type compute_runtime: Optional[~azure.ai.ml.entities.ComputeRuntime]
    :param offline_store: The offline store for feature store.
        materialization_identity is required when offline_store is passed. Defaults to None.
    :type offline_store: Optional[~azure.ai.ml.entities.MaterializationStore]
    :param online_store: The online store for feature store.
        materialization_identity is required when online_store is passed.  Defaults to None.
    :type online_store: Optional[~azure.ai.ml.entities.MaterializationStore]
    :param materialization_identity: The identity used for materialization. Defaults to None.
    :type materialization_identity: Optional[~azure.ai.ml.entities.ManagedIdentityConfiguration]
    :param description: The description of the feature store. Defaults to None.
    :type description: Optional[str]
    :param tags: Tags of the feature store.
    :type tags: dict
    :param display_name: The display name for the feature store. This is non-unique within the resource group.
        Defaults to None.
    :type display_name: Optional[str]
    :param location: The location to create the feature store in.
        If not specified, the same location as the resource group will be used. Defaults to None.
    :type location: Optional[str]
    :param resource_group: The name of the resource group to create the feature store in. Defaults to None.
    :type resource_group: Optional[str]
    :param hbi_workspace: Boolean for whether the customer data is of high business impact (HBI),
        containing sensitive business information. Defaults to False.
        For more information, see
        https://docs.microsoft.com/azure/machine-learning/concept-data-encryption#encryption-at-rest.
    :type hbi_workspace: Optional[bool]
    :param storage_account: The resource ID of an existing storage account to use instead of creating a new one.
        Defaults to None.
    :type storage_account: Optional[str]
    :param container_registry: The resource ID of an existing container registry
        to use instead of creating a new one. Defaults to None.
    :type container_registry: Optional[str]
    :param key_vault: The resource ID of an existing key vault to use instead of creating a new one. Defaults to None.
    :type key_vault: Optional[str]
    :param application_insights: The resource ID of an existing application insights
        to use instead of creating a new one. Defaults to None.
    :type application_insights: Optional[str]
    :param customer_managed_key: The key vault details for encrypting data with customer-managed keys.
        If not specified, Microsoft-managed keys will be used by default. Defaults to None.
    :type customer_managed_key: Optional[CustomerManagedKey]
    :param image_build_compute: The name of the compute target to use for building environment
        Docker images with the container registry is behind a VNet. Defaults to None.
    :type image_build_compute: Optional[str]
    :param public_network_access: Whether to allow public endpoint connectivity
        when a workspace is private link enabled. Defaults to None.
    :type public_network_access: Optional[str]
    :param identity: The workspace's Managed Identity (user assigned, or system assigned). Defaults to None.
    :type identity: Optional[IdentityConfiguration]
    :param primary_user_assigned_identity: The workspace's primary user assigned identity. Defaults to None.
    :type primary_user_assigned_identity: Optional[str]
    :param managed_network: The workspace's Managed Network configuration. Defaults to None.
    :type managed_network: Optional[ManagedNetwork]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_featurestore.py
            :start-after: [START create_feature_store]
            :end-before: [END create_feature_store]
            :language: Python
            :dedent: 8
            :caption: Instantiating a Feature Store object
    """

    def __init__(
        self,
        *,
        name: str,
        compute_runtime: Optional[ComputeRuntime] = None,
        offline_store: Optional[MaterializationStore] = None,
        online_store: Optional[MaterializationStore] = None,
        materialization_identity: Optional[ManagedIdentityConfiguration] = None,
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
        **kwargs: Any,
    ) -> None:
        feature_store_settings = kwargs.pop(
            "feature_store_settings",
            FeatureStoreSettings(
                compute_runtime=(
                    compute_runtime
                    if compute_runtime
                    else ComputeRuntime(spark_runtime_version=DEFAULT_SPARK_RUNTIME_VERSION)
                ),
            ),
        )
        # TODO: Refactor this so that super().__init__() is not called twice coming from _from_rest_object()
        super().__init__(
            name=name,
            description=description,
            tags=tags,
            kind=WorkspaceKind.FEATURE_STORE,
            display_name=display_name,
            location=location,
            resource_group=resource_group,
            hbi_workspace=hbi_workspace,
            storage_account=storage_account,
            container_registry=container_registry,
            key_vault=key_vault,
            application_insights=application_insights,
            customer_managed_key=customer_managed_key,
            image_build_compute=image_build_compute,
            public_network_access=public_network_access,
            managed_network=managed_network,
            identity=identity,
            primary_user_assigned_identity=primary_user_assigned_identity,
            feature_store_settings=feature_store_settings,
            **kwargs,
        )
        self.offline_store = offline_store
        self.online_store = online_store
        self.materialization_identity = materialization_identity
        self.identity = identity
        self.public_network_access = public_network_access
        self.managed_network = managed_network
        # here, compute_runtime is used instead of feature_store_settings because
        # it uses default spark version if no compute_runtime is specified during update
        self.compute_runtime = compute_runtime

    @classmethod
    def _from_rest_object(
        cls, rest_obj: RestWorkspace, v2_service_context: Optional[object] = None
    ) -> Optional["FeatureStore"]:
        if not rest_obj:
            return None

        workspace_object = Workspace._from_rest_object(rest_obj, v2_service_context)
        if workspace_object is not None:
            return FeatureStore(
                name=str(workspace_object.name),
                id=workspace_object.id,
                description=workspace_object.description,
                tags=workspace_object.tags,
                compute_runtime=ComputeRuntime._from_rest_object(
                    workspace_object._feature_store_settings.compute_runtime
                    if workspace_object._feature_store_settings
                    else None
                ),
                display_name=workspace_object.display_name,
                discovery_url=workspace_object.discovery_url,
                location=workspace_object.location,
                resource_group=workspace_object.resource_group,
                hbi_workspace=workspace_object.hbi_workspace,
                storage_account=workspace_object.storage_account,
                container_registry=workspace_object.container_registry,
                key_vault=workspace_object.key_vault,
                application_insights=workspace_object.application_insights,
                customer_managed_key=workspace_object.customer_managed_key,
                image_build_compute=workspace_object.image_build_compute,
                public_network_access=workspace_object.public_network_access,
                identity=workspace_object.identity,
                primary_user_assigned_identity=workspace_object.primary_user_assigned_identity,
                managed_network=workspace_object.managed_network,
                workspace_id=rest_obj.workspace_id,
                feature_store_settings=workspace_object._feature_store_settings,
            )

        return None

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs: Any,
    ) -> "FeatureStore":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }
        loaded_schema = load_from_dict(FeatureStoreSchema, data, context, **kwargs)
        return FeatureStore(**loaded_schema)

    def _to_dict(self) -> Dict:
        # pylint: disable=no-member
        res: dict = FeatureStoreSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)
        return res
