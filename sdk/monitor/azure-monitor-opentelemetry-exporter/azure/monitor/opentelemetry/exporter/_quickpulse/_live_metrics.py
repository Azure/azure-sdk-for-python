# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from typing import Any

from azure.monitor.opentelemetry.exporter._quickpulse._manager import _QuickpulseManager
from azure.monitor.opentelemetry.exporter.statsbeat._state import (
    set_statsbeat_live_metrics_feature_set,
)


def enable_live_metrics(**kwargs: Any) -> None:  # pylint: disable=C4758
    """Live metrics entry point.

    :keyword str connection_string: The connection string used for your Application Insights resource.
    :keyword Resource resource: The OpenTelemetry Resource used for this Python application.
    :keyword TokenCredential credential: Token credential, such as ManagedIdentityCredential or
        ClientSecretCredential, used for Azure Active Directory (AAD) authentication. Defaults to None.
    :rtype: None
    """
    _QuickpulseManager(**kwargs)
    # We can detect feature usage for statsbeat since we are in an opt-in model currently
    # Once we move to live metrics on-by-default, we will have to check for both explicit usage
    # and whether or not user is actually using live metrics (being on live metrics blade in UX)
    set_statsbeat_live_metrics_feature_set()
