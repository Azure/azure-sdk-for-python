# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, List

from azure.ai.ml._utils._experimental import experimental


@experimental
class AlertNotification:
    def __init__(
        self,
        *,
        azure_monitor_signals: Dict[str, str] = None,
        emails: List[str] = None,
    ):
        self.azure_monitoring_signals = azure_monitor_signals
        self.emails = emails
