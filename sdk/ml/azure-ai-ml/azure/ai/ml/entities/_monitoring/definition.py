# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Union

from typing_extensions import Literal

from azure.ai.ml.constants._monitoring import AZMONITORING
from azure.ai.ml.entities._monitoring.target import MonitoringTarget
from azure.ai.ml.entities._monitoring.signals import (
    DataDriftSignal,
    DataQualitySignal,
    PredictionDriftSignal,
    FeatureAttributionDriftSignal,
    ModelPerformanceSignal,
    CustomMonitoringSignal,
)
from azure.ai.ml.entities._monitoring.alert_notification import AlertNotification
from azure.ai.ml._utils._experimental import experimental


@experimental
class MonitorDefinition:
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
