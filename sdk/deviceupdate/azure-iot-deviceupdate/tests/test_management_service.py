# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from devtools_testutils import recorded_by_proxy
from testcase import DeviceUpdateTest, DeviceUpdatePowerShellPreparer
from azure.core.exceptions import ResourceNotFoundError
import pytest

class TestDeviceManagementClient(DeviceUpdateTest):
    @recorded_by_proxy
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
            assert len(result) > 0
        except ResourceNotFoundError as e:
            assert 404 == e.status_code

    @recorded_by_proxy
    @DeviceUpdatePowerShellPreparer()
    def test_get_device_not_found(
            self,
            deviceupdate_endpoint,
            deviceupdate_instance_id
    ):
        client = self.create_client(endpoint=deviceupdate_endpoint, instance_id=deviceupdate_instance_id)
        try:
            client.device_management.get_device("foo")
            pytest.fail("NotFound response expected")
        except ResourceNotFoundError as e:
            assert 404 == e.status_code

    @recorded_by_proxy
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
            assert len(result) > 0
        except ResourceNotFoundError as e:
            assert 404 == e.status_code

    @recorded_by_proxy
    @DeviceUpdatePowerShellPreparer()
    def test_get_group(
            self,
            deviceupdate_endpoint,
            deviceupdate_instance_id,
            deviceupdate_device_group
    ):
        client = self.create_client(endpoint=deviceupdate_endpoint, instance_id=deviceupdate_instance_id)
        response = client.device_management.get_group(deviceupdate_device_group)
        assert response is not None

    @recorded_by_proxy
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
            assert 404 == e.status_code

    @recorded_by_proxy
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
            assert len(result) > 0
        except ResourceNotFoundError as e:
            assert 404 == e.status_code

    @recorded_by_proxy
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
            assert 404 == e.status_code

    @recorded_by_proxy
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
        assert len(result) > 0

    @recorded_by_proxy
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
            assert len(result) > 0
        except ResourceNotFoundError as e:
            assert 404 == e.status_code

    @recorded_by_proxy
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
        assert len(result) > 0

    @recorded_by_proxy
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
            assert len(result) > 0
        except ResourceNotFoundError as e:
            assert 404 == e.status_code

