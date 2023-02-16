# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import EasmTest, EasmParameterProvider
from devtools_testutils import recorded_by_proxy

class TestEasmReportClient(EasmTest):
    metric = 'savedfilter_metric_40610'
    time_format = '%Y-%m-%dT%H:%M:%S.%f%z'

    @EasmParameterProvider()
    @recorded_by_proxy
    def test_report_billable(self, easm_endpoint, easm_resource_group, easm_subscription_id, easm_workspace):
        client = self.create_client(endpoint=easm_endpoint, resource_group=easm_resource_group, subscription_id=easm_subscription_id, workspace=easm_workspace)
        report = client.reports.billable()
        assert report['assetSummaries']

    @EasmParameterProvider()
    @recorded_by_proxy
    def test_report_snapshot(self, easm_endpoint, easm_resource_group, easm_subscription_id, easm_workspace):
        client = self.create_client(endpoint=easm_endpoint, resource_group=easm_resource_group, subscription_id=easm_subscription_id, workspace=easm_workspace)
        snapshot = client.reports.snapshot(body={'metric': self.metric})
        assert snapshot['displayName']
        assert snapshot['metric'] == self.metric
        assert snapshot['description']
        assert snapshot['assets']
        self.check_timestamp_format(self.time_format, snapshot['updatedAt'])

    @EasmParameterProvider()
    @recorded_by_proxy
    def test_report_summarize(self, easm_endpoint, easm_resource_group, easm_subscription_id, easm_workspace):
        client = self.create_client(endpoint=easm_endpoint, resource_group=easm_resource_group, subscription_id=easm_subscription_id, workspace=easm_workspace)
        summary = client.reports.summary(body={'metrics': [self.metric]})
        assert summary['assetSummaries']
