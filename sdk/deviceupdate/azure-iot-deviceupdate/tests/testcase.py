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
    def __init__(self, method_name, **kwargs):
        super(DeviceUpdateTest, self).__init__(method_name, **kwargs)

    def create_client(self, endpoint, instance_id):
        credential = self.get_credential(DeviceUpdateClient)
        return self.create_client_from_credential(
            DeviceUpdateClient,
            endpoint=endpoint,
            instance_id=instance_id,
            credential=credential
        )


DeviceUpdatePowerShellPreparer = functools.partial(
    PowerShellPreparer,
    "deviceupdate",
    deviceupdate_endpoint="fake_account.account.purview.azure.com",
    deviceupdate_instance_id="instance"
)
