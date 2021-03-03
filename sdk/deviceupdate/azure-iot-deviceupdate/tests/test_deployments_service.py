# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from azure.core.exceptions import ResourceNotFoundError
from azure.iot.deviceupdate import DeviceUpdateClient
from azure.iot.deviceupdate.models import *
from testcase import DeviceUpdateTest, DeviceUpdatePowerShellPreparer, callback
import uuid
from datetime import datetime


class DeploymentsClientTestCase(DeviceUpdateTest):

    @DeviceUpdatePowerShellPreparer()
    def test_get_all_deployments(self, deviceupdate_account_endpoint, deviceupdate_instance_id):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        response = client.deployments.get_all_deployments()
        self.assertIsNotNone(response)
        providers = list(response)
        self.assertTrue(len(providers) > 0)

    @DeviceUpdatePowerShellPreparer()
    def test_get_deployment(
        self,
        deviceupdate_account_endpoint,
        deviceupdate_instance_id,
        deviceupdate_deployment_id,
        deviceupdate_provider,
        deviceupdate_model,
        deviceupdate_version,
    ):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        response = client.deployments.get_deployment(deviceupdate_deployment_id)
        self.assertIsNotNone(response)
        self.assertEqual(deviceupdate_deployment_id, response.deployment_id)
        self.assertEqual(DeploymentType.complete, response.deployment_type)
        self.assertEqual(DeviceGroupType.DEVICE_GROUP_DEFINITIONS, response.device_group_type)
        self.assertEqual(deviceupdate_provider, response.update_id.provider)
        self.assertEqual(deviceupdate_model, response.update_id.name)
        self.assertEqual(deviceupdate_version, response.update_id.version)

    @DeviceUpdatePowerShellPreparer()
    def test_get_deployment_not_found(self, deviceupdate_account_endpoint, deviceupdate_instance_id):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        try:
            _ = client.deployments.get_deployment("foo")
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    @pytest.mark.live_test_only
    @DeviceUpdatePowerShellPreparer()
    def test_create_cancel_and_delete_deployment(
        self,
        deviceupdate_account_endpoint,
        deviceupdate_instance_id,
        deviceupdate_device_id,
        deviceupdate_provider,
        deviceupdate_model,
        deviceupdate_version,
    ):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        # The following test works *ONLY* when run LIVE -> not recorded

        deployment_id = uuid.uuid4().hex
        response = client.deployments.create_or_update_deployment(
            deployment_id=deployment_id,
            deployment=Deployment(
                deployment_id=deployment_id,
                deployment_type=DeploymentType.complete,
                start_date_time=datetime(2020, 1, 1, 0, 0, 0, 0),
                device_group_type=DeviceGroupType.DEVICE_GROUP_DEFINITIONS,
                device_group_definition=[deviceupdate_device_id],
                update_id=UpdateId(provider=deviceupdate_provider, name=deviceupdate_model, version=deviceupdate_version)))
        self.assertIsNotNone(response)
        self.assertEqual(deployment_id, response.deployment_id)

        response = client.deployments.get_deployment(deployment_id)
        self.assertIsNotNone(response)
        self.assertEqual(deployment_id, response.deployment_id)

        response = client.deployments.get_deployment_status(deployment_id)
        self.assertIsNotNone(response)
        self.assertEqual(DeploymentState.ACTIVE, response.deployment_state)

        response, value, _ = client.deployments.cancel_deployment(deployment_id, cls=callback)
        self.assertIsNotNone(response)
        self.assertEqual(200, response.http_response.status_code)
        self.assertIsNotNone(value)
        self.assertEqual(deployment_id, value.deployment_id)
        self.assertTrue(value.is_canceled)

        response, _, _ = client.deployments.delete_deployment(deployment_id, cls=callback)
        self.assertIsNotNone(response)
        self.assertEqual(200, response.http_response.status_code)

        try:
            _ = client.deployments.get_deployment(deployment_id)
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    @DeviceUpdatePowerShellPreparer()
    def test_get_deployment_status(self, deviceupdate_account_endpoint, deviceupdate_instance_id, deviceupdate_deployment_id):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        response = client.deployments.get_deployment_status(deviceupdate_deployment_id)
        self.assertIsNotNone(response)
        self.assertEqual(DeploymentState.ACTIVE, response.deployment_state)

    @DeviceUpdatePowerShellPreparer()
    def test_get_deployment_status_not_found(self, deviceupdate_account_endpoint, deviceupdate_instance_id):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        try:
            _ = client.deployments.get_deployment_status("foo")
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)

    @DeviceUpdatePowerShellPreparer()
    def test_get_deployment_devices(self, deviceupdate_account_endpoint, deviceupdate_instance_id, deviceupdate_deployment_id):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        response = client.deployments.get_deployment_devices(deviceupdate_deployment_id)
        self.assertIsNotNone(response)
        providers = list(response)
        self.assertTrue(len(providers) > 0)

    @DeviceUpdatePowerShellPreparer()
    def test_get_deployment_devices_not_found(self, deviceupdate_account_endpoint, deviceupdate_instance_id):
        client = self.create_client(account_endpoint=deviceupdate_account_endpoint, instance_id=deviceupdate_instance_id)
        try:
            response = client.deployments.get_deployment_devices("foo")
            _ = list(response)
            self.fail("NotFound expected")
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)
