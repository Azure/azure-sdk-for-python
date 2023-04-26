# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging

module_logger = logging.getLogger(__name__)


def get_log_analytics_arm_id(subscription_id: str, resource_group_name: str, log_analytics_name: str) -> str:
    return (
        f"/subscriptions/{subscription_id}/"
        f"resourceGroups/{resource_group_name}/"
        "providers/Microsoft.OperationalInsights/workspaces/"
        f"{log_analytics_name}"
    )
