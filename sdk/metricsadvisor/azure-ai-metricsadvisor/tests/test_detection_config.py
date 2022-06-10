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

from azure.ai.metricsadvisor.models import (
    MetricDetectionCondition,
    MetricSeriesGroupDetectionCondition,
    MetricSingleSeriesDetectionCondition,
    SmartDetectionCondition,
    SuppressCondition,
    ChangeThresholdCondition,
    HardThresholdCondition,
)
from devtools_testutils import recorded_by_proxy
from azure.ai.metricsadvisor import MetricsAdvisorAdministrationClient
from base_testcase import TestMetricsAdvisorClientBase, MetricsAdvisorClientPreparer, CREDENTIALS, ids
MetricsAdvisorPreparer = functools.partial(MetricsAdvisorClientPreparer, MetricsAdvisorAdministrationClient)


class TestMetricsAdvisorAdministrationClient(TestMetricsAdvisorClientBase):

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(data_feed=True)
    @recorded_by_proxy
    def test_create_ad_config_whole_series_detection(self, client, variables):
        detection_config_name = self.create_random_name("testdetectionconfig")
        if self.is_live:
            variables["detection_config_name"] = detection_config_name
        try:
            config = client.create_detection_configuration(
                name=variables["detection_config_name"],
                metric_id=variables["data_feed_metric_id"],
                description="My test metric anomaly detection configuration",
                whole_series_detection_condition=MetricDetectionCondition(
                    condition_operator="OR",
                    smart_detection_condition=SmartDetectionCondition(
                        sensitivity=50,
                        anomaly_detector_direction="Both",
                        suppress_condition=SuppressCondition(
                            min_number=5,
                            min_ratio=5
                        )
                    ),
                    hard_threshold_condition=HardThresholdCondition(
                        anomaly_detector_direction="Both",
                        suppress_condition=SuppressCondition(
                            min_number=5,
                            min_ratio=5
                        ),
                        lower_bound=0,
                        upper_bound=100
                    ),
                    change_threshold_condition=ChangeThresholdCondition(
                        change_percentage=50,
                        shift_point=30,
                        within_range=True,
                        anomaly_detector_direction="Both",
                        suppress_condition=SuppressCondition(
                            min_number=2,
                            min_ratio=2
                        )
                    )
                )
            )
            if self.is_live:
                variables["detection_config_id"] = config.id
            assert config.id is not None
            assert config.metric_id == variables["data_feed_metric_id"]
            assert config.description == "My test metric anomaly detection configuration"
            assert config.name is not None
            assert config.series_detection_conditions == []
            assert config.series_group_detection_conditions == []
            assert config.whole_series_detection_condition.condition_operator == "OR"
            assert config.whole_series_detection_condition.change_threshold_condition.anomaly_detector_direction == "Both"
            assert config.whole_series_detection_condition.change_threshold_condition.change_percentage == 50
            assert config.whole_series_detection_condition.change_threshold_condition.shift_point == 30
            assert config.whole_series_detection_condition.change_threshold_condition.within_range
            assert config.whole_series_detection_condition.change_threshold_condition.suppress_condition.min_number == 2
            assert config.whole_series_detection_condition.change_threshold_condition.suppress_condition.min_ratio == 2
            assert config.whole_series_detection_condition.hard_threshold_condition.anomaly_detector_direction == "Both"
            assert config.whole_series_detection_condition.hard_threshold_condition.lower_bound == 0
            assert config.whole_series_detection_condition.hard_threshold_condition.upper_bound == 100
            assert config.whole_series_detection_condition.hard_threshold_condition.suppress_condition.min_number == 5
            assert config.whole_series_detection_condition.hard_threshold_condition.suppress_condition.min_ratio == 5
            assert config.whole_series_detection_condition.smart_detection_condition.anomaly_detector_direction == "Both"
            assert config.whole_series_detection_condition.smart_detection_condition.sensitivity == 50
            assert config.whole_series_detection_condition.smart_detection_condition.suppress_condition.min_number == 5
            assert config.whole_series_detection_condition.smart_detection_condition.suppress_condition.min_ratio == 5

            self.clean_up(client.delete_detection_configuration, variables, key="detection_config_id")

            with pytest.raises(ResourceNotFoundError):
                client.get_detection_configuration(variables["detection_config_id"])
        finally:
            self.clean_up(client.delete_data_feed, variables)
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(data_feed=True)
    @recorded_by_proxy
    def test_create_ad_conf_series_and_group_cond(self, client, variables):
        detection_config_name = self.create_random_name("testdetectionconfig")
        if self.is_live:
            variables["detection_config_name"] = detection_config_name
        try:
            detection_config = client.create_detection_configuration(
                name=variables["detection_config_name"],
                metric_id=variables["data_feed_metric_id"],
                description="My test metric anomaly detection configuration",
                whole_series_detection_condition=MetricDetectionCondition(
                    condition_operator="AND",
                    smart_detection_condition=SmartDetectionCondition(
                        sensitivity=50,
                        anomaly_detector_direction="Both",
                        suppress_condition=SuppressCondition(
                            min_number=5,
                            min_ratio=5
                        )
                    ),
                    hard_threshold_condition=HardThresholdCondition(
                        anomaly_detector_direction="Both",
                        suppress_condition=SuppressCondition(
                            min_number=5,
                            min_ratio=5
                        ),
                        lower_bound=0,
                        upper_bound=100
                    ),
                    change_threshold_condition=ChangeThresholdCondition(
                        change_percentage=50,
                        shift_point=30,
                        within_range=True,
                        anomaly_detector_direction="Both",
                        suppress_condition=SuppressCondition(
                            min_number=2,
                            min_ratio=2
                        )
                    )
                ),
                series_detection_conditions=[MetricSingleSeriesDetectionCondition(
                    series_key={"region": "Shenzhen", "category": "Jewelry"},
                    smart_detection_condition=SmartDetectionCondition(
                        anomaly_detector_direction="Both",
                        sensitivity=63,
                        suppress_condition=SuppressCondition(
                            min_number=1,
                            min_ratio=100
                        )
                    )
                )],
                series_group_detection_conditions=[MetricSeriesGroupDetectionCondition(
                    series_group_key={"region": "Sao Paulo"},
                    smart_detection_condition=SmartDetectionCondition(
                        anomaly_detector_direction="Both",
                        sensitivity=63,
                        suppress_condition=SuppressCondition(
                            min_number=1,
                            min_ratio=100
                        )
                    )
                )]
            )

            assert detection_config.id is not None
            assert detection_config.metric_id == variables["data_feed_metric_id"]
            assert detection_config.description == "My test metric anomaly detection configuration"
            assert detection_config.name is not None
            assert detection_config.whole_series_detection_condition.condition_operator == "AND"
            assert detection_config.whole_series_detection_condition.change_threshold_condition.anomaly_detector_direction == "Both"
            assert detection_config.whole_series_detection_condition.change_threshold_condition.change_percentage == 50
            assert detection_config.whole_series_detection_condition.change_threshold_condition.shift_point == 30
            assert detection_config.whole_series_detection_condition.change_threshold_condition.within_range
            assert detection_config.whole_series_detection_condition.change_threshold_condition.suppress_condition.min_number == 2
            assert detection_config.whole_series_detection_condition.change_threshold_condition.suppress_condition.min_ratio == 2
            assert detection_config.whole_series_detection_condition.hard_threshold_condition.anomaly_detector_direction == "Both"
            assert detection_config.whole_series_detection_condition.hard_threshold_condition.lower_bound == 0
            assert detection_config.whole_series_detection_condition.hard_threshold_condition.upper_bound == 100
            assert detection_config.whole_series_detection_condition.hard_threshold_condition.suppress_condition.min_number == 5
            assert detection_config.whole_series_detection_condition.hard_threshold_condition.suppress_condition.min_ratio == 5
            assert detection_config.whole_series_detection_condition.smart_detection_condition.anomaly_detector_direction == "Both"
            assert detection_config.whole_series_detection_condition.smart_detection_condition.sensitivity == 50
            assert detection_config.whole_series_detection_condition.smart_detection_condition.suppress_condition.min_number == 5
            assert detection_config.whole_series_detection_condition.smart_detection_condition.suppress_condition.min_ratio == 5
            assert detection_config.series_detection_conditions[0].smart_detection_condition.suppress_condition.min_ratio == 100
            assert detection_config.series_detection_conditions[0].smart_detection_condition.suppress_condition.min_number == 1
            assert detection_config.series_detection_conditions[0].smart_detection_condition.sensitivity == 63
            assert detection_config.series_detection_conditions[0].smart_detection_condition.anomaly_detector_direction == "Both"
            assert detection_config.series_detection_conditions[0].series_key == {'region': 'Shenzhen',  'category': 'Jewelry'}
            assert detection_config.series_group_detection_conditions[0].smart_detection_condition.suppress_condition.min_ratio == 100
            assert detection_config.series_group_detection_conditions[0].smart_detection_condition.suppress_condition.min_number == 1
            assert detection_config.series_group_detection_conditions[0].smart_detection_condition.sensitivity == 63
            assert detection_config.series_group_detection_conditions[0].smart_detection_condition.anomaly_detector_direction == "Both"
            assert detection_config.series_group_detection_conditions[0].series_group_key == {'region': 'Sao Paulo'}
        finally:
            self.clean_up(client.delete_data_feed, variables)
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(data_feed=True)
    @recorded_by_proxy
    def test_create_ad_conf_series_and_group_conds(self, client, variables):
        detection_config_name = self.create_random_name("testdetectionconfig")
        if self.is_live:
            variables["detection_config_name"] = detection_config_name
        try:
            detection_config = client.create_detection_configuration(
                name=variables["detection_config_name"],
                metric_id=variables["data_feed_metric_id"],
                description="My test metric anomaly detection configuration",
                whole_series_detection_condition=MetricDetectionCondition(
                    condition_operator="AND",
                    smart_detection_condition=SmartDetectionCondition(
                        sensitivity=50,
                        anomaly_detector_direction="Both",
                        suppress_condition=SuppressCondition(
                            min_number=5,
                            min_ratio=5
                        )
                    ),
                    hard_threshold_condition=HardThresholdCondition(
                        anomaly_detector_direction="Both",
                        suppress_condition=SuppressCondition(
                            min_number=5,
                            min_ratio=5
                        ),
                        lower_bound=0,
                        upper_bound=100
                    ),
                    change_threshold_condition=ChangeThresholdCondition(
                        change_percentage=50,
                        shift_point=30,
                        within_range=True,
                        anomaly_detector_direction="Both",
                        suppress_condition=SuppressCondition(
                            min_number=2,
                            min_ratio=2
                        )
                    )
                ),
                series_detection_conditions=[
                    MetricSingleSeriesDetectionCondition(
                        series_key={"region": "Shenzhen", "category": "Jewelry"},
                        condition_operator="AND",
                        smart_detection_condition=SmartDetectionCondition(
                            anomaly_detector_direction="Both",
                            sensitivity=63,
                            suppress_condition=SuppressCondition(
                                min_number=1,
                                min_ratio=100
                            )
                        ),
                        hard_threshold_condition=HardThresholdCondition(
                            anomaly_detector_direction="Both",
                            suppress_condition=SuppressCondition(
                                min_number=5,
                                min_ratio=5
                            ),
                            lower_bound=0,
                            upper_bound=100
                        ),
                        change_threshold_condition=ChangeThresholdCondition(
                            change_percentage=50,
                            shift_point=30,
                            within_range=True,
                            anomaly_detector_direction="Both",
                            suppress_condition=SuppressCondition(
                                min_number=2,
                                min_ratio=2
                            )
                        )
                    ),
                    MetricSingleSeriesDetectionCondition(
                        series_key={"region": "Osaka", "category": "Cell Phones"},
                        condition_operator="AND",
                        smart_detection_condition=SmartDetectionCondition(
                            anomaly_detector_direction="Both",
                            sensitivity=63,
                            suppress_condition=SuppressCondition(
                                min_number=1,
                                min_ratio=100
                            )
                        )
                    )
                ],
                series_group_detection_conditions=[
                    MetricSeriesGroupDetectionCondition(
                        series_group_key={"region": "Sao Paulo"},
                        condition_operator="AND",
                        smart_detection_condition=SmartDetectionCondition(
                            anomaly_detector_direction="Both",
                            sensitivity=63,
                            suppress_condition=SuppressCondition(
                                min_number=1,
                                min_ratio=100
                            )
                        ),
                        hard_threshold_condition=HardThresholdCondition(
                            anomaly_detector_direction="Both",
                            suppress_condition=SuppressCondition(
                                min_number=5,
                                min_ratio=5
                            ),
                            lower_bound=0,
                            upper_bound=100
                        ),
                        change_threshold_condition=ChangeThresholdCondition(
                            change_percentage=50,
                            shift_point=30,
                            within_range=True,
                            anomaly_detector_direction="Both",
                            suppress_condition=SuppressCondition(
                                min_number=2,
                                min_ratio=2
                            )
                        )
                    ),
                    MetricSeriesGroupDetectionCondition(
                        series_group_key={"region": "Seoul"},
                        condition_operator="AND",
                        smart_detection_condition=SmartDetectionCondition(
                            anomaly_detector_direction="Both",
                            sensitivity=63,
                            suppress_condition=SuppressCondition(
                                min_number=1,
                                min_ratio=100
                            )
                        )
                    )
                ]
            )

            assert detection_config.id is not None
            assert detection_config.metric_id == variables["data_feed_metric_id"]
            assert detection_config.description == "My test metric anomaly detection configuration"
            assert detection_config.name is not None

            # whole series detection condition
            assert detection_config.whole_series_detection_condition.condition_operator == "AND"
            assert detection_config.whole_series_detection_condition.change_threshold_condition.anomaly_detector_direction == "Both"
            assert detection_config.whole_series_detection_condition.change_threshold_condition.change_percentage == 50
            assert detection_config.whole_series_detection_condition.change_threshold_condition.shift_point == 30
            assert detection_config.whole_series_detection_condition.change_threshold_condition.within_range
            assert detection_config.whole_series_detection_condition.change_threshold_condition.suppress_condition.min_number == 2
            assert detection_config.whole_series_detection_condition.change_threshold_condition.suppress_condition.min_ratio == 2
            assert detection_config.whole_series_detection_condition.hard_threshold_condition.anomaly_detector_direction == "Both"
            assert detection_config.whole_series_detection_condition.hard_threshold_condition.lower_bound == 0
            assert detection_config.whole_series_detection_condition.hard_threshold_condition.upper_bound == 100
            assert detection_config.whole_series_detection_condition.hard_threshold_condition.suppress_condition.min_number == 5
            assert detection_config.whole_series_detection_condition.hard_threshold_condition.suppress_condition.min_ratio == 5
            assert detection_config.whole_series_detection_condition.smart_detection_condition.anomaly_detector_direction == "Both"
            assert detection_config.whole_series_detection_condition.smart_detection_condition.sensitivity == 50
            assert detection_config.whole_series_detection_condition.smart_detection_condition.suppress_condition.min_number == 5
            assert detection_config.whole_series_detection_condition.smart_detection_condition.suppress_condition.min_ratio == 5

            # series detection conditions
            assert detection_config.series_detection_conditions[0].series_key == {'region': 'Shenzhen',  'category': 'Jewelry'}
            assert detection_config.series_detection_conditions[0].condition_operator == "AND"
            assert detection_config.series_detection_conditions[0].smart_detection_condition.suppress_condition.min_ratio == 100
            assert detection_config.series_detection_conditions[0].smart_detection_condition.suppress_condition.min_number == 1
            assert detection_config.series_detection_conditions[0].smart_detection_condition.sensitivity == 63
            assert detection_config.series_detection_conditions[0].smart_detection_condition.anomaly_detector_direction == "Both"
            assert detection_config.series_detection_conditions[0].change_threshold_condition.anomaly_detector_direction == "Both"
            assert detection_config.series_detection_conditions[0].change_threshold_condition.change_percentage == 50
            assert detection_config.series_detection_conditions[0].change_threshold_condition.shift_point == 30
            assert detection_config.series_detection_conditions[0].change_threshold_condition.within_range
            assert detection_config.series_detection_conditions[0].change_threshold_condition.suppress_condition.min_number == 2
            assert detection_config.series_detection_conditions[0].change_threshold_condition.suppress_condition.min_ratio == 2
            assert detection_config.series_detection_conditions[0].hard_threshold_condition.anomaly_detector_direction == "Both"
            assert detection_config.series_detection_conditions[0].hard_threshold_condition.lower_bound == 0
            assert detection_config.series_detection_conditions[0].hard_threshold_condition.upper_bound == 100
            assert detection_config.series_detection_conditions[0].hard_threshold_condition.suppress_condition.min_number == 5
            assert detection_config.series_detection_conditions[0].hard_threshold_condition.suppress_condition.min_ratio == 5
            assert detection_config.series_detection_conditions[1].series_key == {"region": "Osaka",  "category": "Cell Phones"}
            assert detection_config.series_detection_conditions[1].smart_detection_condition.suppress_condition.min_ratio == 100
            assert detection_config.series_detection_conditions[1].smart_detection_condition.suppress_condition.min_number == 1
            assert detection_config.series_detection_conditions[1].smart_detection_condition.sensitivity == 63
            assert detection_config.series_detection_conditions[1].smart_detection_condition.anomaly_detector_direction == "Both"

            # series group detection conditions
            assert detection_config.series_group_detection_conditions[0].series_group_key == {"region": "Sao Paulo"}
            assert detection_config.series_group_detection_conditions[0].condition_operator == "AND"
            assert detection_config.series_group_detection_conditions[0].smart_detection_condition.suppress_condition.min_ratio == 100
            assert detection_config.series_group_detection_conditions[0].smart_detection_condition.suppress_condition.min_number == 1
            assert detection_config.series_group_detection_conditions[0].smart_detection_condition.sensitivity == 63
            assert detection_config.series_group_detection_conditions[0].smart_detection_condition.anomaly_detector_direction == "Both"
            assert detection_config.series_group_detection_conditions[0].change_threshold_condition.anomaly_detector_direction == "Both"
            assert detection_config.series_group_detection_conditions[0].change_threshold_condition.change_percentage == 50
            assert detection_config.series_group_detection_conditions[0].change_threshold_condition.shift_point == 30
            assert detection_config.series_group_detection_conditions[0].change_threshold_condition.within_range
            assert detection_config.series_group_detection_conditions[0].change_threshold_condition.suppress_condition.min_number == 2
            assert detection_config.series_group_detection_conditions[0].change_threshold_condition.suppress_condition.min_ratio == 2
            assert detection_config.series_group_detection_conditions[0].hard_threshold_condition.anomaly_detector_direction == "Both"
            assert detection_config.series_group_detection_conditions[0].hard_threshold_condition.lower_bound == 0
            assert detection_config.series_group_detection_conditions[0].hard_threshold_condition.upper_bound == 100
            assert detection_config.series_group_detection_conditions[0].hard_threshold_condition.suppress_condition.min_number == 5
            assert detection_config.series_group_detection_conditions[0].hard_threshold_condition.suppress_condition.min_ratio == 5
            assert detection_config.series_group_detection_conditions[1].series_group_key == {"region": "Seoul"}
            assert detection_config.series_group_detection_conditions[1].smart_detection_condition.suppress_condition.min_ratio == 100
            assert detection_config.series_group_detection_conditions[1].smart_detection_condition.suppress_condition.min_number == 1
            assert detection_config.series_group_detection_conditions[1].smart_detection_condition.sensitivity == 63
            assert detection_config.series_group_detection_conditions[1].smart_detection_condition.anomaly_detector_direction == "Both"

        finally:
            self.clean_up(client.delete_data_feed, variables)
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_list_detection_configs(self, client, **kwargs):
        configs = client.list_detection_configurations(metric_id=self.metric_id)
        assert len(list(configs)) > 0

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(data_feed=True, detection_config=True)
    @recorded_by_proxy
    def test_update_detection_config_with_model(self, client, variables):
        try:
            detection_config = client.get_detection_configuration(variables["detection_config_id"])
            update_name = "update" + str(uuid.uuid4())
            if self.is_live:
                variables["data_feed_updated_name"] = update_name
            detection_config.name = variables["data_feed_updated_name"]
            detection_config.description = "updated"
            change_threshold_condition = ChangeThresholdCondition(
                anomaly_detector_direction="Both",
                change_percentage=20,
                shift_point=10,
                within_range=True,
                suppress_condition=SuppressCondition(
                    min_number=5,
                    min_ratio=2
                )
            )
            hard_threshold_condition = HardThresholdCondition(
                anomaly_detector_direction="Up",
                upper_bound=100,
                suppress_condition=SuppressCondition(
                    min_number=5,
                    min_ratio=2
                )
            )
            smart_detection_condition = SmartDetectionCondition(
                anomaly_detector_direction="Up",
                sensitivity=10,
                suppress_condition=SuppressCondition(
                    min_number=5,
                    min_ratio=2
                )
            )
            detection_config.series_detection_conditions[0].change_threshold_condition = change_threshold_condition
            detection_config.series_detection_conditions[0].hard_threshold_condition = hard_threshold_condition
            detection_config.series_detection_conditions[0].smart_detection_condition = smart_detection_condition
            detection_config.series_detection_conditions[0].condition_operator = "AND"
            detection_config.series_group_detection_conditions[0].change_threshold_condition = change_threshold_condition
            detection_config.series_group_detection_conditions[0].hard_threshold_condition = hard_threshold_condition
            detection_config.series_group_detection_conditions[0].smart_detection_condition = smart_detection_condition
            detection_config.series_group_detection_conditions[0].condition_operator = "AND"
            detection_config.whole_series_detection_condition.hard_threshold_condition = hard_threshold_condition
            detection_config.whole_series_detection_condition.smart_detection_condition = smart_detection_condition
            detection_config.whole_series_detection_condition.change_threshold_condition = change_threshold_condition
            detection_config.whole_series_detection_condition.condition_operator = "OR"

            client.update_detection_configuration(detection_config)
            updated = client.get_detection_configuration(variables["detection_config_id"])

            assert updated.name == variables["data_feed_updated_name"]
            assert updated.description == "updated"
            assert updated.series_detection_conditions[0].change_threshold_condition.anomaly_detector_direction == "Both"
            assert updated.series_detection_conditions[0].change_threshold_condition.change_percentage == 20
            assert updated.series_detection_conditions[0].change_threshold_condition.shift_point == 10
            assert updated.series_detection_conditions[0].change_threshold_condition.within_range
            assert updated.series_detection_conditions[0].change_threshold_condition.suppress_condition.min_number == 5
            assert updated.series_detection_conditions[0].change_threshold_condition.suppress_condition.min_ratio == 2
            assert updated.series_detection_conditions[0].hard_threshold_condition.anomaly_detector_direction == "Up"
            assert updated.series_detection_conditions[0].hard_threshold_condition.upper_bound == 100
            assert updated.series_detection_conditions[0].hard_threshold_condition.suppress_condition.min_number == 5
            assert updated.series_detection_conditions[0].hard_threshold_condition.suppress_condition.min_ratio == 2
            assert updated.series_detection_conditions[0].smart_detection_condition.anomaly_detector_direction == "Up"
            assert updated.series_detection_conditions[0].smart_detection_condition.sensitivity == 10
            assert updated.series_detection_conditions[0].smart_detection_condition.suppress_condition.min_number == 5
            assert updated.series_detection_conditions[0].smart_detection_condition.suppress_condition.min_ratio == 2
            assert updated.series_detection_conditions[0].condition_operator == "AND"

            assert updated.series_group_detection_conditions[0].change_threshold_condition.anomaly_detector_direction == "Both"
            assert updated.series_group_detection_conditions[0].change_threshold_condition.change_percentage == 20
            assert updated.series_group_detection_conditions[0].change_threshold_condition.shift_point == 10
            assert updated.series_group_detection_conditions[0].change_threshold_condition.within_range
            assert updated.series_group_detection_conditions[0].change_threshold_condition.suppress_condition.min_number == 5
            assert updated.series_group_detection_conditions[0].change_threshold_condition.suppress_condition.min_ratio == 2
            assert updated.series_group_detection_conditions[0].hard_threshold_condition.anomaly_detector_direction == "Up"
            assert updated.series_group_detection_conditions[0].hard_threshold_condition.upper_bound == 100
            assert updated.series_group_detection_conditions[0].hard_threshold_condition.suppress_condition.min_number == 5
            assert updated.series_group_detection_conditions[0].hard_threshold_condition.suppress_condition.min_ratio == 2
            assert updated.series_group_detection_conditions[0].smart_detection_condition.anomaly_detector_direction == "Up"
            assert updated.series_group_detection_conditions[0].smart_detection_condition.sensitivity == 10
            assert updated.series_group_detection_conditions[0].smart_detection_condition.suppress_condition.min_number == 5
            assert updated.series_group_detection_conditions[0].smart_detection_condition.suppress_condition.min_ratio == 2
            assert updated.series_group_detection_conditions[0].condition_operator == "AND"

            assert updated.whole_series_detection_condition.change_threshold_condition.anomaly_detector_direction == "Both"
            assert updated.whole_series_detection_condition.change_threshold_condition.change_percentage == 20
            assert updated.whole_series_detection_condition.change_threshold_condition.shift_point == 10
            assert updated.whole_series_detection_condition.change_threshold_condition.within_range
            assert updated.whole_series_detection_condition.change_threshold_condition.suppress_condition.min_number == 5
            assert updated.whole_series_detection_condition.change_threshold_condition.suppress_condition.min_ratio == 2
            assert updated.whole_series_detection_condition.hard_threshold_condition.anomaly_detector_direction == "Up"
            assert updated.whole_series_detection_condition.hard_threshold_condition.upper_bound == 100
            assert updated.whole_series_detection_condition.hard_threshold_condition.suppress_condition.min_number == 5
            assert updated.whole_series_detection_condition.hard_threshold_condition.suppress_condition.min_ratio == 2
            assert updated.whole_series_detection_condition.smart_detection_condition.anomaly_detector_direction == "Up"
            assert updated.whole_series_detection_condition.smart_detection_condition.sensitivity == 10
            assert updated.whole_series_detection_condition.smart_detection_condition.suppress_condition.min_number == 5
            assert updated.whole_series_detection_condition.smart_detection_condition.suppress_condition.min_ratio == 2
            assert updated.whole_series_detection_condition.condition_operator == "OR"
        finally:
            self.clean_up(client.delete_data_feed, variables)
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(data_feed=True, detection_config=True)
    @recorded_by_proxy
    def test_update_detection_config_with_kwargs(self, client, variables):
        try:
            change_threshold_condition = ChangeThresholdCondition(
                anomaly_detector_direction="Both",
                change_percentage=20,
                shift_point=10,
                within_range=True,
                suppress_condition=SuppressCondition(
                    min_number=5,
                    min_ratio=2
                )
            )
            hard_threshold_condition = HardThresholdCondition(
                anomaly_detector_direction="Up",
                upper_bound=100,
                suppress_condition=SuppressCondition(
                    min_number=5,
                    min_ratio=2
                )
            )
            smart_detection_condition = SmartDetectionCondition(
                anomaly_detector_direction="Up",
                sensitivity=10,
                suppress_condition=SuppressCondition(
                    min_number=5,
                    min_ratio=2
                )
            )
            update_name = "update" + str(uuid.uuid4())
            if self.is_live:
                variables["data_feed_updated_name"] = update_name
            client.update_detection_configuration(
                variables["detection_config_id"],
                name=variables["data_feed_updated_name"],
                description="updated",
                whole_series_detection_condition=MetricDetectionCondition(
                    condition_operator="OR",
                    smart_detection_condition=smart_detection_condition,
                    hard_threshold_condition=hard_threshold_condition,
                    change_threshold_condition=change_threshold_condition
                ),
                series_detection_conditions=[MetricSingleSeriesDetectionCondition(
                    series_key={"region": "San Paulo", "category": "Jewelry"},
                    condition_operator="AND",
                    smart_detection_condition=smart_detection_condition,
                    hard_threshold_condition=hard_threshold_condition,
                    change_threshold_condition=change_threshold_condition
                )],
                series_group_detection_conditions=[MetricSeriesGroupDetectionCondition(
                    series_group_key={"region": "Shenzen"},
                    condition_operator="AND",
                    smart_detection_condition=smart_detection_condition,
                    hard_threshold_condition=hard_threshold_condition,
                    change_threshold_condition=change_threshold_condition
                )]
            )
            updated = client.get_detection_configuration(variables["detection_config_id"])
            assert updated.name == variables["data_feed_updated_name"]
            assert updated.description == "updated"
            assert updated.series_detection_conditions[0].change_threshold_condition.anomaly_detector_direction == "Both"
            assert updated.series_detection_conditions[0].change_threshold_condition.change_percentage == 20
            assert updated.series_detection_conditions[0].change_threshold_condition.shift_point == 10
            assert updated.series_detection_conditions[0].change_threshold_condition.within_range
            assert updated.series_detection_conditions[0].change_threshold_condition.suppress_condition.min_number == 5
            assert updated.series_detection_conditions[0].change_threshold_condition.suppress_condition.min_ratio == 2
            assert updated.series_detection_conditions[0].hard_threshold_condition.anomaly_detector_direction == "Up"
            assert updated.series_detection_conditions[0].hard_threshold_condition.upper_bound == 100
            assert updated.series_detection_conditions[0].hard_threshold_condition.suppress_condition.min_number == 5
            assert updated.series_detection_conditions[0].hard_threshold_condition.suppress_condition.min_ratio == 2
            assert updated.series_detection_conditions[0].smart_detection_condition.anomaly_detector_direction == "Up"
            assert updated.series_detection_conditions[0].smart_detection_condition.sensitivity == 10
            assert updated.series_detection_conditions[0].smart_detection_condition.suppress_condition.min_number == 5
            assert updated.series_detection_conditions[0].smart_detection_condition.suppress_condition.min_ratio == 2
            assert updated.series_detection_conditions[0].condition_operator == "AND"
            assert updated.series_detection_conditions[0].series_key == {"region": "San Paulo",  "category": "Jewelry"}

            assert updated.series_group_detection_conditions[0].change_threshold_condition.anomaly_detector_direction == "Both"
            assert updated.series_group_detection_conditions[0].change_threshold_condition.change_percentage == 20
            assert updated.series_group_detection_conditions[0].change_threshold_condition.shift_point == 10
            assert updated.series_group_detection_conditions[0].change_threshold_condition.within_range
            assert updated.series_group_detection_conditions[0].change_threshold_condition.suppress_condition.min_number == 5
            assert updated.series_group_detection_conditions[0].change_threshold_condition.suppress_condition.min_ratio == 2
            assert updated.series_group_detection_conditions[0].hard_threshold_condition.anomaly_detector_direction == "Up"
            assert updated.series_group_detection_conditions[0].hard_threshold_condition.upper_bound == 100
            assert updated.series_group_detection_conditions[0].hard_threshold_condition.suppress_condition.min_number == 5
            assert updated.series_group_detection_conditions[0].hard_threshold_condition.suppress_condition.min_ratio == 2
            assert updated.series_group_detection_conditions[0].smart_detection_condition.anomaly_detector_direction == "Up"
            assert updated.series_group_detection_conditions[0].smart_detection_condition.sensitivity == 10
            assert updated.series_group_detection_conditions[0].smart_detection_condition.suppress_condition.min_number == 5
            assert updated.series_group_detection_conditions[0].smart_detection_condition.suppress_condition.min_ratio == 2
            assert updated.series_group_detection_conditions[0].condition_operator == "AND"
            assert updated.series_group_detection_conditions[0].series_group_key == {"region": "Shenzen"}

            assert updated.whole_series_detection_condition.change_threshold_condition.anomaly_detector_direction == "Both"
            assert updated.whole_series_detection_condition.change_threshold_condition.change_percentage == 20
            assert updated.whole_series_detection_condition.change_threshold_condition.shift_point == 10
            assert updated.whole_series_detection_condition.change_threshold_condition.within_range
            assert updated.whole_series_detection_condition.change_threshold_condition.suppress_condition.min_number == 5
            assert updated.whole_series_detection_condition.change_threshold_condition.suppress_condition.min_ratio == 2
            assert updated.whole_series_detection_condition.hard_threshold_condition.anomaly_detector_direction == "Up"
            assert updated.whole_series_detection_condition.hard_threshold_condition.upper_bound == 100
            assert updated.whole_series_detection_condition.hard_threshold_condition.suppress_condition.min_number == 5
            assert updated.whole_series_detection_condition.hard_threshold_condition.suppress_condition.min_ratio == 2
            assert updated.whole_series_detection_condition.smart_detection_condition.anomaly_detector_direction == "Up"
            assert updated.whole_series_detection_condition.smart_detection_condition.sensitivity == 10
            assert updated.whole_series_detection_condition.smart_detection_condition.suppress_condition.min_number == 5
            assert updated.whole_series_detection_condition.smart_detection_condition.suppress_condition.min_ratio == 2
            assert updated.whole_series_detection_condition.condition_operator == "OR"
        finally:
            self.clean_up(client.delete_data_feed, variables)
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(data_feed=True, detection_config=True)
    @recorded_by_proxy
    def test_update_ad_conf_model_and_kwargs(self, client, variables):
        try:
            detection_config = client.get_detection_configuration(variables["detection_config_id"])
            change_threshold_condition = ChangeThresholdCondition(
                anomaly_detector_direction="Both",
                change_percentage=20,
                shift_point=10,
                within_range=True,
                suppress_condition=SuppressCondition(
                    min_number=5,
                    min_ratio=2
                )
            )
            hard_threshold_condition = HardThresholdCondition(
                anomaly_detector_direction="Up",
                upper_bound=100,
                suppress_condition=SuppressCondition(
                    min_number=5,
                    min_ratio=2
                )
            )
            smart_detection_condition = SmartDetectionCondition(
                anomaly_detector_direction="Up",
                sensitivity=10,
                suppress_condition=SuppressCondition(
                    min_number=5,
                    min_ratio=2
                )
            )
            update_name = "update" + str(uuid.uuid4())
            if self.is_live:
                variables["data_feed_updated_name"] = update_name
            detection_config.name = variables["data_feed_updated_name"]
            detection_config.description = "updateMe"
            client.update_detection_configuration(
                detection_config,
                whole_series_detection_condition=MetricDetectionCondition(
                    condition_operator="OR",
                    smart_detection_condition=smart_detection_condition,
                    hard_threshold_condition=hard_threshold_condition,
                    change_threshold_condition=change_threshold_condition
                ),
                series_detection_conditions=[MetricSingleSeriesDetectionCondition(
                    series_key={"region": "San Paulo", "category": "Jewelry"},
                    condition_operator="AND",
                    smart_detection_condition=smart_detection_condition,
                    hard_threshold_condition=hard_threshold_condition,
                    change_threshold_condition=change_threshold_condition
                )],
                series_group_detection_conditions=[MetricSeriesGroupDetectionCondition(
                    series_group_key={"region": "Shenzen"},
                    condition_operator="AND",
                    smart_detection_condition=smart_detection_condition,
                    hard_threshold_condition=hard_threshold_condition,
                    change_threshold_condition=change_threshold_condition
                )]
            )
            updated = client.get_detection_configuration(variables["detection_config_id"])
            assert updated.name == variables["data_feed_updated_name"]
            assert updated.description == "updateMe"
            assert updated.series_detection_conditions[0].change_threshold_condition.anomaly_detector_direction == "Both"
            assert updated.series_detection_conditions[0].change_threshold_condition.change_percentage == 20
            assert updated.series_detection_conditions[0].change_threshold_condition.shift_point == 10
            assert updated.series_detection_conditions[0].change_threshold_condition.within_range
            assert updated.series_detection_conditions[0].change_threshold_condition.suppress_condition.min_number == 5
            assert updated.series_detection_conditions[0].change_threshold_condition.suppress_condition.min_ratio == 2
            assert updated.series_detection_conditions[0].hard_threshold_condition.anomaly_detector_direction == "Up"
            assert updated.series_detection_conditions[0].hard_threshold_condition.upper_bound == 100
            assert updated.series_detection_conditions[0].hard_threshold_condition.suppress_condition.min_number == 5
            assert updated.series_detection_conditions[0].hard_threshold_condition.suppress_condition.min_ratio == 2
            assert updated.series_detection_conditions[0].smart_detection_condition.anomaly_detector_direction == "Up"
            assert updated.series_detection_conditions[0].smart_detection_condition.sensitivity == 10
            assert updated.series_detection_conditions[0].smart_detection_condition.suppress_condition.min_number == 5
            assert updated.series_detection_conditions[0].smart_detection_condition.suppress_condition.min_ratio == 2
            assert updated.series_detection_conditions[0].condition_operator == "AND"
            assert updated.series_detection_conditions[0].series_key == {"region": "San Paulo",  "category": "Jewelry"}

            assert updated.series_group_detection_conditions[0].change_threshold_condition.anomaly_detector_direction == "Both"
            assert updated.series_group_detection_conditions[0].change_threshold_condition.change_percentage == 20
            assert updated.series_group_detection_conditions[0].change_threshold_condition.shift_point == 10
            assert updated.series_group_detection_conditions[0].change_threshold_condition.within_range
            assert updated.series_group_detection_conditions[0].change_threshold_condition.suppress_condition.min_number == 5
            assert updated.series_group_detection_conditions[0].change_threshold_condition.suppress_condition.min_ratio == 2
            assert updated.series_group_detection_conditions[0].hard_threshold_condition.anomaly_detector_direction == "Up"
            assert updated.series_group_detection_conditions[0].hard_threshold_condition.upper_bound == 100
            assert updated.series_group_detection_conditions[0].hard_threshold_condition.suppress_condition.min_number == 5
            assert updated.series_group_detection_conditions[0].hard_threshold_condition.suppress_condition.min_ratio == 2
            assert updated.series_group_detection_conditions[0].smart_detection_condition.anomaly_detector_direction == "Up"
            assert updated.series_group_detection_conditions[0].smart_detection_condition.sensitivity == 10
            assert updated.series_group_detection_conditions[0].smart_detection_condition.suppress_condition.min_number == 5
            assert updated.series_group_detection_conditions[0].smart_detection_condition.suppress_condition.min_ratio == 2
            assert updated.series_group_detection_conditions[0].condition_operator == "AND"
            assert updated.series_group_detection_conditions[0].series_group_key == {"region": "Shenzen"}

            assert updated.whole_series_detection_condition.change_threshold_condition.anomaly_detector_direction == "Both"
            assert updated.whole_series_detection_condition.change_threshold_condition.change_percentage == 20
            assert updated.whole_series_detection_condition.change_threshold_condition.shift_point == 10
            assert updated.whole_series_detection_condition.change_threshold_condition.within_range
            assert updated.whole_series_detection_condition.change_threshold_condition.suppress_condition.min_number == 5
            assert updated.whole_series_detection_condition.change_threshold_condition.suppress_condition.min_ratio == 2
            assert updated.whole_series_detection_condition.hard_threshold_condition.anomaly_detector_direction == "Up"
            assert updated.whole_series_detection_condition.hard_threshold_condition.upper_bound == 100
            assert updated.whole_series_detection_condition.hard_threshold_condition.suppress_condition.min_number == 5
            assert updated.whole_series_detection_condition.hard_threshold_condition.suppress_condition.min_ratio == 2
            assert updated.whole_series_detection_condition.smart_detection_condition.anomaly_detector_direction == "Up"
            assert updated.whole_series_detection_condition.smart_detection_condition.sensitivity == 10
            assert updated.whole_series_detection_condition.smart_detection_condition.suppress_condition.min_number == 5
            assert updated.whole_series_detection_condition.smart_detection_condition.suppress_condition.min_ratio == 2
            assert updated.whole_series_detection_condition.condition_operator == "OR"
        finally:
            self.clean_up(client.delete_data_feed, variables)
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer(data_feed=True, detection_config=True)
    @recorded_by_proxy
    def test_update_ad_conf_by_reset_props(self, client, variables):
        try:
            update_name = "update" + str(uuid.uuid4())
            if self.is_live:
                variables["data_feed_updated_name"] = update_name
            client.update_detection_configuration(
                variables["detection_config_id"],
                name=variables["data_feed_updated_name"],
                description="",
                # series_detection_conditions=None,
                # series_group_detection_conditions=None
            )
            updated = client.get_detection_configuration(variables["detection_config_id"])
            assert updated.name == variables["data_feed_updated_name"]
            assert updated.description == ""  # currently won't update with None

            # service bug says these are required
            # assert updated.series_detection_conditions == None
            # assert updated.series_group_detection_conditions == None

        finally:
            self.clean_up(client.delete_data_feed, variables)
        return variables
