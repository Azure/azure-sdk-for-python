# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
from testcase import DevcenterTest, DevcenterPowerShellPreparer


class DevcenterSmokeTest(DevcenterTest):
    @DevcenterPowerShellPreparer()
    def test_smoke(self):
        dev_center = "TestDevCenter"
        tenant_id = "00000000-0000-0000-0000-000000000000"
        client = self.create_client(tenant_id=tenant_id, dev_center=dev_center)
        # test your code here, for example:
        # result = client.xxx.xx(...)
        # assert result is not None
