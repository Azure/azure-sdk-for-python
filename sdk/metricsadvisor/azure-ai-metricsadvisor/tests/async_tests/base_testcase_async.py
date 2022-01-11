# coding=utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import datetime
import uuid
from devtools_testutils import AzureRecordedTestCase, is_live
from azure.ai.metricsadvisor import MetricsAdvisorKeyCredential
from azure.ai.metricsadvisor.models import (
    SqlServerDataFeedSource,
    DataFeedSchema,
    DataFeedMetric,
    DataFeedDimension,
    DataFeedGranularity,
    DataFeedIngestionSettings,
    DataFeedMissingDataPointFillSettings,
    DataFeedRollupSettings,
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

# for pytest.parametrize
subscription_key = os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY", "metrics_advisor_subscription_key")
api_key = os.getenv("METRICS_ADVISOR_API_KEY", "metrics_advisor_api_key")
API_KEY = [MetricsAdvisorKeyCredential(subscription_key, api_key)]
AAD = ["AAD"]
CREDENTIALS = [MetricsAdvisorKeyCredential(subscription_key, api_key), "AAD"]


def ids(val):
    if isinstance(val, MetricsAdvisorKeyCredential):
        return "APIKey"
    else:
        return "AAD"


class MetricsAdvisorClientPreparer(object):
    def __init__(self, client_cls, client_kwargs={}, **kwargs):
        self.client_cls = client_cls
        self.client_kwargs = client_kwargs
        self.service_endpoint = os.getenv("METRICS_ADVISOR_ENDPOINT", "https://fakeendpoint.cognitiveservices.azure.com")
        self.data_feed = kwargs.pop("data_feed", False)
        self.detection_config = kwargs.pop("detection_config", False)
        self.alert_config = kwargs.pop("alert_config", False)
        self.email_hook = kwargs.pop("email_hook", False)
        self.web_hook = kwargs.pop("web_hook", False)
        self.variables = kwargs.pop("variables", {})

    def __call__(self, fn):
        async def _preparer_wrapper(test_class, credential, **kwargs):
            self.create_test_client(credential)
            await self.create_resources(**kwargs)
            if is_live():
                await fn(test_class, self.client, variables=self.variables)
            else:
                await fn(test_class, self.client)
        return _preparer_wrapper

    def create_test_client(self, credential):
        if credential == "AAD":
            credential = AzureRecordedTestCase().get_credential(self.client_cls, is_async=True)
        self.client = self.client_cls(self.service_endpoint, credential, **self.client_kwargs)

    async def create_resources(self, **kwargs):
        if not is_live():
            return kwargs

        try:
            if self.data_feed:
                self.data_feed = await self.create_data_feed("datafeed")

            if self.detection_config:
                self.detection_config = await self.create_detection_config("detectionconfig")

            if self.alert_config:
                self.alert_config = await self.create_alert_config("alertconfig")

            if self.email_hook:
                self.email_hook = await self.create_email_hook("emailhook")

            if self.web_hook:
                self.web_hook = await self.create_web_hook("web_hook")

        except Exception as e:
            try:
                await self.client.delete_data_feed(self.variables["data_feed_id"])
            except KeyError:
                pass
            raise e

    def create_random_name(self, name):
        return name + str(uuid.uuid4())

    async def create_data_feed(self, name):
        name = self.create_random_name(name)
        if is_live():
            self.variables["data_feed_name"] = name
        data_feed = await self.client.create_data_feed(
            name=self.variables["data_feed_name"],
            source=SqlServerDataFeedSource(
                connection_string=os.getenv("METRICS_ADVISOR_SQL_SERVER_CONNECTION_STRING", "metrics_advisor_sql_server_connection_string"),
                query="select * from adsample2 where Timestamp = @StartTime"
            ),
            granularity=DataFeedGranularity(
                granularity_type="Daily",
            ),
            schema=DataFeedSchema(
                metrics=[
                    DataFeedMetric(name="cost", description="the cost"),
                    DataFeedMetric(name="revenue", description="the revenue")
                ],
                dimensions=[
                    DataFeedDimension(name="category"),
                    DataFeedDimension(name="region")
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
            admins=["yournamehere@microsoft.com"],
            data_feed_description="my first data feed",
            missing_data_point_fill_settings=DataFeedMissingDataPointFillSettings(
                fill_type="SmartFilling"
            ),
            rollup_settings=DataFeedRollupSettings(
                rollup_type="NoRollup",
                rollup_method="None",
            ),
            viewers=["viewers"],
            access_mode="Private",
            action_link_template="action link template"
        )

        if is_live():
            self.variables["data_feed_id"] = data_feed.id
            self.variables["data_feed_metric_id"] = data_feed.metric_ids['cost']
        return data_feed

    async def create_detection_config(self, name):
        detection_config_name = self.create_random_name(name)
        if is_live():
            self.variables["detection_config_name"] = detection_config_name
        detection_config = await self.client.create_detection_configuration(
            name=self.variables["detection_config_name"],
            metric_id=self.variables["data_feed_metric_id"],
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
                series_key={"region": "Beijing", "category": "Shoes Handbags & Sunglasses"},
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
                series_group_key={"region": "Beijing"},
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
        if is_live():
            self.variables["detection_config_id"] = detection_config.id
        return detection_config

    async def create_alert_config(self, name):
        alert_config_name = self.create_random_name(name)
        if is_live():
            self.variables["alert_config_name"] = alert_config_name
        alert_config = await self.client.create_alert_configuration(
            name=self.variables["alert_config_name"],
            cross_metrics_operator="AND",
            metric_alert_configurations=[
                MetricAlertConfiguration(
                    detection_configuration_id=self.variables["detection_config_id"],
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
                            companion_metric_id=self.variables["data_feed_metric_id"],
                            lower=1.0,
                            upper=5.0
                        )
                    )
                ),
                MetricAlertConfiguration(
                    detection_configuration_id=self.variables["detection_config_id"],
                    alert_scope=MetricAnomalyAlertScope(
                        scope_type="SeriesGroup",
                        series_group_in_scope={'region': 'Beijing'}
                    ),
                    alert_conditions=MetricAnomalyAlertConditions(
                        severity_condition=SeverityCondition(
                            min_alert_severity="Low",
                            max_alert_severity="High"
                        )
                    )
                ),
                MetricAlertConfiguration(
                    detection_configuration_id=self.variables["detection_config_id"],
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
        if is_live():
            self.variables["alert_config_id"] = alert_config.id
        return alert_config

    async def create_email_hook(self, name):
        email_hook_name = self.create_random_name(name)
        if is_live():
            self.variables["email_hook_name"] = email_hook_name
        email_hook = await self.client.create_hook(
            hook=EmailNotificationHook(
                name=self.variables["email_hook_name"],
                emails_to_alert=["yournamehere@microsoft.com"],
                description="my email hook",
                external_link="external link"
            )
        )
        if is_live():
            self.variables["email_hook_id"] = email_hook.id
        return email_hook

    async def create_web_hook(self, name):
        web_hook_name = self.create_random_name(name)
        if is_live():
            self.variables["web_hook_name"] = web_hook_name
        web_hook = await self.client.create_hook(
            hook=WebNotificationHook(
                name=self.variables["web_hook_name"],
                endpoint="https://httpbin.org/post",
                description="my web hook",
                external_link="external link",
                username="krista",
                password="123"
            )
        )

        if is_live():
            self.variables["web_hook_id"] = web_hook.id
        return web_hook


class TestMetricsAdvisorClientBase(AzureRecordedTestCase):

    @property
    def service_endpoint(self):
        return os.getenv("METRICS_ADVISOR_ENDPOINT", "https://fakeendpoint.cognitiveservices.azure.com")

    @property
    def subscription_key(self):
        return os.getenv("METRICS_ADVISOR_SUBSCRIPTION_KEY", "metrics_advisor_subscription_key")

    @property
    def api_key(self):
        return os.getenv("METRICS_ADVISOR_API_KEY", "metrics_advisor_api_key")

    @property
    def sql_server_connection_string(self):
        return os.getenv("METRICS_ADVISOR_SQL_SERVER_CONNECTION_STRING", "metrics_advisor_sql_server_connection_string")

    @property
    def data_feed_id(self):
        return os.getenv("METRICS_ADVISOR_DATA_FEED_ID", "metrics_advisor_data_feed_id")

    @property
    def anomaly_detection_configuration_id(self):
        return os.getenv("METRICS_ADVISOR_ANOMALY_DETECTION_CONFIGURATION_ID", "metrics_advisor_anomaly_detection_configuration_id")

    @property
    def anomaly_alert_configuration_id(self):
        return os.getenv("METRICS_ADVISOR_ANOMALY_ALERT_CONFIGURATION_ID", "metrics_advisor_anomaly_alert_configuration_id")

    @property
    def metric_id(self):
        return os.getenv("METRICS_ADVISOR_METRIC_ID", "metrics_advisor_metric_id")

    @property
    def incident_id(self):
        return os.getenv("METRICS_ADVISOR_INCIDENT_ID", "metrics_advisor_incident_id")

    @property
    def feedback_id(self):
        return os.getenv("METRICS_ADVISOR_FEEDBACK_ID", "metrics_advisor_feedback_id")

    @property
    def alert_id(self):
        return os.getenv("METRICS_ADVISOR_ALERT_ID", "metrics_advisor_alert_id")

    async def clean_up(self, delete_func, variables, key=None):
        try:
            id_to_delete = variables[key] if key else variables["data_feed_id"]
            await delete_func(id_to_delete)
        except KeyError:
            pass

    def create_random_name(self, name):
        return name + str(uuid.uuid4())