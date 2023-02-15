# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-instance-attributes

from typing import IO, AnyStr, Dict, Optional, Union

from azure.ai.ml._restclient.v2022_12_01_preview.models import Workspace as RestWorkspace
from azure.ai.ml.entities import Workspace, CustomerManagedKey, FeatureStoreSettings, ComputeRuntimeDto
from azure.ai.ml.entities._credentials import IdentityConfiguration


class FeatureStore:
    def __init__(
        self,
        *,
        name: str,
        spark_runtime_version: Optional[str] = None,
        offline_store: Optional[str] = None,
        online_store: Optional[str] = None,
        allow_role_assignments_on_resource_group_level: bool = False,
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
        **kwargs,
    ):
        feature_store_settings = FeatureStoreSettings(
            compute_runtime=ComputeRuntimeDto(
                spark_runtime_version=spark_runtime_version
            ),
            offline_store_connection_name=offline_store,
            online_store_connection_name=online_store,
            allow_role_assignments_on_resource_group_level=allow_role_assignments_on_resource_group_level
        )
        Workspace(
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
            primary_user_assigned_identity=primary_user_assigned_identity,
            feature_store_settings=feature_store_settings,
            ** kwargs
        )

    @classmethod
    def _from_rest_object(cls, rest_obj: RestWorkspace) -> "FeatureStore":

        if not rest_obj:
            return None

        workspace_object = Workspace._from_rest_object(rest_obj)

        return FeatureStore(
            name=workspace_object.name
        )
