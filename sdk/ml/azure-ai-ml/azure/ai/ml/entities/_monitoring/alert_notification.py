# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List

from azure.ai.ml._utils._experimental import experimental


@experimental
class AlertNotification:
    def __init__(
        self,
        *,
        emails: List[str] = None,
    ):
        self.emails = emails
