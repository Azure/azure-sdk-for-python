# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import DeviceUpdateTest, DeviceUpdatePowerShellPreparer
from azure.core.exceptions import ResourceNotFoundError
import pytest
import os

class DeviceUpdateSmokeTest(DeviceUpdateTest):
    @DeviceUpdatePowerShellPreparer()
    def test_get_devices(
            self,
            deviceupdate_endpoint,
            deviceupdate_instance_id
    ):
        client = self.create_client(endpoint=deviceupdate_endpoint, instance_id=deviceupdate_instance_id)
        try:
            response = client.device_management.list_devices()
            result = [item for item in response]
            self.assertTrue(len(result) > 0)
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    @DeviceUpdatePowerShellPreparer()
    def test_get_device_not_found(
            self,
            deviceupdate_endpoint,
            deviceupdate_instance_id
    ):
        client = self.create_client(endpoint=deviceupdate_endpoint, instance_id=deviceupdate_instance_id)
        try:
            client.device_management.get_device("foo")
            self.fail("NotFound response expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    @DeviceUpdatePowerShellPreparer()
    def test_get_groups(
            self,
            deviceupdate_endpoint,
            deviceupdate_instance_id
    ):
        client = self.create_client(endpoint=deviceupdate_endpoint, instance_id=deviceupdate_instance_id)
        try:
            response = client.device_management.list_groups()
            result = [item for item in response]
            self.assertTrue(len(result) > 0)
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    @DeviceUpdatePowerShellPreparer()
    def test_get_group(
            self,
            deviceupdate_endpoint,
            deviceupdate_instance_id,
            deviceupdate_device_group
    ):
        client = self.create_client(endpoint=deviceupdate_endpoint, instance_id=deviceupdate_instance_id)
        response = client.device_management.get_group(deviceupdate_device_group)
        self.assertIsNotNone(response)

    @DeviceUpdatePowerShellPreparer()
    def test_get_group_not_found(
            self,
            deviceupdate_endpoint,
            deviceupdate_instance_id
    ):
        client = self.create_client(endpoint=deviceupdate_endpoint, instance_id=deviceupdate_instance_id)
        try:
            client.device_management.get_group("foo")
            self.fail("NotFound response expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    @DeviceUpdatePowerShellPreparer()
    def _test_get_device_classes(
            self,
            deviceupdate_endpoint,
            deviceupdate_instance_id
    ):
        client = self.create_client(endpoint=deviceupdate_endpoint, instance_id=deviceupdate_instance_id)
        try:
            response = client.device_management.list_device_classes()
            result = [item for item in response]
            self.assertTrue(len(result) > 0)
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    @DeviceUpdatePowerShellPreparer()
    def test_get_device_class_not_found(
            self,
            deviceupdate_endpoint,
            deviceupdate_instance_id
    ):
        client = self.create_client(endpoint=deviceupdate_endpoint, instance_id=deviceupdate_instance_id)
        try:
            client.device_management.get_device_class("foo")
            self.fail("NotFound response expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    @DeviceUpdatePowerShellPreparer()
    def _test_get_best_updates_for_group(
            self,
            deviceupdate_endpoint,
            deviceupdate_instance_id,
            deviceupdate_device_group
    ):
        client = self.create_client(endpoint=deviceupdate_endpoint, instance_id=deviceupdate_instance_id)
        response = client.device_management.list_best_updates_for_group(deviceupdate_device_group)
        result = [item for item in response]
        self.assertTrue(len(result) > 0)

    @DeviceUpdatePowerShellPreparer()
    def test_get_best_updates_for_group_not_found(
            self,
            deviceupdate_endpoint,
            deviceupdate_instance_id
    ):
        client = self.create_client(endpoint=deviceupdate_endpoint, instance_id=deviceupdate_instance_id)
        try:
            response = client.device_management.list_best_updates_for_group("foo")
            result = [item for item in response]
            self.assertTrue(len(result) > 0)
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    @DeviceUpdatePowerShellPreparer()
    def _test_get_deployments_for_group(
            self,
            deviceupdate_endpoint,
            deviceupdate_instance_id,
            deviceupdate_device_group
    ):
        client = self.create_client(endpoint=deviceupdate_endpoint, instance_id=deviceupdate_instance_id)
        response = client.device_management.list_best_updates_for_group(deviceupdate_device_group)
        result = [item for item in response]
        self.assertTrue(len(result) > 0)

    @DeviceUpdatePowerShellPreparer()
    def test_get_deployments_for_group_not_found(
            self,
            deviceupdate_endpoint,
            deviceupdate_instance_id
    ):
        client = self.create_client(endpoint=deviceupdate_endpoint, instance_id=deviceupdate_instance_id)
        try:
            response = client.device_management.list_best_updates_for_group("foo")
            result = [item for item in response]
            self.assertTrue(len(result) > 0)
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

