# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, List, Union

from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    NotificationSetting,
    EmailMonitoringAlertNotificationSettings,
)


@experimental
class AlertNotification(RestTranslatableMixin):
    def __init__(
        self,
        *,
        emails: List[str] = None,
    ):
        self.emails = emails

    def _to_rest_object(
        self,
    ) -> EmailMonitoringAlertNotificationSettings:
        return EmailMonitoringAlertNotificationSettings(
            email_notification_setting=NotificationSetting(emails=self.emails)
        )

    @classmethod
    def _from_rest_object(cls, obj: EmailMonitoringAlertNotificationSettings) -> "AlertNotification":
        return cls(emails=obj.email_notification_setting.emails)
