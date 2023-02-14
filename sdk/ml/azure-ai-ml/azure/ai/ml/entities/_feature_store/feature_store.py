# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-instance-attributes

from typing import IO, AnyStr, Dict, Optional, Union

from azure.ai.ml.entities._workspace.workspace import Workspace, CustomerManagedKey, FeatureStoreSettings
from azure.ai.ml.entities._credentials import IdentityConfiguration


class FeatureStore(Workspace):
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
        feature_store_settings: FeatureStoreSettings,
        **kwargs,
    ):
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
            primary_user_assigned_identity=primary_user_assigned_identity,
            feature_store_settings=feature_store_settings,
            ** kwargs
        )
