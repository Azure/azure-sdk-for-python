# coding=utf-8
# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
import six
import datetime
from typing import Any, List, Union, cast, overload, Dict
from azure.core.tracing.decorator import distributed_trace
from ._operations import MetricsAdvisorClientOperationsMixin as _MetricsAdvisorClientOperationsMixin
from ..models import *
from msrest import Serializer
from azure.core.paging import ItemPaged
from azure.core.exceptions import HttpResponseError

DATA_FEED = {
    "SqlServer": SqlServerDataFeedSource,
    "AzureApplicationInsights": AzureApplicationInsightsDataFeedSource,
    "AzureBlob": AzureBlobDataFeedSource,
    "AzureCosmosDB": AzureCosmosDbDataFeedSource,
    "AzureDataExplorer": AzureDataExplorerDataFeedSource,
    "AzureTable": AzureTableDataFeedSource,
    "AzureLogAnalytics": AzureLogAnalyticsDataFeedSource,
    "InfluxDB": InfluxDbDataFeedSource,
    "MySql": MySqlDataFeedSource,
    "PostgreSql": PostgreSqlDataFeedSource,
    "MongoDB": MongoDbDataFeedSource,
    "AzureDataLakeStorageGen2": AzureDataLakeStorageGen2DataFeedSource,
    "AzureEventHubs": AzureEventHubsDataFeedSource,
}

DATA_FEED_PATCH = {
    "SqlServer": SQLServerDataFeedPatch,
    "AzureApplicationInsights": AzureApplicationInsightsDataFeedPatch,
    "AzureBlob": AzureBlobDataFeedPatch,
    "AzureCosmosDB": AzureCosmosDBDataFeedPatch,
    "AzureDataExplorer": AzureDataExplorerDataFeedPatch,
    "AzureTable": AzureTableDataFeedPatch,
    "AzureEventHubs": AzureEventHubsDataFeedPatch,
    "InfluxDB": InfluxDBDataFeedPatch,
    "MySql": MySqlDataFeedPatch,
    "PostgreSql": PostgreSqlDataFeedPatch,
    "MongoDB": MongoDBDataFeedPatch,
    "AzureDataLakeStorageGen2": AzureDataLakeStorageGen2DataFeedPatch,
    "AzureLogAnalytics": AzureLogAnalyticsDataFeedPatch,
}

DatasourceCredentialUnion = Union[
    DatasourceSqlConnectionString,
    DatasourceDataLakeGen2SharedKey,
    DatasourceServicePrincipal,
    DatasourceServicePrincipalInKeyVault,
]

DataFeedSourceUnion = Union[
    AzureApplicationInsightsDataFeedSource,
    AzureBlobDataFeedSource,
    AzureCosmosDbDataFeedSource,
    AzureDataExplorerDataFeedSource,
    AzureTableDataFeedSource,
    AzureLogAnalyticsDataFeedSource,
    InfluxDbDataFeedSource,
    MySqlDataFeedSource,
    PostgreSqlDataFeedSource,
    SqlServerDataFeedSource,
    MongoDbDataFeedSource,
    AzureDataLakeStorageGen2DataFeedSource,
    AzureEventHubsDataFeedSource,
]

FeedbackUnion = Union[
    AnomalyFeedback,
    ChangePointFeedback,
    CommentFeedback,
    PeriodFeedback,
]

########################### HELPERS ###########################


def convert_to_sub_feedback(feedback):
    # type: (MetricFeedback) -> Union[AnomalyFeedback, ChangePointFeedback, CommentFeedback, PeriodFeedback]
    if feedback.feedback_type == "Anomaly":
        return AnomalyFeedback._from_generated(feedback)  # type: ignore
    if feedback.feedback_type == "ChangePoint":
        return ChangePointFeedback._from_generated(feedback)  # type: ignore
    if feedback.feedback_type == "Comment":
        return CommentFeedback._from_generated(feedback)  # type: ignore
    if feedback.feedback_type == "Period":
        return PeriodFeedback._from_generated(feedback)  # type: ignore
    raise HttpResponseError("Invalid feedback type returned in the response.")


def convert_to_datasource_credential(datasource_credential):
    if datasource_credential.data_source_credential_type == "AzureSQLConnectionString":
        return DatasourceSqlConnectionString._from_generated(datasource_credential)
    if datasource_credential.data_source_credential_type == "DataLakeGen2SharedKey":
        return DatasourceDataLakeGen2SharedKey._from_generated(datasource_credential)
    if datasource_credential.data_source_credential_type == "ServicePrincipal":
        return DatasourceServicePrincipal._from_generated(datasource_credential)
    return DatasourceServicePrincipalInKeyVault._from_generated(datasource_credential)


def construct_hook_dict(update_kwargs, hook_type):

    if hook_type.lower() == "email" and "toList" in update_kwargs:
        update_kwargs["hookType"] = "Email"
        update_kwargs["hookParameter"] = {}
        update_kwargs["hookParameter"]["toList"] = update_kwargs["toList"]
        update_kwargs.pop("toList")
    elif hook_type.lower() == "web" and any(
        key in update_kwargs
        for key in [
            "endpoint",
            "username",
            "password",
            "certificateKey",
            "certificatePassword",
        ]
    ):
        update_kwargs["hookType"] = "Webhook"
        update_kwargs["hookParameter"] = {}
        if "endpoint" in update_kwargs:
            update_kwargs["hookParameter"]["endpoint"] = update_kwargs.pop("endpoint")
        if "username" in update_kwargs:
            update_kwargs["hookParameter"]["username"] = update_kwargs.pop("username")
        if "password" in update_kwargs:
            update_kwargs["hookParameter"]["password"] = update_kwargs.pop("password")
        if "certificateKey" in update_kwargs:
            update_kwargs["hookParameter"]["certificateKey"] = update_kwargs.pop("certificateKey")
        if "certificatePassword" in update_kwargs:
            update_kwargs["hookParameter"]["certificatePassword"] = update_kwargs.pop("certificatePassword")

    return update_kwargs


