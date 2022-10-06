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
from devtools_testutils import AzureTestCase, PowerShellPreparer
from azure.identity import DefaultAzureCredential
from azure.developer.devcenter import DevCenterClient
from azure.core.exceptions import HttpResponseError

DevcenterPowerShellPreparer = functools.partial(PowerShellPreparer, 'devcenter')

class DevcenterTest(AzureTestCase):
    def __init__(self, method_name, **kwargs):
        super(DevcenterTest, self).__init__(method_name, **kwargs)
        self.logger = logging.getLogger(__name__)

    def create_client(self, dev_center_name, tenant_id):
        credential = self.get_credential(DevCenterClient)
        return DevCenterClient(
            tenant_id,
            dev_center_name,
            credential=credential
        )
    
    @DevcenterPowerShellPreparer()
    def test_devbox_operations(self):
        dev_center_name = os.environ.get("DEFAULT_DEVCENTER_NAME")
        tenant_id = os.environ["AZURE_TENANT_ID"]
        client = self.create_client(dev_center_name, tenant_id)
        
        # Fetch control plane resource dependencies
        target_project_name = os.environ["DEFAULT_PROJECT_NAME"]
        target_pool_name = os.environ["DEFAULT_POOL_NAME"]
        target_user_id = os.environ["STATIC_TEST_USER_ID"]

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
    def test_environment_operations(self):
        dev_center_name = os.environ["DEFAULT_DEVCENTER_NAME"]
        tenant_id = os.environ["AZURE_TENANT_ID"]
        client = self.create_client(dev_center_name, tenant_id)
        
        # Fetch control plane resource dependencies
        target_project_name = os.environ["DEFAULT_PROJECT_NAME"]
        target_environment_type = os.environ["DEFAULT_ENVIRONMENT_TYPE_NAME"]
        target_catalog_item = os.environ["DEFAULT_CATALOG_ITEM_NAME"]
        target_catalog = os.environ["DEFAULT_CATALOG_NAME"]

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