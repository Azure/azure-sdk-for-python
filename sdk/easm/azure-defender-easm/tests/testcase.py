# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
from azure.defender.easm import EasmClient
import datetime


class EasmTest(AzureRecordedTestCase):
    def create_client(self, endpoint, resource_group, subscription_id, workspace):
        credential = self.get_credential(EasmClient)
        return self.create_client_from_credential(
            EasmClient,
            credential=credential,
            endpoint=endpoint,
            resource_group_name=resource_group,
            subscription_id=subscription_id,
            workspace_name=workspace
        )

    def check_timestamp_format(self, time_format, timestamp):
        try:
            datetime.datetime.strptime(timestamp, time_format)
        except ValueError as e:
            assert False, 'invalid timestamp format'

    def check_guid_format(self, guid):
        parts = guid.split('-')
        lengths = [8, 4, 4, 4, 12]
        assert all(len(seg) == l for seg, l in zip(parts, lengths)), 'invalid guid'


EasmParameterProvider = functools.partial(
    EnvironmentVariableLoader,
    "easm",
    easm_endpoint="fake_endpoint.easm.defender.microsoft.com",
    easm_resource_group="fake_resource_group",
    easm_subscription_id="fake-sub-id",
    easm_workspace="fakename"
)
