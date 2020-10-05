# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._version import VERSION
from ._metrics_advisor_client import MetricsAdvisorClient
from ._metrics_advisor_administration_client import MetricsAdvisorAdministrationClient
from ._metrics_advisor_key_credential import MetricsAdvisorKeyCredential


__all__ = [
    "MetricsAdvisorClient",
    "MetricsAdvisorAdministrationClient",
    "MetricsAdvisorKeyCredential",
]


__version__ = VERSION
