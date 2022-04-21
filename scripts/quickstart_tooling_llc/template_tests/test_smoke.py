# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import {{ test_prefix.capitalize() }}Test, {{ test_prefix.capitalize() }}PowerShellPreparer

class {{ test_prefix.capitalize() }}SmokeTest({{ test_prefix.capitalize() }}Test):


    @{{ test_prefix.capitalize() }}PowerShellPreparer()
    def test_smoke(self, {{ test_prefix }}_endpoint):
        client = self.create_client(endpoint={{ test_prefix }}_endpoint)
        # test your code here, for example:
        # result = client.xxx.xx(...)
        # assert result is not None
