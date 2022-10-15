# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import functools
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
from azure.developer.devcenter import DevCenterClient


class DevcenterTest(AzureRecordedTestCase):
    def create_client(self, tenant_id, dev_center):
        credential = self.get_credential(DevCenterClient)
        return DevCenterClient(
            dev_center=dev_center,
            tenant_id=tenant_id,
            credential=credential
        )


DevcenterPowerShellPreparer = functools.partial(
    PowerShellPreparer, "devcenter", dev_center=os.environ.get("DEVCENTER_NAME", "sdk-default-dc"), tenant_id=os.environ.get("AZURE_TENANT_ID", "88888888-8888-8888-8888-888888888888")
)
