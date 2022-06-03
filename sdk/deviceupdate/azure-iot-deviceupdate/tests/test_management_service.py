# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import DeviceUpdateTest, DeviceUpdatePowerShellPreparer
import pytest
import os

class DeviceUpdateSmokeTest(DeviceUpdateTest):

    @DeviceUpdatePowerShellPreparer()
    def test_get_all_device_classes(self, deviceupdate_endpoint, deviceupdate_instance_id):
        client = self.create_client(endpoint=deviceupdate_endpoint, instance_id=deviceupdate_instance_id)
        response = client.device_management.list_device_classes()
        result = [item for item in response]
        self.assertTrue(len(result) == 0)
