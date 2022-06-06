# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from testcase import DeviceUpdateTest, DeviceUpdatePowerShellPreparer
from azure.core.exceptions import ResourceNotFoundError
import pytest
import os


class UpdatesClientTest(DeviceUpdateTest):
    @DeviceUpdatePowerShellPreparer()
    def test_get_names_not_found(
            self,
            deviceupdate_endpoint,
            deviceupdate_instance_id,
    ):
        client = self.create_client(endpoint=deviceupdate_endpoint, instance_id=deviceupdate_instance_id)
        try:
            response = client.device_update.list_names("foo")
            result = [item for item in response]
            self.assertTrue(len(result) > 0)
        except ResourceNotFoundError as e:
            self.assertEqual(404, e.status_code)