def construct_detection_config_dict(update_kwargs):

    if "wholeMetricConfiguration" in update_kwargs:
        update_kwargs["wholeMetricConfiguration"] = (
            update_kwargs["wholeMetricConfiguration"]._to_generated_patch()
            if update_kwargs["wholeMetricConfiguration"]
            else None
        )
    if "dimensionGroupOverrideConfigurations" in update_kwargs:
        update_kwargs["dimensionGroupOverrideConfigurations"] = (
            [group._to_generated() for group in update_kwargs["dimensionGroupOverrideConfigurations"]]
            if update_kwargs["dimensionGroupOverrideConfigurations"]
            else None
        )
    if "seriesOverrideConfigurations" in update_kwargs:
        update_kwargs["seriesOverrideConfigurations"] = (
            [series._to_generated() for series in update_kwargs["seriesOverrideConfigurations"]]
            if update_kwargs["seriesOverrideConfigurations"]
            else None
        )

    return update_kwargs


def construct_alert_config_dict(update_kwargs):

    if "metricAlertingConfigurations" in update_kwargs:
        update_kwargs["metricAlertingConfigurations"] = (
            [config._to_generated() for config in update_kwargs["metricAlertingConfigurations"]]
            if update_kwargs["metricAlertingConfigurations"]
            else None
        )

    return update_kwargs


def construct_data_feed_dict(update_kwargs):
    if "dataStartFrom" in update_kwargs:
        update_kwargs["dataStartFrom"] = Serializer.serialize_iso(update_kwargs["dataStartFrom"])

    if "dataSourceParameter" in update_kwargs:
        update_kwargs["authenticationType"] = update_kwargs["dataSourceParameter"].authentication_type
        update_kwargs["credentialId"] = update_kwargs["dataSourceParameter"].credential_id
        update_kwargs["dataSourceParameter"] = update_kwargs["dataSourceParameter"]._to_generated_patch()
    return update_kwargs


def convert_datetime(date_time):
    # type: (Union[str, datetime.datetime]) -> datetime.datetime
    if isinstance(date_time, datetime.datetime):
        return date_time
    if isinstance(date_time, six.string_types):
        try:
            return datetime.datetime.strptime(date_time, "%Y-%m-%d")
        except ValueError:
            try:
                return datetime.datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                return datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    raise TypeError("Bad datetime type")


def convert_to_generated_data_feed_type(
    generated_feed_type,
    name,
    source,
    granularity,
    schema,
    ingestion_settings,
    admins=None,
    data_feed_description=None,
    missing_data_point_fill_settings=None,
    rollup_settings=None,
    viewers=None,
    access_mode=None,
    action_link_template=None,
):
    """Convert input to data feed generated model type
    :param generated_feed_type: generated model type of data feed
    :type generated_feed_type: Union[AzureApplicationInsightsDataFeed, AzureBlobDataFeed, AzureCosmosDBDataFeed,
        AzureDataExplorerDataFeed, AzureDataLakeStorageGen2DataFeed, AzureTableDataFeed, AzureLogAnalyticsDataFeed,
        InfluxDBDataFeed, MySqlDataFeed, PostgreSqlDataFeed, SQLServerDataFeed, MongoDBDataFeed,
        AzureEventHubsDataFeed]
    :param str name: Name for the data feed.
    :param source: The exposed model source of the data feed
    :type source: Union[AzureApplicationInsightsDataFeedSource, AzureBlobDataFeedSource, AzureCosmosDbDataFeedSource,
        AzureDataExplorerDataFeedSource, AzureDataLakeStorageGen2DataFeedSource, AzureTableDataFeedSource,
        AzureLogAnalyticsDataFeedSource, InfluxDbDataFeedSource, MySqlDataFeedSource, PostgreSqlDataFeedSource,
        SqlServerDataFeedSource, MongoDbDataFeedSource, AzureEventHubsDataFeedSource]
    :param granularity: Granularity type and amount if using custom.
    :type granularity: ~azure.ai.metricsadvisor.models.DataFeedGranularity
    :param schema: Data feed schema
    :type schema: ~azure.ai.metricsadvisor.models.DataFeedSchema
    :param ingestion_settings: The data feed ingestions settings
    :type ingestion_settings: ~azure.ai.metricsadvisor.models.DataFeedIngestionSettings
    :param list[str] admins: Data feed administrators.
    :param str data_feed_description: Data feed description.
    :param missing_data_point_fill_settings: The fill missing point type and value.
    :type missing_data_point_fill_settings:
        ~azure.ai.metricsadvisor.models.DataFeedMissingDataPointFillSettings
    :param rollup_settings: The rollup settings.
    :type rollup_settings:
        ~azure.ai.metricsadvisor.models.DataFeedRollupSettings
    :param list[str] viewers: Data feed viewers.
    :param access_mode: Data feed access mode. Possible values include:
        "Private", "Public". Default value: "Private".
    :type access_mode: str or ~azure.ai.metricsadvisor.models.DataFeedAccessMode
    :param str action_link_template: action link for alert.
    :rtype: Union[AzureApplicationInsightsDataFeed, AzureBlobDataFeed, AzureCosmosDBDataFeed,
        AzureDataExplorerDataFeed, AzureDataLakeStorageGen2DataFeed, AzureTableDataFeed, AzureLogAnalyticsDataFeed,
        InfluxDBDataFeed, MySqlDataFeed, PostgreSqlDataFeed, SQLServerDataFeed, MongoDBDataFeed,
        AzureEventHubsDataFeed]
    :return: The generated model for the data source type
    """

    if isinstance(granularity, (DataFeedGranularityType, six.string_types)):
        granularity = DataFeedGranularity(
            granularity_type=granularity,
        )

    if isinstance(schema, list):
        schema = DataFeedSchema(metrics=[DataFeedMetric(name=metric_name) for metric_name in schema])

    if isinstance(ingestion_settings, (datetime.datetime, six.string_types)):
        ingestion_settings = DataFeedIngestionSettings(ingestion_begin_time=ingestion_settings)

    return generated_feed_type(
        data_source_parameter=source._to_generated(),
        authentication_type=source.authentication_type,
        credential_id=source.credential_id,
        data_feed_name=name,
        granularity_name=granularity.granularity_type,
        granularity_amount=granularity.custom_granularity_value,
        metrics=[metric._to_generated() for metric in schema.metrics],
        dimension=[dimension._to_generated() for dimension in schema.dimensions] if schema.dimensions else None,
        timestamp_column=schema.timestamp_column,
        data_start_from=ingestion_settings.ingestion_begin_time,
        max_concurrency=ingestion_settings.data_source_request_concurrency,
        min_retry_interval_in_seconds=ingestion_settings.ingestion_retry_delay,
        start_offset_in_seconds=ingestion_settings.ingestion_start_offset,
        stop_retry_after_in_seconds=ingestion_settings.stop_retry_after,
        data_feed_description=data_feed_description,
        need_rollup=DataFeedRollupType._to_generated(rollup_settings.rollup_type) if rollup_settings else None,
        roll_up_method=rollup_settings.rollup_method if rollup_settings else None,
        roll_up_columns=rollup_settings.auto_rollup_group_by_column_names if rollup_settings else None,
        all_up_identification=rollup_settings.rollup_identification_value if rollup_settings else None,
        fill_missing_point_type=missing_data_point_fill_settings.fill_type
        if missing_data_point_fill_settings
        else None,
        fill_missing_point_value=missing_data_point_fill_settings.custom_fill_value
        if missing_data_point_fill_settings
        else None,
        viewers=viewers,
        view_mode=access_mode,
        admins=admins,
        action_link_template=action_link_template,
    )


