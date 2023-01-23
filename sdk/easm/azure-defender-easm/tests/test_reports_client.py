# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import EasmTest, EasmPowerShellPreparer

class EasmReportsTest(EasmTest):
    metric = 'savedfilter_metric_40610'
    time_format = '%Y-%m-%dT%H:%M:%S.%f%z'

    @EasmPowerShellPreparer()
    def test_report_billable(self, easm_endpoint):
        client = self.create_client(endpoint=easm_endpoint)
        report = client.reports.billable()
        assert report['assetSummaries']

    @EasmPowerShellPreparer()
    def test_report_snapshot(self, easm_endpoint):
        client = self.create_client(endpoint=easm_endpoint)
        snapshot = client.reports.snapshot(body={'metric': self.metric})
        assert snapshot['displayName']
        assert snapshot['metric'] == self.metric
        assert snapshot['description']
        assert snapshot['assets']
        self.check_timestamp_format(self.time_format, snapshot['updatedAt'])

    @EasmPowerShellPreparer()
    def test_report_summarize(self, easm_endpoint):
        client = self.create_client(endpoint=easm_endpoint)
        summary = client.reports.summarize(body={'metrics': [self.metric]})
        assert summary['assetSummaries']
