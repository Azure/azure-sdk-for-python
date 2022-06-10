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
from devtools_testutils import recorded_by_proxy
from azure.ai.metricsadvisor import MetricsAdvisorClient
from base_testcase import TestMetricsAdvisorClientBase, MetricsAdvisorClientPreparer, CREDENTIALS, API_KEY, ids
MetricsAdvisorPreparer = functools.partial(MetricsAdvisorClientPreparer, MetricsAdvisorClient)


class TestMetricsAdvisorClient(TestMetricsAdvisorClientBase):

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_list_anomalies_for_detection_configuration(self, client, **kwargs):
        results = list(client.list_anomalies(
            detection_configuration_id=self.anomaly_detection_configuration_id,
            start_time=datetime.datetime(2021, 1, 1),
            end_time=datetime.datetime(2021, 9, 9),
        ))
        assert len(results) > 0

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_list_anomaly_dimension_values(self, client, **kwargs):
        results = list(client.list_anomaly_dimension_values(
            detection_configuration_id=self.anomaly_detection_configuration_id,
            dimension_name="region",
            start_time=datetime.datetime(2021, 1, 1),
            end_time=datetime.datetime(2021, 9, 9),
        ))
        assert len(results) > 0

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_list_incidents_for_detection_configuration(self, client, **kwargs):
        results = list(client.list_incidents(
            detection_configuration_id=self.anomaly_detection_configuration_id,
            start_time=datetime.datetime(2021, 1, 1),
            end_time=datetime.datetime(2021, 9, 9),
        ))
        assert len(results) > 0

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_list_metric_dimension_values(self, **kwargs):
        client = kwargs.pop("client")
        results = list(client.list_metric_dimension_values(
            metric_id=self.metric_id,
            dimension_name="region",
        ))
        assert len(results) > 0

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_list_incident_root_cause(self, client, **kwargs):
        results = list(client.list_incident_root_causes(
            detection_configuration_id=self.anomaly_detection_configuration_id,
            incident_id=self.incident_id,
        ))
        assert len(results) > 0

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_list_metric_enriched_series_data(self, client, **kwargs):
        series_identity = {"region": "Los Angeles"}
        results = list(client.list_metric_enriched_series_data(
            detection_configuration_id=self.anomaly_detection_configuration_id,
            start_time=datetime.datetime(2021, 1, 1),
            end_time=datetime.datetime(2021, 9, 9),
            series=[series_identity]
        ))
        assert len(results) > 0

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_list_metric_enrichment_status(self, client, **kwargs):
        results = list(client.list_metric_enrichment_status(
            metric_id=self.metric_id,
            start_time=datetime.datetime(2021, 1, 1),
            end_time=datetime.datetime(2021, 9, 9),
        ))
        assert len(results) > 0

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_list_alerts(self, client, **kwargs):
        results = list(client.list_alerts(
            alert_configuration_id=self.anomaly_alert_configuration_id,
            start_time=datetime.datetime(2021, 1, 1),
            end_time=datetime.datetime(2021, 9, 9),
            time_mode="AnomalyTime",
        ))
        assert len(list(results)) > 0

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_list_metrics_series_data(self, client, **kwargs):
        results = list(client.list_metric_series_data(
            metric_id=self.metric_id,
            start_time=datetime.datetime(2021, 1, 1),
            end_time=datetime.datetime(2021, 9, 9),
            series_keys=[
                {"region": "Los Angeles", "category": "Homemade"}
            ]
        ))
        assert len(results) > 0

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_list_metric_series_definitions(self, client, **kwargs):
        results = list(client.list_metric_series_definitions(
            metric_id=self.metric_id,
            active_since=datetime.datetime(2021, 1, 1),
        ))
        assert len(results) > 0

    @pytest.mark.parametrize("credential", API_KEY, ids=ids)  # only using API key for now since service issue with AAD
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_add_anomaly_feedback(self, client, **kwargs):
        anomaly_feedback = AnomalyFeedback(metric_id=self.metric_id,
                                           dimension_key={"category": "Shoes Handbags & Sunglasses"},
                                           start_time=datetime.datetime(2021, 8, 5),
                                           end_time=datetime.datetime(2021, 9, 9),
                                           value="NotAnomaly")
        client.add_feedback(anomaly_feedback)

    @pytest.mark.parametrize("credential", API_KEY, ids=ids)  # only using API key for now since service issue with AAD
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_add_change_point_feedback(self, client, **kwargs):
        change_point_feedback = ChangePointFeedback(metric_id=self.metric_id,
                                                    dimension_key={"category": "Shoes Handbags & Sunglasses"},
                                                    start_time=datetime.datetime(2021, 8, 5),
                                                    end_time=datetime.datetime(2021, 9, 9),
                                                    value="NotChangePoint")
        client.add_feedback(change_point_feedback)

    @pytest.mark.parametrize("credential", API_KEY, ids=ids)  # only using API key for now since service issue with AAD
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_add_comment_feedback(self, client, **kwargs):
        comment_feedback = CommentFeedback(metric_id=self.metric_id,
                                           dimension_key={"category": "Shoes Handbags & Sunglasses"},
                                           start_time=datetime.datetime(2021, 8, 5),
                                           end_time=datetime.datetime(2021, 9, 9),
                                           value="comment")
        client.add_feedback(comment_feedback)

    @pytest.mark.parametrize("credential", API_KEY, ids=ids)  # only using API key for now since service issue with AAD
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_add_period_feedback(self, client, **kwargs):
        period_feedback = PeriodFeedback(metric_id=self.metric_id,
                                         dimension_key={"category": "Shoes Handbags & Sunglasses"},
                                         start_time=datetime.datetime(2021, 8, 5),
                                         end_time=datetime.datetime(2021, 9, 9),
                                         period_type="AssignValue",
                                         value=2)
        client.add_feedback(period_feedback)

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_list_feedback(self, client, **kwargs):
        results = list(client.list_feedback(
            metric_id=self.metric_id,
            start_time=datetime.datetime(2021, 9, 1),
            end_time=datetime.datetime(2021, 9, 9),
            time_mode="FeedbackCreatedTime"
        ))
        assert len(results) > 0

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_get_feedback(self, client, **kwargs):
        result = client.get_feedback(feedback_id=self.feedback_id)
        assert result

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_list_anomalies_for_alert(self, client, **kwargs):
        result = list(client.list_anomalies(
            alert_configuration_id=self.anomaly_alert_configuration_id,
            alert_id=self.alert_id,
        ))
        assert len(result) > 0

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_list_incidents_for_alert(self, client, **kwargs):
        results = list(client.list_incidents(
            alert_configuration_id=self.anomaly_alert_configuration_id,
            alert_id=self.alert_id,
        ))
        assert len(results) > 0

    def test_models_removed(self):
        with pytest.raises(ImportError):
            from azure.ai.metricsadvisor.models import AlertResultList
        with pytest.raises(ImportError):
            from azure.ai.metricsadvisor.models import AnomalyAlertingConfigurationList
        with pytest.raises(ImportError):
            from azure.ai.metricsadvisor.models import MetricDimensionList
        with pytest.raises(ImportError):
            from azure.ai.metricsadvisor.models import MetricFeedbackList
        with pytest.raises(ImportError):
            from azure.ai.metricsadvisor.models import MetricSeriesList
        with pytest.raises(ImportError):
            from azure.ai.metricsadvisor.models import RootCauseList
        with pytest.raises(ImportError):
            from azure.ai.metricsadvisor.models import SeriesResultList
