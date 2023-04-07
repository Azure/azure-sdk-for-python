# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
import os
import pytest
import logging
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.identity import InteractiveBrowserCredential 
from azure.developer.devcenter import DevCenterClient
from azure.core.exceptions import HttpResponseError
from testcase import DevcenterPowerShellPreparer

class TestDevcenter(AzureRecordedTestCase):
    def create_client(self, endpoint):
        credential = self.get_credential(DevCenterClient)
        return DevCenterClient(endpoint, credential=credential)
    
    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_devbox_operations(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        default_project_name = kwargs.pop("devcenter_project_name")
        default_pool_name = kwargs.pop("devcenter_pool_name")
        static_test_user_id = kwargs.pop("devcenter_test_user_id")

        client = self.create_client(endpoint)

        # Fetch control plane resource dependencies

        # Stand up a new dev box
        create_response = client.dev_boxes.begin_create_dev_box(default_project_name, "Test_DevBox", {"poolName": default_pool_name}, user_id=static_test_user_id)
        devbox_result = create_response.result()

        self.logger.info(f"Provisioned dev box with status {devbox_result['provisioningState']}.")
        assert devbox_result['provisioningState'] in ["Succeeded", "ProvisionedWithWarning"]

        # Tear down the dev box
        delete_response = client.dev_boxes.begin_delete_dev_box(default_project_name, "Test_DevBox")
        delete_response.wait()
        self.logger.info("Completed deletion for the dev box.")

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_environment_operations(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        default_project_name = kwargs.pop("devcenter_project_name")
        default_environment_type_name = kwargs.pop("devcenter_environment_type_name")
        default_catalog_name = kwargs.pop("devcenter_catalog_name")
        default_catalog_item_name = kwargs.pop("devcenter_catalog_item_name")

        client = self.create_client(endpoint)

        # Fetch control plane resource dependencies
        create_response = client.environments.begin_create_or_update_environment(default_project_name,
                                                           "Dev_Environment",
                                                           {"catalogItemName": default_catalog_item_name,
                                                            "environmentType": default_environment_type_name,
                                                            "catalogName": default_catalog_name})
        environment_result = create_response.result()

        self.logger.info(f"Provisioned environment with status {environment_result['provisioningState']}.")
        assert environment_result['provisioningState'] == "Succeeded"
        
        # Tear down the environment when finished
        delete_response = client.environments.begin_delete_environment(default_project_name, "Dev_Environment")
        delete_response.wait()
        self.logger.info("Completed deletion for the environment.")