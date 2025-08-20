# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from .azure_recorded_testcase import AzureRecordedTestCase


class AzureMgmtRecordedTestCase(AzureRecordedTestCase):
    """Test class for use by management-plane tests that use the azure-sdk-tools test proxy.

    For more details and usage examples, refer to
    https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/test_proxy_migration_guide.md
    """

    def create_mgmt_client(self, client_class, **kwargs):
        subscription_id = self.get_settings_value("SUBSCRIPTION_ID")
        credential = self.get_credential(client_class)
        return self.create_client_from_credential(client_class, credential, subscription_id=subscription_id, **kwargs)
