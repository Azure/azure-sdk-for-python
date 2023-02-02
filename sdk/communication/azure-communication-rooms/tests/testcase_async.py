# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
from _shared.asynctestcase import AsyncCommunicationTestCase
from azure.communication.rooms.aio import RoomsClient


class RoomsAsyncTestCase(AsyncCommunicationTestCase):
    def __init__(self, method_name, **kwargs):
        super(RoomsAsyncTestCase, self).__init__(method_name, **kwargs)

    def create_client(self, endpoint):
        credential = self.get_credential(RoomsClient, is_async=True)
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
                return super(RoomsAsyncTestCase, self)._get_connection_str(resource_type)
            return con_str
