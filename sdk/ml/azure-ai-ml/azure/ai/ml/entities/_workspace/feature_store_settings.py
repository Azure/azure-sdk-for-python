# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional, Any

from azure.ai.ml._restclient.v2022_12_01_preview.models import FeatureStoreSettings as RestFeatureStoreSettings
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from .compute_runtime_dto import ComputeRuntimeDto


class FeatureStoreSettings(RestTranslatableMixin):
    def __init__(
        self,
        *,
        compute_runtime: ComputeRuntimeDto,
        offline_store_connection_name: Optional[str] = None,
        online_store_connection_name: Optional[str] = None,
        allow_role_assignments_on_resource_group_level: Optional[bool] = None,
        **kwargs
    ):
        """
        :keyword compute_runtime:
        :paramtype compute_runtime: ~azure.mgmt.machinelearningservices.models.ComputeRuntimeDto
        :keyword offline_store_connection_name:
        :paramtype offline_store_connection_name: str
        :keyword online_store_connection_name:
        :paramtype online_store_connection_name: str
        :keyword allow_role_assignments_on_resource_group_level:
        :paramtype allow_role_assignments_on_resource_group_level: bool
        """
        self.compute_runtime = compute_runtime
        self.offline_store_connection_name = offline_store_connection_name
        self.online_store_connection_name = online_store_connection_name
        self.allow_role_assignments_on_resource_group_level = allow_role_assignments_on_resource_group_level

    def _to_rest_object(self) -> RestFeatureStoreSettings:
        return RestFeatureStoreSettings(
            compute_runtime=ComputeRuntimeDto._to_rest_object(self.compute_runtime),
            offline_store_connection_name=self.offline_store_connection_name,
            online_store_connection_name=self.online_store_connection_name,
            allow_role_assignments_on_resource_group_level=self.allow_role_assignments_on_resource_group_level
        )
        pass

    @classmethod
    def _from_rest_object(cls, rest_obj: RestFeatureStoreSettings) -> "FeatureStoreSettings":
        if not rest_obj:
            return None
        return FeatureStoreSettings(
            compute_runtime=ComputeRuntimeDto._from_rest_object(rest_obj.compute_runtime),
            offline_store_connection_name=rest_obj.offline_store_connection_name,
            online_store_connection_name=rest_obj.online_store_connection_name,
            allow_role_assignments_on_resource_group_level=rest_obj.allow_role_assignments_on_resource_group_level
        )