# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools

from devtools_testutils import PowerShellPreparer, AzureRecordedTestCase

from azure.purview.workflow import PurviewWorkflowClient


class WorkflowTest(AzureRecordedTestCase):

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
    workflow_endpoint="https://test-create-account.purview.azure.com"
)
