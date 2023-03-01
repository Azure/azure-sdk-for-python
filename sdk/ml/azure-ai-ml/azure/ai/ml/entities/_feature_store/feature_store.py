# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-instance-attributes

from typing import Dict, Optional

from azure.ai.ml._restclient.v2022_12_01_preview.models import Workspace as RestWorkspace
from azure.ai.ml.entities import Workspace, CustomerManagedKey, FeatureStoreSettings, ComputeRuntime
from azure.ai.ml.entities._credentials import IdentityConfiguration, ManagedIdentityConfiguration
from azure.ai.ml._utils._experimental import experimental

from .materialization_store import MaterializationStore
from ._constants import OFFLINE_STORE_CONNECTION_NAME, DEFAULT_SPARK_RUNTIME_VERSION, FEATURE_STORE_KIND


@experimental
class FeatureStore(Workspace):
    def __init__(
        self,
        *,
        name: str,
        compute_runtime: Optional[ComputeRuntime] = None,
        offline_store: Optional[MaterializationStore] = None,
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
        **kwargs,
    ):

        """FeatureStore.

        :param name: Name of the feature store.
        :type name: str
        :param compute_runtime: Compute runtime of the feature store.
        :type compute_runtime: ~azure.ai.ml.entities.ComputeRuntime
        :param offline_store: Offline store for feature store.
        :type offline_store: ~azure.ai.ml.entities.MaterializationStore
        :param materialization_identity: Identity used for materialization.
        :type materialization_identity: ~azure.ai.ml.entities.ManagedIdentityConfiguration
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
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict
        """

        feature_store_settings = FeatureStoreSettings(
            compute_runtime=compute_runtime
            if compute_runtime
            else ComputeRuntime(spark_runtime_version=DEFAULT_SPARK_RUNTIME_VERSION),
            offline_store_connection_name=(
                OFFLINE_STORE_CONNECTION_NAME if materialization_identity and offline_store else None
            ),
        )
        super().__init__(
            name=name,
            description=description,
            tags=tags,
            kind=FEATURE_STORE_KIND,
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
            identity=identity,
            feature_store_settings=feature_store_settings,
            **kwargs,
        )
        self.offline_store = offline_store
        self.materialization_identity = materialization_identity
        self.identity = identity

    @classmethod
    def _from_rest_object(cls, rest_obj: RestWorkspace) -> "FeatureStore":
        if not rest_obj:
            return None

        workspace_object = Workspace._from_rest_object(rest_obj)  # pylint: disable=protected-access

        return FeatureStore(
            name=workspace_object.name,
            description=workspace_object.description,
            tags=workspace_object.tags,
            compute_runtime=ComputeRuntime._from_rest_object(  # pylint: disable=protected-access
                workspace_object.feature_store_settings.compute_runtime
                if workspace_object.feature_store_settings
                else None
            ),
            display_name=workspace_object.display_name,
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
        )
