# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.core.exceptions import ResourceNotFoundError
from azure.iot.deviceupdate import DeviceUpdateClient
from azure.iot.deviceupdate.models import *
from testcase import DeviceUpdateTest, DeviceUpdatePowerShellPreparer


class DevicesClientTestCase(DeviceUpdateTest):

    @DeviceUpdatePowerShellPreparer()
    def test_get_all_device_classes(self, deviceupdate_account_endpoint, deviceupdate_instance_id):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        response = client.devices.get_all_device_classes()
        self.assertIsNotNone(response)
        providers = list(response)
        self.assertTrue(len(providers) > 0)

    @DeviceUpdatePowerShellPreparer()
    def test_get_device_class(
        self,
        deviceupdate_account_endpoint,
        deviceupdate_instance_id,
        deviceupdate_device_class_id,
        deviceupdate_provider,
        deviceupdate_model,
    ):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        response = client.devices.get_device_class(deviceupdate_device_class_id)
        self.assertIsNotNone(response)
        self.assertEqual(deviceupdate_provider, response.manufacturer)
        self.assertEqual(deviceupdate_model, response.model)

    @DeviceUpdatePowerShellPreparer()
    def test_get_device_class_not_found(self, deviceupdate_account_endpoint, deviceupdate_instance_id):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        try:
            _ = client.devices.get_device_class("foo")
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    @DeviceUpdatePowerShellPreparer()
    def test_get_device_class_device_ids(
        self,
        deviceupdate_account_endpoint,
        deviceupdate_instance_id,
        deviceupdate_device_class_id,
    ):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        response = client.devices.get_device_class_device_ids(deviceupdate_device_class_id)
        self.assertIsNotNone(response)
        providers = list(response)
        self.assertTrue(len(providers) > 0)

    @DeviceUpdatePowerShellPreparer()
    def test_get_device_class_device_ids_not_found(self, deviceupdate_account_endpoint, deviceupdate_instance_id):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        try:
            response = client.devices.get_device_class_device_ids("foo")
            _ = list(response)
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    @DeviceUpdatePowerShellPreparer()
    def test_get_device_class_installable_updates(
        self,
        deviceupdate_account_endpoint,
        deviceupdate_instance_id,
        deviceupdate_device_class_id,
        deviceupdate_provider,
        deviceupdate_model,
        deviceupdate_version,
    ):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        response = client.devices.get_device_class_installable_updates(deviceupdate_device_class_id)
        self.assertIsNotNone(response)
        providers = list(response)
        self.assertTrue(len(providers) > 0)
        self.assertTrue(UpdateId(provider=deviceupdate_provider, name=deviceupdate_model, version=deviceupdate_version) in providers)

    @DeviceUpdatePowerShellPreparer()
    def test_get_device_class_installable_updates_not_found(self, deviceupdate_account_endpoint, deviceupdate_instance_id):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        try:
            response = client.devices.get_device_class_installable_updates("foo")
            _ = list(response)
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    @DeviceUpdatePowerShellPreparer()
    def test_get_all_devices(self, deviceupdate_account_endpoint, deviceupdate_instance_id):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        response = client.devices.get_all_devices()
        self.assertIsNotNone(response)
        providers = list(response)
        self.assertTrue(len(providers) > 0)

    @DeviceUpdatePowerShellPreparer()
    def test_get_device(
        self,
        deviceupdate_account_endpoint,
        deviceupdate_instance_id,
        deviceupdate_device_id,
        deviceupdate_provider,
        deviceupdate_model,
    ):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        response = client.devices.get_device(deviceupdate_device_id)
        self.assertIsNotNone(response)
        self.assertEqual(deviceupdate_provider, response.manufacturer)
        self.assertEqual(deviceupdate_model, response.model)

    @DeviceUpdatePowerShellPreparer()
    def test_get_device_not_found(self, deviceupdate_account_endpoint, deviceupdate_instance_id):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        try:
            _ = client.devices.get_device("foo")
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    @DeviceUpdatePowerShellPreparer()
    def test_get_update_compliance(self, deviceupdate_account_endpoint, deviceupdate_instance_id):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        response = client.devices.get_update_compliance()
        self.assertIsNotNone(response)
        self.assertTrue(response.total_device_count > 0)

    @DeviceUpdatePowerShellPreparer()
    def test_get_all_device_tags(self, deviceupdate_account_endpoint, deviceupdate_instance_id):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        response = client.devices.get_all_device_tags()
        self.assertIsNotNone(response)
        providers = list(response)
        self.assertTrue(len(providers) > 0)

    @DeviceUpdatePowerShellPreparer()
    def test_get_device_tag(self, deviceupdate_account_endpoint, deviceupdate_instance_id, deviceupdate_device_id):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        tag_name = deviceupdate_device_id
        response = client.devices.get_device_tag(tag_name)
        self.assertIsNotNone(response)
        self.assertEqual(tag_name, response.tag_name)

    @DeviceUpdatePowerShellPreparer()
    def test_get_device_tag_not_found(self, deviceupdate_account_endpoint, deviceupdate_instance_id):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        try:
            _ = client.devices.get_device_tag("foo")
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    @DeviceUpdatePowerShellPreparer()
    def test_get_all_groups(self, deviceupdate_account_endpoint, deviceupdate_instance_id):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        response = client.devices.get_all_groups()
        self.assertIsNotNone(response)
        providers = list(response)
        self.assertTrue(len(providers) > 0)

    @DeviceUpdatePowerShellPreparer()
    def test_get_group(self, deviceupdate_account_endpoint, deviceupdate_instance_id, deviceupdate_device_id):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        group_id = deviceupdate_device_id
        response = client.devices.get_group(group_id)
        self.assertIsNotNone(response)
        self.assertEqual(group_id, response.group_id)

    @DeviceUpdatePowerShellPreparer()
    def test_get_group_not_found(self, deviceupdate_account_endpoint, deviceupdate_instance_id):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        try:
            _ = client.devices.get_group("foo")
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    @DeviceUpdatePowerShellPreparer()
    def test_get_group_update_compliance(self, deviceupdate_account_endpoint, deviceupdate_instance_id, deviceupdate_device_id):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        group_id = deviceupdate_device_id
        response = client.devices.get_group_update_compliance(group_id)
        self.assertIsNotNone(response)
        self.assertTrue(response.total_device_count > 0)

    @DeviceUpdatePowerShellPreparer()
    def test_get_group_update_compliance_not_found(self, deviceupdate_account_endpoint, deviceupdate_instance_id):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        try:
            _ = client.devices.get_group_update_compliance("foo")
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    @DeviceUpdatePowerShellPreparer()
    def test_get_group_best_updates(self, deviceupdate_account_endpoint, deviceupdate_instance_id, deviceupdate_device_id):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        group_id = deviceupdate_device_id
        response = client.devices.get_group_best_updates(group_id)
        self.assertIsNotNone(response)
        updates = list(response)
        self.assertTrue(len(updates) > 0)

    @DeviceUpdatePowerShellPreparer()
    def test_get_group_best_updates_not_found(self, deviceupdate_account_endpoint, deviceupdate_instance_id):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        try:
            response = client.devices.get_group_best_updates("foo")
            _ = list(response)
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)
