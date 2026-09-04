# coding: utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

import functools

from azure.iot.deviceregistrysoftwareupdate import DeviceRegistrySoftwareUpdateClient
from devtools_testutils import (
    AzureRecordedTestCase,
    EnvironmentVariableLoader,
    EnvironmentVariableOptions,
)


class DeviceRegistrySoftwareUpdateTest(AzureRecordedTestCase):
    def create_client(self, endpoint):
        credential = self.get_credential(DeviceRegistrySoftwareUpdateClient, process_timeout=60)
        return self.create_client_from_credential(
            DeviceRegistrySoftwareUpdateClient,
            endpoint=endpoint,
            credential=credential,
            connection_timeout=10,
            read_timeout=30,
            retry_total=0,
        )


DeviceRegistrySoftwareUpdatePreparer = functools.partial(
    EnvironmentVariableLoader,
    "deviceregistrysoftwareupdate",
    options=EnvironmentVariableOptions(
        hide_secrets=[
            "deviceregistrysoftwareupdate_manifest_url",
            "deviceregistrysoftwareupdate_file_url",
        ]
    ),
    deviceregistrysoftwareupdate_endpoint="fake.api.dev.adu.microsoft.com",
    deviceregistrysoftwareupdate_manifest_url="https://fake.blob.core.windows.net/container/manifest.json?sanitized",
    deviceregistrysoftwareupdate_file_url="https://fake.blob.core.windows.net/container/README.md?sanitized",
)
