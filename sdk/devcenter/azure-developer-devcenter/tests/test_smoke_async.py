# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
from testcase import DevcenterPowerShellPreparer
from testcase_async import DevcenterAsyncTest
from devtools_testutils.aio import recorded_by_proxy_async

class TestDevcenterSmokeAsync(DevcenterAsyncTest):
    @DevcenterPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_smoke_async(self, **kwargs):
        azure_tenant_id = kwargs.pop("devcenter_tenant_id")
        devcenter_name = kwargs.pop("devcenter_name")
        client = self.create_client(tenant_id=azure_tenant_id, dev_center=devcenter_name)
