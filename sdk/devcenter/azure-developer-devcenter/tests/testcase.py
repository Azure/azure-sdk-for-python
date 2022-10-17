# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import functools
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
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
    EnvironmentVariableLoader, "devcenter", devcenter_name="sdk-default-dc", devcenter_tenant_id="88888888-8888-8888-8888-888888888888"
)
