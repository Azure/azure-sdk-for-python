# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Optional

from azure.ai.ml._restclient.v2023_02_01_preview.models import (
    MaterializationSettings as RestMaterializationSettings,
    MaterializationStoreType,
)
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.entities._schedule.trigger import RecurrenceTrigger
from azure.ai.ml.entities._notification.notification import Notification
from azure.ai.ml.entities._feature_set.materialization_compute_resource import MaterializationComputeResource
from azure.ai.ml._utils._experimental import experimental


@experimental
class MaterializationSettings(RestTranslatableMixin):
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
    ):
        """MaterializationSettings.

        :param schedule: Specifies the schedule details.
        :type schedule: ~azure.ai.ml.entities.RecurrenceTrigger
        :param offline_enabled: Specifies if offline store is enabled.
        :type offline_enabled: bool
        :param online_enabled: Specifies if online store is enabled.
        :type online_enabled: bool
        :param notification: Specifies the notification details.
        :type notification: ~azure.ai.ml.entities.Notification
        :param resource: Specifies the compute resource settings.
        :type resource: ~azure.ai.ml.entities.MaterializationComputeResource
        :param spark_configuration: Specifies the spark compute settings.
        :type spark_configuration: dict[str, str]
        """

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
            offline_enabled=obj.store_type == MaterializationStoreType.OFFLINE
            or obj.store_type == MaterializationStoreType.ONLINE_AND_OFFLINE,
            online_enabled=obj.store_type == MaterializationStoreType.ONLINE
            or obj.store_type == MaterializationStoreType.ONLINE_AND_OFFLINE,
        )
