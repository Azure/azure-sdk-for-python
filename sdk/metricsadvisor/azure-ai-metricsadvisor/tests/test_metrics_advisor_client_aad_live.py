# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core import MatchConditions
from devtools_testutils import AzureMgmtTestCase
from azure.core.exceptions import (
    ResourceModifiedError,
    ResourceNotFoundError,
    ResourceExistsError,
    AzureError,
)
from azure.ai.metricsadvisor.models import (
    AnomalyFeedback,
    ChangePointFeedback,
    CommentFeedback,
    PeriodFeedback,
)
import pytest
import datetime
import os
from base_testcase_aad import TestMetricsAdvisorClientBase

class TestMetricsAdvisorClient(TestMetricsAdvisorClientBase):
    def test_list_anomalies_for_detection_configuration(self):
        results = list(self.client.list_anomalies(
            detection_configuration_id=self.anomaly_detection_configuration_id,
            start_time=datetime.datetime(2020, 1, 1),
            end_time=datetime.datetime(2020, 10, 21),
        ))
        assert len(results) > 0

    def test_list_anomaly_dimension_values(self):
        results = list(self.client.list_anomaly_dimension_values(
            detection_configuration_id=self.anomaly_detection_configuration_id,
            dimension_name=self.dimension_name,
            start_time=datetime.datetime(2020, 1, 1),
            end_time=datetime.datetime(2020, 10, 21),
        ))
        assert len(results) > 0

    def test_list_incidents_for_detection_configuration(self):
        results = list(self.client.list_incidents(
            detection_configuration_id=self.anomaly_detection_configuration_id,
            start_time=datetime.datetime(2020, 1, 1),
            end_time=datetime.datetime(2020, 10, 21),
        ))
        assert len(results) > 0

    def test_list_metric_dimension_values(self):
        results = list(self.client.list_metric_dimension_values(
            metric_id=self.metric_id,
            dimension_name=self.dimension_name,
        ))
        assert len(results) > 0

    def test_list_incident_root_cause(self):
        results = list(self.client.list_incident_root_causes(
            detection_configuration_id=self.anomaly_detection_configuration_id,
            incident_id=self.incident_id,
        ))
        assert len(results) > 0

    def test_list_metric_enriched_series_data(self):
        series_identity = {"city": "Los Angeles"}
        results = list(self.client.list_metric_enriched_series_data(
            detection_configuration_id=self.anomaly_detection_configuration_id,
            start_time=datetime.datetime(2020, 1, 1),
            end_time=datetime.datetime(2020, 10, 21),
            series=[series_identity]
        ))
        assert len(results) > 0

    def test_list_metric_enrichment_status(self):
        results = list(self.client.list_metric_enrichment_status(
            metric_id=self.metric_id,
            start_time=datetime.datetime(2020, 1, 1),
            end_time=datetime.datetime(2020, 10, 21),
        ))
        assert len(results) > 0

    def test_list_alerts(self):
        results = list(self.client.list_alerts(
            alert_configuration_id=self.anomaly_alert_configuration_id,
            start_time=datetime.datetime(2020, 1, 1),
            end_time=datetime.datetime(2020, 10, 21),
            time_mode="AnomalyTime",
        ))
        assert len(list(results)) > 0

    def test_list_metrics_series_data(self):
        results = list(self.client.list_metrics_series_data(
            metric_id=self.metric_id,
            start_time=datetime.datetime(2020, 1, 1),
            end_time=datetime.datetime(2020, 10, 21),
            series_to_filter=[
                {"city": "Los Angeles", "category": "Homemade"}
            ]
        ))
        assert len(results) > 0

    def test_list_metric_series_definitions(self):
        results = list(self.client.list_metric_series_definitions(
            metric_id=self.metric_id,
            active_since=datetime.datetime(2020, 1, 1),
        ))
        assert len(results) > 0

    def test_add_anomaly_feedback(self):
        anomaly_feedback = AnomalyFeedback(metric_id=self.metric_id,
                                           dimension_key={"city": "Los Angeles"},
                                           start_time=datetime.datetime(2020, 8, 5),
                                           end_time=datetime.datetime(2020, 10, 21),
                                           value="NotAnomaly")
        self.client.add_feedback(anomaly_feedback)

    def test_add_change_point_feedback(self):
        change_point_feedback = ChangePointFeedback(metric_id=self.metric_id,
                                                    dimension_key={"city": "Los Angeles"},
                                                    start_time=datetime.datetime(2020, 8, 5),
                                                    end_time=datetime.datetime(2020, 10, 21),
                                                    value="NotChangePoint")
        self.client.add_feedback(change_point_feedback)

    def test_add_comment_feedback(self):
        comment_feedback = CommentFeedback(metric_id=self.metric_id,
                                           dimension_key={"city": "Los Angeles"},
                                           start_time=datetime.datetime(2020, 8, 5),
                                           end_time=datetime.datetime(2020, 10, 21),
                                           value="comment")
        self.client.add_feedback(comment_feedback)

    def test_add_period_feedback(self):
        period_feedback = PeriodFeedback(metric_id=self.metric_id,
                                         dimension_key={"city": "Los Angeles"},
                                         start_time=datetime.datetime(2020, 8, 5),
                                         end_time=datetime.datetime(2020, 10, 21),
                                         period_type="AssignValue",
                                         value=2)
        self.client.add_feedback(period_feedback)

    def test_list_feedback(self):
        results = list(self.client.list_feedback(metric_id=self.metric_id))
        assert len(results) > 0

    def test_get_feedback(self):
        result = self.client.get_feedback(feedback_id=self.feedback_id)
        assert result

    def test_list_anomalies_for_alert(self):
        result = list(self.client.list_anomalies(
            alert_configuration_id=self.anomaly_alert_configuration_id,
            alert_id=self.alert_id,
        ))
        assert len(result) > 0

    def test_list_incidents_for_alert(self):
        results = list(self.client.list_incidents(
            alert_configuration_id=self.anomaly_alert_configuration_id,
            alert_id=self.alert_id,
        ))
        assert len(results) > 0
