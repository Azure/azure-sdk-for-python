# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Optional, Dict, Union

from typing_extensions import Literal

from azure.ai.ml.constants._monitoring import (
    AZMONITORING,
    DefaultMonitorSignalNames,
    SPARK_INSTANCE_TYPE_KEY,
    SPARK_RUNTIME_VERSION,
)
from azure.ai.ml.entities._monitoring.target import MonitoringTarget
from azure.ai.ml.entities._monitoring.signals import (
    MonitoringSignal,
    DataDriftSignal,
    DataQualitySignal,
    PredictionDriftSignal,
    FeatureAttributionDriftSignal,
    CustomMonitoringSignal,
)
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.entities._monitoring.alert_notification import AlertNotification
from azure.ai.ml.entities._job.spark_resource_configuration import SparkResourceConfiguration
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    MonitorDefinition as RestMonitorDefinition,
    AzMonMonitoringAlertNotificationSettings,
)
from azure.ai.ml._utils._experimental import experimental


@experimental
class MonitorDefinition(RestTranslatableMixin):
    """Monitor definition

    :param compute: Information on spark configuration associated with the monitor
    :type compute: ~azure.ai.ml.entities.SparkResourceConfiguration
    :param monitoring_target: Metadata describing the model or deployment that is being monitored
    :type monitoring_target: ~azure.ai.ml.entities.MonitoringTarget
    :param monitoring_signals: Dictionary of signals to monitor
    :type monitoring_signals: Dict[str, Union[~azure.ai.ml.entities.DataDriftSignal
        , ~azure.ai.ml.entities.DataQualitySignal, ~azure.ai.ml.entities.PredictionDriftSignal
        , ~azure.ai.ml.entities.FeatureAttributionDriftSignal
        , ~azure.ai.ml.entities.CustomMonitoringSignal]]
    :param alert_notification: Alert configuration for the monitor
    :type alert_notification: Union[Literal['azmonitoring'], ~azure.ai.ml.entities.AlertNotification]
    """

    def __init__(
        self,
        *,
        compute: SparkResourceConfiguration,
        monitoring_target: MonitoringTarget = None,
        monitoring_signals: Dict[
            str,
            Union[
                DataDriftSignal,
                DataQualitySignal,
                PredictionDriftSignal,
                FeatureAttributionDriftSignal,
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
            compute_id="spark",
            monitoring_target=(self.monitoring_target.endpoint_deployment_id or self.monitoring_target.model_id)
            if self.monitoring_target
            else None,
            signals={signal_name: signal._to_rest_object() for signal_name, signal in self.monitoring_signals.items()},
            alert_notification_setting=rest_alert_notification,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestMonitorDefinition, **kwargs) -> "MonitorDefinition":
        tags = kwargs.get("tags")
        from_rest_alert_notification = None
        if obj.alert_notification_setting:
            if isinstance(obj.alert_notification_setting, AzMonMonitoringAlertNotificationSettings):
                from_rest_alert_notification = AZMONITORING
            else:
                from_rest_alert_notification = AlertNotification._from_rest_object(obj.alert_notification_setting)
        return cls(
            compute=SparkResourceConfiguration(
                instance_type=tags.pop(SPARK_INSTANCE_TYPE_KEY),
                runtime_version=tags.pop(SPARK_RUNTIME_VERSION),
            ),
            monitoring_target=MonitoringTarget(endpoint_deployment_id=obj.monitoring_target),
            monitoring_signals={
                signal_name: MonitoringSignal._from_rest_object(signal) for signal_name, signal in obj.signals.items()
            },
            alert_notification=from_rest_alert_notification,
        )

    def _populate_default_signal_information(
        self,
        model_inputs_arm_id: str,
        model_inputs_type: str,
        model_outputs_arm_id: str,
        model_outputs_type: str,
    ):
        self.monitoring_signals = {
            DefaultMonitorSignalNames.DATA_DRIFT_SIGNAL: DataDriftSignal._get_default_data_drift_signal(
                model_inputs_arm_id, model_inputs_type
            ),
            DefaultMonitorSignalNames.PREDICTION_DRIFT_SIGNAL: PredictionDriftSignal._get_default_prediction_drift_signal(  # pylint: disable=line-too-long
                model_outputs_arm_id, model_outputs_type
            ),
            DefaultMonitorSignalNames.DATA_QUALITY_SIGNAL: DataQualitySignal._get_default_data_quality_signal(
                model_inputs_arm_id, model_inputs_type
            ),
        }
