# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os

from devtools_testutils import AzureRecordedTestCase


ENV_MONITOR_ENVIRONMENT = "MONITOR_ENVIRONMENT"
AUDIENCE_MAP = {
    "AzureCloud": "https://monitor.azure.com",
    "AzureChinaCloud": "https://monitor.azure.cn",
    "AzureUSGovernment": "https://monitor.azure.us",
}


class LogsIngestionClientTestCase(AzureRecordedTestCase):

    def get_client(self, client_class, credential, **kwargs):

        environment = os.getenv(ENV_MONITOR_ENVIRONMENT)
        if environment:
            audience = AUDIENCE_MAP.get(environment)
            kwargs["credential_scopes"] = [f"{audience}/.default"]

        return self.create_client_from_credential(client_class, credential, **kwargs)
