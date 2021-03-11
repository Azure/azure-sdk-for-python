# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import AzureTestCase, PowerShellPreparer
from azure.iot.deviceupdate import DeviceUpdateClient


class DeviceUpdateTest(AzureTestCase):

    def create_client(self, account_endpoint, instance_id):
        credential = self.get_credential(DeviceUpdateClient)
        return self.create_client_from_credential(
            DeviceUpdateClient,
            credential=credential,
            account_endpoint=account_endpoint,
            instance_id=instance_id,
        )

DeviceUpdatePowerShellPreparer = functools.partial(
    PowerShellPreparer,
    "deviceupdate",
    deviceupdate_account_endpoint="fake_endpoint.com",
    deviceupdate_instance_id="blue",
    deviceupdate_operation_id="fakeOperationId",
    deviceupdate_provider="Contoso",
    deviceupdate_model="Virtual-Machine",
    deviceupdate_version="fakeVersion",
    deviceupdate_deployment_id="fakeDeploymentId",
    deviceupdate_device_id="fakeDeviceId",
    deviceupdate_device_class_id="fakeDeviceClassId"
)

def callback(response, value, headers):
    return response, value, headers
