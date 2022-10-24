# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import functools
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, PowerShellPreparer
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
    PowerShellPreparer,
    "devcenter", 
    devcenter_name="sdk-default-dc",
    devcenter_tenant_id="88888888-8888-8888-8888-888888888888",
    devcenter_project_name="sdk-default-project",
    devcenter_pool_name="sdk-default-pool",
    devcenter_test_user_id="11111111-1111-1111-1111-111111111111",
    devcenter_environment_type_name="sdk-default-environment-type",
    devcenter_catalog_name="sdk-default-catalog",
    devcenter_catalog_item_name="Empty")