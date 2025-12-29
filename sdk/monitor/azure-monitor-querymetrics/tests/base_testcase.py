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


METRICS_CLIENT_ENVIRONMENT_AUDIENCE_MAP = {
    "AzureCloud": "https://metrics.monitor.azure.com",
    "AzureChinaCloud": "https://metrics.monitor.azure.cn",
    "AzureUSGovernment": "https://metrics.monitor.azure.us",
}

TLD_MAP = {"AzureCloud": "com", "AzureChinaCloud": "cn", "AzureUSGovernment": "us"}


class MetricsClientTestCase(AzureRecordedTestCase):

    def get_client(self, client_class, credential, endpoint=None):

        environment = os.getenv(ENV_MONITOR_ENVIRONMENT)
        kwargs = {}
        tld = "com"
        if environment:
            kwargs["audience"] = METRICS_CLIENT_ENVIRONMENT_AUDIENCE_MAP.get(environment)
            tld = TLD_MAP.get(environment, "com")

        if not endpoint:
            region = os.getenv(ENV_MONITOR_LOCATION) or "westus2"
            kwargs["endpoint"] = f"https://{region}.metrics.monitor.azure.{tld}"

        return self.create_client_from_credential(client_class, credential, **kwargs)
