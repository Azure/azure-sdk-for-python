# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional, Any

from azure.ai.ml._restclient.v2022_12_01_preview.models import FeatureStoreSettings as RestFeatureStoreSettings
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from .compute_runtime import ComputeRuntime


class FeatureStoreSettings(RestTranslatableMixin):
    def __init__(
        self,
        *,
        compute_runtime: ComputeRuntime,
        offline_store_connection_name: Optional[str] = None,
        **kwargs
    ):
        """
        :keyword compute_runtime:
        :paramtype compute_runtime: ~azure.mgmt.machinelearningservices.models.ComputeRuntimeDto
        :keyword offline_store_connection_name:
        :paramtype offline_store_connection_name: str
        """
        self.compute_runtime = compute_runtime
        self.offline_store_connection_name = offline_store_connection_name

    def _to_rest_object(self) -> RestFeatureStoreSettings:
        return RestFeatureStoreSettings(
            compute_runtime=ComputeRuntime._to_rest_object(self.compute_runtime),
            offline_store_connection_name=self.offline_store_connection_name,
            online_store_connection_name=None
        )
        pass

    @classmethod
    def _from_rest_object(cls, rest_obj: RestFeatureStoreSettings) -> "FeatureStoreSettings":
        if not rest_obj:
            return None
        return FeatureStoreSettings(
            compute_runtime=ComputeRuntime._from_rest_object(rest_obj.compute_runtime),
            offline_store_connection_name=rest_obj.offline_store_connection_name
        )