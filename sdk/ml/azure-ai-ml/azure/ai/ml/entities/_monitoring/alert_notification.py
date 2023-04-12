# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, List, Union

from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    NotificationSetting,
    MonitoringAlertNotificationSettingsBase,
    AzMonMonitoringAlertNotificationSettings,
    EmailMonitoringAlertNotificationSettings
)

@experimental
class AlertNotification(RestTranslatableMixin):
    def __init__(
        self,
        *,
        monitoring_signals_enabled: List[str] = None,
        azure_monitor_signals: Dict[str, str] = None,
        emails: List[str] = None,
    ):
        self.monitoring_signals_enabled = monitoring_signals_enabled
        self.azure_monitoring_signals = azure_monitor_signals
        self.emails = emails

    def _to_rest_object(self) -> Union[EmailMonitoringAlertNotificationSettings, AzMonMonitoringAlertNotificationSettings]:
        if self.emails:
            return EmailMonitoringAlertNotificationSettings(
                email_notification_setting=NotificationSetting(emails=self.emails)
            )
        elif self.azure_monitoring_signals:
            return AzMonMonitoringAlertNotificationSettings()

    @classmethod
    def _from_rest_object(cls, obj: MonitoringAlertNotificationSettingsBase) -> "AlertNotification":
        if isinstance(obj, EmailMonitoringAlertNotificationSettings):
            return cls(
                emails=obj.email_notification_setting.emails
            )
        return cls(
            azure_monitoring_signals={}
        )
