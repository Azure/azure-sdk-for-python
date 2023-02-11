# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
from devtools_testutils import AzureTestCase
from azure.purview.workflow.aio import PurviewWorkflowClient
from azure.identity import UsernamePasswordCredential

class WorkflowAsyncTest(AzureTestCase):
    def __init__(self, method_name, **kwargs):
        super(WorkflowAsyncTest, self).__init__(method_name, **kwargs)

    def create_async_client(self, endpoint):
        credential = self.get_credential()
        return self.create_client_from_credential(
            PurviewWorkflowClient,
            credential=credential,
            endpoint=endpoint,
        )

    def get_credential(self):
        username = os.getenv("USERNAME")
        password = os.getenv("PASSWORD")
        client_id = os.getenv("AZURE_CLIENT_ID")
        tenant_id = os.getenv("AZURE_TENANT_ID")
        return UsernamePasswordCredential(client_id=client_id, username=username, password=password,
                                          tenant_id=tenant_id)
