# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Union

from typing_extensions import Literal

from azure.ai.ml.constants._monitoring import AZMONITORING
from azure.ai.ml.entities._monitoring.target import MonitoringTarget
from azure.ai.ml.entities._monitoring.signals import (
    MonitoringSignal,
    DataDriftSignal,
    DataQualitySignal,
    PredictionDriftSignal,
    FeatureAttributionDriftSignal,
    ModelPerformanceSignal,
    CustomMonitoringSignal,
)
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.entities._monitoring.alert_notification import AlertNotification
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    MonitorDefinition as RestMonitorDefinition,
    AzMonMonitoringAlertNotificationSettings,
)
from azure.ai.ml._utils._experimental import experimental


@experimental
class MonitorDefinition(RestTranslatableMixin):
    def __init__(
        self,
        *,
        compute: str = None,
        monitoring_target: MonitoringTarget = None,
        monitoring_signals: Dict[
            str,
            Union[
                DataDriftSignal,
                DataQualitySignal,
                PredictionDriftSignal,
                FeatureAttributionDriftSignal,
                ModelPerformanceSignal,
                CustomMonitoringSignal,
            ],
        ] = None,
        alert_notification: Union[Literal[AZMONITORING], AlertNotification] = None,
    ):
        self.compute = compute
        self.monitoring_target = monitoring_target
        self.monitoring_signals = monitoring_signals
        self.alert_notification = alert_notification

    def _to_rest_object(self) -> RestMonitorDefinition:
        rest_alert_notification = None
        if self.alert_notification:
            if isinstance(self.alert_notification, str) and self.alert_notification.lower() == AZMONITORING:
                rest_alert_notification = AzMonMonitoringAlertNotificationSettings()
            else:
                rest_alert_notification = self.alert_notification._to_rest_object()
        return RestMonitorDefinition(
            compute_id=self.compute,
            monitoring_target=self.monitoring_target.endpoint_deployment_id or self.monitoring_target.model_id,
            signals={signal_name: signal._to_rest_object() for signal_name, signal in self.monitoring_signals.items()},
            alert_notification_setting=self.alert_notification._to_rest_object(),
        )

    @classmethod
    def _from_rest_object(cls, obj: RestMonitorDefinition) -> "MonitorDefinition":
        return cls(
            compute=obj.compute_id,
            monitoring_target=MonitoringTarget(endpoint_deployment_id=obj.monitoring_target),
            monitoring_signals={
                signal_name: MonitoringSignal._from_rest_object(signal) for signal_name, signal in obj.signals.items()
            },
            alert_notification=AlertNotification._from_rest_object(obj.alert_notification_setting),
        )
