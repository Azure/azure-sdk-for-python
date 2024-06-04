# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List, Optional

from azure.ai.ml._restclient.v2023_02_01_preview.models import NotificationSetting as RestNotificationSetting
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class Notification(RestTranslatableMixin):
    """Configuration for notification.

    :param email_on: Send email notification to user on specified notification type. Accepted values are
        "JobCompleted", "JobFailed", and "JobCancelled".
    :type email_on: Optional[list[str]]
    :param: The email recipient list which. Note that this parameter has a character limit of 499 which
        includes all of the recipient strings and each comma seperator.
    :paramtype emails: Optional[list[str]]
    """

    def __init__(self, *, email_on: Optional[List[str]] = None, emails: Optional[List[str]] = None) -> None:
        self.email_on = email_on
        self.emails = emails

    def _to_rest_object(self) -> RestNotificationSetting:
        return RestNotificationSetting(email_on=self.email_on, emails=self.emails)

    @classmethod
    def _from_rest_object(cls, obj: RestNotificationSetting) -> Optional["Notification"]:
        if not obj:
            return None
        return Notification(email_on=obj.email_on, emails=obj.emails)
