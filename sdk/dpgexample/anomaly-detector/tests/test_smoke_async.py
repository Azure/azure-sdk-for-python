# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import AnomalydetectorPowerShellPreparer
from testcase_async import AnomalydetectorAsyncTest


class AnomalydetectorSmokeAsyncTest(AnomalydetectorAsyncTest):

    @AnomalydetectorPowerShellPreparer()
    async def test_smoke_async(self, anomalydetector_endpoint):
        client = self.create_client(endpoint=anomalydetector_endpoint)
        # test your code here, for example:
        # result = await client.xxx.xx(...)
        # assert result is not None
