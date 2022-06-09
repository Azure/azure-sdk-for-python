# coding=utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import uuid
import functools
from azure.core.exceptions import ResourceNotFoundError
from devtools_testutils import recorded_by_proxy
from azure.ai.metricsadvisor import MetricsAdvisorAdministrationClient
from azure.ai.metricsadvisor.models import (
    MetricAlertConfiguration,
    MetricAnomalyAlertScope,
    MetricAnomalyAlertConditions,
    MetricBoundaryCondition,
    TopNGroupScope,
    SeverityCondition,
    MetricAnomalyAlertSnoozeCondition,
)
from base_testcase import TestMetricsAdvisorClientBase, MetricsAdvisorClientPreparer, CREDENTIALS, ids
MetricsAdvisorPreparer = functools.partial(MetricsAdvisorClientPreparer, MetricsAdvisorAdministrationClient)


class TestMetricsAdvisorAdministrationClient(TestMetricsAdvisorClientBase):

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(data_feed=True, detection_config=True)
    @recorded_by_proxy
    def test_create_alert_config_top_n_alert_direction_both(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables")
        alert_config_name = self.create_random_name("alertconfig")
        if self.is_live:
            variables["alert_config_name"] = alert_config_name

        try:
            alert_config = client.create_alert_configuration(
                name=variables["alert_config_name"],
                metric_alert_configurations=[
                    MetricAlertConfiguration(
                        detection_configuration_id=variables["detection_config_id"],
                        alert_scope=MetricAnomalyAlertScope(
                            scope_type="TopN",
                            top_n_group_in_scope=TopNGroupScope(
                                top=5,
                                period=10,
                                min_top_count=9
                            )
                        ),
                        alert_conditions=MetricAnomalyAlertConditions(
                            metric_boundary_condition=MetricBoundaryCondition(
                                direction="Both",
                                companion_metric_id=variables["data_feed_metric_id"],
                                lower=1.0,
                                upper=5.0
                            )
                        )
                    )
                ],
                hook_ids=[]
            )
            if self.is_live:
                variables["alert_config_id"] = alert_config.id
            assert alert_config.cross_metrics_operator is None
            assert alert_config.id is not None
            assert alert_config.name is not None
            assert len(alert_config.metric_alert_configurations) == 1
            assert alert_config.metric_alert_configurations[0].detection_configuration_id is not None
            assert not alert_config.metric_alert_configurations[0].negation_operation
            assert alert_config.metric_alert_configurations[0].alert_scope.scope_type == "TopN"
            assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.min_top_count == 9
            assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.period == 10
            assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.top == 5
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.companion_metric_id is not None
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.upper == 5.0
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.lower == 1.0
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.direction == "Both"
            assert not alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.trigger_for_missing

            self.clean_up(client.delete_alert_configuration, variables, key="alert_config_id")

            with pytest.raises(ResourceNotFoundError):
                client.get_alert_configuration(variables["alert_config_id"])

        finally:
            self.clean_up(client.delete_detection_configuration, variables, key="detection_config_id")
            self.clean_up(client.delete_data_feed, variables)
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(data_feed=True, detection_config=True)
    @recorded_by_proxy
    def test_create_alert_config_top_n_alert_direction_down(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables")
        alert_config_name = self.create_random_name("alertconfig")
        if self.is_live:
            variables["alert_config_name"] = alert_config_name

        try:
            alert_config = client.create_alert_configuration(
                name=variables["alert_config_name"],
                metric_alert_configurations=[
                    MetricAlertConfiguration(
                        detection_configuration_id=variables["detection_config_id"],
                        alert_scope=MetricAnomalyAlertScope(
                            scope_type="TopN",
                            top_n_group_in_scope=TopNGroupScope(
                                top=5,
                                period=10,
                                min_top_count=9
                            )
                        ),
                        alert_conditions=MetricAnomalyAlertConditions(
                            metric_boundary_condition=MetricBoundaryCondition(
                                direction="Down",
                                companion_metric_id=variables["data_feed_metric_id"],
                                lower=1.0,
                            )
                        )
                    )
                ],
                hook_ids=[]
            )
            assert alert_config.cross_metrics_operator is None
            assert alert_config.id is not None
            assert alert_config.name is not None
            assert len(alert_config.metric_alert_configurations) == 1
            assert alert_config.metric_alert_configurations[0].detection_configuration_id is not None
            assert not alert_config.metric_alert_configurations[0].negation_operation
            assert alert_config.metric_alert_configurations[0].alert_scope.scope_type == "TopN"
            assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.min_top_count == 9
            assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.period == 10
            assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.top == 5
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.companion_metric_id is not None
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.direction == "Down"
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.lower == 1.0
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.upper is None
            assert not alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.trigger_for_missing

        finally:
            self.clean_up(client.delete_data_feed, variables)
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(data_feed=True, detection_config=True)
    @recorded_by_proxy
    def test_create_alert_config_top_n_alert_direction_up(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables")
        alert_config_name = self.create_random_name("alertconfig")
        if self.is_live:
            variables["alert_config_name"] = alert_config_name

        try:
            alert_config = client.create_alert_configuration(
                name=variables["alert_config_name"],
                metric_alert_configurations=[
                    MetricAlertConfiguration(
                        detection_configuration_id=variables["detection_config_id"],
                        alert_scope=MetricAnomalyAlertScope(
                            scope_type="TopN",
                            top_n_group_in_scope=TopNGroupScope(
                                top=5,
                                period=10,
                                min_top_count=9
                            )
                        ),
                        alert_conditions=MetricAnomalyAlertConditions(
                            metric_boundary_condition=MetricBoundaryCondition(
                                direction="Up",
                                companion_metric_id=variables["data_feed_metric_id"],
                                upper=5.0,
                            )
                        )
                    )
                ],
                hook_ids=[]
            )
            assert alert_config.cross_metrics_operator is None
            assert alert_config.id is not None
            assert alert_config.name is not None
            assert len(alert_config.metric_alert_configurations) == 1
            assert alert_config.metric_alert_configurations[0].detection_configuration_id is not None
            assert not alert_config.metric_alert_configurations[0].negation_operation
            assert alert_config.metric_alert_configurations[0].alert_scope.scope_type == "TopN"
            assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.min_top_count == 9
            assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.period == 10
            assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.top == 5
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.companion_metric_id is not None
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.direction == "Up"
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.upper == 5.0
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.lower is None
            assert not alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.trigger_for_missing

        finally:
            self.clean_up(client.delete_data_feed, variables)
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(data_feed=True, detection_config=True)
    @recorded_by_proxy
    def test_create_alert_config_top_n_severity_condition(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables")
        alert_config_name = self.create_random_name("alertconfig")
        if self.is_live:
            variables["alert_config_name"] = alert_config_name

        try:
            alert_config = client.create_alert_configuration(
                name=variables["alert_config_name"],
                metric_alert_configurations=[
                    MetricAlertConfiguration(
                        detection_configuration_id=variables["detection_config_id"],
                        alert_scope=MetricAnomalyAlertScope(
                            scope_type="TopN",
                            top_n_group_in_scope=TopNGroupScope(
                                top=5,
                                period=10,
                                min_top_count=9
                            )
                        ),
                        alert_conditions=MetricAnomalyAlertConditions(
                            severity_condition=SeverityCondition(
                                min_alert_severity="Low",
                                max_alert_severity="High"
                            )
                        )
                    )
                ],
                hook_ids=[]
            )
            assert alert_config.cross_metrics_operator is None
            assert alert_config.id is not None
            assert alert_config.name is not None
            assert len(alert_config.metric_alert_configurations) == 1
            assert alert_config.metric_alert_configurations[0].detection_configuration_id is not None
            assert not alert_config.metric_alert_configurations[0].negation_operation
            assert alert_config.metric_alert_configurations[0].alert_scope.scope_type == "TopN"
            assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.min_top_count == 9
            assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.period == 10
            assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.top == 5
            assert alert_config.metric_alert_configurations[0].alert_conditions.severity_condition.min_alert_severity == "Low"
            assert alert_config.metric_alert_configurations[0].alert_conditions.severity_condition.max_alert_severity == "High"

        finally:
            self.clean_up(client.delete_data_feed, variables)
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(data_feed=True, detection_config=True)
    @recorded_by_proxy
    def test_create_alert_config_snooze_condition(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables")
        alert_config_name = self.create_random_name("alertconfig")
        if self.is_live:
            variables["alert_config_name"] = alert_config_name

        try:
            alert_config = client.create_alert_configuration(
                name=variables["alert_config_name"],
                metric_alert_configurations=[
                    MetricAlertConfiguration(
                        detection_configuration_id=variables["detection_config_id"],
                        alert_scope=MetricAnomalyAlertScope(
                            scope_type="TopN",
                            top_n_group_in_scope=TopNGroupScope(
                                top=5,
                                period=10,
                                min_top_count=9
                            )
                        ),
                        alert_snooze_condition=MetricAnomalyAlertSnoozeCondition(
                            auto_snooze=5,
                            snooze_scope="Metric",
                            only_for_successive=True
                        )
                    )
                ],
                hook_ids=[]
            )
            assert alert_config.cross_metrics_operator is None
            assert alert_config.id is not None
            assert alert_config.name is not None
            assert len(alert_config.metric_alert_configurations) == 1
            assert alert_config.metric_alert_configurations[0].detection_configuration_id is not None
            assert not alert_config.metric_alert_configurations[0].negation_operation
            assert alert_config.metric_alert_configurations[0].alert_scope.scope_type == "TopN"
            assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.min_top_count == 9
            assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.period == 10
            assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.top == 5
            assert alert_config.metric_alert_configurations[0].alert_snooze_condition.auto_snooze == 5
            assert alert_config.metric_alert_configurations[0].alert_snooze_condition.snooze_scope == "Metric"
            assert alert_config.metric_alert_configurations[0].alert_snooze_condition.only_for_successive

        finally:
            self.clean_up(client.delete_data_feed, variables)
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(data_feed=True, detection_config=True)
    @recorded_by_proxy
    def test_create_alert_conf_whole_series_dir_both(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables")
        alert_config_name = self.create_random_name("alertconfig")
        if self.is_live:
            variables["alert_config_name"] = alert_config_name

        try:
            alert_config = client.create_alert_configuration(
                name=variables["alert_config_name"],
                metric_alert_configurations=[
                    MetricAlertConfiguration(
                        detection_configuration_id=variables["detection_config_id"],
                        alert_scope=MetricAnomalyAlertScope(
                            scope_type="WholeSeries",
                        ),
                        alert_conditions=MetricAnomalyAlertConditions(
                            metric_boundary_condition=MetricBoundaryCondition(
                                direction="Both",
                                companion_metric_id=variables["data_feed_metric_id"],
                                lower=1.0,
                                upper=5.0
                            )
                        )
                    )
                ],
                hook_ids=[]
            )
            assert alert_config.cross_metrics_operator is None
            assert alert_config.id is not None
            assert alert_config.name is not None
            assert len(alert_config.metric_alert_configurations) == 1
            assert alert_config.metric_alert_configurations[0].detection_configuration_id is not None
            assert not alert_config.metric_alert_configurations[0].negation_operation
            assert alert_config.metric_alert_configurations[0].alert_scope.scope_type == "WholeSeries"
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.companion_metric_id is not None
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.upper == 5.0
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.lower == 1.0
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.direction == "Both"
            assert not alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.trigger_for_missing

        finally:
            self.clean_up(client.delete_data_feed, variables)
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(data_feed=True, detection_config=True)
    @recorded_by_proxy
    def test_create_alert_conf_whole_series_dir_down(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables")
        alert_config_name = self.create_random_name("alertconfig")
        if self.is_live:
            variables["alert_config_name"] = alert_config_name

        try:
            alert_config = client.create_alert_configuration(
                name=variables["alert_config_name"],
                metric_alert_configurations=[
                    MetricAlertConfiguration(
                        detection_configuration_id=variables["detection_config_id"],
                        alert_scope=MetricAnomalyAlertScope(
                            scope_type="WholeSeries"
                        ),
                        alert_conditions=MetricAnomalyAlertConditions(
                            metric_boundary_condition=MetricBoundaryCondition(
                                direction="Down",
                                companion_metric_id=variables["data_feed_metric_id"],
                                lower=1.0,
                            )
                        )
                    )
                ],
                hook_ids=[]
            )
            assert alert_config.cross_metrics_operator is None
            assert alert_config.id is not None
            assert alert_config.name is not None
            assert len(alert_config.metric_alert_configurations) == 1
            assert alert_config.metric_alert_configurations[0].detection_configuration_id is not None
            assert not alert_config.metric_alert_configurations[0].negation_operation
            assert alert_config.metric_alert_configurations[0].alert_scope.scope_type == "WholeSeries"
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.companion_metric_id is not None
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.direction == "Down"
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.lower == 1.0
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.upper is None
            assert not alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.trigger_for_missing

        finally:
            self.clean_up(client.delete_data_feed, variables)
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(data_feed=True, detection_config=True)
    @recorded_by_proxy
    def test_create_alert_config_whole_series_alert_direction_up(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables")
        alert_config_name = self.create_random_name("alertconfig")
        if self.is_live:
            variables["alert_config_name"] = alert_config_name

        try:
            alert_config = client.create_alert_configuration(
                name=variables["alert_config_name"],
                metric_alert_configurations=[
                    MetricAlertConfiguration(
                        detection_configuration_id=variables["detection_config_id"],
                        alert_scope=MetricAnomalyAlertScope(
                            scope_type="WholeSeries"
                        ),
                        alert_conditions=MetricAnomalyAlertConditions(
                            metric_boundary_condition=MetricBoundaryCondition(
                                direction="Up",
                                companion_metric_id=variables["data_feed_metric_id"],
                                upper=5.0,
                            )
                        )
                    )
                ],
                hook_ids=[]
            )
            assert alert_config.cross_metrics_operator is None
            assert alert_config.id is not None
            assert alert_config.name is not None
            assert len(alert_config.metric_alert_configurations) == 1
            assert alert_config.metric_alert_configurations[0].detection_configuration_id is not None
            assert not alert_config.metric_alert_configurations[0].negation_operation
            assert alert_config.metric_alert_configurations[0].alert_scope.scope_type == "WholeSeries"
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.companion_metric_id is not None
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.direction == "Up"
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.upper == 5.0
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.lower is None
            assert not alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.trigger_for_missing

        finally:
            self.clean_up(client.delete_data_feed, variables)
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(data_feed=True, detection_config=True)
    @recorded_by_proxy
    def test_create_alert_config_whole_series_sev_cond(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables")
        alert_config_name = self.create_random_name("alertconfig")
        if self.is_live:
            variables["alert_config_name"] = alert_config_name

        try:
            alert_config = client.create_alert_configuration(
                name=variables["alert_config_name"],
                metric_alert_configurations=[
                    MetricAlertConfiguration(
                        detection_configuration_id=variables["detection_config_id"],
                        alert_scope=MetricAnomalyAlertScope(
                            scope_type="WholeSeries"
                        ),
                        alert_conditions=MetricAnomalyAlertConditions(
                            severity_condition=SeverityCondition(
                                min_alert_severity="Low",
                                max_alert_severity="High"
                            )
                        )
                    )
                ],
                hook_ids=[]
            )
            assert alert_config.cross_metrics_operator is None
            assert alert_config.id is not None
            assert alert_config.name is not None
            assert len(alert_config.metric_alert_configurations) == 1
            assert alert_config.metric_alert_configurations[0].detection_configuration_id is not None
            assert not alert_config.metric_alert_configurations[0].negation_operation
            assert alert_config.metric_alert_configurations[0].alert_scope.scope_type == "WholeSeries"
            assert alert_config.metric_alert_configurations[0].alert_conditions.severity_condition.min_alert_severity == "Low"
            assert alert_config.metric_alert_configurations[0].alert_conditions.severity_condition.max_alert_severity == "High"

        finally:
            self.clean_up(client.delete_data_feed, variables)
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(data_feed=True, detection_config=True)
    @recorded_by_proxy
    def test_create_alert_conf_series_group_dir_both(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables")
        alert_config_name = self.create_random_name("alertconfig")
        if self.is_live:
            variables["alert_config_name"] = alert_config_name

        try:
            alert_config = client.create_alert_configuration(
                name=variables["alert_config_name"],
                metric_alert_configurations=[
                    MetricAlertConfiguration(
                        detection_configuration_id=variables["detection_config_id"],
                        alert_scope=MetricAnomalyAlertScope(
                            scope_type="SeriesGroup",
                            series_group_in_scope={'region': 'Shenzhen'}
                        ),
                        alert_conditions=MetricAnomalyAlertConditions(
                            metric_boundary_condition=MetricBoundaryCondition(
                                direction="Both",
                                companion_metric_id=variables["data_feed_metric_id"],
                                lower=1.0,
                                upper=5.0
                            )
                        )
                    )
                ],
                hook_ids=[]
            )
            assert alert_config.cross_metrics_operator is None
            assert alert_config.id is not None
            assert alert_config.name is not None
            assert len(alert_config.metric_alert_configurations) == 1
            assert alert_config.metric_alert_configurations[0].detection_configuration_id is not None
            assert not alert_config.metric_alert_configurations[0].negation_operation
            assert alert_config.metric_alert_configurations[0].alert_scope.scope_type == "SeriesGroup"
            assert alert_config.metric_alert_configurations[0].alert_scope.series_group_in_scope == {'region': 'Shenzhen'}
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.companion_metric_id is not None
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.upper == 5.0
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.lower == 1.0
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.direction == "Both"
            assert not alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.trigger_for_missing

        finally:
            self.clean_up(client.delete_data_feed, variables)
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(data_feed=True, detection_config=True)
    @recorded_by_proxy
    def test_create_alert_conf_series_group_dir_down(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables")
        alert_config_name = self.create_random_name("alertconfig")
        if self.is_live:
            variables["alert_config_name"] = alert_config_name

        try:
            alert_config = client.create_alert_configuration(
                name=variables["alert_config_name"],
                metric_alert_configurations=[
                    MetricAlertConfiguration(
                        detection_configuration_id=variables["detection_config_id"],
                        alert_scope=MetricAnomalyAlertScope(
                            scope_type="SeriesGroup",
                            series_group_in_scope={'region': 'Shenzhen'}
                        ),
                        alert_conditions=MetricAnomalyAlertConditions(
                            metric_boundary_condition=MetricBoundaryCondition(
                                direction="Down",
                                companion_metric_id=variables["data_feed_metric_id"],
                                lower=1.0,
                            )
                        )
                    )
                ],
                hook_ids=[]
            )
            assert alert_config.cross_metrics_operator is None
            assert alert_config.id is not None
            assert alert_config.name is not None
            assert len(alert_config.metric_alert_configurations) == 1
            assert alert_config.metric_alert_configurations[0].detection_configuration_id is not None
            assert not alert_config.metric_alert_configurations[0].negation_operation
            assert alert_config.metric_alert_configurations[0].alert_scope.scope_type == "SeriesGroup"
            assert alert_config.metric_alert_configurations[0].alert_scope.series_group_in_scope == {'region': 'Shenzhen'}
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.companion_metric_id is not None
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.direction == "Down"
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.lower == 1.0
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.upper is None
            assert not alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.trigger_for_missing

        finally:
            self.clean_up(client.delete_data_feed, variables)
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(data_feed=True, detection_config=True)
    @recorded_by_proxy
    def test_create_alert_config_series_group_alert_direction_up(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables")
        alert_config_name = self.create_random_name("alertconfig")
        if self.is_live:
            variables["alert_config_name"] = alert_config_name

        try:
            alert_config = client.create_alert_configuration(
                name=variables["alert_config_name"],
                metric_alert_configurations=[
                    MetricAlertConfiguration(
                        detection_configuration_id=variables["detection_config_id"],
                        alert_scope=MetricAnomalyAlertScope(
                            scope_type="SeriesGroup",
                            series_group_in_scope={'region': 'Shenzhen'}
                        ),
                        alert_conditions=MetricAnomalyAlertConditions(
                            metric_boundary_condition=MetricBoundaryCondition(
                                direction="Up",
                                companion_metric_id=variables["data_feed_metric_id"],
                                upper=5.0,
                            )
                        )
                    )
                ],
                hook_ids=[]
            )
            assert alert_config.cross_metrics_operator is None
            assert alert_config.id is not None
            assert alert_config.name is not None
            assert len(alert_config.metric_alert_configurations) == 1
            assert alert_config.metric_alert_configurations[0].detection_configuration_id is not None
            assert not alert_config.metric_alert_configurations[0].negation_operation
            assert alert_config.metric_alert_configurations[0].alert_scope.scope_type == "SeriesGroup"
            assert alert_config.metric_alert_configurations[0].alert_scope.series_group_in_scope == {'region': 'Shenzhen'}
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.companion_metric_id is not None
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.direction == "Up"
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.upper == 5.0
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.lower is None
            assert not alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.trigger_for_missing

        finally:
            self.clean_up(client.delete_data_feed, variables)
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(data_feed=True, detection_config=True)
    @recorded_by_proxy
    def test_create_alert_conf_series_group_sev_cond(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables")
        alert_config_name = self.create_random_name("alertconfig")
        if self.is_live:
            variables["alert_config_name"] = alert_config_name

        try:
            alert_config = client.create_alert_configuration(
                name=variables["alert_config_name"],
                metric_alert_configurations=[
                    MetricAlertConfiguration(
                        detection_configuration_id=variables["detection_config_id"],
                        alert_scope=MetricAnomalyAlertScope(
                            scope_type="SeriesGroup",
                            series_group_in_scope={'region': 'Shenzhen'}
                        ),
                        alert_conditions=MetricAnomalyAlertConditions(
                            severity_condition=SeverityCondition(
                                min_alert_severity="Low",
                                max_alert_severity="High"
                            )
                        )
                    )
                ],
                hook_ids=[]
            )
            assert alert_config.cross_metrics_operator is None
            assert alert_config.id is not None
            assert alert_config.name is not None
            assert len(alert_config.metric_alert_configurations) == 1
            assert alert_config.metric_alert_configurations[0].detection_configuration_id is not None
            assert not alert_config.metric_alert_configurations[0].negation_operation
            assert alert_config.metric_alert_configurations[0].alert_scope.scope_type == "SeriesGroup"
            assert alert_config.metric_alert_configurations[0].alert_scope.series_group_in_scope == {'region': 'Shenzhen'}
            assert alert_config.metric_alert_configurations[0].alert_conditions.severity_condition.min_alert_severity == "Low"
            assert alert_config.metric_alert_configurations[0].alert_conditions.severity_condition.max_alert_severity == "High"

        finally:
            self.clean_up(client.delete_data_feed, variables)
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(data_feed=True, detection_config=True)
    @recorded_by_proxy
    def test_create_alert_config_multiple_configurations(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables")
        alert_config_name = self.create_random_name("alertconfig")
        if self.is_live:
            variables["alert_config_name"] = alert_config_name

        try:
            alert_config = client.create_alert_configuration(
                name=variables["alert_config_name"],
                cross_metrics_operator="AND",
                metric_alert_configurations=[
                    MetricAlertConfiguration(
                        detection_configuration_id=variables["detection_config_id"],
                        alert_scope=MetricAnomalyAlertScope(
                            scope_type="TopN",
                            top_n_group_in_scope=TopNGroupScope(
                                top=5,
                                period=10,
                                min_top_count=9
                            )
                        ),
                        alert_conditions=MetricAnomalyAlertConditions(
                            metric_boundary_condition=MetricBoundaryCondition(
                                direction="Both",
                                companion_metric_id=variables["data_feed_metric_id"],
                                lower=1.0,
                                upper=5.0
                            )
                        )
                    ),
                    MetricAlertConfiguration(
                        detection_configuration_id=variables["detection_config_id"],
                        alert_scope=MetricAnomalyAlertScope(
                            scope_type="SeriesGroup",
                            series_group_in_scope={'region': 'Shenzhen'}
                        ),
                        alert_conditions=MetricAnomalyAlertConditions(
                            severity_condition=SeverityCondition(
                                min_alert_severity="Low",
                                max_alert_severity="High"
                            )
                        )
                    ),
                    MetricAlertConfiguration(
                        detection_configuration_id=variables["detection_config_id"],
                        alert_scope=MetricAnomalyAlertScope(
                            scope_type="WholeSeries"
                        ),
                        alert_conditions=MetricAnomalyAlertConditions(
                            severity_condition=SeverityCondition(
                                min_alert_severity="Low",
                                max_alert_severity="High"
                            )
                        )
                    )
                ],
                hook_ids=[]
            )
            assert alert_config.cross_metrics_operator == "AND"
            assert alert_config.id is not None
            assert alert_config.name is not None
            assert len(alert_config.metric_alert_configurations) == 3
            assert alert_config.metric_alert_configurations[0].detection_configuration_id is not None
            assert not alert_config.metric_alert_configurations[0].negation_operation
            assert alert_config.metric_alert_configurations[0].alert_scope.scope_type == "TopN"
            assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.min_top_count == 9
            assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.period == 10
            assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.top == 5
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.companion_metric_id is not None
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.upper == 5.0
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.lower == 1.0
            assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.direction == "Both"
            assert not alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.trigger_for_missing
            assert alert_config.metric_alert_configurations[1].alert_scope.scope_type == "SeriesGroup"
            assert alert_config.metric_alert_configurations[1].alert_conditions.severity_condition.min_alert_severity == "Low"
            assert alert_config.metric_alert_configurations[1].alert_conditions.severity_condition.max_alert_severity == "High"
            assert alert_config.metric_alert_configurations[2].alert_scope.scope_type == "WholeSeries"
            assert alert_config.metric_alert_configurations[2].alert_conditions.severity_condition.min_alert_severity == "Low"
            assert alert_config.metric_alert_configurations[2].alert_conditions.severity_condition.max_alert_severity == "High"

        finally:
            self.clean_up(client.delete_data_feed, variables)
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_list_alert_configs(self, **kwargs):
        client = kwargs.pop("client")

        configs = client.list_alert_configurations(
            detection_configuration_id=self.anomaly_detection_configuration_id
        )
        assert len(list(configs)) > 0

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(data_feed=True, detection_config=True, alert_config=True)
    @recorded_by_proxy
    def test_update_alert_config_with_model(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables")

        alert_config = client.get_alert_configuration(variables["alert_config_id"])
        try:
            update_name = "update" + str(uuid.uuid4())
            if self.is_live:
                variables["alert_config_updated_name"] = update_name
            alert_config.name = variables["alert_config_updated_name"]
            alert_config.description = "update description"
            alert_config.cross_metrics_operator = "OR"
            alert_config.metric_alert_configurations[0].alert_conditions.severity_condition = \
                SeverityCondition(max_alert_severity="High", min_alert_severity="Low")
            alert_config.metric_alert_configurations[1].alert_conditions.metric_boundary_condition = \
                MetricBoundaryCondition(
                    direction="Both",
                    upper=5,
                    lower=1
                )
            alert_config.metric_alert_configurations[2].alert_conditions.metric_boundary_condition = \
                MetricBoundaryCondition(
                    direction="Both",
                    upper=5,
                    lower=1
                )

            client.update_alert_configuration(alert_config)
            updated = client.get_alert_configuration(variables["alert_config_id"])

            assert updated.name == variables["alert_config_updated_name"]
            assert updated.description == "update description"
            assert updated.cross_metrics_operator == "OR"
            assert updated.metric_alert_configurations[0].alert_conditions.severity_condition.max_alert_severity == "High"
            assert updated.metric_alert_configurations[0].alert_conditions.severity_condition.min_alert_severity == "Low"
            assert updated.metric_alert_configurations[1].alert_conditions.metric_boundary_condition.direction == "Both"
            assert updated.metric_alert_configurations[1].alert_conditions.metric_boundary_condition.upper == 5
            assert updated.metric_alert_configurations[1].alert_conditions.metric_boundary_condition.lower == 1
            assert updated.metric_alert_configurations[2].alert_conditions.metric_boundary_condition.direction == "Both"
            assert updated.metric_alert_configurations[2].alert_conditions.metric_boundary_condition.upper == 5
            assert updated.metric_alert_configurations[2].alert_conditions.metric_boundary_condition.lower == 1

        finally:
            self.clean_up(client.delete_data_feed, variables)
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(data_feed=True, detection_config=True, alert_config=True)
    @recorded_by_proxy
    def test_update_alert_config_with_kwargs(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables")

        try:
            update_name = "update" + str(uuid.uuid4())
            if self.is_live:
                variables["alert_config_updated_name"] = update_name
            client.update_alert_configuration(
                variables["alert_config_id"],
                name=variables["alert_config_updated_name"],
                description="update description",
                cross_metrics_operator="OR",
                metric_alert_configurations=[
                    MetricAlertConfiguration(
                        detection_configuration_id=variables["detection_config_id"],
                        alert_scope=MetricAnomalyAlertScope(
                            scope_type="TopN",
                            top_n_group_in_scope=TopNGroupScope(
                                top=5,
                                period=10,
                                min_top_count=9
                            )
                        ),
                        alert_conditions=MetricAnomalyAlertConditions(
                            metric_boundary_condition=MetricBoundaryCondition(
                                direction="Both",
                                companion_metric_id=variables["data_feed_metric_id"],
                                lower=1.0,
                                upper=5.0
                            ),
                            severity_condition=SeverityCondition(max_alert_severity="High", min_alert_severity="Low")
                        )
                    ),
                    MetricAlertConfiguration(
                        detection_configuration_id=variables["detection_config_id"],
                        alert_scope=MetricAnomalyAlertScope(
                            scope_type="SeriesGroup",
                            series_group_in_scope={'region': 'Shenzhen'}
                        ),
                        alert_conditions=MetricAnomalyAlertConditions(
                            severity_condition=SeverityCondition(
                                min_alert_severity="Low",
                                max_alert_severity="High"
                            ),
                            metric_boundary_condition=MetricBoundaryCondition(
                                direction="Both",
                                upper=5,
                                lower=1
                            )
                        )
                    ),
                    MetricAlertConfiguration(
                        detection_configuration_id=variables["detection_config_id"],
                        alert_scope=MetricAnomalyAlertScope(
                            scope_type="WholeSeries"
                        ),
                        alert_conditions=MetricAnomalyAlertConditions(
                            severity_condition=SeverityCondition(
                                min_alert_severity="Low",
                                max_alert_severity="High"
                            ),
                            metric_boundary_condition=MetricBoundaryCondition(
                                direction="Both",
                                upper=5,
                                lower=1
                            )
                        )
                    )
                ]
            )
            updated = client.get_alert_configuration(variables["alert_config_id"])
            assert updated.name == variables["alert_config_updated_name"]
            assert updated.description == "update description"
            assert updated.cross_metrics_operator == "OR"
            assert updated.metric_alert_configurations[0].alert_conditions.severity_condition.max_alert_severity == "High"
            assert updated.metric_alert_configurations[0].alert_conditions.severity_condition.min_alert_severity == "Low"
            assert updated.metric_alert_configurations[1].alert_conditions.metric_boundary_condition.direction == "Both"
            assert updated.metric_alert_configurations[1].alert_conditions.metric_boundary_condition.upper == 5
            assert updated.metric_alert_configurations[1].alert_conditions.metric_boundary_condition.lower == 1
            assert updated.metric_alert_configurations[2].alert_conditions.metric_boundary_condition.direction == "Both"
            assert updated.metric_alert_configurations[2].alert_conditions.metric_boundary_condition.upper == 5
            assert updated.metric_alert_configurations[2].alert_conditions.metric_boundary_condition.lower == 1

        finally:
            self.clean_up(client.delete_data_feed, variables)
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(data_feed=True, detection_config=True, alert_config=True)
    @recorded_by_proxy
    def test_update_alert_config_with_model_and_kwargs(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables")
        alert_config = client.get_alert_configuration(variables["alert_config_id"])

        try:
            update_name = "update" + str(uuid.uuid4())
            if self.is_live:
                variables["alert_config_updated_name"] = update_name
            alert_config.name = variables["alert_config_updated_name"]
            alert_config.description = "updateMe"
            alert_config.cross_metrics_operator = "don't update me"
            alert_config.metric_alert_configurations[0].alert_conditions.severity_condition = None
            alert_config.metric_alert_configurations[1].alert_conditions.metric_boundary_condition = None
            alert_config.metric_alert_configurations[2].alert_conditions.metric_boundary_condition = None

            client.update_alert_configuration(
                alert_config,
                cross_metrics_operator="OR",
                metric_alert_configurations=[
                    MetricAlertConfiguration(
                        detection_configuration_id=variables["detection_config_id"],
                        alert_scope=MetricAnomalyAlertScope(
                            scope_type="TopN",
                            top_n_group_in_scope=TopNGroupScope(
                                top=5,
                                period=10,
                                min_top_count=9
                            )
                        ),
                        alert_conditions=MetricAnomalyAlertConditions(
                            metric_boundary_condition=MetricBoundaryCondition(
                                direction="Both",
                                companion_metric_id=variables["data_feed_metric_id"],
                                lower=1.0,
                                upper=5.0
                            ),
                            severity_condition=SeverityCondition(max_alert_severity="High", min_alert_severity="Low")
                        )
                    ),
                    MetricAlertConfiguration(
                        detection_configuration_id=variables["detection_config_id"],
                        alert_scope=MetricAnomalyAlertScope(
                            scope_type="SeriesGroup",
                            series_group_in_scope={'region': 'Shenzhen'}
                        ),
                        alert_conditions=MetricAnomalyAlertConditions(
                            severity_condition=SeverityCondition(
                                min_alert_severity="Low",
                                max_alert_severity="High"
                            ),
                            metric_boundary_condition=MetricBoundaryCondition(
                                direction="Both",
                                upper=5,
                                lower=1
                            )
                        )
                    ),
                    MetricAlertConfiguration(
                        detection_configuration_id=variables["detection_config_id"],
                        alert_scope=MetricAnomalyAlertScope(
                            scope_type="WholeSeries"
                        ),
                        alert_conditions=MetricAnomalyAlertConditions(
                            severity_condition=SeverityCondition(
                                min_alert_severity="Low",
                                max_alert_severity="High"
                            ),
                            metric_boundary_condition=MetricBoundaryCondition(
                                direction="Both",
                                upper=5,
                                lower=1
                            )
                        )
                    )
                ]
            )
            updated = client.get_alert_configuration(variables["alert_config_id"])
            assert updated.name == variables["alert_config_updated_name"]
            assert updated.description == "updateMe"
            assert updated.cross_metrics_operator == "OR"
            assert updated.metric_alert_configurations[0].alert_conditions.severity_condition.max_alert_severity == "High"
            assert updated.metric_alert_configurations[0].alert_conditions.severity_condition.min_alert_severity == "Low"
            assert updated.metric_alert_configurations[1].alert_conditions.metric_boundary_condition.direction == "Both"
            assert updated.metric_alert_configurations[1].alert_conditions.metric_boundary_condition.upper == 5
            assert updated.metric_alert_configurations[1].alert_conditions.metric_boundary_condition.lower == 1
            assert updated.metric_alert_configurations[2].alert_conditions.metric_boundary_condition.direction == "Both"
            assert updated.metric_alert_configurations[2].alert_conditions.metric_boundary_condition.upper == 5
            assert updated.metric_alert_configurations[2].alert_conditions.metric_boundary_condition.lower == 1

        finally:
            self.clean_up(client.delete_data_feed, variables)
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(data_feed=True, detection_config=True, alert_config=True)
    @recorded_by_proxy
    def test_update_anomaly_alert_by_resetting_properties(self, **kwargs):
        client = kwargs.pop("client")
        variables = kwargs.pop("variables")

        try:
            update_name = "update" + str(uuid.uuid4())
            if self.is_live:
                variables["alert_config_updated_name"] = update_name
            client.update_alert_configuration(
                variables["alert_config_id"],
                name=variables["alert_config_updated_name"],
                description="",  # can't pass None currently, bug says description is required
                metric_alert_configurations=[
                    MetricAlertConfiguration(
                        detection_configuration_id=variables["detection_config_id"],
                        alert_scope=MetricAnomalyAlertScope(
                            scope_type="TopN",
                            top_n_group_in_scope=TopNGroupScope(
                                top=5,
                                period=10,
                                min_top_count=9
                            )
                        ),
                        alert_conditions=None
                    )
                ]
            )
            updated = client.get_alert_configuration(variables["alert_config_id"])
            assert updated.name == variables["alert_config_updated_name"]
            assert updated.description == ""
            assert updated.cross_metrics_operator is None
            assert len(updated.metric_alert_configurations) == 1
            assert updated.metric_alert_configurations[0].alert_conditions.severity_condition is None
            assert updated.metric_alert_configurations[0].alert_conditions.metric_boundary_condition is None

        finally:
            self.clean_up(client.delete_data_feed, variables)
        return variables
