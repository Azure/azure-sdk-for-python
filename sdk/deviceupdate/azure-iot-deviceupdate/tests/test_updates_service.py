# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from devtools_testutils import recorded_by_proxy
from testcase import DeviceUpdateTest, DeviceUpdatePowerShellPreparer
from azure.core.exceptions import ResourceNotFoundError
import pytest


class TestDeviceUpdateClient(DeviceUpdateTest):
    @recorded_by_proxy
    @DeviceUpdatePowerShellPreparer()
    def test_get_update_providers(
            self,
            deviceupdate_endpoint,
            deviceupdate_instance_id,
    ):
        client = self.create_client(endpoint=deviceupdate_endpoint, instance_id=deviceupdate_instance_id)
        try:
            response = client.device_update.list_providers()
            result = [item for item in response]
            assert len(result) > 0
        except ResourceNotFoundError as e:
            assert 404 == e.status_code

    @recorded_by_proxy
    @DeviceUpdatePowerShellPreparer()
    def test_get_update_names(
            self,
            deviceupdate_endpoint,
            deviceupdate_instance_id,
            deviceupdate_update_provider,
    ):
        client = self.create_client(endpoint=deviceupdate_endpoint, instance_id=deviceupdate_instance_id)
        try:
            response = client.device_update.list_names(deviceupdate_update_provider)
            result = [item for item in response]
            assert len(result) > 0
        except ResourceNotFoundError as e:
            assert 404 == e.status_code

    @recorded_by_proxy
    @DeviceUpdatePowerShellPreparer()
    def test_get_update_names_not_found(
            self,
            deviceupdate_endpoint,
            deviceupdate_instance_id,
    ):
        client = self.create_client(endpoint=deviceupdate_endpoint, instance_id=deviceupdate_instance_id)
        try:
            response = client.device_update.list_names("foo")
            result = [item for item in response]
            assert len(result) > 0
        except ResourceNotFoundError as e:
            assert 404 == e.status_code

    @recorded_by_proxy
    @DeviceUpdatePowerShellPreparer()
    def test_get_update_versions(
            self,
            deviceupdate_endpoint,
            deviceupdate_instance_id,
            deviceupdate_update_provider,
            deviceupdate_update_name,
    ):
        client = self.create_client(endpoint=deviceupdate_endpoint, instance_id=deviceupdate_instance_id)
        try:
            response = client.device_update.list_versions(deviceupdate_update_provider, deviceupdate_update_name)
            result = [item for item in response]
            assert len(result) > 0
        except ResourceNotFoundError as e:
            assert 404 == e.status_code

    @recorded_by_proxy
    @DeviceUpdatePowerShellPreparer()
    def test_get_update_versions_not_found(
            self,
            deviceupdate_endpoint,
            deviceupdate_instance_id,
    ):
        client = self.create_client(endpoint=deviceupdate_endpoint, instance_id=deviceupdate_instance_id)
        try:
            response = client.device_update.list_versions("foo", "bar")
            result = [item for item in response]
            assert len(result) > 0
        except ResourceNotFoundError as e:
            assert 404 == e.status_code

    @recorded_by_proxy
    @DeviceUpdatePowerShellPreparer()
    def test_get_update(
            self,
            deviceupdate_endpoint,
            deviceupdate_instance_id,
            deviceupdate_update_provider,
            deviceupdate_update_name,
            deviceupdate_update_version,
    ):
        client = self.create_client(endpoint=deviceupdate_endpoint, instance_id=deviceupdate_instance_id)
        response = client.device_update.get_update(deviceupdate_update_provider, deviceupdate_update_name, deviceupdate_update_version)
        assert response is not None

    @recorded_by_proxy
    @DeviceUpdatePowerShellPreparer()
    def test_get_update_not_found(
            self,
            deviceupdate_endpoint,
            deviceupdate_instance_id,
    ):
        client = self.create_client(endpoint=deviceupdate_endpoint, instance_id=deviceupdate_instance_id)
        try:
            client.device_update.get_update("foo", "bar", "1.2")
            pytest.fail("NotFound response expected")
        except ResourceNotFoundError as e:
            assert 404 == e.status_code

    @recorded_by_proxy
    @DeviceUpdatePowerShellPreparer()
    def test_get_update_files(
            self,
            deviceupdate_endpoint,
            deviceupdate_instance_id,
            deviceupdate_update_provider,
            deviceupdate_update_name,
            deviceupdate_update_version,
    ):
        client = self.create_client(endpoint=deviceupdate_endpoint, instance_id=deviceupdate_instance_id)
        try:
            response = client.device_update.list_files(deviceupdate_update_provider, deviceupdate_update_name, deviceupdate_update_version)
            result = [item for item in response]
            assert len(result) > 0
        except ResourceNotFoundError as e:
            assert 404 == e.status_code

    @recorded_by_proxy
    @DeviceUpdatePowerShellPreparer()
    def test_get_update_files_not_found(
            self,
            deviceupdate_endpoint,
            deviceupdate_instance_id,
    ):
        client = self.create_client(endpoint=deviceupdate_endpoint, instance_id=deviceupdate_instance_id)
        try:
            response = client.device_update.list_files("foo", "bar", "1.2")
            result = [item for item in response]
            assert len(result) > 0
        except ResourceNotFoundError as e:
            assert 404 == e.status_code
