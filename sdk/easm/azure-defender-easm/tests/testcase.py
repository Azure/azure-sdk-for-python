# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import AzureTestCase, PowerShellPreparer
from azure.defender.easm import EasmClient
from azure.identity import InteractiveBrowserCredential
import datetime

RG='nate-test-rg'
SUB_ID='59af3bf1-d118-4916-808e-923509b34a94'
WS='testSdkWorkspace9271133'
ENDPOINT='eastus.easm.defender.microsoft.com'

class EasmTest(AzureTestCase):
    def __init__(self, method_name, **kwargs):
        super(EasmTest, self).__init__(method_name, **kwargs)

    def create_client(self, endpoint):
        credential = self.get_credential(EasmClient)
        return self.create_client_from_credential(
            EasmClient,
            #credential=InteractiveBrowserCredential(),
            credential=credential,
            endpoint=endpoint,
            resource_group_name=RG,
            subscription_id=SUB_ID,
            workspace_name=WS
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



EasmPowerShellPreparer = functools.partial(
    PowerShellPreparer,
    'easm',
    easm_endpoint=ENDPOINT
)
