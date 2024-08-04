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
    EnvironmentVariableLoader,
    "devcenter",
    devcenter_endpoint="https://dddd3333-d3d3-3333-d3d3-dddddd333333-fake-dev-center.location.devcenter.azure.com",
    devcenter_project_name="fake-proj",
    devcenter_pool_name="fake-pool",
    devcenter_test_user_id="11111111-1111-1111-1111-111111111111",
    devcenter_environment_type_name="fake-environment-type",
    devcenter_catalog_name="fake-catalog",
    devcenter_environment_definition_name="fake-sandbox",
    devcenter_devbox_name="fake-devbox",
    devcenter_environment_name="fake-environment",
)
