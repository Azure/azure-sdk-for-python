# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._version import VERSION
from ._generated import MetricsAdvisorClient
from ._generated._patch import MetricsAdvisorAdministrationClient, MetricsAdvisorKeyCredential


__all__ = [
    "MetricsAdvisorClient",
    "MetricsAdvisorAdministrationClient",
    "MetricsAdvisorKeyCredential",
]


__version__ = VERSION
