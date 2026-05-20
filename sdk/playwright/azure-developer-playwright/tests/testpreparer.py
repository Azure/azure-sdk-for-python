# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import functools

from azure.developer.playwright import PlaywrightClient
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer


class PlaywrightClientTestBase(AzureRecordedTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(PlaywrightClient)
        return self.create_client_from_credential(
            PlaywrightClient,
            credential=credential,
            endpoint=endpoint,
        )


PlaywrightPreparer = functools.partial(
    PowerShellPreparer,
    "playwright",
    playwright_endpoint="https://fake.api.playwright.microsoft.com",
    playwright_workspace_id="00000000-0000-0000-0000-000000000000",
)
