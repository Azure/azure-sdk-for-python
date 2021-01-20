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
from azure.synapse.monitoring.aio import MonitoringClient
from azure.identity.aio import DefaultAzureCredential

class MockCredential():
    async def get_token(self, *scopes, **kwargs):
        from azure.core.credentials import AccessToken
        return AccessToken("fake-token", 0)

class TestSynapseMonitoringClientAsync(AzureTestCase):

    def __init__(self, method_name):
        super(TestSynapseMonitoringClientAsync, self).__init__(method_name)
        self.vcr.match_on = ["path", "method", "query"]
        if self.is_live:
            service_endpoint = self.get_settings_value("SYNAPSE_ENDPOINT")
            credential = DefaultAzureCredential()
        else:
            service_endpoint = "https://endpointname.dev.azuresynapse.net"
            credential = MockCredential()
        self.client = MonitoringClient(credential=credential,
                         endpoint=service_endpoint)

    @AzureTestCase.await_prepared_test
    async def test_monitoring_spark_job(self):
        async with self.client:
            spark_jobs = (await self.client.monitoring.get_spark_job_list()).spark_jobs
            job_count = 0
            for job in spark_jobs:
                job_count = job_count + 1
            assert job_count > 0

    @AzureTestCase.await_prepared_test
    async def test_monitoring_sql_job(self):
        async with self.client:
            job = await self.client.monitoring.get_sql_job_query_string()
            assert job.query.startswith('select *')
