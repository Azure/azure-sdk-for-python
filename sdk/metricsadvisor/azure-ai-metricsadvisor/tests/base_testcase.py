# coding=utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import datetime
from devtools_testutils import AzureTestCase
from azure_devtools.scenario_tests import (
    ReplayableTest,
    create_random_name
)

from azure.ai.metricsadvisor import (
    MetricsAdvisorKeyCredential,
    MetricsAdvisorAdministrationClient,
    MetricsAdvisorClient,
)
from azure.ai.metricsadvisor.models import (
    SQLServerDataFeed,
    DataFeedSchema,
    DataFeedMetric,
    DataFeedDimension,
    DataFeedGranularity,
    DataFeedIngestionSettings,
    DataFeedMissingDataPointFillSettings,
    DataFeedRollupSettings,
    DataFeedOptions,
    MetricAlertConfiguration,
    MetricAnomalyAlertScope,
    MetricAnomalyAlertConditions,
    MetricBoundaryCondition,
    TopNGroupScope,
    SeverityCondition,
    MetricDetectionCondition,
    MetricSeriesGroupDetectionCondition,
    MetricSingleSeriesDetectionCondition,
    SmartDetectionCondition,
    SuppressCondition,
    ChangeThresholdCondition,
    HardThresholdCondition,
    EmailNotificationHook,
    WebNotificationHook,
)


