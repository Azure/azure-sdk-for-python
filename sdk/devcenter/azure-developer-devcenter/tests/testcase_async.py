# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import AzureTestCase
from azure.developer.devcenter.aio import DevCenterClient


class DevcenterAsyncTest(AzureTestCase):
    def __init__(self, method_name, **kwargs):
        super(DevcenterAsyncTest, self).__init__(method_name, **kwargs)
        
    def create_client(self, tenant_id, dev_center):
        credential = self.get_credential(DevCenterClient)
        return DevCenterClient(
            dev_center=dev_center,
            tenant_id=tenant_id,
            credential=credential
        )
