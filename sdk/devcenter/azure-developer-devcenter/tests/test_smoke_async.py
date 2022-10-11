# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
from testcase import DevcenterPowerShellPreparer
from testcase_async import DevcenterAsyncTest


class DevcenterSmokeAsyncTest(DevcenterAsyncTest):
    @DevcenterPowerShellPreparer()
    async def test_smoke_async(self):
        dev_center = "sdk-default-dc"
        tenant_id = "88888888-8888-8888-8888-888888888888"
        client = self.create_client(tenant_id=tenant_id, dev_center=dev_center)
        # test your code here, for example:
        # result = await client.xxx.xx(...)
        # assert result is not None
