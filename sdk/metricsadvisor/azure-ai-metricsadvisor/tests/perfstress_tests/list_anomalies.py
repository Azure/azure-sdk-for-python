# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure_devtools.perfstress_tests import PerfStressTest

from azure.ai.metricsadvisor import MetricsAdvisorClient as SyncClient, MetricsAdvisorKeyCredential
from azure.ai.metricsadvisor.aio import MetricsAdvisorClient as AsyncClient


class ListAnomaliesTest(PerfStressTest):
    def __init__(self, arguments):
        super().__init__(arguments)
        service_endpoint = os.getenv("AZURE_METRICS_ADVISOR_ENDPOINT")
        subscription_key = os.getenv("AZURE_METRICS_ADVISOR_SUBSCRIPTION_KEY")
        api_key = os.getenv("AZURE_METRICS_ADVISOR_API_KEY")
        self.anomaly_alert_configuration_id = os.getenv("AZURE_METRICS_ADVISOR_ANOMALY_ALERT_CONFIGURATION_ID")
        self.alert_id = os.getenv("AZURE_METRICS_ADVISOR_ALERT_ID")
        self.service_client = SyncClient(service_endpoint, MetricsAdvisorKeyCredential(subscription_key, api_key))
        self.async_service_client = AsyncClient(service_endpoint, MetricsAdvisorKeyCredential(subscription_key, api_key))

    async def global_setup(self):
        await super().global_setup()

    async def close(self):
        await self.async_service_client.close()
        await super().close()

    def run_sync(self):
        ret = list(self.service_client.list_anomalies(
            alert_configuration_id=self.anomaly_alert_configuration_id,
            alert_id=self.alert_id,
        ))

    async def run_async(self):
        results = self.async_service_client.list_anomalies(
            alert_configuration_id=self.anomaly_alert_configuration_id,
            alert_id=self.alert_id,
        )
        tolist = []
        async for result in results:
            tolist.append(result)
