# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import functools
from azure.communication.rooms._shared.utils import parse_connection_str
from _shared.testcase import CommunicationTestCase
from devtools_testutils import PowerShellPreparer
from azure.communication.rooms import RoomsClient

class RoomsTestCase(CommunicationTestCase):
    def __init__(self, method_name, **kwargs):
        super(RoomsTestCase, self).__init__(method_name, **kwargs)
    def create_client(self, endpoint):
        credential = self.get_credential(RoomsClient)
        return self.create_client_from_credential(
            RoomsClient,
            credential=credential,
            endpoint=endpoint,
        )
    def _get_connection_str(self, resource_type):
        if self.is_playback():
            return "endpoint=https://sanitized.communication.azure.com/;accesskey=fake==="
        else:
            con_str = os.getenv('COMMUNICATION_CONNECTION_STRING_ROOMS')
            if con_str == None:
                return super(RoomsTestCase, self)._get_connection_str(resource_type)
            return con_str

RoomsPowerShellPreparer = functools.partial(
    PowerShellPreparer,
    "rooms",
    rooms_endpoint="https://myservice.azure.com"
)
