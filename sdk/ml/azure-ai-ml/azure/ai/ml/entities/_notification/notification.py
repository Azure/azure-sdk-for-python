# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List, Optional


from azure.ai.ml._restclient.v2023_02_01_preview.models import NotificationSetting as RestNotificationSetting
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._utils._experimental import experimental


@experimental
class Notification(RestTranslatableMixin):
    """Configuration for notification."""

    def __init__(self, *, email_on: Optional[List[str]] = None, emails: Optional[List[str]] = None):
        """
        :keyword email_on: Send email notification to user on specified notification type.
        :paramtype email_on: list[Literal]. Values can be [JobCompleted, JobFailed, JobCancelled]
        :keyword emails: This is the email recipient list which has a limitation of 499 characters in
         total concat with comma seperator.
        :paramtype emails: list[str]
        """
        self.email_on = email_on
        self.emails = emails

    def _to_rest_object(self) -> RestNotificationSetting:
        return RestNotificationSetting(email_on=self.email_on, emails=self.emails)

    @classmethod
    def _from_rest_object(cls, obj: RestNotificationSetting) -> "Notification":
        if not obj:
            return None
        return Notification(email_on=obj.email_on, emails=obj.emails)
