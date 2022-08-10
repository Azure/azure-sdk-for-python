# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import AzureTestCase, PowerShellPreparer
from azure.communication.rooms import RoomsClient


class RoomsTest(AzureTestCase):
    def __init__(self, method_name, **kwargs):
        super(RoomsTest, self).__init__(method_name, **kwargs)

    def create_client(self, endpoint):
        credential = self.get_credential(RoomsClient)
        return self.create_client_from_credential(
            RoomsClient,
            credential=credential,
            endpoint=endpoint,
        )


RoomsPowerShellPreparer = functools.partial(
    PowerShellPreparer,
    "rooms",
    rooms_endpoint="https://myservice.azure.com"
)
