# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import unittest
from unittest.mock import patch

from azure.monitor.opentelemetry.exporter.resource.app_service_resource_detector import (
    AzureAppServiceResourceDetector,
)

TEST_WEBSITE_SITE_NAME = "TEST_WEBSITE_SITE_NAME"
TEST_REGION_NAME = "TEST_REGION_NAME"
TEST_WEBSITE_SLOT_NAME = "TEST_WEBSITE_SLOT_NAME"
TEST_WEBSITE_HOSTNAME = "TEST_WEBSITE_HOSTNAME"
TEST_WEBSITE_INSTANCE_ID = "TEST_WEBSITE_INSTANCE_ID"
TEST_WEBSITE_HOME_STAMPNAME = "TEST_WEBSITE_HOME_STAMPNAME"

TEST_WEBSITE_RESOURCE_GROUP = "TEST_WEBSITE_RESOURCE_GROUP"
TEST_WEBSITE_OWNER_NAME = "TEST_WEBSITE_OWNER_NAME"

class TestAzureAppServiceResourceDetector(unittest.TestCase):
    @patch.dict("os.environ", {
        "WEBSITE_SITE_NAME": TEST_WEBSITE_SITE_NAME,
        "REGION_NAME": TEST_REGION_NAME,
        "WEBSITE_SLOT_NAME": TEST_WEBSITE_SLOT_NAME,
        "WEBSITE_HOSTNAME": TEST_WEBSITE_HOSTNAME,
        "WEBSITE_INSTANCE_ID": TEST_WEBSITE_INSTANCE_ID,
        "WEBSITE_HOME_STAMPNAME": TEST_WEBSITE_HOME_STAMPNAME,
        "WEBSITE_RESOURCE_GROUP": TEST_WEBSITE_RESOURCE_GROUP,
        "WEBSITE_OWNER_NAME": TEST_WEBSITE_OWNER_NAME,
    }, clear=True)
    def test_on_app_service(self):
        resource = AzureAppServiceResourceDetector().detect()
        attributes = resource.attributes
        # self.assertEqual(attributes {
        #     "service.name": TEST_WEBSITE_SITE_NAME,
        #     "cloud.provider": ,
        #     "cloud.platform": ,
        #     "cloud.resource_id": ,
        #     "cloud.region": ,
        #     "deployment.environment": ,
        #     "deployment.environment": ,
        # })
        self.assertEqual(attributes["service.name"], TEST_WEBSITE_SITE_NAME)
        self.assertEqual(attributes["cloud.provider"], "azure")
        self.assertEqual(attributes["cloud.platform"], "azure_app_service")

        self.assertEqual(attributes["cloud.resource_id"], \
            f"/subscriptions/{TEST_WEBSITE_OWNER_NAME}/resourceGroups/{TEST_WEBSITE_RESOURCE_GROUP}/providers/Microsoft.Web/sites/{TEST_WEBSITE_SITE_NAME}")

        self.assertEqual(attributes["cloud.region"], TEST_REGION_NAME)
        self.assertEqual(attributes["deployment.environment"], TEST_WEBSITE_SLOT_NAME)
        self.assertEqual(attributes["host.id"], TEST_WEBSITE_HOSTNAME)
        self.assertEqual(attributes["service.instance.id"], TEST_WEBSITE_INSTANCE_ID)
        self.assertEqual(attributes["azure.app.service.stamp"], TEST_WEBSITE_HOME_STAMPNAME)

    @patch.dict("os.environ", {
        "WEBSITE_SITE_NAME": TEST_WEBSITE_SITE_NAME,
        "REGION_NAME": TEST_REGION_NAME,
        "WEBSITE_SLOT_NAME": TEST_WEBSITE_SLOT_NAME,
        "WEBSITE_HOSTNAME": TEST_WEBSITE_HOSTNAME,
        "WEBSITE_INSTANCE_ID": TEST_WEBSITE_INSTANCE_ID,
        "WEBSITE_HOME_STAMPNAME": TEST_WEBSITE_HOME_STAMPNAME,
        "WEBSITE_OWNER_NAME": TEST_WEBSITE_OWNER_NAME,
    }, clear=True)
    def test_on_app_service_no_resource_group(self):
        resource = AzureAppServiceResourceDetector().detect()
        attributes = resource.attributes
        self.assertEqual(attributes["service.name"], TEST_WEBSITE_SITE_NAME)
        self.assertEqual(attributes["cloud.provider"], "azure")
        self.assertEqual(attributes["cloud.platform"], "azure_app_service")

        self.assertTrue("cloud.resource_id" not in attributes)

        self.assertEqual(attributes["cloud.region"], TEST_REGION_NAME)
        self.assertEqual(attributes["deployment.environment"], TEST_WEBSITE_SLOT_NAME)
        self.assertEqual(attributes["host.id"], TEST_WEBSITE_HOSTNAME)
        self.assertEqual(attributes["service.instance.id"], TEST_WEBSITE_INSTANCE_ID)
        self.assertEqual(attributes["azure.app.service.stamp"], TEST_WEBSITE_HOME_STAMPNAME)

    @patch.dict("os.environ", {
        "WEBSITE_SITE_NAME": TEST_WEBSITE_SITE_NAME,
        "REGION_NAME": TEST_REGION_NAME,
        "WEBSITE_SLOT_NAME": TEST_WEBSITE_SLOT_NAME,
        "WEBSITE_HOSTNAME": TEST_WEBSITE_HOSTNAME,
        "WEBSITE_INSTANCE_ID": TEST_WEBSITE_INSTANCE_ID,
        "WEBSITE_HOME_STAMPNAME": TEST_WEBSITE_HOME_STAMPNAME,
        "WEBSITE_OWNER_NAME": TEST_WEBSITE_OWNER_NAME,
    }, clear=True)
    def test_on_app_service_no_owner(self):
        resource = AzureAppServiceResourceDetector().detect()
        attributes = resource.attributes
        self.assertEqual(attributes["service.name"], TEST_WEBSITE_SITE_NAME)
        self.assertEqual(attributes["cloud.provider"], "azure")
        self.assertEqual(attributes["cloud.platform"], "azure_app_service")

        self.assertTrue("cloud.resource_id" not in attributes)

        self.assertEqual(attributes["cloud.region"], TEST_REGION_NAME)
        self.assertEqual(attributes["deployment.environment"], TEST_WEBSITE_SLOT_NAME)
        self.assertEqual(attributes["host.id"], TEST_WEBSITE_HOSTNAME)
        self.assertEqual(attributes["service.instance.id"], TEST_WEBSITE_INSTANCE_ID)
        self.assertEqual(attributes["azure.app.service.stamp"], TEST_WEBSITE_HOME_STAMPNAME)

    @patch.dict("os.environ", {
        "REGION_NAME": TEST_REGION_NAME,
        "WEBSITE_SLOT_NAME": TEST_WEBSITE_SLOT_NAME,
        "WEBSITE_HOSTNAME": TEST_WEBSITE_HOSTNAME,
        "WEBSITE_INSTANCE_ID": TEST_WEBSITE_INSTANCE_ID,
        "WEBSITE_HOME_STAMPNAME": TEST_WEBSITE_HOME_STAMPNAME,
        "WEBSITE_OWNER_NAME": TEST_WEBSITE_OWNER_NAME,
    }, clear=True)
    def test_off_app_service(self):
        resource = AzureAppServiceResourceDetector().detect()
        self.assertEqual(resource.attributes, {})
