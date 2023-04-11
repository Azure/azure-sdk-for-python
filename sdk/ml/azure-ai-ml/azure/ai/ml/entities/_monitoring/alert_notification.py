# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, List

from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._restclient.v2023_04_01_preview.models import NotificationSetting


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

    def _to_rest_object(self) -> NotificationSetting:
        return NotificationSetting(
            emails=self.emails,
        )

    @classmethod
    def _from_rest_object(cls, obj: NotificationSetting) -> "AlertNotification":
        return cls(emails=obj.emails)
