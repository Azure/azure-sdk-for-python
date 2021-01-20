# coding=utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from azure.core.exceptions import ResourceNotFoundError

from devtools_testutils import AzureTestCase
from azure_devtools.scenario_tests import (
    ReplayableTest,
    create_random_name
)
from azure.synapse.monitoring import MonitoringClient
from azure.identity import DefaultAzureCredential

class TestSynapseMonitoringClient(AzureTestCase):

    def __init__(self, method_name):
        super(TestSynapseMonitoringClient, self).__init__(method_name)
        self.vcr.match_on = ["path", "method", "query"]
        if self.is_live:
            service_endpoint = self.get_settings_value("SYNAPSE_ENDPOINT")
        else:
            service_endpoint = "https://endpointname.dev.azuresynapse.net"
        self.client = MonitoringClient(credential=DefaultAzureCredential(),
                         endpoint=service_endpoint)

    def test_monitoring_spark_job(self):
        spark_jobs = self.client.monitoring.get_spark_job_list().spark_jobs
        job_count = 0
        for job in spark_jobs:
            job_count = job_count + 1
        assert job_count > 0

    def test_monitoring_sql_job(self):
        job = self.client.monitoring.get_sql_job_query_string()
        assert job.query.startswith('select *')
