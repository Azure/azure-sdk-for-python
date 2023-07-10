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
    def create_client(self, endpoint):
        credential = self.get_credential(DevCenterClient)
        return DevCenterClient(endpoint=endpoint, credential=credential)
    
DevcenterPowerShellPreparer = functools.partial(
    PowerShellPreparer,
    "devcenter", 
    devcenter_endpoint="https://8ab2df1c-ed88-4946-a8a9-e1bbb3e4d1fd-sdk-dc-na4b3zkj5hmeo.eastus.devcenter.azure.com",
    devcenter_project_name="sdk-default-project",
    devcenter_pool_name="sdk-default-pool",
    devcenter_test_user_id="11111111-1111-1111-1111-111111111111",
    devcenter_environment_type_name="sdk-default-environment-type",
    devcenter_catalog_name="sdk-default-catalog",
    devcenter_catalog_item_name="Empty")