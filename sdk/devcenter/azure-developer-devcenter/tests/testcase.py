# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import functools
from devtools_testutils import AzureTestCase, PowerShellPreparer
from azure.developer.devcenter import DevCenterClient


class DevcenterTest(AzureTestCase):
    def __init__(self, method_name, **kwargs):
        super(DevcenterTest, self).__init__(method_name, **kwargs)

    def create_client(self, tenant_id, dev_center):
        credential = self.get_credential(DevCenterClient)
        return DevCenterClient(
            dev_center=dev_center,
            tenant_id=tenant_id,
            credential=credential
        )


DevcenterPowerShellPreparer = functools.partial(
    PowerShellPreparer, "devcenter", dev_center=os.environ.get("DEVCENTER_NAME", "TestDevCenter"), tenant_id=os.environ.get("AZURE_TENANT_ID", "00000000-0000-0000-0000-000000000000")
)
