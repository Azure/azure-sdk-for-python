# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Optional, Any

from azure.ai.ml._restclient.v2022_12_01_preview.models import FeatureStoreSettings as RestFeatureStoreSettings
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._utils._experimental import experimental
from .compute_runtime import _ComputeRuntime


@experimental
class _FeatureStoreSettings(RestTranslatableMixin):
    def __init__(
        self,
        *,
        compute_runtime: Optional[_ComputeRuntime] = None,
        offline_store_connection_name: Optional[str] = None,
        online_store_connection_name: Optional[str] = None,
    ):
        """
        :keyword compute_runtime:
        :paramtype compute_runtime: ~azure.ai.ml.entities.ComputeRuntime
        :keyword offline_store_connection_name:
        :paramtype offline_store_connection_name: str
        :keyword online_store_connection_name:
        :paramtype online_store_connection_name: str
        """
        self.compute_runtime = compute_runtime if compute_runtime else _ComputeRuntime(spark_runtime_version="3.1.0")
        self.offline_store_connection_name = offline_store_connection_name
        self.online_store_connection_name = online_store_connection_name

    def _to_rest_object(self) -> RestFeatureStoreSettings:
        return RestFeatureStoreSettings(
            compute_runtime=_ComputeRuntime._to_rest_object(self.compute_runtime),
            offline_store_connection_name=self.offline_store_connection_name,
            online_store_connection_name=self.online_store_connection_name,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestFeatureStoreSettings) -> "_FeatureStoreSettings":
        if not obj:
            return None
        return _FeatureStoreSettings(
            compute_runtime=_ComputeRuntime._from_rest_object(obj.compute_runtime),
            offline_store_connection_name=obj.offline_store_connection_name,
            online_store_connection_name=obj.online_store_connection_name
        )
