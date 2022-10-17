# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
from testcase import DevcenterTest, DevcenterPowerShellPreparer
from devtools_testutils import recorded_by_proxy

class TestDevcenterSmoke(DevcenterTest):
    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_smoke(self, **kwargs):
        azure_tenant_id = kwargs.pop("devcenter_tenant_id")
        devcenter_name = kwargs.pop("devcenter_name")
        client = self.create_client(tenant_id=azure_tenant_id, dev_center=devcenter_name)
