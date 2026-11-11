# coding: utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from azure.iot.deviceregistrysoftwareupdate.models import DeviceClass
from devtools_testutils import recorded_by_proxy

from testcase import DeviceRegistrySoftwareUpdatePreparer, DeviceRegistrySoftwareUpdateTest


class TestDeviceClasses(DeviceRegistrySoftwareUpdateTest):
    @DeviceRegistrySoftwareUpdatePreparer()
    @recorded_by_proxy
    def test_list_device_classes(self, deviceregistrysoftwareupdate_endpoint):
        client = self.create_client(deviceregistrysoftwareupdate_endpoint)

        device_classes = list(client.device_classes.list())

        assert all(isinstance(device_class, DeviceClass) for device_class in device_classes)
