# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import AzureTestCase, PowerShellPreparer
from azure.purview.workflow import PurviewWorkflowClient


class WorkflowTest(AzureTestCase):
    def __init__(self, method_name, **kwargs):
        super(WorkflowTest, self).__init__(method_name, **kwargs)

    def create_client(self, endpoint):
        credential = self.get_credential(PurviewWorkflowClient)
        return self.create_client_from_credential(
            PurviewWorkflowClient,
            credential=credential,
            endpoint=endpoint,
        )


WorkflowPowerShellPreparer = functools.partial(
    PowerShellPreparer,
    "workflow",
    workflow_endpoint="https://myservice.azure.com"
)
