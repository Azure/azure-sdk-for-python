# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-instance-attributes

from typing import Dict, Optional

from azure.ai.ml._restclient.v2022_12_01_preview.models import Workspace as RestWorkspace
from azure.ai.ml.entities import (
    Workspace,
    CustomerManagedKey,
    FeatureStoreSettings,
    ComputeRuntime,
    WorkspaceConnection,
    ManagedNetwork
)
from .materialization_store import MaterializationStore
from azure.ai.ml.entities._credentials import (
    IdentityConfiguration,
    ManagedIdentityConfiguration
)
from ._constants import OFFLINE_STORE_CONNECTION_NAME, DEFAULT_SPARK_RUNTIME_VERSION


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
        managed_network: Optional[ManagedNetwork] = None,
        **kwargs,
    ):
        feature_store_settings = FeatureStoreSettings(
            compute_runtime=compute_runtime if compute_runtime else ComputeRuntime(
                spark_runtime_version=DEFAULT_SPARK_RUNTIME_VERSION),
            offline_store_connection_name=OFFLINE_STORE_CONNECTION_NAME if materialization_identity and offline_store else None
        )
        super().__init__(
            name=name,
            description=description,
            tags=tags,
            kind="FeatureStore",
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
            managed_network=managed_network,
            feature_store_settings=feature_store_settings,
            ** kwargs
        )
        self.offline_store = offline_store
        self.materialization_identity = materialization_identity
        self.identity = identity

    @classmethod
    def _from_rest_object(cls, rest_obj: RestWorkspace) -> "FeatureStore":

        if not rest_obj:
            return None

        workspace_object = Workspace._from_rest_object(rest_obj)

        return FeatureStore(
            name=workspace_object.name,
            description=workspace_object.description,
            tags=workspace_object.tags,
            compute_runtime=workspace_object.feature_store_settings.compute_runtime,
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
            managed_network=workspace_object.managed_network,
        )
