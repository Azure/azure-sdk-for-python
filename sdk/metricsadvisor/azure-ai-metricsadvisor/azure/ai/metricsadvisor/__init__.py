# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._version import VERSION
from ._patch import MetricsAdvisorClient, MetricsAdvisorAdministrationClient, MetricsAdvisorKeyCredential


__all__ = [
    "MetricsAdvisorClient",
    "MetricsAdvisorAdministrationClient",
    "MetricsAdvisorKeyCredential",
]


__version__ = VERSION
