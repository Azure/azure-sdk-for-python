# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Live-runnable rewrites of the generated InformationalOperations tests."""
from azure.mgmt.fileshares import FileSharesClient

from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy

from _helpers import ARM_ENDPOINT, AZURE_LOCATION


class TestFileSharesInformationalOperationsOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(
            FileSharesClient,
            base_url=ARM_ENDPOINT,
            credential_scopes=["https://management.azure.com/.default"],
        )

    @recorded_by_proxy
    def test_informational_operations_get_usage_data(self):
        response = self.client.informational_operations.get_usage_data(
            location=AZURE_LOCATION,
        )
        assert response is not None

    @recorded_by_proxy
    def test_informational_operations_get_limits(self):
        response = self.client.informational_operations.get_limits(
            location=AZURE_LOCATION,
        )
        assert response is not None

    @recorded_by_proxy
    def test_informational_operations_get_provisioning_recommendation(self):
        response = self.client.informational_operations.get_provisioning_recommendation(
            location=AZURE_LOCATION,
            body={"properties": {"provisionedStorageGiB": 1024}},
        )
        assert response is not None
