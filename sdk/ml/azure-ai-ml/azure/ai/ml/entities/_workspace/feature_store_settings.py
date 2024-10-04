# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Optional

from azure.ai.ml._restclient.v2024_07_01_preview.models import FeatureStoreSettings as RestFeatureStoreSettings
from azure.ai.ml.entities._mixins import RestTranslatableMixin

from .compute_runtime import ComputeRuntime


class FeatureStoreSettings(RestTranslatableMixin):
    """Feature Store Settings

    :param compute_runtime: The spark compute runtime settings. defaults to None.
    :type compute_runtime: Optional[~compute_runtime.ComputeRuntime]
    :param offline_store_connection_name: The offline store connection name. Defaults to None.
    :type offline_store_connection_name: Optional[str]
    :param online_store_connection_name: The online store connection name. Defaults to None.
    :type online_store_connection_name: Optional[str]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_featurestore.py
            :start-after: [START configure_feature_store_settings]
            :end-before: [END configure_feature_store_settings]
            :language: python
            :dedent: 8
            :caption: Instantiating FeatureStoreSettings
    """

    def __init__(
        self,
        *,
        compute_runtime: Optional[ComputeRuntime] = None,
        offline_store_connection_name: Optional[str] = None,
        online_store_connection_name: Optional[str] = None,
    ) -> None:
        self.compute_runtime = compute_runtime if compute_runtime else ComputeRuntime(spark_runtime_version="3.3.0")
        self.offline_store_connection_name = offline_store_connection_name
        self.online_store_connection_name = online_store_connection_name

    def _to_rest_object(self) -> RestFeatureStoreSettings:
        return RestFeatureStoreSettings(
            compute_runtime=ComputeRuntime._to_rest_object(self.compute_runtime),
            offline_store_connection_name=self.offline_store_connection_name,
            online_store_connection_name=self.online_store_connection_name,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestFeatureStoreSettings) -> Optional["FeatureStoreSettings"]:
        if not obj:
            return None
        return FeatureStoreSettings(
            compute_runtime=ComputeRuntime._from_rest_object(obj.compute_runtime),
            offline_store_connection_name=obj.offline_store_connection_name,
            online_store_connection_name=obj.online_store_connection_name,
        )