class MetricsAdvisorClientOperationsMixin(_MetricsAdvisorClientOperationsMixin):
    @distributed_trace
    def create_alert_configuration(
        self,
        name,  # type: str
        metric_alert_configurations,  # type: List[MetricAlertConfiguration]
        hook_ids,  # type: List[str]
        **kwargs  # type: Any
    ):  # type: (...) -> AnomalyAlertConfiguration
        cross_metrics_operator = kwargs.pop("cross_metrics_operator", None)
        response_headers = super().create_alert_configuration(  # type: ignore
            AnomalyAlertConfiguration(
                name=name,
                metric_alert_configurations=metric_alert_configurations,
                hook_ids=hook_ids,
                cross_metrics_operator=cross_metrics_operator,
                description=kwargs.pop("description", None),
            ),
            cls=lambda pipeline_response, _, response_headers: response_headers,
            **kwargs
        )

        config_id = response_headers["Location"].split("configurations/")[1]
        return self.get_alert_configuration(config_id)

    @distributed_trace
    def create_data_feed(
        self,
        name,  # type: str
        source,  # type: DataFeedSourceUnion
        granularity,  # type: Union[str, DataFeedGranularityType, DataFeedGranularity]
        schema,  # type: Union[List[str], DataFeedSchema]
        ingestion_settings,  # type: Union[datetime.datetime, DataFeedIngestionSettings]
        **kwargs  # type: Any
    ):  # type: (...) -> DataFeed
        admins = kwargs.pop("admins", None)
        data_feed_description = kwargs.pop("data_feed_description", None)
        missing_data_point_fill_settings = kwargs.pop("missing_data_point_fill_settings", None)
        rollup_settings = kwargs.pop("rollup_settings", None)
        viewers = kwargs.pop("viewers", None)
        access_mode = kwargs.pop("access_mode", "Private")
        action_link_template = kwargs.pop("action_link_template", None)
        data_feed_type = DATA_FEED[source.data_source_type]
        data_feed_detail = convert_to_generated_data_feed_type(
            generated_feed_type=data_feed_type,
            name=name,
            source=source,
            granularity=granularity,
            schema=schema,
            ingestion_settings=ingestion_settings,
            admins=admins,
            data_feed_description=data_feed_description,
            missing_data_point_fill_settings=missing_data_point_fill_settings,
            rollup_settings=rollup_settings,
            viewers=viewers,
            access_mode=access_mode,
            action_link_template=action_link_template,
        )

        response_headers = super().create_data_feed(  # type: ignore
            data_feed_detail, cls=lambda pipeline_response, _, response_headers: response_headers, **kwargs
        )
        data_feed_id = response_headers["Location"].split("dataFeeds/")[1]
        return self.get_data_feed(data_feed_id)

    @distributed_trace
    def create_hook(
        self,
        hook,  # type: Union[EmailNotificationHook, WebNotificationHook]
        **kwargs  # type: Any
    ):  # type: (...) -> Union[NotificationHook, EmailNotificationHook, WebNotificationHook]
        hook_request = None
        if hook.hook_type == "Email":
            hook_request = hook._to_generated()

        if hook.hook_type == "Webhook":
            hook_request = hook._to_generated()

        response_headers = super().create_hook(  # type: ignore
            hook_request, cls=lambda pipeline_response, _, response_headers: response_headers, **kwargs  # type: ignore
        )
        hook_id = response_headers["Location"].split("hooks/")[1]
        return self.get_hook(hook_id)

    @distributed_trace
    def create_detection_configuration(
        self,
        name,  # type: str
        metric_id,  # type: str
        whole_series_detection_condition,  # type: MetricDetectionCondition
        **kwargs  # type: Any
    ):  # type: (...) -> AnomalyDetectionConfiguration
        description = kwargs.pop("description", None)
        series_group_detection_conditions = kwargs.pop("series_group_detection_conditions", None)
        series_detection_conditions = kwargs.pop("series_detection_conditions", None)
        config = AnomalyDetectionConfiguration(
            name=name,
            metric_id=metric_id,
            description=description,
            whole_metric_configuration=whole_series_detection_condition._to_generated(),
            dimension_group_override_configurations=[
                group._to_generated() for group in series_group_detection_conditions
            ]
            if series_group_detection_conditions
            else None,
            series_override_configurations=[series._to_generated() for series in series_detection_conditions]
            if series_detection_conditions
            else None,
        )

        response_headers = super().create_detection_configuration(  # type: ignore
            config, cls=lambda pipeline_response, _, response_headers: response_headers, **kwargs
        )
        config_id = response_headers["Location"].split("configurations/")[1]
        return self.get_detection_configuration(config_id)

    @distributed_trace
    def get_data_feed(self, data_feed_id, **kwargs):
        # type: (str, Any) -> DataFeed
        data_feed = super().get_data_feed(data_feed_id, **kwargs)
        return DataFeed._from_generated(data_feed)

    @distributed_trace
    def get_alert_configuration(self, alert_configuration_id, **kwargs):
        # type: (str, Any) -> AnomalyAlertConfiguration
        config = super().get_alert_configuration(alert_configuration_id, **kwargs)
        return AnomalyAlertConfiguration._from_generated(config)

    @distributed_trace
    def get_detection_configuration(self, detection_configuration_id, **kwargs):
        # type: (str, Any) -> AnomalyDetectionConfiguration
        config = super().get_detection_configuration(detection_configuration_id, **kwargs)
        return AnomalyDetectionConfiguration._from_generated(config)

    @distributed_trace
    def get_hook(
        self,
        hook_id,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> Union[NotificationHook, EmailNotificationHook, WebNotificationHook]
        hook = super().get_hook(hook_id, **kwargs)
        if hook.hook_type == "Email":
            return EmailNotificationHook._from_generated(hook)
        return WebNotificationHook._from_generated(hook)

    @distributed_trace
    def get_data_feed_ingestion_progress(
        self,
        data_feed_id,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> DataFeedIngestionProgress
        ingestion_process = super().get_data_feed_ingestion_progress(data_feed_id, **kwargs)
        return DataFeedIngestionProgress._from_generated(ingestion_process)

    @distributed_trace
    def refresh_data_feed_ingestion(
        self,
        data_feed_id,  # type: str
        start_time,  # type: Union[str, datetime.datetime]
        end_time,  # type: Union[str, datetime.datetime]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        converted_start_time = convert_datetime(start_time)
        converted_end_time = convert_datetime(end_time)
        super().refresh_data_feed_ingestion(
            data_feed_id,
            body=IngestionProgressResetOptions(start_time=converted_start_time, end_time=converted_end_time),
            **kwargs
        )

    @distributed_trace
    def delete_alert_configuration(self, *alert_configuration_id, **kwargs):
        # type: (*str, Any) -> None
        if len(alert_configuration_id) != 1:
            raise TypeError("Alert configuration requires exactly one id.")

        super().delete_alert_configuration(alert_configuration_id[0], **kwargs)

    @distributed_trace
    def delete_detection_configuration(self, *detection_configuration_id, **kwargs):
        # type: (*str, Any) -> None
        if len(detection_configuration_id) != 1:
            raise TypeError("Detection configuration requires exactly one id.")

        super().delete_detection_configuration(detection_configuration_id[0], **kwargs)

    @distributed_trace
    def delete_data_feed(self, *data_feed_id, **kwargs):
        # type: (*str, Any) -> None
        if len(data_feed_id) != 1:
            raise TypeError("Data feed requires exactly one id.")

        super().delete_data_feed(data_feed_id[0], **kwargs)

    @distributed_trace
    def delete_hook(self, *hook_id, **kwargs):
        # type: (*str, Any) -> None
        if len(hook_id) != 1:
            raise TypeError("Hook requires exactly one id.")

        super().delete_hook(hook_id[0], **kwargs)

    @distributed_trace
    def update_data_feed(
        self,
        data_feed,  # type: Union[str, DataFeed]
        **kwargs  # type: Any
    ):  # type: (...) -> DataFeed
        unset = object()
        update_kwargs = {}
        update_kwargs["dataFeedName"] = kwargs.pop("name", unset)
        update_kwargs["dataFeedDescription"] = kwargs.pop("data_feed_description", unset)
        update_kwargs["timestampColumn"] = kwargs.pop("timestamp_column", unset)
        update_kwargs["dataStartFrom"] = kwargs.pop("ingestion_begin_time", unset)
        update_kwargs["startOffsetInSeconds"] = kwargs.pop("ingestion_start_offset", unset)
        update_kwargs["maxConcurrency"] = kwargs.pop("data_source_request_concurrency", unset)
        update_kwargs["minRetryIntervalInSeconds"] = kwargs.pop("ingestion_retry_delay", unset)
        update_kwargs["stopRetryAfterInSeconds"] = kwargs.pop("stop_retry_after", unset)
        update_kwargs["needRollup"] = kwargs.pop("rollup_type", unset)
        update_kwargs["rollUpMethod"] = kwargs.pop("rollup_method", unset)
        update_kwargs["rollUpColumns"] = kwargs.pop("auto_rollup_group_by_column_names", unset)
        update_kwargs["allUpIdentification"] = kwargs.pop("rollup_identification_value", unset)
        update_kwargs["fillMissingPointType"] = kwargs.pop("fill_type", unset)
        update_kwargs["fillMissingPointValue"] = kwargs.pop("custom_fill_value", unset)
        update_kwargs["viewMode"] = kwargs.pop("access_mode", unset)
        update_kwargs["admins"] = kwargs.pop("admins", unset)
        update_kwargs["viewers"] = kwargs.pop("viewers", unset)
        update_kwargs["status"] = kwargs.pop("status", unset)
        update_kwargs["actionLinkTemplate"] = kwargs.pop("action_link_template", unset)
        update_kwargs["dataSourceParameter"] = kwargs.pop("source", unset)

        update = {key: value for key, value in update_kwargs.items() if value != unset}

        if isinstance(data_feed, six.string_types):
            data_feed_id = data_feed
            data_feed_patch = construct_data_feed_dict(update)

        else:
            data_feed_id = data_feed.id
            data_feed_patch_type = DATA_FEED_PATCH[data_feed.source.data_source_type]
            data_feed_patch = data_feed._to_generated_patch(data_feed_patch_type, update)

        return DataFeed._from_generated(super().update_data_feed(data_feed_id, data_feed_patch, **kwargs))

    @distributed_trace
    def update_alert_configuration(
        self,
        alert_configuration,  # type: Union[str, AnomalyAlertConfiguration]
        **kwargs  # type: Any
    ):
        # type: (...) -> AnomalyAlertConfiguration
        unset = object()
        update_kwargs = {}
        update_kwargs["name"] = kwargs.pop("name", unset)
        update_kwargs["hookIds"] = kwargs.pop("hook_ids", unset)
        update_kwargs["crossMetricsOperator"] = kwargs.pop("cross_metrics_operator", unset)
        update_kwargs["metricAlertingConfigurations"] = kwargs.pop("metric_alert_configurations", unset)
        update_kwargs["description"] = kwargs.pop("description", unset)

        update = {key: value for key, value in update_kwargs.items() if value != unset}
        if isinstance(alert_configuration, six.string_types):
            alert_configuration_id = alert_configuration
            alert_configuration_patch = construct_alert_config_dict(update)

        else:
            alert_configuration_id = alert_configuration.id
            alert_configuration_patch = alert_configuration._to_generated_patch(
                name=update.pop("name", None),
                metric_alert_configurations=update.pop("metricAlertingConfigurations", None),
                hook_ids=update.pop("hookIds", None),
                cross_metrics_operator=update.pop("crossMetricsOperator", None),
                description=update.pop("description", None),
            )

        return AnomalyAlertConfiguration._from_generated(
            super().update_alert_configuration(alert_configuration_id, alert_configuration_patch, **kwargs)
        )

    @distributed_trace
    def update_detection_configuration(
        self,
        detection_configuration,  # type: Union[str, AnomalyDetectionConfiguration]
        **kwargs  # type: Any
    ):
        # type: (...) -> AnomalyDetectionConfiguration
        unset = object()
        update_kwargs = {}
        update_kwargs["name"] = kwargs.pop("name", unset)
        update_kwargs["wholeMetricConfiguration"] = kwargs.pop("whole_series_detection_condition", unset)
        update_kwargs["dimensionGroupOverrideConfigurations"] = kwargs.pop("series_group_detection_conditions", unset)
        update_kwargs["seriesOverrideConfigurations"] = kwargs.pop("series_detection_conditions", unset)
        update_kwargs["description"] = kwargs.pop("description", unset)

        update = {key: value for key, value in update_kwargs.items() if value != unset}
        if isinstance(detection_configuration, six.string_types):
            detection_configuration_id = detection_configuration
            detection_config_patch = construct_detection_config_dict(update)

        else:
            detection_configuration_id = detection_configuration.id
            detection_config_patch = detection_configuration._to_generated_patch(
                name=update.pop("name", None),
                description=update.pop("description", None),
                whole_series_detection_condition=update.pop("wholeMetricConfiguration", None),
                series_group_detection_conditions=update.pop("dimensionGroupOverrideConfigurations", None),
                series_detection_conditions=update.pop("seriesOverrideConfigurations", None),
            )

        return AnomalyDetectionConfiguration._from_generated(
            super().update_anomaly_detection_configuration(detection_configuration_id, detection_config_patch, **kwargs)
        )

    @distributed_trace
    def update_hook(
        self,
        hook,  # type: Union[str, EmailNotificationHook, WebNotificationHook]
        **kwargs  # type: Any
    ):
        # type: (...) -> Union[NotificationHook, EmailNotificationHook, WebNotificationHook]
        unset = object()
        update_kwargs = {}
        hook_patch = None
        hook_type = kwargs.pop("hook_type", None)
        update_kwargs["hookName"] = kwargs.pop("name", unset)
        update_kwargs["description"] = kwargs.pop("description", unset)
        update_kwargs["externalLink"] = kwargs.pop("external_link", unset)
        update_kwargs["toList"] = kwargs.pop("emails_to_alert", unset)
        update_kwargs["endpoint"] = kwargs.pop("endpoint", unset)
        update_kwargs["username"] = kwargs.pop("username", unset)
        update_kwargs["password"] = kwargs.pop("password", unset)
        update_kwargs["certificateKey"] = kwargs.pop("certificate_key", unset)
        update_kwargs["certificatePassword"] = kwargs.pop("certificate_password", unset)

        update = {key: value for key, value in update_kwargs.items() if value != unset}
        if isinstance(hook, six.string_types):
            hook_id = hook
            if hook_type is None:
                raise ValueError("hook_type must be passed with a hook ID.")

            hook_patch = construct_hook_dict(update, hook_type)

        else:
            hook_id = hook.id
            if hook.hook_type == "Email":
                hook = cast(EmailNotificationHook, hook)
                hook_patch = hook._to_generated_patch(
                    name=update.pop("hookName", None),
                    description=update.pop("description", None),
                    external_link=update.pop("externalLink", None),
                    emails_to_alert=update.pop("toList", None),
                )

            elif hook.hook_type == "Webhook":
                hook = cast(WebNotificationHook, hook)
                hook_patch = hook._to_generated_patch(
                    name=update.pop("hookName", None),
                    description=update.pop("description", None),
                    external_link=update.pop("externalLink", None),
                    endpoint=update.pop("endpoint", None),
                    password=update.pop("password", None),
                    username=update.pop("username", None),
                    certificate_key=update.pop("certificateKey", None),
                    certificate_password=update.pop("certificatePassword", None),
                )

        updated_hook = super().update_hook(hook_id, hook_patch, **kwargs)

        if updated_hook.hook_type == "Email":
            return EmailNotificationHook._from_generated(updated_hook)
        return WebNotificationHook._from_generated(updated_hook)

    @distributed_trace
    def list_hooks(
        self, **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[Union[NotificationHook, EmailNotificationHook, WebNotificationHook]]
        hook_name = kwargs.pop("hook_name", None)
        skip = kwargs.pop("skip", None)

        def _convert_to_hook_type(hook):
            if hook.hook_type == "Email":
                return EmailNotificationHook._from_generated(hook)
            return WebNotificationHook._from_generated(hook)

        return super().list_hooks(  # type: ignore
            hook_name=hook_name,
            skip=skip,
            cls=kwargs.pop("cls", lambda hooks: [_convert_to_hook_type(hook) for hook in hooks]),
            **kwargs
        )

    @distributed_trace
    def list_data_feeds(
        self, **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[DataFeed]
        data_feed_name = kwargs.pop("data_feed_name", None)
        data_source_type = kwargs.pop("data_source_type", None)
        granularity_type = kwargs.pop("granularity_type", None)
        status = kwargs.pop("status", None)
        creator = kwargs.pop("creator", None)
        skip = kwargs.pop("skip", None)

        return super().list_data_feeds(  # type: ignore
            data_feed_name=data_feed_name,
            data_source_type=data_source_type,
            granularity_name=granularity_type,
            status=status,
            creator=creator,
            skip=skip,
            cls=kwargs.pop("cls", lambda feeds: [DataFeed._from_generated(feed) for feed in feeds]),
            **kwargs
        )

    @distributed_trace
    def list_alert_configurations(
        self,
        detection_configuration_id,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[AnomalyAlertConfiguration]
        return super().list_alert_configurations(  # type: ignore
            detection_configuration_id,
            cls=kwargs.pop(
                "cls",
                lambda confs: [AnomalyAlertConfiguration._from_generated(conf) for conf in confs],
            ),
            **kwargs
        )

    @distributed_trace
    def list_detection_configurations(
        self,
        metric_id,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[AnomalyDetectionConfiguration]
        return super().list_detection_configurations(  # type: ignore
            metric_id,
            cls=kwargs.pop(
                "cls",
                lambda confs: [AnomalyDetectionConfiguration._from_generated(conf) for conf in confs],
            ),
            **kwargs
        )

    @distributed_trace
    def list_data_feed_ingestion_status(
        self,
        data_feed_id,  # type: str
        start_time,  # type: Union[str, datetime.datetime]
        end_time,  # type: Union[str, datetime.datetime]
        **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[DataFeedIngestionStatus]
        skip = kwargs.pop("skip", None)
        converted_start_time = convert_datetime(start_time)
        converted_end_time = convert_datetime(end_time)

        return super().list_data_feed_ingestion_status(  # type: ignore
            data_feed_id=data_feed_id,
            body=IngestionStatusQueryOptions(start_time=converted_start_time, end_time=converted_end_time),
            skip=skip,
            **kwargs
        )

    @distributed_trace
    def get_datasource_credential(
        self,
        credential_id,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> DatasourceCredentialUnion
        datasource_credential = super().get_datasource_credential(credential_id, **kwargs)
        return convert_to_datasource_credential(datasource_credential)

    @distributed_trace
    def create_datasource_credential(
        self,
        datasource_credential,  # type: DatasourceCredentialUnion
        **kwargs  # type: Any
    ):
        # type: (...) -> DatasourceCredentialUnion
        datasource_credential_request = None
        if datasource_credential.credential_type in [
            "AzureSQLConnectionString",
            "DataLakeGen2SharedKey",
            "ServicePrincipal",
            "ServicePrincipalInKV",
        ]:
            datasource_credential_request = datasource_credential._to_generated()

        response_headers = super().create_datasource_credential(  # type: ignore
            datasource_credential_request,  # type: ignore
            cls=lambda pipeline_response, _, response_headers: response_headers,
            **kwargs
        )
        credential_id = response_headers["Location"].split("credentials/")[1]
        return self.get_datasource_credential(credential_id)

    @distributed_trace
    def list_datasource_credentials(
        self, **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[DatasourceCredential]
        return super().list_credentials(  # type: ignore
            cls=kwargs.pop(
                "cls",
                lambda credentials: [convert_to_datasource_credential(credential) for credential in credentials],
            ),
            **kwargs
        )

    @distributed_trace
    def update_datasource_credential(
        self,
        datasource_credential,  # type: DatasourceCredential
        **kwargs  # type: Any
    ):
        # type: (...) -> DatasourceCredential
        datasource_credential_request = None
        if datasource_credential.credential_type in [
            "AzureSQLConnectionString",
            "DataLakeGen2SharedKey",
            "ServicePrincipal",
            "ServicePrincipalInKV",
        ]:
            datasource_credential_request = datasource_credential._to_generated_patch()

        updated_datasource_credential = super().update_credential(  # type: ignore
            datasource_credential.id, datasource_credential_request, **kwargs  # type: ignore
        )

        return convert_to_datasource_credential(updated_datasource_credential)

    @distributed_trace
    def delete_datasource_credential(self, *credential_id, **kwargs):
        # type: (*str, Any) -> None
        if len(credential_id) != 1:
            raise TypeError("Credential requires exactly one id.")

        super().delete_datasource_credential(credential_id=credential_id[0], **kwargs)

    @distributed_trace
    def add_feedback(self, feedback, **kwargs):
        # type: (FeedbackUnion, Any) -> None
        return super().add_feedback(body=feedback._to_generated(), **kwargs)

    @distributed_trace
    def get_feedback(self, feedback_id, **kwargs):
        # type: (str, Any) -> Union[MetricFeedback, FeedbackUnion]
        return convert_to_sub_feedback(super().get_feedback(feedback_id=feedback_id, **kwargs))

    @distributed_trace
    def list_feedback(self, metric_id, **kwargs):
        # type: (str, Any) -> ItemPaged[Union[MetricFeedback, FeedbackUnion]]
        skip = kwargs.pop("skip", None)
        dimension_filter = None
        dimension_key = kwargs.pop("dimension_key", None)
        if dimension_key:
            dimension_filter = FeedbackDimensionFilter(dimension=dimension_key)
        feedback_type = kwargs.pop("feedback_type", None)
        start_time = kwargs.pop("start_time", None)
        end_time = kwargs.pop("end_time", None)
        converted_start_time = convert_datetime(start_time) if start_time else None
        converted_end_time = convert_datetime(end_time) if end_time else None
        time_mode = kwargs.pop("time_mode", None)
        feedback_filter = MetricFeedbackFilter(
            metric_id=metric_id,
            dimension_filter=dimension_filter,
            feedback_type=feedback_type,
            start_time=converted_start_time,
            end_time=converted_end_time,
            time_mode=time_mode,
        )

        return super().list_feedback(  # type: ignore
            skip=skip,
            body=feedback_filter,
            cls=kwargs.pop("cls", lambda result: [convert_to_sub_feedback(x) for x in result]),
            **kwargs
        )

    @distributed_trace
    def list_incident_root_causes(self, detection_configuration_id, incident_id, **kwargs):
        # type: (str, str, Any) -> ItemPaged[IncidentRootCause]
        return super().list_incident_root_causes(  # type: ignore
            configuration_id=detection_configuration_id,
            incident_id=incident_id,
            cls=kwargs.pop(
                "cls",
                lambda result: [IncidentRootCause._from_generated(x) for x in result],
            ),
            **kwargs
        )

    @distributed_trace
    def list_metric_enriched_series_data(
        self,
        detection_configuration_id,  # type: str
        series,  # type: Union[List[SeriesIdentity], List[Dict[str, str]]]
        start_time,  # type: Union[str, datetime.datetime]
        end_time,  # type: Union[str, datetime.datetime]
        **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[MetricEnrichedSeriesData]
        series_list = [
            SeriesIdentity(dimension=dimension) for dimension in series if isinstance(dimension, dict)
        ] or series

        series_list = cast(List[SeriesIdentity], series_list)
        converted_start_time = convert_datetime(start_time)
        converted_end_time = convert_datetime(end_time)
        detection_series_query = DetectionSeriesQuery(
            start_time=converted_start_time,
            end_time=converted_end_time,
            series=series_list,
        )

        return super().list_metric_enriched_series_data(  # type: ignore
            configuration_id=detection_configuration_id,
            body=detection_series_query,
            cls=kwargs.pop(
                "cls",
                lambda series: [MetricEnrichedSeriesData._from_generated(data) for data in series],
            ),
            **kwargs
        )

    @distributed_trace
    def list_alerts(
        self,
        alert_configuration_id,  # type: str
        start_time,  # type: datetime.datetime
        end_time,  # type: datetime.datetime
        time_mode,  # type: Union[str, AlertQueryTimeMode]
        **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[AnomalyAlert]
        skip = kwargs.pop("skip", None)
        converted_start_time = convert_datetime(start_time)
        converted_end_time = convert_datetime(end_time)

        alerting_result_query = AlertingResultQuery(
            start_time=converted_start_time,
            end_time=converted_end_time,
            time_mode=time_mode,
        )

        return super().list_alerts(  # type: ignore
            configuration_id=alert_configuration_id,
            skip=skip,
            body=alerting_result_query,
            cls=kwargs.pop(
                "cls",
                lambda alerts: [AnomalyAlert._from_generated(alert) for alert in alerts],
            ),
            **kwargs
        )

    def _list_anomalies_for_alert(self, alert_configuration_id, alert_id, **kwargs):
        # type: (str, str, Any) -> ItemPaged[DataPointAnomaly]

        skip = kwargs.pop("skip", None)

        return super().get_anomalies_from_alert_by_anomaly_alerting_configuration(  # type: ignore
            configuration_id=alert_configuration_id,
            alert_id=alert_id,
            skip=skip,
            cls=lambda objs: [DataPointAnomaly._from_generated(x) for x in objs],
            **kwargs
        )

    def _list_anomalies_for_detection_configuration(self, detection_configuration_id, start_time, end_time, **kwargs):
        # type: (...) -> ItemPaged[DataPointAnomaly]

        skip = kwargs.pop("skip", None)
        condition = kwargs.pop("filter", None)
        filter_condition = condition._to_generated() if condition else None
        converted_start_time = convert_datetime(start_time)
        converted_end_time = convert_datetime(end_time)
        detection_anomaly_result_query = DetectionAnomalyResultQuery(
            start_time=converted_start_time,
            end_time=converted_end_time,
            filter=filter_condition,
        )

        return super().get_anomalies_by_anomaly_detection_configuration(  # type: ignore
            configuration_id=detection_configuration_id,
            skip=skip,
            body=detection_anomaly_result_query,
            cls=lambda objs: [DataPointAnomaly._from_generated(x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def list_anomalies(self, **kwargs):
        # type: (Any) -> ItemPaged[DataPointAnomaly]
        alert_configuration_id = kwargs.get("alert_configuration_id", None)
        alert_id = kwargs.get("alert_id", None)
        detection_configuration_id = kwargs.get("detection_configuration_id", None)
        start_time = kwargs.get("start_time", None)
        end_time = kwargs.get("end_time", None)
        if detection_configuration_id:
            if alert_configuration_id or alert_id:
                raise TypeError(
                    'Specify either "detection_configuration_id" or "alert_configuration_id" and "alert_id"'
                )
            if not start_time or not end_time:
                raise TypeError('"start_time" and "end_time" are required')
            return self._list_anomalies_for_detection_configuration(**kwargs)
        if not alert_configuration_id or not alert_id:
            raise TypeError('"alert_configuration_id" and "alert_id" are required')
        return self._list_anomalies_for_alert(**kwargs)

    @distributed_trace
    def list_anomaly_dimension_values(self, detection_configuration_id, dimension_name, start_time, end_time, **kwargs):
        # type: (str, str, Union[str, datetime.datetime], Union[str, datetime.datetime], Any) -> ItemPaged[str]
        skip = kwargs.pop("skip", None)
        dimension = kwargs.pop("dimension_filter", None)
        dimension_filter = DimensionGroupIdentity(dimension=dimension) if dimension else None
        converted_start_time = convert_datetime(start_time)
        converted_end_time = convert_datetime(end_time)
        anomaly_dimension_query = AnomalyDimensionQuery(
            start_time=converted_start_time,
            end_time=converted_end_time,
            dimension_name=dimension_name,
            dimension_filter=dimension_filter,
        )

        return super().list_anomaly_dimension_values(  # type: ignore
            configuration_id=detection_configuration_id, skip=skip, body=anomaly_dimension_query, **kwargs
        )

    def _list_incidents_for_alert(self, alert_configuration_id, alert_id, **kwargs):
        # type: (str, str, Any) -> ItemPaged[AnomalyIncident]

        skip = kwargs.pop("skip", None)

        return super().get_incidents_from_alert_by_anomaly_alerting_configuration(  # type: ignore
            configuration_id=alert_configuration_id,
            alert_id=alert_id,
            skip=skip,
            cls=lambda objs: [AnomalyIncident._from_generated(x) for x in objs],
            **kwargs
        )

    def _list_incidents_for_detection_configuration(self, detection_configuration_id, start_time, end_time, **kwargs):
        # type: (str, Union[str, datetime.datetime], Union[str, datetime.datetime], Any) -> ItemPaged[AnomalyIncident]

        condition = kwargs.pop("filter", None)
        filter_condition = condition._to_generated() if condition else None
        converted_start_time = convert_datetime(start_time)
        converted_end_time = convert_datetime(end_time)

        detection_incident_result_query = DetectionIncidentResultQuery(
            start_time=converted_start_time,
            end_time=converted_end_time,
            filter=filter_condition,
        )

        return super().get_incidents_by_anomaly_detection_configuration(  # type: ignore
            configuration_id=detection_configuration_id,
            body=detection_incident_result_query,
            cls=lambda objs: [AnomalyIncident._from_generated(x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def list_incidents(self, **kwargs):
        # type: (Any) -> ItemPaged[AnomalyIncident]
        alert_configuration_id = kwargs.get("alert_configuration_id", None)
        alert_id = kwargs.get("alert_id", None)
        detection_configuration_id = kwargs.get("detection_configuration_id", None)
        start_time = kwargs.get("start_time", None)
        end_time = kwargs.get("end_time", None)
        if detection_configuration_id:
            if alert_configuration_id or alert_id:
                raise TypeError(
                    'Specify either "detection_configuration_id" or "alert_configuration_id" and "alert_id"'
                )
            if not start_time or not end_time:
                raise TypeError('"start_time" and "end_time" are required')
            return self._list_incidents_for_detection_configuration(**kwargs)
        if not alert_configuration_id or not alert_id:
            raise TypeError('"alert_configuration_id" and "alert_id" are required')
        return self._list_incidents_for_alert(**kwargs)

    @distributed_trace
    def list_metric_dimension_values(self, metric_id, dimension_name, **kwargs):
        # type: (str, str, Any) -> ItemPaged[str]
        skip = kwargs.pop("skip", None)
        dimension_value_filter = kwargs.pop("dimension_value_filter", None)

        metric_dimension_query_options = MetricDimensionQueryOptions(
            dimension_name=dimension_name,
            dimension_value_filter=dimension_value_filter,
        )

        return super().list_metric_dimension_values(  # type: ignore
            metric_id=metric_id, body=metric_dimension_query_options, skip=skip, **kwargs
        )

    @distributed_trace
    def list_metric_series_data(
        self,
        metric_id,  # type: str
        series_keys,  # type: List[Dict[str, str]]
        start_time,  # type: Union[str, datetime.datetime]
        end_time,  # type: Union[str, datetime.datetime]
        **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[MetricSeriesData]
        converted_start_time = convert_datetime(start_time)
        converted_end_time = convert_datetime(end_time)

        metric_data_query_options = MetricDataQueryOptions(
            start_time=converted_start_time,
            end_time=converted_end_time,
            series=series_keys,
        )

        return super().list_metric_series_data(  # type: ignore
            metric_id=metric_id,
            body=metric_data_query_options,
            cls=kwargs.pop(
                "cls",
                lambda result: [MetricSeriesData._from_generated(series) for series in result],
            ),
            **kwargs
        )

    @distributed_trace
    def list_metric_series_definitions(self, metric_id, active_since, **kwargs):
        # type: (str, datetime.datetime, Any) -> ItemPaged[MetricSeriesDefinition]
        skip = kwargs.pop("skip", None)
        dimension_filter = kwargs.pop("dimension_filter", None)

        metric_series_query_options = MetricSeriesQueryOptions(
            active_since=active_since,
            dimension_filter=dimension_filter,
        )

        return super().list_metric_series_definitions(  # type: ignore
            metric_id=metric_id, body=metric_series_query_options, skip=skip, **kwargs
        )

    @distributed_trace
    def list_metric_enrichment_status(self, metric_id, start_time, end_time, **kwargs):
        # type: (str, Union[str, datetime.datetime], Union[str, datetime.datetime], Any) -> ItemPaged[EnrichmentStatus]
        skip = kwargs.pop("skip", None)
        converted_start_time = convert_datetime(start_time)
        converted_end_time = convert_datetime(end_time)
        enrichment_status_query_option = EnrichmentStatusQueryOption(
            start_time=converted_start_time,
            end_time=converted_end_time,
        )

        return super().list_metric_enrichment_status(  # type: ignore
            metric_id=metric_id, skip=skip, body=enrichment_status_query_option, **kwargs
        )


__all__ = ["MetricsAdvisorClientOperationsMixin"]


def patch_sdk():
    pass
