# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Optional

from azure.ai.ml._restclient.v2023_04_01_preview.models import MaterializationSettings as RestMaterializationSettings
from azure.ai.ml._restclient.v2023_04_01_preview.models import MaterializationStoreType
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.entities._feature_set.materialization_compute_resource import MaterializationComputeResource
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.entities._notification.notification import Notification
from azure.ai.ml.entities._schedule.trigger import RecurrenceTrigger


@experimental
class MaterializationSettings(RestTranslatableMixin):
    """Defines materialization settings.

    :keyword schedule: The schedule details.
    :paramtype schedule: Optional[~azure.ai.ml.entities.RecurrenceTrigger]
    :keyword offline_enabled: Specifies if offline store is enabled.
    :paramtype offline_enabled: Optional[bool]
    :keyword online_enabled: Specifies if online store is enabled.
    :paramtype online_enabled: Optional[bool]
    :keyword notification: The notification details.
    :paramtype notification: Optional[~azure.ai.ml.entities.Notification]
    :keyword resource: The compute resource settings.
    :paramtype resource: Optional[~azure.ai.ml.entities.MaterializationComputeResource]
    :keyword spark_configuration: The spark compute settings.
    :paramtype spark_configuration: Optional[dict[str, str]]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_spark_configurations.py
            :start-after: [START materialization_setting_configuration]
            :end-before: [END materialization_setting_configuration]
            :language: python
            :dedent: 8
            :caption: Configuring MaterializationSettings.
    """

    def __init__(
        self,
        *,
        schedule: Optional[RecurrenceTrigger] = None,
        offline_enabled: Optional[bool] = None,
        online_enabled: Optional[bool] = None,
        notification: Optional[Notification] = None,
        resource: Optional[MaterializationComputeResource] = None,
        spark_configuration: Optional[Dict[str, str]] = None,
        **kwargs  # pylint: disable=unused-argument
    ) -> None:
        self.schedule = schedule
        self.offline_enabled = offline_enabled
        self.online_enabled = online_enabled
        self.notification = notification
        self.resource = resource
        self.spark_configuration = spark_configuration

    def _to_rest_object(self) -> RestMaterializationSettings:
        store_type = None
        if self.offline_enabled and self.online_enabled:
            store_type = MaterializationStoreType.ONLINE_AND_OFFLINE
        elif self.offline_enabled:
            store_type = MaterializationStoreType.OFFLINE
        elif self.online_enabled:
            store_type = MaterializationStoreType.ONLINE
        else:
            store_type = MaterializationStoreType.NONE

        return RestMaterializationSettings(
            schedule=self.schedule._to_rest_object() if self.schedule else None,  # pylint: disable=protected-access
            notification=self.notification._to_rest_object()  # pylint: disable=protected-access
            if self.notification
            else None,
            resource=self.resource._to_rest_object() if self.resource else None,  # pylint: disable=protected-access
            spark_configuration=self.spark_configuration,
            store_type=store_type,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestMaterializationSettings) -> "MaterializationSettings":
        if not obj:
            return None
        return MaterializationSettings(
            schedule=RecurrenceTrigger._from_rest_object(obj.schedule)  # pylint: disable=protected-access
            if obj.schedule
            else None,
            notification=Notification._from_rest_object(obj.notification),  # pylint: disable=protected-access
            resource=MaterializationComputeResource._from_rest_object(obj.resource),  # pylint: disable=protected-access
            spark_configuration=obj.spark_configuration,
            offline_enabled=obj.store_type
            in {MaterializationStoreType.OFFLINE, MaterializationStoreType.ONLINE_AND_OFFLINE},
            online_enabled=obj.store_type
            in {MaterializationStoreType.ONLINE, MaterializationStoreType.ONLINE_AND_OFFLINE},
        )
