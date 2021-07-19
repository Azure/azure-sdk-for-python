# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=protected-access

from typing import (
    Union,
    TYPE_CHECKING
)
import datetime
import six
from msrest import Serializer
from azure.core.exceptions import HttpResponseError
from .models import (
    DataFeedGranularityType,
    DataFeedGranularity,
    DataFeedSchema,
    DataFeedMetric,
    DataFeedIngestionSettings,
    AnomalyFeedback,
    ChangePointFeedback,
    CommentFeedback,
    PeriodFeedback,
    DataFeedRollupType,
    DatasourceSqlConnectionString,
    DatasourceDataLakeGen2SharedKey,
    DatasourceServicePrincipal,
    DatasourceServicePrincipalInKeyVault
)
from ._metrics_advisor_key_credential import MetricsAdvisorKeyCredential
from ._metrics_advisor_key_credential_policy import MetricsAdvisorKeyCredentialPolicy
if TYPE_CHECKING:
    from ._generated.models import MetricFeedback


def construct_alert_config_dict(update_kwargs):

    if "metricAlertingConfigurations" in update_kwargs:
        update_kwargs["metricAlertingConfigurations"] = [
            config._to_generated() for config in
            update_kwargs["metricAlertingConfigurations"]
        ] if update_kwargs["metricAlertingConfigurations"] else None

    return update_kwargs


def construct_detection_config_dict(update_kwargs):

    if "wholeMetricConfiguration" in update_kwargs:
        update_kwargs["wholeMetricConfiguration"] = update_kwargs["wholeMetricConfiguration"]._to_generated_patch() \
            if update_kwargs["wholeMetricConfiguration"] else None
    if "dimensionGroupOverrideConfigurations" in update_kwargs:
        update_kwargs["dimensionGroupOverrideConfigurations"] = [
            group._to_generated() for group in update_kwargs["dimensionGroupOverrideConfigurations"]
        ] if update_kwargs["dimensionGroupOverrideConfigurations"] else None
    if "seriesOverrideConfigurations" in update_kwargs:
        update_kwargs["seriesOverrideConfigurations"] = [
            series._to_generated() for series in update_kwargs["seriesOverrideConfigurations"]
        ] if update_kwargs["seriesOverrideConfigurations"] else None

    return update_kwargs


def construct_hook_dict(update_kwargs, hook_type):

    if hook_type.lower() == "email" and "toList" in update_kwargs:
        update_kwargs["hookType"] = "Email"
        update_kwargs["hookParameter"] = {}
        update_kwargs["hookParameter"]["toList"] = update_kwargs["toList"]
        update_kwargs.pop("toList")
    elif hook_type.lower() == "web" \
            and any(key in update_kwargs for key in
                    ["endpoint", "username", "password", "certificateKey", "certificatePassword"]):
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


def construct_data_feed_dict(update_kwargs):
    if "dataStartFrom" in update_kwargs:
        update_kwargs["dataStartFrom"] = Serializer.serialize_iso(update_kwargs["dataStartFrom"])

    if "dataSourceParameter" in update_kwargs:
        update_kwargs["authenticationType"] = update_kwargs["dataSourceParameter"].authentication_type
        update_kwargs["credentialId"] = update_kwargs["dataSourceParameter"].credential_id
        update_kwargs["dataSourceParameter"] = update_kwargs["dataSourceParameter"]._to_generated_patch()
    return update_kwargs


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
        action_link_template=None
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
        schema = DataFeedSchema(
            metrics=[DataFeedMetric(name=metric_name) for metric_name in schema]
        )

    if isinstance(ingestion_settings, (datetime.datetime, six.string_types)):
        ingestion_settings = DataFeedIngestionSettings(
            ingestion_begin_time=ingestion_settings
        )

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
        need_rollup=DataFeedRollupType._to_generated(rollup_settings.rollup_type)
        if rollup_settings else None,
        roll_up_method=rollup_settings.rollup_method if rollup_settings else None,
        roll_up_columns=rollup_settings.auto_rollup_group_by_column_names
        if rollup_settings else None,
        all_up_identification=rollup_settings.rollup_identification_value
        if rollup_settings else None,
        fill_missing_point_type=missing_data_point_fill_settings.fill_type
        if missing_data_point_fill_settings else None,
        fill_missing_point_value=missing_data_point_fill_settings.custom_fill_value
        if missing_data_point_fill_settings else None,
        viewers=viewers,
        view_mode=access_mode,
        admins=admins,
        action_link_template=action_link_template
    )

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

def get_authentication_policy(credential):
    authentication_policy = None
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if isinstance(credential, MetricsAdvisorKeyCredential):
        return MetricsAdvisorKeyCredentialPolicy(credential)
    if credential is not None and not hasattr(credential, "get_token"):
        raise TypeError(
            "Unsupported credential: {}. Use an instance of MetricsAdvisorKeyCredential "
            "or a token credential from azure.identity".format(type(credential))
        )

    return authentication_policy

def convert_to_datasource_credential(datasource_credential):
    if datasource_credential.data_source_credential_type == "AzureSQLConnectionString":
        return DatasourceSqlConnectionString._from_generated(datasource_credential)
    if datasource_credential.data_source_credential_type == "DataLakeGen2SharedKey":
        return DatasourceDataLakeGen2SharedKey._from_generated(datasource_credential)
    if datasource_credential.data_source_credential_type == "ServicePrincipal":
        return DatasourceServicePrincipal._from_generated(datasource_credential)
    return DatasourceServicePrincipalInKeyVault._from_generated(datasource_credential)
