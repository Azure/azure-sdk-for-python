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

DevcenterPowerShellPreparer = functools.partial(PowerShellPreparer, 'devcenter')

class TestDevcenter(AzureRecordedTestCase):
    def create_client(self, dev_center_name, tenant_id):
        credential = self.get_credential(DevCenterClient)
        return DevCenterClient(
            tenant_id,
            dev_center_name,
            credential=credential
        )
    
    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_devbox_operations(self):
        self.logger = logging.getLogger(__name__)
        dev_center_name = os.environ.get("DEFAULT_DEVCENTER_NAME", "sdk-default-dc")
        tenant_id = os.environ.get("AZURE_TENANT_ID", "88888888-8888-8888-8888-888888888888")
        client = self.create_client(dev_center_name, tenant_id)
        
        # Fetch control plane resource dependencies
        target_project_name = os.environ.get("DEFAULT_PROJECT_NAME", "sdk-default-project")
        target_pool_name = os.environ.get("DEFAULT_POOL_NAME", "sdk-default-pool")
        target_user_id = os.environ.get("STATIC_TEST_USER_ID", "11111111-1111-1111-1111-111111111111")

        # Stand up a new dev box
        create_response = client.dev_boxes.begin_create_dev_box(target_project_name, "Test_DevBox", {"poolName": target_pool_name}, user_id=target_user_id)
        devbox_result = create_response.result()

        self.logger.info(f"Provisioned dev box with status {devbox_result['provisioningState']}.")
        assert devbox_result['provisioningState'] in ["Succeeded", "ProvisionedWithWarning"]

        # Tear down the dev box
        delete_response = client.dev_boxes.begin_delete_dev_box(target_project_name, "Test_DevBox")
        delete_response.wait()
        self.logger.info("Completed deletion for the dev box.")

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_environment_operations(self):
        self.logger = logging.getLogger(__name__)
        dev_center_name = os.environ.get("DEFAULT_DEVCENTER_NAME", "sdk-default-dc")
        tenant_id = os.environ.get("AZURE_TENANT_ID", "88888888-8888-8888-8888-888888888888")
        client = self.create_client(dev_center_name, tenant_id)
        
        # Fetch control plane resource dependencies
        target_project_name = os.environ.get("DEFAULT_PROJECT_NAME", "sdk-default-project")
        target_environment_type = os.environ.get("DEFAULT_ENVIRONMENT_TYPE_NAME", "sdk-default-environment-type")
        target_catalog_item = os.environ.get("DEFAULT_CATALOG_ITEM_NAME", "Empty")
        target_catalog = os.environ.get("DEFAULT_CATALOG_NAME", "sdk-default-catalog")

        create_response = client.environments.begin_create_or_update_environment(target_project_name,
                                                           "Dev_Environment",
                                                           {"catalogItemName": target_catalog_item,
                                                            "environmentType": target_environment_type,
                                                            "catalogName": target_catalog})
        environment_result = create_response.result()

        self.logger.info(f"Provisioned environment with status {environment_result['provisioningState']}.")
        assert environment_result['provisioningState'] == "Succeeded"
        
        # Tear down the environment when finished
        delete_response = client.environments.begin_delete_environment(target_project_name, "Dev_Environment")
        delete_response.wait()
        self.logger.info("Completed deletion for the environment.")