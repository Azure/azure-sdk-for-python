# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from devtools_testutils import AzureTestCase
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

from base_testcase_async import TestMetricsAdvisorAdministrationClientBaseAsync


class TestMetricsAdvisorAdministrationClientAsync(TestMetricsAdvisorAdministrationClientBaseAsync):

    @AzureTestCase.await_prepared_test
    async def test_create_ad_config_whole_series_detection(self):

        data_feed = await self._create_data_feed("adconfigasync")
        async with self.admin_client:
            try:
                detection_config_name = self.create_random_name("testdetectionconfigasync")
                config = await self.admin_client.create_detection_configuration(
                    name=detection_config_name,
                    metric_id=data_feed.metric_ids[0],
                    description="My test metric anomaly detection configuration",
                    whole_series_detection_condition=MetricDetectionCondition(
                        cross_conditions_operator="OR",
                        smart_detection_condition=SmartDetectionCondition(
                            sensitivity=50,
                            anomaly_detector_direction="Both",
                            suppress_condition=SuppressCondition(
                                min_number=50,
                                min_ratio=50
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
                self.assertIsNotNone(config.id)
                self.assertEqual(config.metric_id, data_feed.metric_ids[0])
                self.assertEqual(config.description, "My test metric anomaly detection configuration")
                self.assertIsNotNone(config.name)
                self.assertIsNone(config.series_detection_conditions)
                self.assertIsNone(config.series_group_detection_conditions)
                self.assertEqual(config.whole_series_detection_condition.cross_conditions_operator, "OR")
                self.assertEqual(
                    config.whole_series_detection_condition.change_threshold_condition.anomaly_detector_direction, "Both")
                self.assertEqual(config.whole_series_detection_condition.change_threshold_condition.change_percentage, 50)
                self.assertEqual(config.whole_series_detection_condition.change_threshold_condition.shift_point, 30)
                self.assertTrue(config.whole_series_detection_condition.change_threshold_condition.within_range)
                self.assertEqual(
                    config.whole_series_detection_condition.change_threshold_condition.suppress_condition.min_number, 2)
                self.assertEqual(
                    config.whole_series_detection_condition.change_threshold_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(
                    config.whole_series_detection_condition.hard_threshold_condition.anomaly_detector_direction, "Both")
                self.assertEqual(config.whole_series_detection_condition.hard_threshold_condition.lower_bound, 0)
                self.assertEqual(config.whole_series_detection_condition.hard_threshold_condition.upper_bound, 100)
                self.assertEqual(
                    config.whole_series_detection_condition.hard_threshold_condition.suppress_condition.min_number, 5)
                self.assertEqual(
                    config.whole_series_detection_condition.hard_threshold_condition.suppress_condition.min_ratio, 5)
                self.assertEqual(
                    config.whole_series_detection_condition.smart_detection_condition.anomaly_detector_direction, "Both")
                self.assertEqual(config.whole_series_detection_condition.smart_detection_condition.sensitivity, 50)
                self.assertEqual(
                    config.whole_series_detection_condition.smart_detection_condition.suppress_condition.min_number, 50)
                self.assertEqual(
                    config.whole_series_detection_condition.smart_detection_condition.suppress_condition.min_ratio, 50)

                await self.admin_client.delete_detection_configuration(config.id)

                with self.assertRaises(ResourceNotFoundError):
                    await self.admin_client.get_detection_configuration(config.id)
            finally:
                await self.admin_client.delete_data_feed(data_feed.id)

    @AzureTestCase.await_prepared_test
    async def test_create_ad_config_with_series_and_group_conds(self):
        data_feed = await self._create_data_feed("adconfiggetasync")
        async with self.admin_client:
            try:
                detection_config_name = self.create_random_name("testdetectionconfigetasync")
                detection_config = await self.admin_client.create_detection_configuration(
                    name=detection_config_name,
                    metric_id=data_feed.metric_ids[0],
                    description="My test metric anomaly detection configuration",
                    whole_series_detection_condition=MetricDetectionCondition(
                        cross_conditions_operator="AND",
                        smart_detection_condition=SmartDetectionCondition(
                            sensitivity=50,
                            anomaly_detector_direction="Both",
                            suppress_condition=SuppressCondition(
                                min_number=50,
                                min_ratio=50
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
                        series_key={"city": "Shenzhen", "category": "Jewelry"},
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
                        series_group_key={"city": "Sao Paulo"},
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

                self.assertIsNotNone(detection_config.id)
                self.assertEqual(detection_config.metric_id, data_feed.metric_ids[0])
                self.assertEqual(detection_config.description, "My test metric anomaly detection configuration")
                self.assertIsNotNone(detection_config.name)
                self.assertEqual(detection_config.whole_series_detection_condition.cross_conditions_operator, "AND")
                self.assertEqual(
                    detection_config.whole_series_detection_condition.change_threshold_condition.anomaly_detector_direction, "Both")
                self.assertEqual(detection_config.whole_series_detection_condition.change_threshold_condition.change_percentage, 50)
                self.assertEqual(detection_config.whole_series_detection_condition.change_threshold_condition.shift_point, 30)
                self.assertTrue(detection_config.whole_series_detection_condition.change_threshold_condition.within_range)
                self.assertEqual(
                    detection_config.whole_series_detection_condition.change_threshold_condition.suppress_condition.min_number, 2)
                self.assertEqual(
                    detection_config.whole_series_detection_condition.change_threshold_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(
                    detection_config.whole_series_detection_condition.hard_threshold_condition.anomaly_detector_direction, "Both")
                self.assertEqual(detection_config.whole_series_detection_condition.hard_threshold_condition.lower_bound, 0)
                self.assertEqual(detection_config.whole_series_detection_condition.hard_threshold_condition.upper_bound, 100)
                self.assertEqual(
                    detection_config.whole_series_detection_condition.hard_threshold_condition.suppress_condition.min_number, 5)
                self.assertEqual(
                    detection_config.whole_series_detection_condition.hard_threshold_condition.suppress_condition.min_ratio, 5)
                self.assertEqual(
                    detection_config.whole_series_detection_condition.smart_detection_condition.anomaly_detector_direction, "Both")
                self.assertEqual(detection_config.whole_series_detection_condition.smart_detection_condition.sensitivity, 50)
                self.assertEqual(
                    detection_config.whole_series_detection_condition.smart_detection_condition.suppress_condition.min_number, 50)
                self.assertEqual(
                    detection_config.whole_series_detection_condition.smart_detection_condition.suppress_condition.min_ratio, 50)
                self.assertEqual(
                    detection_config.series_detection_conditions[0].smart_detection_condition.suppress_condition.min_ratio, 100)
                self.assertEqual(
                    detection_config.series_detection_conditions[0].smart_detection_condition.suppress_condition.min_number, 1)
                self.assertEqual(
                    detection_config.series_detection_conditions[0].smart_detection_condition.sensitivity, 63)
                self.assertEqual(
                    detection_config.series_detection_conditions[0].smart_detection_condition.anomaly_detector_direction, "Both")
                self.assertEqual(
                    detection_config.series_detection_conditions[0].series_key, {'city': 'Shenzhen', 'category': 'Jewelry'})
                self.assertEqual(
                    detection_config.series_group_detection_conditions[0].smart_detection_condition.suppress_condition.min_ratio, 100)
                self.assertEqual(
                    detection_config.series_group_detection_conditions[0].smart_detection_condition.suppress_condition.min_number, 1)
                self.assertEqual(
                    detection_config.series_group_detection_conditions[0].smart_detection_condition.sensitivity, 63)
                self.assertEqual(
                    detection_config.series_group_detection_conditions[0].smart_detection_condition.anomaly_detector_direction, "Both")
                self.assertEqual(
                    detection_config.series_group_detection_conditions[0].series_group_key, {'city': 'Sao Paulo'})

            finally:
                await self.admin_client.delete_data_feed(data_feed.id)

    @AzureTestCase.await_prepared_test
    async def test_create_ad_config_multiple_series_and_group_conds(self):
        data_feed = await self._create_data_feed("datafeedconfigasync")
        async with self.admin_client:
            try:
                detection_config_name = self.create_random_name("multipledetectionconfigsasync")
                detection_config = await self.admin_client.create_detection_configuration(
                    name=detection_config_name,
                    metric_id=data_feed.metric_ids[0],
                    description="My test metric anomaly detection configuration",
                    whole_series_detection_condition=MetricDetectionCondition(
                        cross_conditions_operator="AND",
                        smart_detection_condition=SmartDetectionCondition(
                            sensitivity=50,
                            anomaly_detector_direction="Both",
                            suppress_condition=SuppressCondition(
                                min_number=50,
                                min_ratio=50
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
                            series_key={"city": "Shenzhen", "category": "Jewelry"},
                            cross_conditions_operator="AND",
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
                            series_key={"city": "Osaka", "category": "Cell Phones"},
                            cross_conditions_operator="AND",
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
                            series_group_key={"city": "Sao Paulo"},
                            cross_conditions_operator="AND",
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
                            series_group_key={"city": "Seoul"},
                            cross_conditions_operator="AND",
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

                self.assertIsNotNone(detection_config.id)
                self.assertEqual(detection_config.metric_id, data_feed.metric_ids[0])
                self.assertEqual(detection_config.description, "My test metric anomaly detection configuration")
                self.assertIsNotNone(detection_config.name)

                # whole series detection condition
                self.assertEqual(detection_config.whole_series_detection_condition.cross_conditions_operator, "AND")
                self.assertEqual(
                    detection_config.whole_series_detection_condition.change_threshold_condition.anomaly_detector_direction, "Both")
                self.assertEqual(detection_config.whole_series_detection_condition.change_threshold_condition.change_percentage, 50)
                self.assertEqual(detection_config.whole_series_detection_condition.change_threshold_condition.shift_point, 30)
                self.assertTrue(detection_config.whole_series_detection_condition.change_threshold_condition.within_range)
                self.assertEqual(
                    detection_config.whole_series_detection_condition.change_threshold_condition.suppress_condition.min_number, 2)
                self.assertEqual(
                    detection_config.whole_series_detection_condition.change_threshold_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(
                    detection_config.whole_series_detection_condition.hard_threshold_condition.anomaly_detector_direction, "Both")
                self.assertEqual(detection_config.whole_series_detection_condition.hard_threshold_condition.lower_bound, 0)
                self.assertEqual(detection_config.whole_series_detection_condition.hard_threshold_condition.upper_bound, 100)
                self.assertEqual(
                    detection_config.whole_series_detection_condition.hard_threshold_condition.suppress_condition.min_number, 5)
                self.assertEqual(
                    detection_config.whole_series_detection_condition.hard_threshold_condition.suppress_condition.min_ratio, 5)
                self.assertEqual(
                    detection_config.whole_series_detection_condition.smart_detection_condition.anomaly_detector_direction, "Both")
                self.assertEqual(detection_config.whole_series_detection_condition.smart_detection_condition.sensitivity, 50)
                self.assertEqual(
                    detection_config.whole_series_detection_condition.smart_detection_condition.suppress_condition.min_number, 50)
                self.assertEqual(
                    detection_config.whole_series_detection_condition.smart_detection_condition.suppress_condition.min_ratio, 50)

                # series detection conditions
                self.assertEqual(
                    detection_config.series_detection_conditions[0].series_key, {'city': 'Shenzhen', 'category': 'Jewelry'})
                self.assertEqual(detection_config.series_detection_conditions[0].cross_conditions_operator, "AND")
                self.assertEqual(
                    detection_config.series_detection_conditions[0].smart_detection_condition.suppress_condition.min_ratio, 100)
                self.assertEqual(
                    detection_config.series_detection_conditions[0].smart_detection_condition.suppress_condition.min_number, 1)
                self.assertEqual(
                    detection_config.series_detection_conditions[0].smart_detection_condition.sensitivity, 63)
                self.assertEqual(
                    detection_config.series_detection_conditions[0].smart_detection_condition.anomaly_detector_direction, "Both")
                self.assertEqual(
                    detection_config.series_detection_conditions[0].change_threshold_condition.anomaly_detector_direction, "Both")
                self.assertEqual(detection_config.series_detection_conditions[0].change_threshold_condition.change_percentage, 50)
                self.assertEqual(detection_config.series_detection_conditions[0].change_threshold_condition.shift_point, 30)
                self.assertTrue(detection_config.series_detection_conditions[0].change_threshold_condition.within_range)
                self.assertEqual(
                    detection_config.series_detection_conditions[0].change_threshold_condition.suppress_condition.min_number, 2)
                self.assertEqual(
                    detection_config.series_detection_conditions[0].change_threshold_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(
                    detection_config.series_detection_conditions[0].hard_threshold_condition.anomaly_detector_direction, "Both")
                self.assertEqual(detection_config.series_detection_conditions[0].hard_threshold_condition.lower_bound, 0)
                self.assertEqual(detection_config.series_detection_conditions[0].hard_threshold_condition.upper_bound, 100)
                self.assertEqual(
                    detection_config.series_detection_conditions[0].hard_threshold_condition.suppress_condition.min_number, 5)
                self.assertEqual(
                    detection_config.series_detection_conditions[0].hard_threshold_condition.suppress_condition.min_ratio, 5)
                self.assertEqual(
                    detection_config.series_detection_conditions[1].series_key, {"city": "Osaka", "category": "Cell Phones"})
                self.assertEqual(
                    detection_config.series_detection_conditions[1].smart_detection_condition.suppress_condition.min_ratio, 100)
                self.assertEqual(
                    detection_config.series_detection_conditions[1].smart_detection_condition.suppress_condition.min_number, 1)
                self.assertEqual(
                    detection_config.series_detection_conditions[1].smart_detection_condition.sensitivity, 63)
                self.assertEqual(
                    detection_config.series_detection_conditions[1].smart_detection_condition.anomaly_detector_direction, "Both")

                # series group detection conditions
                self.assertEqual(
                    detection_config.series_group_detection_conditions[0].series_group_key, {"city": "Sao Paulo"})
                self.assertEqual(detection_config.series_group_detection_conditions[0].cross_conditions_operator, "AND")
                self.assertEqual(
                    detection_config.series_group_detection_conditions[0].smart_detection_condition.suppress_condition.min_ratio, 100)
                self.assertEqual(
                    detection_config.series_group_detection_conditions[0].smart_detection_condition.suppress_condition.min_number, 1)
                self.assertEqual(
                    detection_config.series_group_detection_conditions[0].smart_detection_condition.sensitivity, 63)
                self.assertEqual(
                    detection_config.series_group_detection_conditions[0].smart_detection_condition.anomaly_detector_direction, "Both")
                self.assertEqual(
                    detection_config.series_group_detection_conditions[0].change_threshold_condition.anomaly_detector_direction, "Both")
                self.assertEqual(detection_config.series_group_detection_conditions[0].change_threshold_condition.change_percentage, 50)
                self.assertEqual(detection_config.series_group_detection_conditions[0].change_threshold_condition.shift_point, 30)
                self.assertTrue(detection_config.series_group_detection_conditions[0].change_threshold_condition.within_range)
                self.assertEqual(
                    detection_config.series_group_detection_conditions[0].change_threshold_condition.suppress_condition.min_number, 2)
                self.assertEqual(
                    detection_config.series_group_detection_conditions[0].change_threshold_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(
                    detection_config.series_group_detection_conditions[0].hard_threshold_condition.anomaly_detector_direction, "Both")
                self.assertEqual(detection_config.series_group_detection_conditions[0].hard_threshold_condition.lower_bound, 0)
                self.assertEqual(detection_config.series_group_detection_conditions[0].hard_threshold_condition.upper_bound, 100)
                self.assertEqual(
                    detection_config.series_group_detection_conditions[0].hard_threshold_condition.suppress_condition.min_number, 5)
                self.assertEqual(
                    detection_config.series_group_detection_conditions[0].hard_threshold_condition.suppress_condition.min_ratio, 5)
                self.assertEqual(
                    detection_config.series_group_detection_conditions[1].series_group_key, {"city": "Seoul"})
                self.assertEqual(
                    detection_config.series_group_detection_conditions[1].smart_detection_condition.suppress_condition.min_ratio, 100)
                self.assertEqual(
                    detection_config.series_group_detection_conditions[1].smart_detection_condition.suppress_condition.min_number, 1)
                self.assertEqual(
                    detection_config.series_group_detection_conditions[1].smart_detection_condition.sensitivity, 63)
                self.assertEqual(
                    detection_config.series_group_detection_conditions[1].smart_detection_condition.anomaly_detector_direction, "Both")

            finally:
                await self.admin_client.delete_data_feed(data_feed.id)

    @AzureTestCase.await_prepared_test
    async def test_list_detection_configs(self):
        async with self.admin_client:
            configs = self.admin_client.list_detection_configurations(metric_id=self.metric_id)
            configs_list = []
            async for config in configs:
                configs_list.append(config)
            assert len(configs_list) > 0

    @AzureTestCase.await_prepared_test
    async def test_update_detection_config_with_model(self):
        async with self.admin_client:
            try:
                detection_config, data_feed = await self._create_detection_config_for_update("updatedetection")

                detection_config.name = "updated"
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
                detection_config.series_detection_conditions[0].cross_conditions_operator = "AND"
                detection_config.series_group_detection_conditions[0].change_threshold_condition = change_threshold_condition
                detection_config.series_group_detection_conditions[0].hard_threshold_condition = hard_threshold_condition
                detection_config.series_group_detection_conditions[0].smart_detection_condition = smart_detection_condition
                detection_config.series_group_detection_conditions[0].cross_conditions_operator = "AND"
                detection_config.whole_series_detection_condition.hard_threshold_condition = hard_threshold_condition
                detection_config.whole_series_detection_condition.smart_detection_condition = smart_detection_condition
                detection_config.whole_series_detection_condition.change_threshold_condition = change_threshold_condition
                detection_config.whole_series_detection_condition.cross_conditions_operator = "OR"

                updated = await self.admin_client.update_detection_configuration(detection_config)

                self.assertEqual(updated.name, "updated")
                self.assertEqual(updated.description, "updated")
                self.assertEqual(updated.series_detection_conditions[0].change_threshold_condition.anomaly_detector_direction, "Both")
                self.assertEqual(updated.series_detection_conditions[0].change_threshold_condition.change_percentage, 20)
                self.assertEqual(updated.series_detection_conditions[0].change_threshold_condition.shift_point, 10)
                self.assertTrue(updated.series_detection_conditions[0].change_threshold_condition.within_range)
                self.assertEqual(updated.series_detection_conditions[0].change_threshold_condition.suppress_condition.min_number, 5)
                self.assertEqual(updated.series_detection_conditions[0].change_threshold_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(updated.series_detection_conditions[0].hard_threshold_condition.anomaly_detector_direction, "Up")
                self.assertEqual(updated.series_detection_conditions[0].hard_threshold_condition.upper_bound, 100)
                self.assertEqual(updated.series_detection_conditions[0].hard_threshold_condition.suppress_condition.min_number, 5)
                self.assertEqual(updated.series_detection_conditions[0].hard_threshold_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(updated.series_detection_conditions[0].smart_detection_condition.anomaly_detector_direction, "Up")
                self.assertEqual(updated.series_detection_conditions[0].smart_detection_condition.sensitivity, 10)
                self.assertEqual(updated.series_detection_conditions[0].smart_detection_condition.suppress_condition.min_number, 5)
                self.assertEqual(updated.series_detection_conditions[0].smart_detection_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(updated.series_detection_conditions[0].cross_conditions_operator, "AND")

                self.assertEqual(updated.series_group_detection_conditions[0].change_threshold_condition.anomaly_detector_direction, "Both")
                self.assertEqual(updated.series_group_detection_conditions[0].change_threshold_condition.change_percentage, 20)
                self.assertEqual(updated.series_group_detection_conditions[0].change_threshold_condition.shift_point, 10)
                self.assertTrue(updated.series_group_detection_conditions[0].change_threshold_condition.within_range)
                self.assertEqual(updated.series_group_detection_conditions[0].change_threshold_condition.suppress_condition.min_number, 5)
                self.assertEqual(updated.series_group_detection_conditions[0].change_threshold_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(updated.series_group_detection_conditions[0].hard_threshold_condition.anomaly_detector_direction, "Up")
                self.assertEqual(updated.series_group_detection_conditions[0].hard_threshold_condition.upper_bound, 100)
                self.assertEqual(updated.series_group_detection_conditions[0].hard_threshold_condition.suppress_condition.min_number, 5)
                self.assertEqual(updated.series_group_detection_conditions[0].hard_threshold_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(updated.series_group_detection_conditions[0].smart_detection_condition.anomaly_detector_direction, "Up")
                self.assertEqual(updated.series_group_detection_conditions[0].smart_detection_condition.sensitivity, 10)
                self.assertEqual(updated.series_group_detection_conditions[0].smart_detection_condition.suppress_condition.min_number, 5)
                self.assertEqual(updated.series_group_detection_conditions[0].smart_detection_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(updated.series_group_detection_conditions[0].cross_conditions_operator, "AND")

                self.assertEqual(updated.whole_series_detection_condition.change_threshold_condition.anomaly_detector_direction, "Both")
                self.assertEqual(updated.whole_series_detection_condition.change_threshold_condition.change_percentage, 20)
                self.assertEqual(updated.whole_series_detection_condition.change_threshold_condition.shift_point, 10)
                self.assertTrue(updated.whole_series_detection_condition.change_threshold_condition.within_range)
                self.assertEqual(updated.whole_series_detection_condition.change_threshold_condition.suppress_condition.min_number, 5)
                self.assertEqual(updated.whole_series_detection_condition.change_threshold_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(updated.whole_series_detection_condition.hard_threshold_condition.anomaly_detector_direction, "Up")
                self.assertEqual(updated.whole_series_detection_condition.hard_threshold_condition.upper_bound, 100)
                self.assertEqual(updated.whole_series_detection_condition.hard_threshold_condition.suppress_condition.min_number, 5)
                self.assertEqual(updated.whole_series_detection_condition.hard_threshold_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(updated.whole_series_detection_condition.smart_detection_condition.anomaly_detector_direction, "Up")
                self.assertEqual(updated.whole_series_detection_condition.smart_detection_condition.sensitivity, 10)
                self.assertEqual(updated.whole_series_detection_condition.smart_detection_condition.suppress_condition.min_number, 5)
                self.assertEqual(updated.whole_series_detection_condition.smart_detection_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(updated.whole_series_detection_condition.cross_conditions_operator, "OR")
            finally:
                await self.admin_client.delete_data_feed(data_feed.id)

    @AzureTestCase.await_prepared_test
    async def test_update_detection_config_with_kwargs(self):
        async with self.admin_client:
            try:
                detection_config, data_feed = await self._create_detection_config_for_update("updatedetection")
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
                updated = await self.admin_client.update_detection_configuration(
                    detection_config.id,
                    name="updated",
                    description="updated",
                    whole_series_detection_condition=MetricDetectionCondition(
                        cross_conditions_operator="OR",
                        smart_detection_condition=smart_detection_condition,
                        hard_threshold_condition=hard_threshold_condition,
                        change_threshold_condition=change_threshold_condition
                    ),
                    series_detection_conditions=[MetricSingleSeriesDetectionCondition(
                        series_key={"city": "San Paulo", "category": "Jewelry"},
                        cross_conditions_operator="AND",
                        smart_detection_condition=smart_detection_condition,
                        hard_threshold_condition=hard_threshold_condition,
                        change_threshold_condition=change_threshold_condition
                    )],
                    series_group_detection_conditions=[MetricSeriesGroupDetectionCondition(
                        series_group_key={"city": "Shenzen"},
                        cross_conditions_operator="AND",
                        smart_detection_condition=smart_detection_condition,
                        hard_threshold_condition=hard_threshold_condition,
                        change_threshold_condition=change_threshold_condition
                    )]
                )

                self.assertEqual(updated.name, "updated")
                self.assertEqual(updated.description, "updated")
                self.assertEqual(updated.series_detection_conditions[0].change_threshold_condition.anomaly_detector_direction, "Both")
                self.assertEqual(updated.series_detection_conditions[0].change_threshold_condition.change_percentage, 20)
                self.assertEqual(updated.series_detection_conditions[0].change_threshold_condition.shift_point, 10)
                self.assertTrue(updated.series_detection_conditions[0].change_threshold_condition.within_range)
                self.assertEqual(updated.series_detection_conditions[0].change_threshold_condition.suppress_condition.min_number, 5)
                self.assertEqual(updated.series_detection_conditions[0].change_threshold_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(updated.series_detection_conditions[0].hard_threshold_condition.anomaly_detector_direction, "Up")
                self.assertEqual(updated.series_detection_conditions[0].hard_threshold_condition.upper_bound, 100)
                self.assertEqual(updated.series_detection_conditions[0].hard_threshold_condition.suppress_condition.min_number, 5)
                self.assertEqual(updated.series_detection_conditions[0].hard_threshold_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(updated.series_detection_conditions[0].smart_detection_condition.anomaly_detector_direction, "Up")
                self.assertEqual(updated.series_detection_conditions[0].smart_detection_condition.sensitivity, 10)
                self.assertEqual(updated.series_detection_conditions[0].smart_detection_condition.suppress_condition.min_number, 5)
                self.assertEqual(updated.series_detection_conditions[0].smart_detection_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(updated.series_detection_conditions[0].cross_conditions_operator, "AND")
                self.assertEqual(updated.series_detection_conditions[0].series_key, {"city": "San Paulo", "category": "Jewelry"})

                self.assertEqual(updated.series_group_detection_conditions[0].change_threshold_condition.anomaly_detector_direction, "Both")
                self.assertEqual(updated.series_group_detection_conditions[0].change_threshold_condition.change_percentage, 20)
                self.assertEqual(updated.series_group_detection_conditions[0].change_threshold_condition.shift_point, 10)
                self.assertTrue(updated.series_group_detection_conditions[0].change_threshold_condition.within_range)
                self.assertEqual(updated.series_group_detection_conditions[0].change_threshold_condition.suppress_condition.min_number, 5)
                self.assertEqual(updated.series_group_detection_conditions[0].change_threshold_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(updated.series_group_detection_conditions[0].hard_threshold_condition.anomaly_detector_direction, "Up")
                self.assertEqual(updated.series_group_detection_conditions[0].hard_threshold_condition.upper_bound, 100)
                self.assertEqual(updated.series_group_detection_conditions[0].hard_threshold_condition.suppress_condition.min_number, 5)
                self.assertEqual(updated.series_group_detection_conditions[0].hard_threshold_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(updated.series_group_detection_conditions[0].smart_detection_condition.anomaly_detector_direction, "Up")
                self.assertEqual(updated.series_group_detection_conditions[0].smart_detection_condition.sensitivity, 10)
                self.assertEqual(updated.series_group_detection_conditions[0].smart_detection_condition.suppress_condition.min_number, 5)
                self.assertEqual(updated.series_group_detection_conditions[0].smart_detection_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(updated.series_group_detection_conditions[0].cross_conditions_operator, "AND")
                self.assertEqual(updated.series_group_detection_conditions[0].series_group_key, {"city": "Shenzen"})

                self.assertEqual(updated.whole_series_detection_condition.change_threshold_condition.anomaly_detector_direction, "Both")
                self.assertEqual(updated.whole_series_detection_condition.change_threshold_condition.change_percentage, 20)
                self.assertEqual(updated.whole_series_detection_condition.change_threshold_condition.shift_point, 10)
                self.assertTrue(updated.whole_series_detection_condition.change_threshold_condition.within_range)
                self.assertEqual(updated.whole_series_detection_condition.change_threshold_condition.suppress_condition.min_number, 5)
                self.assertEqual(updated.whole_series_detection_condition.change_threshold_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(updated.whole_series_detection_condition.hard_threshold_condition.anomaly_detector_direction, "Up")
                self.assertEqual(updated.whole_series_detection_condition.hard_threshold_condition.upper_bound, 100)
                self.assertEqual(updated.whole_series_detection_condition.hard_threshold_condition.suppress_condition.min_number, 5)
                self.assertEqual(updated.whole_series_detection_condition.hard_threshold_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(updated.whole_series_detection_condition.smart_detection_condition.anomaly_detector_direction, "Up")
                self.assertEqual(updated.whole_series_detection_condition.smart_detection_condition.sensitivity, 10)
                self.assertEqual(updated.whole_series_detection_condition.smart_detection_condition.suppress_condition.min_number, 5)
                self.assertEqual(updated.whole_series_detection_condition.smart_detection_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(updated.whole_series_detection_condition.cross_conditions_operator, "OR")
            finally:
                await self.admin_client.delete_data_feed(data_feed.id)

    @AzureTestCase.await_prepared_test
    async def test_update_detection_config_with_model_and_kwargs(self):
        async with self.admin_client:
            try:
                detection_config, data_feed = await self._create_detection_config_for_update("updatedetection")
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

                detection_config.name = "updateMe"
                detection_config.description = "updateMe"
                updated = await self.admin_client.update_detection_configuration(
                    detection_config,
                    whole_series_detection_condition=MetricDetectionCondition(
                        cross_conditions_operator="OR",
                        smart_detection_condition=smart_detection_condition,
                        hard_threshold_condition=hard_threshold_condition,
                        change_threshold_condition=change_threshold_condition
                    ),
                    series_detection_conditions=[MetricSingleSeriesDetectionCondition(
                        series_key={"city": "San Paulo", "category": "Jewelry"},
                        cross_conditions_operator="AND",
                        smart_detection_condition=smart_detection_condition,
                        hard_threshold_condition=hard_threshold_condition,
                        change_threshold_condition=change_threshold_condition
                    )],
                    series_group_detection_conditions=[MetricSeriesGroupDetectionCondition(
                        series_group_key={"city": "Shenzen"},
                        cross_conditions_operator="AND",
                        smart_detection_condition=smart_detection_condition,
                        hard_threshold_condition=hard_threshold_condition,
                        change_threshold_condition=change_threshold_condition
                    )]
                )

                self.assertEqual(updated.name, "updateMe")
                self.assertEqual(updated.description, "updateMe")
                self.assertEqual(updated.series_detection_conditions[0].change_threshold_condition.anomaly_detector_direction, "Both")
                self.assertEqual(updated.series_detection_conditions[0].change_threshold_condition.change_percentage, 20)
                self.assertEqual(updated.series_detection_conditions[0].change_threshold_condition.shift_point, 10)
                self.assertTrue(updated.series_detection_conditions[0].change_threshold_condition.within_range)
                self.assertEqual(updated.series_detection_conditions[0].change_threshold_condition.suppress_condition.min_number, 5)
                self.assertEqual(updated.series_detection_conditions[0].change_threshold_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(updated.series_detection_conditions[0].hard_threshold_condition.anomaly_detector_direction, "Up")
                self.assertEqual(updated.series_detection_conditions[0].hard_threshold_condition.upper_bound, 100)
                self.assertEqual(updated.series_detection_conditions[0].hard_threshold_condition.suppress_condition.min_number, 5)
                self.assertEqual(updated.series_detection_conditions[0].hard_threshold_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(updated.series_detection_conditions[0].smart_detection_condition.anomaly_detector_direction, "Up")
                self.assertEqual(updated.series_detection_conditions[0].smart_detection_condition.sensitivity, 10)
                self.assertEqual(updated.series_detection_conditions[0].smart_detection_condition.suppress_condition.min_number, 5)
                self.assertEqual(updated.series_detection_conditions[0].smart_detection_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(updated.series_detection_conditions[0].cross_conditions_operator, "AND")
                self.assertEqual(updated.series_detection_conditions[0].series_key, {"city": "San Paulo", "category": "Jewelry"})

                self.assertEqual(updated.series_group_detection_conditions[0].change_threshold_condition.anomaly_detector_direction, "Both")
                self.assertEqual(updated.series_group_detection_conditions[0].change_threshold_condition.change_percentage, 20)
                self.assertEqual(updated.series_group_detection_conditions[0].change_threshold_condition.shift_point, 10)
                self.assertTrue(updated.series_group_detection_conditions[0].change_threshold_condition.within_range)
                self.assertEqual(updated.series_group_detection_conditions[0].change_threshold_condition.suppress_condition.min_number, 5)
                self.assertEqual(updated.series_group_detection_conditions[0].change_threshold_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(updated.series_group_detection_conditions[0].hard_threshold_condition.anomaly_detector_direction, "Up")
                self.assertEqual(updated.series_group_detection_conditions[0].hard_threshold_condition.upper_bound, 100)
                self.assertEqual(updated.series_group_detection_conditions[0].hard_threshold_condition.suppress_condition.min_number, 5)
                self.assertEqual(updated.series_group_detection_conditions[0].hard_threshold_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(updated.series_group_detection_conditions[0].smart_detection_condition.anomaly_detector_direction, "Up")
                self.assertEqual(updated.series_group_detection_conditions[0].smart_detection_condition.sensitivity, 10)
                self.assertEqual(updated.series_group_detection_conditions[0].smart_detection_condition.suppress_condition.min_number, 5)
                self.assertEqual(updated.series_group_detection_conditions[0].smart_detection_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(updated.series_group_detection_conditions[0].cross_conditions_operator, "AND")
                self.assertEqual(updated.series_group_detection_conditions[0].series_group_key, {"city": "Shenzen"})

                self.assertEqual(updated.whole_series_detection_condition.change_threshold_condition.anomaly_detector_direction, "Both")
                self.assertEqual(updated.whole_series_detection_condition.change_threshold_condition.change_percentage, 20)
                self.assertEqual(updated.whole_series_detection_condition.change_threshold_condition.shift_point, 10)
                self.assertTrue(updated.whole_series_detection_condition.change_threshold_condition.within_range)
                self.assertEqual(updated.whole_series_detection_condition.change_threshold_condition.suppress_condition.min_number, 5)
                self.assertEqual(updated.whole_series_detection_condition.change_threshold_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(updated.whole_series_detection_condition.hard_threshold_condition.anomaly_detector_direction, "Up")
                self.assertEqual(updated.whole_series_detection_condition.hard_threshold_condition.upper_bound, 100)
                self.assertEqual(updated.whole_series_detection_condition.hard_threshold_condition.suppress_condition.min_number, 5)
                self.assertEqual(updated.whole_series_detection_condition.hard_threshold_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(updated.whole_series_detection_condition.smart_detection_condition.anomaly_detector_direction, "Up")
                self.assertEqual(updated.whole_series_detection_condition.smart_detection_condition.sensitivity, 10)
                self.assertEqual(updated.whole_series_detection_condition.smart_detection_condition.suppress_condition.min_number, 5)
                self.assertEqual(updated.whole_series_detection_condition.smart_detection_condition.suppress_condition.min_ratio, 2)
                self.assertEqual(updated.whole_series_detection_condition.cross_conditions_operator, "OR")
            finally:
                await self.admin_client.delete_data_feed(data_feed.id)

    @AzureTestCase.await_prepared_test
    async def test_update_detection_config_by_resetting_properties(self):
        async with self.admin_client:
            try:
                detection_config, data_feed = await self._create_detection_config_for_update("updatedetection")

                updated = await self.admin_client.update_detection_configuration(
                    detection_config.id,
                    name="reset",
                    description="",
                    # series_detection_conditions=None,
                    # series_group_detection_conditions=None
                )

                self.assertEqual(updated.name, "reset")
                self.assertEqual(updated.description, "")  # currently won't update with None

                # service bug says these are required
                # self.assertEqual(updated.series_detection_conditions, None)
                # self.assertEqual(updated.series_group_detection_conditions, None)

            finally:
                await self.admin_client.delete_data_feed(data_feed.id)
