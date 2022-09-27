# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import AnomalydetectorTest, AnomalydetectorPowerShellPreparer

class AnomalydetectorSmokeTest(AnomalydetectorTest):


    @AnomalydetectorPowerShellPreparer()
    def test_smoke(self, anomalydetector_endpoint):
        client = self.create_client(endpoint=anomalydetector_endpoint)
        # test your code here, for example:
        # result = client.xxx.xx(...)
        # assert result is not None