class TestMetricsAdvisorAdministrationClientBase(AzureTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + ['Ocp-Apim-Subscription-Key', 'x-api-key']

    def __init__(self, method_name):
        super(TestMetricsAdvisorAdministrationClientBase, self).__init__(method_name)
        self.vcr.match_on = ["path", "method", "query"]
        if self.is_live:
            service_endpoint = self.get_settings_value("METRICS_ADVISOR_ENDPOINT")
            subscription_key = self.get_settings_value("METRICS_ADVISOR_SUBSCRIPTION_KEY")
            api_key = self.get_settings_value("METRICS_ADVISOR_API_KEY")
            self.sql_server_connection_string = self.get_settings_value("METRICS_ADVISOR_SQL_SERVER_CONNECTION_STRING")
            self.azure_table_connection_string = self.get_settings_value("METRICS_ADVISOR_AZURE_TABLE_CONNECTION_STRING")
            self.azure_blob_connection_string = self.get_settings_value("METRICS_ADVISOR_AZURE_BLOB_CONNECTION_STRING")
            self.azure_cosmosdb_connection_string = self.get_settings_value("METRICS_ADVISOR_COSMOS_DB_CONNECTION_STRING")
            self.http_request_get_url = self.get_settings_value("METRICS_ADVISOR_HTTP_GET_URL")
            self.http_request_post_url = self.get_settings_value("METRICS_ADVISOR_HTTP_POST_URL")
            self.application_insights_api_key = self.get_settings_value("METRICS_ADVISOR_APPLICATION_INSIGHTS_API_KEY")
            self.azure_data_explorer_connection_string = self.get_settings_value("METRICS_ADVISOR_AZURE_DATA_EXPLORER_CONNECTION_STRING")
            self.influxdb_connection_string = self.get_settings_value("METRICS_ADVISOR_INFLUX_DB_CONNECTION_STRING")
            self.influxdb_password = self.get_settings_value("METRICS_ADVISOR_INFLUX_DB_PASSWORD")
            self.azure_datalake_account_key = self.get_settings_value("METRICS_ADVISOR_AZURE_DATALAKE_ACCOUNT_KEY")
            self.mongodb_connection_string = self.get_settings_value("METRICS_ADVISOR_AZURE_MONGO_DB_CONNECTION_STRING")
            self.mysql_connection_string = self.get_settings_value("METRICS_ADVISOR_MYSQL_CONNECTION_STRING")
            self.postgresql_connection_string = self.get_settings_value("METRICS_ADVISOR_POSTGRESQL_CONNECTION_STRING")
            self.elasticsearch_auth_header = self.get_settings_value("METRICS_ADVISOR_ELASTICSEARCH_AUTH_HEADER")
            self.anomaly_detection_configuration_id = self.get_settings_value("METRICS_ADVISOR_ANOMALY_DETECTION_CONFIGURATION_ID")
            self.data_feed_id = self.get_settings_value("METRICS_ADVISOR_DATA_FEED_ID")
            self.metric_id = self.get_settings_value("METRICS_ADVISOR_METRIC_ID")
            self.scrubber.register_name_pair(
                self.sql_server_connection_string,
                "connectionstring"
            )
            self.scrubber.register_name_pair(
                self.azure_table_connection_string,
                "connectionstring"
            )
            self.scrubber.register_name_pair(
                self.azure_blob_connection_string,
                "connectionstring"
            )
            self.scrubber.register_name_pair(
                self.azure_cosmosdb_connection_string,
                "connectionstring"
            )
            self.scrubber.register_name_pair(
                self.http_request_get_url,
                "connectionstring"
            )
            self.scrubber.register_name_pair(
                self.http_request_post_url,
                "connectionstring"
            )
            self.scrubber.register_name_pair(
                self.application_insights_api_key,
                "connectionstring"
            )
            self.scrubber.register_name_pair(
                self.azure_data_explorer_connection_string,
                "connectionstring"
            )
            self.scrubber.register_name_pair(
                self.influxdb_connection_string,
                "connectionstring"
            )
            self.scrubber.register_name_pair(
                self.influxdb_password,
                "connectionstring"
            )
            self.scrubber.register_name_pair(
                self.azure_datalake_account_key,
                "connectionstring"
            )
            self.scrubber.register_name_pair(
                self.mongodb_connection_string,
                "connectionstring"
            )
            self.scrubber.register_name_pair(
                self.mysql_connection_string,
                "connectionstring"
            )
            self.scrubber.register_name_pair(
                self.postgresql_connection_string,
                "connectionstring"
            )
            self.scrubber.register_name_pair(
                self.elasticsearch_auth_header,
                "connectionstring"
            )

            self.scrubber.register_name_pair(
                self.metric_id,
                "metric_id"
            )
            self.scrubber.register_name_pair(
                self.data_feed_id,
                "data_feed_id"
            )
            self.scrubber.register_name_pair(
                self.anomaly_detection_configuration_id,
                "anomaly_detection_configuration_id"
            )
        else:
            service_endpoint = "https://endpointname.cognitiveservices.azure.com"
            subscription_key = "METRICS_ADVISOR_SUBSCRIPTION_KEY"
            api_key = "METRICS_ADVISOR_API_KEY"
            self.sql_server_connection_string = "SQL_SERVER_CONNECTION_STRING"
            self.azure_table_connection_string = "AZURE_TABLE_CONNECTION_STRING"
            self.azure_blob_connection_string = "AZURE_BLOB_CONNECTION_STRING"
            self.azure_cosmosdb_connection_string = "COSMOS_DB_CONNECTION_STRING"
            self.http_request_get_url = "METRICS_ADVISOR_HTTP_GET_URL"
            self.http_request_post_url = "METRICS_ADVISOR_HTTP_POST_URL"
            self.application_insights_api_key = "METRICS_ADVISOR_APPLICATION_INSIGHTS_API_KEY"
            self.azure_data_explorer_connection_string = "METRICS_ADVISOR_AZURE_DATA_EXPLORER_CONNECTION_STRING"
            self.influxdb_connection_string = "METRICS_ADVISOR_INFLUXDB_CONNECTION_STRING"
            self.influxdb_password = "METRICS_ADVISOR_INFLUXDB_PASSWORD"
            self.azure_datalake_account_key = "METRICS_ADVISOR_AZURE_DATALAKE_ACCOUNT_KEY"
            self.mongodb_connection_string = "METRICS_ADVISOR_AZURE_MONGODB_CONNECTION_STRING"
            self.mysql_connection_string = "METRICS_ADVISOR_MYSQL_CONNECTION_STRING"
            self.postgresql_connection_string = "METRICS_ADVISOR_POSTGRESQL_CONNECTION_STRING"
            self.elasticsearch_auth_header = "METRICS_ADVISOR_ELASTICSEARCH_AUTH"
            self.anomaly_detection_configuration_id = "anomaly_detection_configuration_id"
            self.metric_id = "metric_id"
            self.data_feed_id = "data_feed_id"
        self.admin_client = MetricsAdvisorAdministrationClient(service_endpoint,
                                                               MetricsAdvisorKeyCredential(subscription_key, api_key))

    def _create_data_feed(self, name):
        name = create_random_name(name)
        return self.admin_client.create_data_feed(
            name=name,
            source=SQLServerDataFeed(
                connection_string=self.sql_server_connection_string,
                query="select * from adsample2 where Timestamp = @StartTime"
            ),
            granularity="Daily",
            schema=DataFeedSchema(
                metrics=[
                    DataFeedMetric(name="cost"),
                    DataFeedMetric(name="revenue")
                ],
                dimensions=[
                    DataFeedDimension(name="category"),
                    DataFeedDimension(name="city")
                ],
            ),
            ingestion_settings="2019-10-01T00:00:00Z",
        )

    def _create_data_feed_and_detection_config(self, name):
        data_feed = self._create_data_feed(name)
        detection_config_name = create_random_name(name)
        detection_config = self.admin_client.create_detection_configuration(
            name=detection_config_name,
            metric_id=data_feed.metric_ids[0],
            description="testing",
            whole_series_detection_condition=MetricDetectionCondition(
                smart_detection_condition=SmartDetectionCondition(
                    sensitivity=50,
                    anomaly_detector_direction="Both",
                    suppress_condition=SuppressCondition(
                        min_number=50,
                        min_ratio=50
                    )
                )
            )
        )
        return detection_config, data_feed

    def _create_data_feed_for_update(self, name):
        data_feed_name = create_random_name(name)
        return self.admin_client.create_data_feed(
            name=data_feed_name,
            source=SQLServerDataFeed(
                connection_string=self.sql_server_connection_string,
                query=u"select * from adsample2 where Timestamp = @StartTime"
            ),
            granularity=DataFeedGranularity(
                granularity_type="Daily",
            ),
            schema=DataFeedSchema(
                metrics=[
                    DataFeedMetric(name="cost", display_name="display cost", description="the cost"),
                    DataFeedMetric(name="revenue", display_name="display revenue", description="the revenue")
                ],
                dimensions=[
                    DataFeedDimension(name="category", display_name="display category"),
                    DataFeedDimension(name="city", display_name="display city")
                ],
                timestamp_column="Timestamp"
            ),
            ingestion_settings=DataFeedIngestionSettings(
                ingestion_begin_time=datetime.datetime(2019, 10, 1),
                data_source_request_concurrency=0,
                ingestion_retry_delay=-1,
                ingestion_start_offset=-1,
                stop_retry_after=-1,
            ),
            options=DataFeedOptions(
                admin_emails=["yournamehere@microsoft.com"],
                data_feed_description="my first data feed",
                missing_data_point_fill_settings=DataFeedMissingDataPointFillSettings(
                    fill_type="SmartFilling"
                ),
                rollup_settings=DataFeedRollupSettings(
                    rollup_type="NoRollup",
                    rollup_method="None",
                ),
                viewer_emails=["viewers"],
                access_mode="Private",
                action_link_template="action link template"
            )

        )

    def _create_alert_config_for_update(self, name):
        detection_config, data_feed = self._create_data_feed_and_detection_config(name)
        alert_config_name = create_random_name(name)
        alert_config = self.admin_client.create_alert_configuration(
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
                            companion_metric_id=data_feed.metric_ids[0],
                            lower=1.0,
                            upper=5.0
                        )
                    )
                ),
                MetricAlertConfiguration(
                    detection_configuration_id=detection_config.id,
                    alert_scope=MetricAnomalyAlertScope(
                        scope_type="SeriesGroup",
                        series_group_in_scope={'city': 'Shenzhen'}
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
        return alert_config, data_feed, detection_config

    def _create_detection_config_for_update(self, name):
        data_feed = self._create_data_feed(name)
        detection_config_name = create_random_name("testupdated")
        detection_config = self.admin_client.create_detection_configuration(
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
        return detection_config, data_feed

    def _create_email_hook_for_update(self, name):
        return self.admin_client.create_hook(
            hook=EmailNotificationHook(
                name=name,
                emails_to_alert=["yournamehere@microsoft.com"],
                description="my email hook",
                external_link="external link"
            )
        )

    def _create_web_hook_for_update(self, name):
        return self.admin_client.create_hook(
            hook=WebNotificationHook(
                name=name,
                endpoint="https://httpbin.org/post",
                description="my web hook",
                external_link="external link",
                username="krista",
                password="123"
            )
        )


class TestMetricsAdvisorClientBase(AzureTestCase):
    FILTER_HEADERS = ReplayableTest.FILTER_HEADERS + ['Ocp-Apim-Subscription-Key', 'x-api-key']

    def __init__(self, method_name):
        super(TestMetricsAdvisorClientBase, self).__init__(method_name)
        self.vcr.match_on = ["path", "method", "query"]
        if self.is_live:
            service_endpoint = self.get_settings_value("METRICS_ADVISOR_ENDPOINT")
            subscription_key = self.get_settings_value("METRICS_ADVISOR_SUBSCRIPTION_KEY")
            api_key = self.get_settings_value("METRICS_ADVISOR_API_KEY")
            self.anomaly_detection_configuration_id = self.get_settings_value("METRICS_ADVISOR_ANOMALY_DETECTION_CONFIGURATION_ID")
            self.anomaly_alert_configuration_id = self.get_settings_value("METRICS_ADVISOR_ANOMALY_ALERT_CONFIGURATION_ID")
            self.metric_id = self.get_settings_value("METRICS_ADVISOR_METRIC_ID")
            self.incident_id = self.get_settings_value("METRICS_ADVISOR_INCIDENT_ID")
            self.dimension_name = self.get_settings_value("METRICS_ADVISOR_DIMENSION_NAME")
            self.feedback_id = self.get_settings_value("METRICS_ADVISOR_FEEDBACK_ID")
            self.alert_id = self.get_settings_value("METRICS_ADVISOR_ALERT_ID")
            self.scrubber.register_name_pair(
                self.anomaly_detection_configuration_id,
                "anomaly_detection_configuration_id"
            )
            self.scrubber.register_name_pair(
                self.anomaly_alert_configuration_id,
                "anomaly_alert_configuration_id"
            )
            self.scrubber.register_name_pair(
                self.metric_id,
                "metric_id"
            )
            self.scrubber.register_name_pair(
                self.incident_id,
                "incident_id"
            )
            self.scrubber.register_name_pair(
                self.dimension_name,
                "dimension_name"
            )
            self.scrubber.register_name_pair(
                self.feedback_id,
                "feedback_id"
            )
            self.scrubber.register_name_pair(
                self.alert_id,
                "alert_id"
            )
        else:
            service_endpoint = "https://endpointname.cognitiveservices.azure.com"
            subscription_key = "METRICS_ADVISOR_SUBSCRIPTION_KEY"
            api_key = "METRICS_ADVISOR_API_KEY"
            self.anomaly_detection_configuration_id = "anomaly_detection_configuration_id"
            self.anomaly_alert_configuration_id = "anomaly_alert_configuration_id"
            self.metric_id = "metric_id"
            self.incident_id = "incident_id"
            self.dimension_name = "dimension_name"
            self.feedback_id = "feedback_id"
            self.alert_id = "alert_id"

        self.client = MetricsAdvisorClient(service_endpoint,
                                                 MetricsAdvisorKeyCredential(subscription_key, api_key))

