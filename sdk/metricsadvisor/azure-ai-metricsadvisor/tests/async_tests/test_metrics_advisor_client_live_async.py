# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


import pytest
import datetime
import os
import functools
from azure.ai.metricsadvisor.models import (
    AnomalyFeedback,
    ChangePointFeedback,
    CommentFeedback,
    PeriodFeedback,
)
from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async
from azure.ai.metricsadvisor.aio import MetricsAdvisorClient
from base_testcase_async import TestMetricsAdvisorClientBase, MetricsAdvisorClientPreparer, CREDENTIALS, ids, API_KEY
MetricsAdvisorPreparer = functools.partial(MetricsAdvisorClientPreparer, MetricsAdvisorClient)


class TestMetricsAdvisorClient(TestMetricsAdvisorClientBase):

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy_async
    async def test_list_anomalies_for_detection_configuration(self, client, **kwargs):
        async with client:
            results = client.list_anomalies(
                detection_configuration_id=self.anomaly_detection_configuration_id,
                start_time=datetime.datetime(2021, 1, 1),
                end_time=datetime.datetime(2021, 9, 9),
            )
            tolist = []
            async for result in results:
                tolist.append(result)
            assert len(tolist) > 0

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy_async
    async def test_list_anomaly_dimension_values(self, client, **kwargs):
        async with client:
            results = client.list_anomaly_dimension_values(
                detection_configuration_id=self.anomaly_detection_configuration_id,
                dimension_name="region",
                start_time=datetime.datetime(2021, 1, 1),
                end_time=datetime.datetime(2021, 9, 9),
            )
            tolist = []
            async for result in results:
                tolist.append(result)
            assert len(tolist) > 0

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy_async
    async def test_list_incidents_for_detection_configuration(self, client, **kwargs):
        async with client:
            results = client.list_incidents(
                detection_configuration_id=self.anomaly_detection_configuration_id,
                start_time=datetime.datetime(2021, 1, 1),
                end_time=datetime.datetime(2021, 9, 9),
            )
            tolist = []
            async for result in results:
                tolist.append(result)
            assert len(tolist) > 0

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy_async
    async def test_list_metric_dimension_values(self, client, **kwargs):
        async with client:
            results = client.list_metric_dimension_values(
                metric_id=self.metric_id,
                dimension_name="region",
            )
            tolist = []
            async for result in results:
                tolist.append(result)
            assert len(tolist) > 0

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy_async
    async def test_list_incident_root_cause(self, client, **kwargs):
        async with client:
            results = client.list_incident_root_causes(
                detection_configuration_id=self.anomaly_detection_configuration_id,
                incident_id=self.incident_id,
            )
            tolist = []
            async for result in results:
                tolist.append(result)
            assert len(tolist) > 0

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy_async
    async def test_list_metric_enriched_series_data(self, client, **kwargs):
        async with client:
            series_identity = {"region": "Los Angeles"}
            results = client.list_metric_enriched_series_data(
                detection_configuration_id=self.anomaly_detection_configuration_id,
                start_time=datetime.datetime(2021, 1, 1),
                end_time=datetime.datetime(2021, 9, 9),
                series=[series_identity]
            )
            tolist = []
            async for result in results:
                tolist.append(result)
            assert len(tolist) > 0

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy_async
    async def test_list_metric_enrichment_status(self, client, **kwargs):
        async with client:
            results = client.list_metric_enrichment_status(
                metric_id=self.metric_id,
                start_time=datetime.datetime(2021, 1, 1),
                end_time=datetime.datetime(2021, 9, 9),
            )
            tolist = []
            async for result in results:
                tolist.append(result)
            assert len(tolist) > 0

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy_async
    async def test_list_alerts(self, client, **kwargs):
        async with client:
            results = client.list_alerts(
                alert_configuration_id=self.anomaly_alert_configuration_id,
                start_time=datetime.datetime(2021, 1, 1),
                end_time=datetime.datetime(2021, 9, 9),
                time_mode="AnomalyTime",
            )
            tolist = []
            async for result in results:
                tolist.append(result)
            assert len(tolist) > 0

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy_async
    async def test_list_metrics_series_data(self, client, **kwargs):
        async with client:
            results = client.list_metric_series_data(
                metric_id=self.metric_id,
                start_time=datetime.datetime(2021, 1, 1),
                end_time=datetime.datetime(2021, 9, 9),
                series_keys=[
                    {"region": "Los Angeles", "category": "Homemade"}
                ]
            )
            tolist = []
            async for result in results:
                tolist.append(result)
            assert len(tolist) > 0

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy_async
    async def test_list_metric_series_definitions(self, client, **kwargs):
        async with client:
            results = client.list_metric_series_definitions(
                metric_id=self.metric_id,
                active_since=datetime.datetime(2021, 1, 1),
            )
            tolist = []
            async for result in results:
                tolist.append(result)
            assert len(tolist) > 0

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("credential", API_KEY, ids=ids)  # only using API key for now since service issue with AAD
    @MetricsAdvisorPreparer()
    @recorded_by_proxy_async
    async def test_add_anomaly_feedback(self, client, **kwargs):
        anomaly_feedback = AnomalyFeedback(metric_id=self.metric_id,
                                           dimension_key={"category": "Shoes Handbags & Sunglasses"},
                                           start_time=datetime.datetime(2021, 8, 5),
                                           end_time=datetime.datetime(2021, 9, 9),
                                           value="NotAnomaly")
        async with client:
            await client.add_feedback(anomaly_feedback)

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("credential", API_KEY, ids=ids)  # only using API key for now since service issue with AAD
    @MetricsAdvisorPreparer()
    @recorded_by_proxy_async
    async def test_add_change_point_feedback(self, client, **kwargs):
        change_point_feedback = ChangePointFeedback(metric_id=self.metric_id,
                                                    dimension_key={"category": "Shoes Handbags & Sunglasses"},
                                                    start_time=datetime.datetime(2021, 8, 5),
                                                    end_time=datetime.datetime(2021, 9, 9),
                                                    value="NotChangePoint")
        async with client:
            await client.add_feedback(change_point_feedback)

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("credential", API_KEY, ids=ids)  # only using API key for now since service issue with AAD
    @MetricsAdvisorPreparer()
    @recorded_by_proxy_async
    async def test_add_comment_feedback(self, client, **kwargs):
        comment_feedback = CommentFeedback(metric_id=self.metric_id,
                                           dimension_key={"category": "Shoes Handbags & Sunglasses"},
                                           start_time=datetime.datetime(2021, 8, 5),
                                           end_time=datetime.datetime(2021, 9, 9),
                                           value="comment")
        async with client:
            await client.add_feedback(comment_feedback)

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("credential", API_KEY, ids=ids)  # only using API key for now since service issue with AAD
    @MetricsAdvisorPreparer()
    @recorded_by_proxy_async
    async def test_add_period_feedback(self, client, **kwargs):
        period_feedback = PeriodFeedback(metric_id=self.metric_id,
                                         dimension_key={"category": "Shoes Handbags & Sunglasses"},
                                         start_time=datetime.datetime(2021, 8, 5),
                                         end_time=datetime.datetime(2021, 9, 9),
                                         period_type="AssignValue",
                                         value=2)
        async with client:
            await client.add_feedback(period_feedback)

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy_async
    async def test_list_feedback(self, client, **kwargs):
        async with client:
            results = client.list_feedback(
                metric_id=self.metric_id,
                start_time=datetime.datetime(2021, 9, 1),
                end_time=datetime.datetime(2021, 9, 9),
                time_mode="FeedbackCreatedTime"
            )
            tolist = []
            async for result in results:
                tolist.append(result)
            assert len(tolist) > 0

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy_async
    async def test_get_feedback(self, client, **kwargs):
        async with client:
            result = await client.get_feedback(feedback_id=self.feedback_id)
            assert result


    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy_async
    async def test_list_anomalies_for_alert(self, client, **kwargs):
        async with client:
            results = client.list_anomalies(
                alert_configuration_id=self.anomaly_alert_configuration_id,
                alert_id=self.alert_id,
            )
            tolist = []
            async for result in results:
                tolist.append(result)
            assert len(tolist) > 0

    @AzureRecordedTestCase.await_prepared_test
    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy_async
    async def test_list_incidents_for_alert(self, client, **kwargs):
        async with client:
            results = client.list_incidents(
                alert_configuration_id=self.anomaly_alert_configuration_id,
                alert_id=self.alert_id,
            )
            tolist = []
            async for result in results:
                tolist.append(result)
            assert len(tolist) > 0