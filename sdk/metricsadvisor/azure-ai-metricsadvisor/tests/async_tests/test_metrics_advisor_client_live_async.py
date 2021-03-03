# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio
import functools
from azure.core import MatchConditions
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer
import pytest
import datetime
from devtools_testutils import AzureTestCase
from azure.ai.metricsadvisor.models import (
    AnomalyFeedback,
    ChangePointFeedback,
    CommentFeedback,
    PeriodFeedback,
)
import os
from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function
from base_testcase_async import TestMetricsAdvisorClientBaseAsync

class TestMetricsAdvisorClientAsync(TestMetricsAdvisorClientBaseAsync):

    @AzureTestCase.await_prepared_test
    async def test_list_anomalies_for_detection_configuration(self):
        async with self.client:
            results = self.client.list_anomalies(
                detection_configuration_id=self.anomaly_detection_configuration_id,
                start_time=datetime.datetime(2020, 1, 1),
                end_time=datetime.datetime(2020, 10, 21),
            )
            tolist = []
            async for result in results:
                tolist.append(result)
            assert len(tolist) > 0

    @AzureTestCase.await_prepared_test
    async def test_list_anomaly_dimension_values(self):
        async with self.client:
            results = self.client.list_anomaly_dimension_values(
                detection_configuration_id=self.anomaly_detection_configuration_id,
                dimension_name=self.dimension_name,
                start_time=datetime.datetime(2020, 1, 1),
                end_time=datetime.datetime(2020, 10, 21),
            )
            tolist = []
            async for result in results:
                tolist.append(result)
            assert len(tolist) > 0

    @AzureTestCase.await_prepared_test
    async def test_list_incidents_for_detection_configuration(self):
        async with self.client:
            results = self.client.list_incidents(
                detection_configuration_id=self.anomaly_detection_configuration_id,
                start_time=datetime.datetime(2020, 1, 1),
                end_time=datetime.datetime(2020, 10, 21),
            )
            tolist = []
            async for result in results:
                tolist.append(result)
            assert len(tolist) > 0

    @AzureTestCase.await_prepared_test
    async def test_list_metric_dimension_values(self):
        async with self.client:
            results = self.client.list_metric_dimension_values(
                metric_id=self.metric_id,
                dimension_name=self.dimension_name,
            )
            tolist = []
            async for result in results:
                tolist.append(result)
            assert len(tolist) > 0

    @AzureTestCase.await_prepared_test
    async def test_list_incident_root_cause(self):
        async with self.client:
            results = self.client.list_incident_root_causes(
                detection_configuration_id=self.anomaly_detection_configuration_id,
                incident_id=self.incident_id,
            )
            tolist = []
            async for result in results:
                tolist.append(result)
            assert len(tolist) > 0

    @AzureTestCase.await_prepared_test
    async def test_list_metric_enriched_series_data(self):
        async with self.client:
            series_identity = {"city": "Los Angeles"}
            results = self.client.list_metric_enriched_series_data(
                detection_configuration_id=self.anomaly_detection_configuration_id,
                start_time=datetime.datetime(2020, 1, 1),
                end_time=datetime.datetime(2020, 10, 21),
                series=[series_identity]
            )
            tolist = []
            async for result in results:
                tolist.append(result)
            assert len(tolist) > 0

    @AzureTestCase.await_prepared_test
    async def test_list_metric_enrichment_status(self):
        async with self.client:
            results = self.client.list_metric_enrichment_status(
                metric_id=self.metric_id,
                start_time=datetime.datetime(2020, 1, 1),
                end_time=datetime.datetime(2020, 10, 21),
            )
            tolist = []
            async for result in results:
                tolist.append(result)
            assert len(tolist) > 0

    @AzureTestCase.await_prepared_test
    async def test_list_alerts(self):
        async with self.client:
            results = self.client.list_alerts(
                alert_configuration_id=self.anomaly_alert_configuration_id,
                start_time=datetime.datetime(2020, 1, 1),
                end_time=datetime.datetime(2020, 10, 21),
                time_mode="AnomalyTime",
            )
            tolist = []
            async for result in results:
                tolist.append(result)
            assert len(tolist) > 0

    @AzureTestCase.await_prepared_test
    async def test_list_metrics_series_data(self):
        async with self.client:
            results = self.client.list_metrics_series_data(
                metric_id=self.metric_id,
                start_time=datetime.datetime(2020, 1, 1),
                end_time=datetime.datetime(2020, 10, 21),
                series_to_filter=[
                    {"city": "Los Angeles", "category": "Homemade"}
                ]
            )
            tolist = []
            async for result in results:
                tolist.append(result)
            assert len(tolist) > 0

    @AzureTestCase.await_prepared_test
    async def test_list_metric_series_definitions(self):
        async with self.client:
            results = self.client.list_metric_series_definitions(
                metric_id=self.metric_id,
                active_since=datetime.datetime(2020, 1, 1),
            )
            tolist = []
            async for result in results:
                tolist.append(result)
            assert len(tolist) > 0

    @AzureTestCase.await_prepared_test
    async def test_add_anomaly_feedback(self):
        anomaly_feedback = AnomalyFeedback(metric_id=self.metric_id,
                                           dimension_key={"city": "Los Angeles"},
                                           start_time=datetime.datetime(2020, 8, 5),
                                           end_time=datetime.datetime(2020, 10, 21),
                                           value="NotAnomaly")
        async with self.client:
            await self.client.add_feedback(anomaly_feedback)

    @AzureTestCase.await_prepared_test
    async def test_add_change_point_feedback(self):
        change_point_feedback = ChangePointFeedback(metric_id=self.metric_id,
                                                    dimension_key={"city": "Los Angeles"},
                                                    start_time=datetime.datetime(2020, 8, 5),
                                                    end_time=datetime.datetime(2020, 10, 21),
                                                    value="NotChangePoint")
        async with self.client:
            await self.client.add_feedback(change_point_feedback)

    @AzureTestCase.await_prepared_test
    async def test_add_comment_feedback(self):
        comment_feedback = CommentFeedback(metric_id=self.metric_id,
                                           dimension_key={"city": "Los Angeles"},
                                           start_time=datetime.datetime(2020, 8, 5),
                                           end_time=datetime.datetime(2020, 10, 21),
                                           value="comment")
        async with self.client:
            await self.client.add_feedback(comment_feedback)

    @AzureTestCase.await_prepared_test
    async def test_add_period_feedback(self):
        period_feedback = PeriodFeedback(metric_id=self.metric_id,
                                         dimension_key={"city": "Los Angeles"},
                                         start_time=datetime.datetime(2020, 8, 5),
                                         end_time=datetime.datetime(2020, 10, 21),
                                         period_type="AssignValue",
                                         value=2)
        async with self.client:
            await self.client.add_feedback(period_feedback)

    @AzureTestCase.await_prepared_test
    async def test_list_feedback(self):
        async with self.client:
            results = self.client.list_feedback(metric_id=self.metric_id)
            tolist = []
            async for result in results:
                tolist.append(result)
            assert len(tolist) > 0

    @AzureTestCase.await_prepared_test
    async def test_get_feedback(self):
        async with self.client:
            result = await self.client.get_feedback(feedback_id=self.feedback_id)
            assert result

    @AzureTestCase.await_prepared_test
    async def test_list_anomalies_for_alert(self):
        async with self.client:
            results = self.client.list_anomalies(
                alert_configuration_id=self.anomaly_alert_configuration_id,
                alert_id=self.alert_id,
            )
            tolist = []
            async for result in results:
                tolist.append(result)
            assert len(tolist) > 0

    @AzureTestCase.await_prepared_test
    async def test_list_incidents_for_alert(self):
        async with self.client:
            results = self.client.list_incidents(
                alert_configuration_id=self.anomaly_alert_configuration_id,
                alert_id=self.alert_id,
            )
            tolist = []
            async for result in results:
                tolist.append(result)
            assert len(tolist) > 0
