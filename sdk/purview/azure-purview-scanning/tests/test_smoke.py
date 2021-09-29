# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import PurviewScanningTest, PurviewScanningPowerShellPreparer
from _util import PurviewScanningRecordingProcessor

class PurviewScanningSmokeTest(PurviewScanningTest):

    @PurviewScanningPowerShellPreparer()
    def test_basic_smoke_test(self, purviewscanning_endpoint):
        self.recording_processors.append(PurviewScanningRecordingProcessor())
        client = self.create_client(endpoint=purviewscanning_endpoint)
        response = client.data_sources.list_all()
        result = [item for item in response]
        assert len(result) >= 1
