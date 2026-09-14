# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, List, Optional

from azure.ai.ml._restclient.arm_ml_service.models import EmailNotificationEnableType, NotificationSetting
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
    ) -> Dict:
        # ``EmailMonitoringAlertNotificationSettings`` does not exist in the shared arm_ml_service model. The
        # 2023-06-01-preview wire wraps the email setting in a polymorphic ``alertNotificationType`` ("Email")
        # envelope, so build that envelope as a plain dict around the (still present) ``NotificationSetting`` model.
        return {
            "alertNotificationType": "Email",
            "emailNotificationSetting": NotificationSetting(
                emails=self.emails,
                email_on=[
                    EmailNotificationEnableType.JOB_FAILED,
                    EmailNotificationEnableType.JOB_COMPLETED,
                ],
            ),
        }

    @classmethod
    def _from_rest_object(cls, obj: Any) -> "AlertNotification":
        # ``obj`` is the arm-hybrid / dict ``alertNotificationSetting`` envelope. Read the nested email setting via
        # mapping-or-attribute access to support both shapes.
        email_setting = obj["emailNotificationSetting"] if "emailNotificationSetting" in obj else None
        emails = None
        if email_setting is not None:
            emails = email_setting["emails"] if "emails" in email_setting else None
        return cls(emails=emails)
