# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List, Optional

from azure.ai.ml._restclient.v2023_06_01_preview.models import (
    EmailMonitoringAlertNotificationSettings,
    EmailNotificationEnableType,
    NotificationSetting,
)
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class AlertNotification(RestTranslatableMixin):
    """Alert notification configuration for monitoring jobs

    :keyword emails: A list of email addresses that will receive notifications for monitoring alerts.
        Defaults to None.
    :paramtype emails: Optional[List[str]]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_spark_configurations.py
            :start-after: [START spark_monitor_definition]
            :end-before: [END spark_monitor_definition]
            :language: python
            :dedent: 8
            :caption: Configuring alert notifications for a monitored job.
    """

    def __init__(
        self,
        *,
        emails: Optional[List[str]] = None,
    ) -> None:
        self.emails = emails

    def _to_rest_object(
        self,
    ) -> EmailMonitoringAlertNotificationSettings:
        return EmailMonitoringAlertNotificationSettings(
            email_notification_setting=NotificationSetting(
                emails=self.emails,
                email_on=[
                    EmailNotificationEnableType.JOB_FAILED,
                    EmailNotificationEnableType.JOB_COMPLETED,
                ],
            )
        )

    @classmethod
    def _from_rest_object(cls, obj: EmailMonitoringAlertNotificationSettings) -> "AlertNotification":
        return cls(emails=obj.email_notification_setting.emails)
