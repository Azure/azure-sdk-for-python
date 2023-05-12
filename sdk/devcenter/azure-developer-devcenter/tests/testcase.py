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
    devcenter_endpoint="https://8ab2df1c-ed88-4946-a8a9-e1bbb3e4d1fd-dc-sdk-tests.centraluseuap.devcenter.azure.com",
    devcenter_project_name="proj-sdk-tests",
    devcenter_pool_name="sdk-default-pool",
    devcenter_test_user_id="df428e89-1bc2-4e72-b736-032c31a6cd97",
    devcenter_environment_type_name="sdk-default-environment-type",
    devcenter_catalog_name="sdk-default-catalog",
    devcenter_environment_definition_name="Sandbox",
    devcenter_devbox_name="PythonDevBox",
    devcenter_environment_name="pythonenvironment")