# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from devtools_testutils import AzureTestCase
from azure.core.exceptions import ResourceNotFoundError

from azure.ai.metricsadvisor.models import (
    MetricAlertConfiguration,
    MetricAnomalyAlertScope,
    MetricAnomalyAlertConditions,
    MetricBoundaryCondition,
    TopNGroupScope,
    SeverityCondition,
    MetricAnomalyAlertSnoozeCondition,
)
from base_testcase_aad_async import TestMetricsAdvisorAdministrationClientBaseAsync


class TestMetricsAdvisorAdministrationClientAsync(TestMetricsAdvisorAdministrationClientBaseAsync):

    @AzureTestCase.await_prepared_test
    async def test_create_alert_config_top_n_alert_direction_both(self):

        detection_config, data_feed = await self._create_data_feed_and_detection_config("topnup")
        alert_config_name = self.create_random_name("testalert")
        async with self.admin_client:
            try:
                alert_config = await self.admin_client.create_alert_configuration(
                    name=alert_config_name,
                    metric_alert_configurations=[
                        MetricAlertConfiguration(
                            detection_configuration_id=detection_config.id,
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
                                    companion_metric_id=data_feed.metric_ids['cost'],
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
                assert len(alert_config.metric_alert_configurations) ==  1
                assert alert_config.metric_alert_configurations[0].detection_configuration_id is not None
                assert not alert_config.metric_alert_configurations[0].negation_operation
                assert alert_config.metric_alert_configurations[0].alert_scope.scope_type ==  "TopN"
                assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.min_top_count ==  9
                assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.period ==  10
                assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.top ==  5
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.companion_metric_id is not None
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.upper ==  5.0
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.lower ==  1.0
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.direction ==  "Both"
                assert not alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.trigger_for_missing
                await self.admin_client.delete_alert_configuration(alert_config.id)

                with pytest.raises(ResourceNotFoundError):
                    await self.admin_client.get_alert_configuration(alert_config.id)

            finally:
                await self.admin_client.delete_detection_configuration(detection_config.id)
                await self.admin_client.delete_data_feed(data_feed.id)

    @AzureTestCase.await_prepared_test
    async def test_create_alert_config_top_n_alert_direction_down(self):

        detection_config, data_feed = await self._create_data_feed_and_detection_config("topnup")
        alert_config_name = self.create_random_name("testalert")
        async with self.admin_client:
            try:
                alert_config = await self.admin_client.create_alert_configuration(
                    name=alert_config_name,
                    metric_alert_configurations=[
                        MetricAlertConfiguration(
                            detection_configuration_id=detection_config.id,
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
                                    companion_metric_id=data_feed.metric_ids['cost'],
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
                assert len(alert_config.metric_alert_configurations) ==  1
                assert alert_config.metric_alert_configurations[0].detection_configuration_id is not None
                assert not alert_config.metric_alert_configurations[0].negation_operation
                assert alert_config.metric_alert_configurations[0].alert_scope.scope_type ==  "TopN"
                assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.min_top_count ==  9
                assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.period ==  10
                assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.top ==  5
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.companion_metric_id is not None
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.direction ==  "Down"
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.lower ==  1.0
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.upper is None
                assert not alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.trigger_for_missing

                await self.admin_client.delete_alert_configuration(alert_config.id)

                with pytest.raises(ResourceNotFoundError):
                    await self.admin_client.get_alert_configuration(alert_config.id)

            finally:
                await self.admin_client.delete_detection_configuration(detection_config.id)
                await self.admin_client.delete_data_feed(data_feed.id)

    @AzureTestCase.await_prepared_test
    async def test_create_alert_config_top_n_alert_direction_up(self):

        detection_config, data_feed = await self._create_data_feed_and_detection_config("topnup")
        alert_config_name = self.create_random_name("testalert")
        async with self.admin_client:
            try:
                alert_config = await self.admin_client.create_alert_configuration(
                    name=alert_config_name,
                    metric_alert_configurations=[
                        MetricAlertConfiguration(
                            detection_configuration_id=detection_config.id,
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
                                    companion_metric_id=data_feed.metric_ids['cost'],
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
                assert len(alert_config.metric_alert_configurations) ==  1
                assert alert_config.metric_alert_configurations[0].detection_configuration_id is not None
                assert not alert_config.metric_alert_configurations[0].negation_operation
                assert alert_config.metric_alert_configurations[0].alert_scope.scope_type ==  "TopN"
                assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.min_top_count ==  9
                assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.period ==  10
                assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.top ==  5
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.companion_metric_id is not None
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.direction ==  "Up"
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.upper ==  5.0
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.lower is None
                assert not alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.trigger_for_missing

                await self.admin_client.delete_alert_configuration(alert_config.id)

                with pytest.raises(ResourceNotFoundError):
                    await self.admin_client.get_alert_configuration(alert_config.id)

            finally:
                await self.admin_client.delete_detection_configuration(detection_config.id)
                await self.admin_client.delete_data_feed(data_feed.id)

    @AzureTestCase.await_prepared_test
    async def test_create_alert_config_top_n_severity_condition(self):

        detection_config, data_feed = await self._create_data_feed_and_detection_config("topnup")
        alert_config_name = self.create_random_name("testalert")
        async with self.admin_client:
            try:
                alert_config = await self.admin_client.create_alert_configuration(
                    name=alert_config_name,
                    metric_alert_configurations=[
                        MetricAlertConfiguration(
                            detection_configuration_id=detection_config.id,
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
                assert len(alert_config.metric_alert_configurations) ==  1
                assert alert_config.metric_alert_configurations[0].detection_configuration_id is not None
                assert not alert_config.metric_alert_configurations[0].negation_operation
                assert alert_config.metric_alert_configurations[0].alert_scope.scope_type ==  "TopN"
                assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.min_top_count ==  9
                assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.period ==  10
                assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.top ==  5
                assert alert_config.metric_alert_configurations[0].alert_conditions.severity_condition.min_alert_severity ==  "Low"
                assert alert_config.metric_alert_configurations[0].alert_conditions.severity_condition.max_alert_severity ==  "High"

                await self.admin_client.delete_alert_configuration(alert_config.id)

                with pytest.raises(ResourceNotFoundError):
                    await self.admin_client.get_alert_configuration(alert_config.id)

            finally:
                await self.admin_client.delete_detection_configuration(detection_config.id)
                await self.admin_client.delete_data_feed(data_feed.id)

    @AzureTestCase.await_prepared_test
    async def test_create_alert_config_snooze_condition(self):

        detection_config, data_feed = await self._create_data_feed_and_detection_config("topnup")
        alert_config_name = self.create_random_name("testalert")
        async with self.admin_client:
            try:
                alert_config = await self.admin_client.create_alert_configuration(
                    name=alert_config_name,
                    metric_alert_configurations=[
                        MetricAlertConfiguration(
                            detection_configuration_id=detection_config.id,
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
                assert len(alert_config.metric_alert_configurations) ==  1
                assert alert_config.metric_alert_configurations[0].detection_configuration_id is not None
                assert not alert_config.metric_alert_configurations[0].negation_operation
                assert alert_config.metric_alert_configurations[0].alert_scope.scope_type ==  "TopN"
                assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.min_top_count ==  9
                assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.period ==  10
                assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.top ==  5
                assert alert_config.metric_alert_configurations[0].alert_snooze_condition.auto_snooze ==  5
                assert alert_config.metric_alert_configurations[0].alert_snooze_condition.snooze_scope ==  "Metric"
                assert alert_config.metric_alert_configurations[0].alert_snooze_condition.only_for_successive
                await self.admin_client.delete_alert_configuration(alert_config.id)

                with pytest.raises(ResourceNotFoundError):
                    await self.admin_client.get_alert_configuration(alert_config.id)

            finally:
                await self.admin_client.delete_detection_configuration(detection_config.id)
                await self.admin_client.delete_data_feed(data_feed.id)

    @AzureTestCase.await_prepared_test
    async def test_create_alert_config_whole_series_alert_direction_both(self):

        detection_config, data_feed = await self._create_data_feed_and_detection_config("wholeseries")
        alert_config_name = self.create_random_name("testalert")
        async with self.admin_client:
            try:
                alert_config = await self.admin_client.create_alert_configuration(
                    name=alert_config_name,
                    metric_alert_configurations=[
                        MetricAlertConfiguration(
                            detection_configuration_id=detection_config.id,
                            alert_scope=MetricAnomalyAlertScope(
                                scope_type="WholeSeries",
                            ),
                            alert_conditions=MetricAnomalyAlertConditions(
                                metric_boundary_condition=MetricBoundaryCondition(
                                    direction="Both",
                                    companion_metric_id=data_feed.metric_ids['cost'],
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
                assert len(alert_config.metric_alert_configurations) ==  1
                assert alert_config.metric_alert_configurations[0].detection_configuration_id is not None
                assert not alert_config.metric_alert_configurations[0].negation_operation
                assert alert_config.metric_alert_configurations[0].alert_scope.scope_type ==  "WholeSeries"
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.companion_metric_id is not None
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.upper ==  5.0
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.lower ==  1.0
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.direction ==  "Both"
                assert not alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.trigger_for_missing

                await self.admin_client.delete_alert_configuration(alert_config.id)

                with pytest.raises(ResourceNotFoundError):
                    await self.admin_client.get_alert_configuration(alert_config.id)

            finally:
                await self.admin_client.delete_detection_configuration(detection_config.id)
                await self.admin_client.delete_data_feed(data_feed.id)

    @AzureTestCase.await_prepared_test
    async def test_create_alert_config_whole_series_alert_direction_down(self):

        detection_config, data_feed = await self._create_data_feed_and_detection_config("wholeseries")
        alert_config_name = self.create_random_name("testalert")
        async with self.admin_client:
            try:
                alert_config = await self.admin_client.create_alert_configuration(
                    name=alert_config_name,
                    metric_alert_configurations=[
                        MetricAlertConfiguration(
                            detection_configuration_id=detection_config.id,
                            alert_scope=MetricAnomalyAlertScope(
                                scope_type="WholeSeries"
                            ),
                            alert_conditions=MetricAnomalyAlertConditions(
                                metric_boundary_condition=MetricBoundaryCondition(
                                    direction="Down",
                                    companion_metric_id=data_feed.metric_ids['cost'],
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
                assert len(alert_config.metric_alert_configurations) ==  1
                assert alert_config.metric_alert_configurations[0].detection_configuration_id is not None
                assert not alert_config.metric_alert_configurations[0].negation_operation
                assert alert_config.metric_alert_configurations[0].alert_scope.scope_type ==  "WholeSeries"
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.companion_metric_id is not None
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.direction ==  "Down"
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.lower ==  1.0
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.upper is None
                assert not alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.trigger_for_missing

                await self.admin_client.delete_alert_configuration(alert_config.id)

                with pytest.raises(ResourceNotFoundError):
                    await self.admin_client.get_alert_configuration(alert_config.id)

            finally:
                await self.admin_client.delete_detection_configuration(detection_config.id)
                await self.admin_client.delete_data_feed(data_feed.id)

    @AzureTestCase.await_prepared_test
    async def test_create_alert_config_whole_series_alert_direction_up(self):

        detection_config, data_feed = await self._create_data_feed_and_detection_config("wholeseries")
        alert_config_name = self.create_random_name("testalert")
        async with self.admin_client:
            try:
                alert_config = await self.admin_client.create_alert_configuration(
                    name=alert_config_name,
                    metric_alert_configurations=[
                        MetricAlertConfiguration(
                            detection_configuration_id=detection_config.id,
                            alert_scope=MetricAnomalyAlertScope(
                                scope_type="WholeSeries"
                            ),
                            alert_conditions=MetricAnomalyAlertConditions(
                                metric_boundary_condition=MetricBoundaryCondition(
                                    direction="Up",
                                    companion_metric_id=data_feed.metric_ids['cost'],
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
                assert len(alert_config.metric_alert_configurations) ==  1
                assert alert_config.metric_alert_configurations[0].detection_configuration_id is not None
                assert not alert_config.metric_alert_configurations[0].negation_operation
                assert alert_config.metric_alert_configurations[0].alert_scope.scope_type ==  "WholeSeries"
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.companion_metric_id is not None
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.direction ==  "Up"
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.upper ==  5.0
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.lower is None
                assert not alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.trigger_for_missing

                await self.admin_client.delete_alert_configuration(alert_config.id)

                with pytest.raises(ResourceNotFoundError):
                    await self.admin_client.get_alert_configuration(alert_config.id)

            finally:
                await self.admin_client.delete_detection_configuration(detection_config.id)
                await self.admin_client.delete_data_feed(data_feed.id)

    @AzureTestCase.await_prepared_test
    async def test_create_alert_config_whole_series_severity_condition(self):

        detection_config, data_feed = await self._create_data_feed_and_detection_config("topnup")
        alert_config_name = self.create_random_name("testalert")
        async with self.admin_client:
            try:
                alert_config = await self.admin_client.create_alert_configuration(
                    name=alert_config_name,
                    metric_alert_configurations=[
                        MetricAlertConfiguration(
                            detection_configuration_id=detection_config.id,
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
                assert len(alert_config.metric_alert_configurations) ==  1
                assert alert_config.metric_alert_configurations[0].detection_configuration_id is not None
                assert not alert_config.metric_alert_configurations[0].negation_operation
                assert alert_config.metric_alert_configurations[0].alert_scope.scope_type ==  "WholeSeries"
                assert alert_config.metric_alert_configurations[0].alert_conditions.severity_condition.min_alert_severity ==  "Low"
                assert alert_config.metric_alert_configurations[0].alert_conditions.severity_condition.max_alert_severity ==  "High"

                await self.admin_client.delete_alert_configuration(alert_config.id)

                with pytest.raises(ResourceNotFoundError):
                    await self.admin_client.get_alert_configuration(alert_config.id)

            finally:
                await self.admin_client.delete_detection_configuration(detection_config.id)
                await self.admin_client.delete_data_feed(data_feed.id)

    @AzureTestCase.await_prepared_test
    async def test_create_alert_config_series_group_alert_direction_both(self):

        detection_config, data_feed = await self._create_data_feed_and_detection_config("seriesgroup")
        alert_config_name = self.create_random_name("testalert")
        async with self.admin_client:
            try:
                alert_config = await self.admin_client.create_alert_configuration(
                    name=alert_config_name,
                    metric_alert_configurations=[
                        MetricAlertConfiguration(
                            detection_configuration_id=detection_config.id,
                            alert_scope=MetricAnomalyAlertScope(
                                scope_type="SeriesGroup",
                                series_group_in_scope={'region': 'Shenzhen'}
                            ),
                            alert_conditions=MetricAnomalyAlertConditions(
                                metric_boundary_condition=MetricBoundaryCondition(
                                    direction="Both",
                                    companion_metric_id=data_feed.metric_ids['cost'],
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
                assert len(alert_config.metric_alert_configurations) ==  1
                assert alert_config.metric_alert_configurations[0].detection_configuration_id is not None
                assert not alert_config.metric_alert_configurations[0].negation_operation
                assert alert_config.metric_alert_configurations[0].alert_scope.scope_type ==  "SeriesGroup"
                assert alert_config.metric_alert_configurations[0].alert_scope.series_group_in_scope ==  {'region': 'Shenzhen'}
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.companion_metric_id is not None
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.upper ==  5.0
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.lower ==  1.0
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.direction ==  "Both"
                assert not alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.trigger_for_missing

                await self.admin_client.delete_alert_configuration(alert_config.id)

                with pytest.raises(ResourceNotFoundError):
                    await self.admin_client.get_alert_configuration(alert_config.id)

            finally:
                await self.admin_client.delete_detection_configuration(detection_config.id)
                await self.admin_client.delete_data_feed(data_feed.id)

    @AzureTestCase.await_prepared_test
    async def test_create_alert_config_series_group_alert_direction_down(self):

        detection_config, data_feed = await self._create_data_feed_and_detection_config("seriesgroup")
        alert_config_name = self.create_random_name("testalert")
        async with self.admin_client:
            try:
                alert_config = await self.admin_client.create_alert_configuration(
                    name=alert_config_name,
                    metric_alert_configurations=[
                        MetricAlertConfiguration(
                            detection_configuration_id=detection_config.id,
                            alert_scope=MetricAnomalyAlertScope(
                                scope_type="SeriesGroup",
                                series_group_in_scope={'region': 'Shenzhen'}
                            ),
                            alert_conditions=MetricAnomalyAlertConditions(
                                metric_boundary_condition=MetricBoundaryCondition(
                                    direction="Down",
                                    companion_metric_id=data_feed.metric_ids['cost'],
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
                assert len(alert_config.metric_alert_configurations) ==  1
                assert alert_config.metric_alert_configurations[0].detection_configuration_id is not None
                assert not alert_config.metric_alert_configurations[0].negation_operation
                assert alert_config.metric_alert_configurations[0].alert_scope.scope_type ==  "SeriesGroup"
                assert alert_config.metric_alert_configurations[0].alert_scope.series_group_in_scope ==  {'region': 'Shenzhen'}
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.companion_metric_id is not None
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.direction ==  "Down"
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.lower ==  1.0
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.upper is None
                assert not alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.trigger_for_missing

                await self.admin_client.delete_alert_configuration(alert_config.id)

                with pytest.raises(ResourceNotFoundError):
                    await self.admin_client.get_alert_configuration(alert_config.id)

            finally:
                await self.admin_client.delete_detection_configuration(detection_config.id)
                await self.admin_client.delete_data_feed(data_feed.id)

    @AzureTestCase.await_prepared_test
    async def test_create_alert_config_series_group_alert_direction_up(self):

        detection_config, data_feed = await self._create_data_feed_and_detection_config("seriesgroup")
        alert_config_name = self.create_random_name("testalert")
        async with self.admin_client:
            try:
                alert_config = await self.admin_client.create_alert_configuration(
                    name=alert_config_name,
                    metric_alert_configurations=[
                        MetricAlertConfiguration(
                            detection_configuration_id=detection_config.id,
                            alert_scope=MetricAnomalyAlertScope(
                                scope_type="SeriesGroup",
                                series_group_in_scope={'region': 'Shenzhen'}
                            ),
                            alert_conditions=MetricAnomalyAlertConditions(
                                metric_boundary_condition=MetricBoundaryCondition(
                                    direction="Up",
                                    companion_metric_id=data_feed.metric_ids['cost'],
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
                assert len(alert_config.metric_alert_configurations) ==  1
                assert alert_config.metric_alert_configurations[0].detection_configuration_id is not None
                assert not alert_config.metric_alert_configurations[0].negation_operation
                assert alert_config.metric_alert_configurations[0].alert_scope.scope_type ==  "SeriesGroup"
                assert alert_config.metric_alert_configurations[0].alert_scope.series_group_in_scope ==  {'region': 'Shenzhen'}
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.companion_metric_id is not None
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.direction ==  "Up"
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.upper ==  5.0
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.lower is None
                assert not alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.trigger_for_missing

                await self.admin_client.delete_alert_configuration(alert_config.id)

                with pytest.raises(ResourceNotFoundError):
                    await self.admin_client.get_alert_configuration(alert_config.id)

            finally:
                await self.admin_client.delete_detection_configuration(detection_config.id)
                await self.admin_client.delete_data_feed(data_feed.id)

    @AzureTestCase.await_prepared_test
    async def test_create_alert_config_series_group_severity_condition(self):

        detection_config, data_feed = await self._create_data_feed_and_detection_config("seriesgroupsev")
        alert_config_name = self.create_random_name("testalert")
        async with self.admin_client:
            try:
                alert_config = await self.admin_client.create_alert_configuration(
                    name=alert_config_name,
                    metric_alert_configurations=[
                        MetricAlertConfiguration(
                            detection_configuration_id=detection_config.id,
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
                assert len(alert_config.metric_alert_configurations) ==  1
                assert alert_config.metric_alert_configurations[0].detection_configuration_id is not None
                assert not alert_config.metric_alert_configurations[0].negation_operation
                assert alert_config.metric_alert_configurations[0].alert_scope.scope_type ==  "SeriesGroup"
                assert alert_config.metric_alert_configurations[0].alert_scope.series_group_in_scope ==  {'region': 'Shenzhen'}
                assert alert_config.metric_alert_configurations[0].alert_conditions.severity_condition.min_alert_severity ==  "Low"
                assert alert_config.metric_alert_configurations[0].alert_conditions.severity_condition.max_alert_severity ==  "High"

                await self.admin_client.delete_alert_configuration(alert_config.id)

                with pytest.raises(ResourceNotFoundError):
                    await self.admin_client.get_alert_configuration(alert_config.id)

            finally:
                await self.admin_client.delete_detection_configuration(detection_config.id)
                await self.admin_client.delete_data_feed(data_feed.id)

    @AzureTestCase.await_prepared_test
    async def test_create_alert_config_multiple_configurations(self):

        detection_config, data_feed = await self._create_data_feed_and_detection_config("multiple")
        alert_config_name = self.create_random_name("testalert")
        async with self.admin_client:
            try:
                alert_config = await self.admin_client.create_alert_configuration(
                    name=alert_config_name,
                    cross_metrics_operator="AND",
                    metric_alert_configurations=[
                        MetricAlertConfiguration(
                            detection_configuration_id=detection_config.id,
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
                                    companion_metric_id=data_feed.metric_ids['cost'],
                                    lower=1.0,
                                    upper=5.0
                                )
                            )
                        ),
                        MetricAlertConfiguration(
                            detection_configuration_id=detection_config.id,
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
                            detection_configuration_id=detection_config.id,
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
                assert alert_config.cross_metrics_operator ==  "AND"
                assert alert_config.id is not None
                assert alert_config.name is not None
                assert len(alert_config.metric_alert_configurations) ==  3
                assert alert_config.metric_alert_configurations[0].detection_configuration_id is not None
                assert not alert_config.metric_alert_configurations[0].negation_operation
                assert alert_config.metric_alert_configurations[0].alert_scope.scope_type ==  "TopN"
                assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.min_top_count ==  9
                assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.period ==  10
                assert alert_config.metric_alert_configurations[0].alert_scope.top_n_group_in_scope.top ==  5
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.companion_metric_id is not None
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.upper ==  5.0
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.lower ==  1.0
                assert alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.direction ==  "Both"
                assert not alert_config.metric_alert_configurations[0].alert_conditions.metric_boundary_condition.trigger_for_missing
                assert alert_config.metric_alert_configurations[1].alert_scope.scope_type ==  "SeriesGroup"
                assert alert_config.metric_alert_configurations[1].alert_conditions.severity_condition.min_alert_severity ==  "Low"
                assert alert_config.metric_alert_configurations[1].alert_conditions.severity_condition.max_alert_severity ==  "High"
                assert alert_config.metric_alert_configurations[2].alert_scope.scope_type ==  "WholeSeries"
                assert alert_config.metric_alert_configurations[2].alert_conditions.severity_condition.min_alert_severity ==  "Low"
                assert alert_config.metric_alert_configurations[2].alert_conditions.severity_condition.max_alert_severity ==  "High"

                await self.admin_client.delete_alert_configuration(alert_config.id)

                with pytest.raises(ResourceNotFoundError):
                    await self.admin_client.get_alert_configuration(alert_config.id)

            finally:
                await self.admin_client.delete_detection_configuration(detection_config.id)
                await self.admin_client.delete_data_feed(data_feed.id)

    @AzureTestCase.await_prepared_test
    async def test_list_alert_configs(self):
        async with self.admin_client:
            configs = self.admin_client.list_alert_configurations(
                detection_configuration_id=self.anomaly_detection_configuration_id
            )
            config_list = []
            async for config in configs:
                config_list.append(config)
            assert len(list(config_list)) > 0

    @AzureTestCase.await_prepared_test
    async def test_update_alert_config_with_model(self):
        async with self.admin_client:
            try:
                alert_config, data_feed, _ = await self._create_alert_config_for_update("alertupdate")

                alert_config.name = "update"
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

                await self.admin_client.update_alert_configuration(alert_config)
                updated = await self.admin_client.get_alert_configuration(alert_config.id)

                assert updated.name ==  "update"
                assert updated.description ==  "update description"
                assert updated.cross_metrics_operator ==  "OR"
                assert updated.metric_alert_configurations[0].alert_conditions.severity_condition.max_alert_severity ==  "High"
                assert updated.metric_alert_configurations[0].alert_conditions.severity_condition.min_alert_severity ==  "Low"
                assert updated.metric_alert_configurations[1].alert_conditions.metric_boundary_condition.direction ==  "Both"
                assert updated.metric_alert_configurations[1].alert_conditions.metric_boundary_condition.upper ==  5
                assert updated.metric_alert_configurations[1].alert_conditions.metric_boundary_condition.lower ==  1
                assert updated.metric_alert_configurations[2].alert_conditions.metric_boundary_condition.direction ==  "Both"
                assert updated.metric_alert_configurations[2].alert_conditions.metric_boundary_condition.upper ==  5
                assert updated.metric_alert_configurations[2].alert_conditions.metric_boundary_condition.lower ==  1

            finally:
                await self.admin_client.delete_data_feed(data_feed.id)

    @AzureTestCase.await_prepared_test
    async def test_update_alert_config_with_kwargs(self):
        async with self.admin_client:
            try:
                alert_config, data_feed, detection_config = await self._create_alert_config_for_update("alertupdate")
                await self.admin_client.update_alert_configuration(
                    alert_config.id,
                    name="update",
                    description="update description",
                    cross_metrics_operator="OR",
                    metric_alert_configurations=[
                        MetricAlertConfiguration(
                            detection_configuration_id=detection_config.id,
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
                                    companion_metric_id=data_feed.metric_ids['cost'],
                                    lower=1.0,
                                    upper=5.0
                                ),
                                severity_condition=SeverityCondition(max_alert_severity="High", min_alert_severity="Low")
                            )
                        ),
                        MetricAlertConfiguration(
                            detection_configuration_id=detection_config.id,
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
                            detection_configuration_id=detection_config.id,
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
                updated = await self.admin_client.get_alert_configuration(alert_config.id)
                assert updated.name ==  "update"
                assert updated.description ==  "update description"
                assert updated.cross_metrics_operator ==  "OR"
                assert updated.metric_alert_configurations[0].alert_conditions.severity_condition.max_alert_severity ==  "High"
                assert updated.metric_alert_configurations[0].alert_conditions.severity_condition.min_alert_severity ==  "Low"
                assert updated.metric_alert_configurations[1].alert_conditions.metric_boundary_condition.direction ==  "Both"
                assert updated.metric_alert_configurations[1].alert_conditions.metric_boundary_condition.upper ==  5
                assert updated.metric_alert_configurations[1].alert_conditions.metric_boundary_condition.lower ==  1
                assert updated.metric_alert_configurations[2].alert_conditions.metric_boundary_condition.direction ==  "Both"
                assert updated.metric_alert_configurations[2].alert_conditions.metric_boundary_condition.upper ==  5
                assert updated.metric_alert_configurations[2].alert_conditions.metric_boundary_condition.lower ==  1

            finally:
                await self.admin_client.delete_data_feed(data_feed.id)

    @AzureTestCase.await_prepared_test
    async def test_update_alert_config_with_model_and_kwargs(self):
        async with self.admin_client:
            try:
                alert_config, data_feed, detection_config = await self._create_alert_config_for_update("alertupdate")

                alert_config.name = "updateMe"
                alert_config.description = "updateMe"
                alert_config.cross_metrics_operator = "don't update me"
                alert_config.metric_alert_configurations[0].alert_conditions.severity_condition = None
                alert_config.metric_alert_configurations[1].alert_conditions.metric_boundary_condition = None
                alert_config.metric_alert_configurations[2].alert_conditions.metric_boundary_condition = None

                await self.admin_client.update_alert_configuration(
                    alert_config,
                    cross_metrics_operator="OR",
                    metric_alert_configurations=[
                        MetricAlertConfiguration(
                            detection_configuration_id=detection_config.id,
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
                                    companion_metric_id=data_feed.metric_ids['cost'],
                                    lower=1.0,
                                    upper=5.0
                                ),
                                severity_condition=SeverityCondition(max_alert_severity="High", min_alert_severity="Low")
                            )
                        ),
                        MetricAlertConfiguration(
                            detection_configuration_id=detection_config.id,
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
                            detection_configuration_id=detection_config.id,
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
                updated = await self.admin_client.get_alert_configuration(alert_config.id)
                assert updated.name ==  "updateMe"
                assert updated.description ==  "updateMe"
                assert updated.cross_metrics_operator ==  "OR"
                assert updated.metric_alert_configurations[0].alert_conditions.severity_condition.max_alert_severity ==  "High"
                assert updated.metric_alert_configurations[0].alert_conditions.severity_condition.min_alert_severity ==  "Low"
                assert updated.metric_alert_configurations[1].alert_conditions.metric_boundary_condition.direction ==  "Both"
                assert updated.metric_alert_configurations[1].alert_conditions.metric_boundary_condition.upper ==  5
                assert updated.metric_alert_configurations[1].alert_conditions.metric_boundary_condition.lower ==  1
                assert updated.metric_alert_configurations[2].alert_conditions.metric_boundary_condition.direction ==  "Both"
                assert updated.metric_alert_configurations[2].alert_conditions.metric_boundary_condition.upper ==  5
                assert updated.metric_alert_configurations[2].alert_conditions.metric_boundary_condition.lower ==  1

            finally:
                await self.admin_client.delete_data_feed(data_feed.id)

    @AzureTestCase.await_prepared_test
    async def test_update_anomaly_alert_by_resetting_properties(self):
        async with self.admin_client:
            try:
                alert_config, data_feed, detection_config = await self._create_alert_config_for_update("alertupdate")
                await self.admin_client.update_alert_configuration(
                    alert_config.id,
                    name="reset",
                    description="",  # can't pass None currently, bug says description is required
                    metric_alert_configurations=[
                        MetricAlertConfiguration(
                            detection_configuration_id=detection_config.id,
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
                updated = await self.admin_client.get_alert_configuration(alert_config.id)
                assert updated.name ==  "reset"
                assert updated.description ==  ""
                assert updated.cross_metrics_operator ==  None
                assert len(updated.metric_alert_configurations) ==  1
                assert updated.metric_alert_configurations[0].alert_conditions.severity_condition ==  None
                assert updated.metric_alert_configurations[0].alert_conditions.metric_boundary_condition ==  None

            finally:
                await self.admin_client.delete_data_feed(data_feed.id)
