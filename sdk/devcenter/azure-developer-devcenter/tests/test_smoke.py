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
        endpoint = kwargs.pop("devcenter_endpoint")
        client = self.create_client(endpoint=endpoint)
        assert client is not None
