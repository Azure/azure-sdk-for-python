# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict

from azure.ai.ml.entities._monitoring.monitoring_target import MonitoringTarget
from azure.ai.ml.entities._monitoring.monitoring_input_data import MonitorInputData
from azure.ai.ml.entities._monitoring.monitoring_signals import MonitoringSignal
from azure.ai.ml.entities._monitoring.alert_notification import AlertNotification
from azure.ai.ml._utils._experimental import experimental


@experimental
class MonitorDefinition():
    def __init__(
        self,
        *,
        compute: str = None,
        monitoring_target: MonitoringTarget = None,
        data_ingestion: MonitorInputData = None,
        monitoring_signals: Dict[str, MonitoringSignal] = None,
        alert_notification: AlertNotification = None,
    ):
        self.compute = compute
        self.data_ingestion = data_ingestion
        self.monitoring_target = monitoring_target
        self.monitoring_signals = monitoring_signals
        self.alert_notification = alert_notification
