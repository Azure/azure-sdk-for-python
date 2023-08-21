# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os

from devtools_testutils import AzureRecordedTestCase


ENV_MONITOR_ENVIRONMENT = "MONITOR_ENVIRONMENT"
ENV_MONITOR_RESOURCE_MANAGER_URL = "MONITOR_RESOURCE_MANAGER_URL"
ENV_MONITOR_LOCATION = "MONITOR_LOCATION"

LOGS_ENVIRONMENT_ENDPOINT_MAP = {
    "AzureCloud": "https://api.loganalytics.io/v1",
    "AzureChinaCloud": "https://api.loganalytics.azure.cn/v1",
    "AzureUSGovernment": "https://api.loganalytics.us/v1"
}


class AzureMonitorQueryLogsTestCase(AzureRecordedTestCase):

    def get_client(self, client_class, credential):

        kwargs = {}
        environment = os.getenv(ENV_MONITOR_ENVIRONMENT)
        if environment:
            kwargs["endpoint"] = LOGS_ENVIRONMENT_ENDPOINT_MAP[environment]

        return self.create_client_from_credential(client_class, credential, **kwargs)


class AzureMonitorQueryMetricsTestCase(AzureRecordedTestCase):

    def get_client(self, client_class, credential):

        kwargs = {}
        arm_url = os.getenv(ENV_MONITOR_RESOURCE_MANAGER_URL)
        if arm_url:
            kwargs["endpoint"] = arm_url

        return self.create_client_from_credential(client_class, credential, **kwargs)


class AzureMonitorQueryBatchMetricsTestCase(AzureRecordedTestCase):

    def get_client(self, client_class, credential, endpoint = None):

        kwargs = {}
        if not endpoint:
            region = os.getenv(ENV_MONITOR_LOCATION) or "westus2"
            kwargs["endpoint"] = f"https://{region}.metrics.monitor.azure.com"

        return self.create_client_from_credential(client_class, credential, **kwargs)
