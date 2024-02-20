# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import AzureTestCase
from azure.developer.devcenter.aio import DevCenterClient


class DevcenterAsyncTest(AzureTestCase):
    def create_client(self, endpoint):
        credential = self.get_credential(DevCenterClient)
        return DevCenterClient(endpoint=endpoint, credential=credential)
