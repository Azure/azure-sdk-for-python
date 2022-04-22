# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint:disable=protected-access
# pylint:disable=too-many-lines

import datetime
from typing import Any, Union, List, Dict, TYPE_CHECKING
from enum import Enum
import msrest
from azure.core import CaseInsensitiveEnumMeta
from .._generated.models import (
    MetricAlertingConfiguration as _MetricAlertingConfiguration,
    SeverityCondition as _SeverityCondition,
    TopNGroupScope as _TopNGroupScope,
    AlertSnoozeCondition as _AlertSnoozeCondition,
    ValueCondition as _ValueCondition,
    EmailHookInfo as _EmailHookInfo,
    WebhookHookInfo as _WebhookHookInfo,
    WholeMetricConfiguration as _WholeMetricConfiguration,
    WholeMetricConfigurationPatch as _WholeMetricConfigurationPatch,
    SuppressCondition as _SuppressCondition,
    SuppressConditionPatch as _SuppressConditionPatch,
    HardThresholdCondition as _HardThresholdCondition,
    HardThresholdConditionPatch as _HardThresholdConditionPatch,
    ChangeThresholdCondition as _ChangeThresholdCondition,
    ChangeThresholdConditionPatch as _ChangeThresholdConditionPatch,
    SmartDetectionCondition as _SmartDetectionCondition,
    SmartDetectionConditionPatch as _SmartDetectionConditionPatch,
    DimensionGroupConfiguration as _DimensionGroupConfiguration,
    SeriesConfiguration as _SeriesConfiguration,
    EmailHookInfoPatch as _EmailHookInfoPatch,
    WebhookHookInfoPatch as _WebhookHookInfoPatch,
    Dimension as _Dimension,
    Metric as _Metric,
    AnomalyFeedback as _AnomalyFeedback,
    FeedbackDimensionFilter,
    AnomalyFeedbackValue,
    ChangePointFeedback as _ChangePointFeedback,
    ChangePointFeedbackValue,
    CommentFeedback as _CommentFeedback,
    CommentFeedbackValue,
    PeriodFeedback as _PeriodFeedback,
    PeriodFeedbackValue,
    EmailHookParameterPatch as _EmailHookParameterPatch,
    WebhookHookParameterPatch as _WebhookHookParameterPatch,
    AzureBlobParameter as _AzureBlobParameter,
    AzureBlobParameterPatch as _AzureBlobParameterPatch,
    SqlSourceParameter as _SQLSourceParameter,
    SQLSourceParameterPatch as _SQLSourceParameterPatch,
    AzureApplicationInsightsParameter as _AzureApplicationInsightsParameter,
    AzureApplicationInsightsParameterPatch as _AzureApplicationInsightsParameterPatch,
    AzureCosmosDBParameter as _AzureCosmosDBParameter,
    AzureCosmosDBParameterPatch as _AzureCosmosDBParameterPatch,
    AzureTableParameter as _AzureTableParameter,
    AzureTableParameterPatch as _AzureTableParameterPatch,
    AzureEventHubsParameter as _AzureEventHubsParameter,
    AzureEventHubsParameterPatch as _AzureEventHubsParameterPatch,
    InfluxDBParameter as _InfluxDBParameter,
    InfluxDBParameterPatch as _InfluxDBParameterPatch,
    MongoDBParameter as _MongoDBParameter,
    MongoDBParameterPatch as _MongoDBParameterPatch,
    AzureDataLakeStorageGen2Parameter as _AzureDataLakeStorageGen2Parameter,
    AzureDataLakeStorageGen2ParameterPatch as _AzureDataLakeStorageGen2ParameterPatch,
    AzureLogAnalyticsParameter as _AzureLogAnalyticsParameter,
    AzureLogAnalyticsParameterPatch as _AzureLogAnalyticsParameterPatch,
    DimensionGroupIdentity as _DimensionGroupIdentity,
    SeriesIdentity as _SeriesIdentity,
    AnomalyAlertingConfiguration as _AnomalyAlertingConfiguration,
    AnomalyDetectionConfiguration as _AnomalyDetectionConfiguration,
    AnomalyAlertingConfigurationPatch as _AnomalyAlertingConfigurationPatch,
    AnomalyDetectionConfigurationPatch as _AnomalyDetectionConfigurationPatch,
    AzureSQLConnectionStringParam as _AzureSQLConnectionStringParam,
    AzureSQLConnectionStringParamPatch as _AzureSQLConnectionStringParamPatch,
    AzureSQLConnectionStringCredential as _AzureSQLConnectionStringCredential,
    AzureSQLConnectionStringCredentialPatch as _AzureSQLConnectionStringCredentialPatch,
    DataLakeGen2SharedKeyCredentialPatch as _DataLakeGen2SharedKeyCredentialPatch,
    DataLakeGen2SharedKeyParamPatch as _DataLakeGen2SharedKeyParamPatch,
    DataLakeGen2SharedKeyCredential as _DataLakeGen2SharedKeyCredential,
    DataLakeGen2SharedKeyParam as _DataLakeGen2SharedKeyParam,
    ServicePrincipalCredentialPatch as _ServicePrincipalCredentialPatch,
    ServicePrincipalParamPatch as _ServicePrincipalParamPatch,
    ServicePrincipalCredential as _ServicePrincipalCredential,
    ServicePrincipalParam as _ServicePrincipalParam,
    ServicePrincipalInKVCredentialPatch as _ServicePrincipalInKVCredentialPatch,
    ServicePrincipalInKVParamPatch as _ServicePrincipalInKVParamPatch,
    ServicePrincipalInKVCredential as _ServicePrincipalInKVCredential,
    ServicePrincipalInKVParam as _ServicePrincipalInKVParam,
    DetectionAnomalyFilterCondition as _DetectionAnomalyFilterCondition,
)
from .._generated import models as generated_models

if TYPE_CHECKING:
    from . import (
        SnoozeScope,
        AnomalyDetectorDirection,
    )
    from .._generated.models import (
        AnomalyResult,
        IncidentResult,
        RootCause,
    )
    from .._metrics_advisor_administration_client import DataFeedSourceUnion


class MetricAnomalyAlertScopeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Anomaly scope"""

    WHOLE_SERIES = "WholeSeries"
    SERIES_GROUP = "SeriesGroup"
    TOP_N = "TopN"

    @classmethod
    def _to_generated(cls, alert):
        try:
            alert = alert.value
        except AttributeError:
            pass
        if alert == "WholeSeries":
            return "All"
        if alert == "SeriesGroup":
            return "Dimension"
        return alert

    @classmethod
    def _from_generated(cls, alert):
        try:
            alert = alert.value
        except AttributeError:
            pass
        if alert == "All":
            return "WholeSeries"
        if alert == "Dimension":
            return "SeriesGroup"
        return alert


class DataFeedRollupType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Data feed rollup type"""

    NO_ROLLUP = "NoRollup"
    AUTO_ROLLUP = "AutoRollup"
    ALREADY_ROLLUP = "AlreadyRollup"

    @classmethod
    def _to_generated(cls, rollup):
        try:
            rollup = rollup.value
        except AttributeError:
            pass
        if rollup == "AutoRollup":
            return "NeedRollup"
        return rollup

    @classmethod
    def _from_generated(cls, rollup):
        try:
            rollup = rollup.value
        except AttributeError:
            pass
        if rollup == "NeedRollup":
            return "AutoRollup"
        return rollup


class MetricAnomalyAlertConfigurationsOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Cross metrics operator"""

    AND = "AND"
    OR = "OR"
    XOR = "XOR"


class DetectionConditionOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):

    AND = "AND"
    OR = "OR"


class DataFeedGranularity(object):
    """Data feed granularity

    :param granularity_type: Granularity of the time series. Possible values include:
        "Yearly", "Monthly", "Weekly", "Daily", "Hourly", "Minutely", "Secondly", "Custom".
    :type granularity_type: str or ~azure.ai.metricsadvisor.models.DataFeedGranularityType
    :keyword int custom_granularity_value: Must be populated if granularity_type is "Custom".
    """

    def __init__(self, granularity_type, **kwargs):
        # type: (Union[str, DataFeedGranularityType], Any) -> None
        self.granularity_type = granularity_type
        self.custom_granularity_value = kwargs.get("custom_granularity_value", None)

    def __repr__(self):
        return "DataFeedGranularity(granularity_type={}, custom_granularity_value={})".format(
            self.granularity_type, self.custom_granularity_value
        )[
            :1024
        ]

    @classmethod
    def _from_generated(cls, granularity_name, granularity_amount):
        return cls(
            granularity_type=granularity_name,
            custom_granularity_value=granularity_amount,
        )


class DataFeedIngestionSettings(object):
    """Data feed ingestion settings.

    :param ~datetime.datetime ingestion_begin_time: Ingestion start time.
    :keyword int data_source_request_concurrency: The max concurrency of data ingestion queries against
        user data source. Zero (0) means no limitation.
    :keyword int ingestion_retry_delay: The min retry interval for failed data ingestion tasks, in seconds.
    :keyword int ingestion_start_offset: The time that the beginning of data ingestion task will delay
        for every data slice according to this offset, in seconds.
    :keyword int stop_retry_after: Stop retry data ingestion after the data slice first
        schedule time in seconds.
    """

    def __init__(self, ingestion_begin_time, **kwargs):
        # type: (datetime.datetime, Any) -> None
        self.ingestion_begin_time = ingestion_begin_time
        self.ingestion_start_offset = kwargs.get("ingestion_start_offset", 0)
        self.data_source_request_concurrency = kwargs.get(
            "data_source_request_concurrency", -1
        )
        self.ingestion_retry_delay = kwargs.get("ingestion_retry_delay", -1)
        self.stop_retry_after = kwargs.get("stop_retry_after", -1)

    def __repr__(self):
        return (
            "DataFeedIngestionSettings(ingestion_begin_time={}, ingestion_start_offset={}, "
            "data_source_request_concurrency={}, ingestion_retry_delay={}, stop_retry_after={})".format(
                self.ingestion_begin_time,
                self.ingestion_start_offset,
                self.data_source_request_concurrency,
                self.ingestion_retry_delay,
                self.stop_retry_after,
            )[
                :1024
            ]
        )


class DataFeedMissingDataPointFillSettings(object):
    """Data feed missing data point fill settings

    :keyword fill_type: The type of fill missing point for anomaly detection. Possible
        values include: "SmartFilling", "PreviousValue", "CustomValue", "NoFilling". Default value:
        "SmartFilling".
    :paramtype fill_type: str or ~azure.ai.metricsadvisor.models.DatasourceMissingDataPointFillType
    :keyword float custom_fill_value: The value of fill missing point for anomaly detection
        if "CustomValue" fill type is specified.
    """

    def __init__(self, **kwargs):
        self.fill_type = kwargs.get("fill_type", "SmartFilling")
        self.custom_fill_value = kwargs.get("custom_fill_value", None)

    def __repr__(self):
        return "DataFeedMissingDataPointFillSettings(fill_type={}, custom_fill_value={})".format(
            self.fill_type,
            self.custom_fill_value,
        )[
            :1024
        ]


class DataFeedRollupSettings(object):
    """Data feed rollup settings

    :keyword str rollup_identification_value: The identification value for the row of calculated all-up value.
    :keyword rollup_type: Mark if the data feed needs rollup. Possible values include: "NoRollup",
        "AutoRollup", "AlreadyRollup". Default value: "AutoRollup".
    :paramtype rollup_type: str or ~azure.ai.metricsadvisor.models.DataFeedRollupType
    :keyword list[str] auto_rollup_group_by_column_names: Roll up columns.
    :keyword rollup_method: Roll up method. Possible values include: "None", "Sum", "Max", "Min",
        "Avg", "Count".
    :paramtype rollup_method: str or ~azure.ai.metricsadvisor.models.DataFeedAutoRollupMethod
    """

    def __init__(self, **kwargs):
        self.rollup_identification_value = kwargs.get(
            "rollup_identification_value", None
        )
        self.rollup_type = kwargs.get("rollup_type", "AutoRollup")
        self.auto_rollup_group_by_column_names = kwargs.get(
            "auto_rollup_group_by_column_names", None
        )
        self.rollup_method = kwargs.get("rollup_method", None)

    def __repr__(self):
        return (
            "DataFeedRollupSettings(rollup_identification_value={}, rollup_type={}, "
            "auto_rollup_group_by_column_names={}, rollup_method={})".format(
                self.rollup_identification_value,
                self.rollup_type,
                self.auto_rollup_group_by_column_names,
                self.rollup_method,
            )[:1024]
        )


class DataFeedSchema(object):
    """Data feed schema

    :param metrics: List of metrics.
    :type metrics: list[~azure.ai.metricsadvisor.models.DataFeedMetric]
    :keyword dimensions: List of dimension.
    :paramtype dimensions: list[~azure.ai.metricsadvisor.models.DataFeedDimension]
    :keyword str timestamp_column: User-defined timestamp column.
        If timestamp_column is None, start time of every time slice will be used as default value.
    """

    def __init__(self, metrics, **kwargs):
        # type: (List[DataFeedMetric], Any) -> None
        self.metrics = metrics
        self.dimensions = kwargs.get("dimensions", None)
        self.timestamp_column = kwargs.get("timestamp_column", None)

    def __repr__(self):
        return "DataFeedSchema(metrics={}, dimensions={}, timestamp_column={})".format(
            repr(self.metrics),
            repr(self.dimensions),
            self.timestamp_column,
        )[:1024]


class DataFeed(object):  # pylint:disable=too-many-instance-attributes
    """Represents a data feed.

    :ivar ~datetime.datetime created_time: Data feed created time.
    :ivar granularity: Granularity of the time series.
    :vartype granularity: ~azure.ai.metricsadvisor.models.DataFeedGranularity
    :ivar str id: Data feed unique id.
    :ivar ingestion_settings: Data feed ingestion settings.
    :vartype ingestion_settings: ~azure.ai.metricsadvisor.models.DataFeedIngestionSettings
    :ivar bool is_admin: Whether the query user is one of data feed administrators or not.
    :ivar dict metric_ids: metric name and metric id dict
    :ivar str name: Data feed name.
    :ivar schema: Data feed schema
    :vartype schema: ~azure.ai.metricsadvisor.models.DataFeedSchema
    :ivar source: Data feed source.
    :vartype source: Union[AzureApplicationInsightsDataFeedSource, AzureBlobDataFeedSource, AzureCosmosDbDataFeedSource,
        AzureDataExplorerDataFeedSource, AzureDataLakeStorageGen2DataFeedSource, AzureTableDataFeedSource,
        AzureEventHubsDataFeedSource, InfluxDbDataFeedSource, MySqlDataFeedSource, PostgreSqlDataFeedSource,
        SqlServerDataFeedSource, MongoDbDataFeedSource, AzureLogAnalyticsDataFeedSource]
    :ivar status: Data feed status. Possible values include: "Active", "Paused".
        Default value: "Active".
    :vartype status: str or ~azure.ai.metricsadvisor.models.DataFeedStatus
    :ivar list[str] admins: Data feed administrators.
    :ivar str data_feed_description: Data feed description.
    :ivar missing_data_point_fill_settings: The fill missing point type and value.
    :vartype missing_data_point_fill_settings:
        ~azure.ai.metricsadvisor.models.DataFeedMissingDataPointFillSettings
    :ivar rollup_settings: The rollup settings.
    :vartype rollup_settings:
        ~azure.ai.metricsadvisor.models.DataFeedRollupSettings
    :ivar list[str] viewers: Data feed viewers.
    :ivar access_mode: Data feed access mode. Possible values include:
        "Private", "Public". Default value: "Private".
    :vartype access_mode: str or ~azure.ai.metricsadvisor.models.DataFeedAccessMode
    :ivar str action_link_template: action link for alert.
    """

    def __init__(
        self,
        name,  # type: str
        source,  # type: DataFeedSourceUnion
        granularity,  # type: DataFeedGranularity
        schema,  # type: DataFeedSchema
        ingestion_settings,  # type: DataFeedIngestionSettings
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        self.name = name
        self.granularity = granularity
        self.ingestion_settings = ingestion_settings
        self.schema = schema
        self.source = source
        self.id = kwargs.get("id", None)
        self.created_time = kwargs.get("created_time", None)
        self.is_admin = kwargs.get("is_admin", None)
        self.metric_ids = kwargs.get("metric_ids", None)
        self.status = kwargs.get("status", None)
        self.admins = kwargs.get("admins", None)
        self.data_feed_description = kwargs.get("data_feed_description", None)
        self.missing_data_point_fill_settings = kwargs.get(
            "missing_data_point_fill_settings", None
        )
        self.rollup_settings = kwargs.get("rollup_settings", None)
        self.viewers = kwargs.get("viewers", None)
        self.access_mode = kwargs.get("access_mode", "Private")
        self.action_link_template = kwargs.get("action_link_template", None)

    def __repr__(self):
        return (
            "DataFeed(created_time={}, granularity={}, id={}, ingestion_settings={}, is_admin={}, "
            "metric_ids={}, name={}, schema={}, source={}, status={}, admins={}, "
            "data_feed_description={}, missing_data_point_fill_settings={}, "
            "rollup_settings={}, viewers={}, access_mode={}, action_link_template={})".format(
                self.created_time,
                repr(self.granularity),
                self.id,
                repr(self.ingestion_settings),
                self.is_admin,
                self.metric_ids,
                self.name,
                repr(self.schema),
                repr(self.source),
                self.status,
                self.admins,
                self.data_feed_description,
                repr(self.missing_data_point_fill_settings),
                repr(self.rollup_settings),
                self.viewers,
                self.access_mode,
                self.action_link_template,
            )[
                :1024
            ]
        )

    @classmethod
    def _from_generated(cls, data_feed):
        return cls(
            created_time=data_feed.created_time,
            granularity=DataFeedGranularity._from_generated(
                data_feed.granularity_name, data_feed.granularity_amount
            ),
            id=data_feed.data_feed_id,
            ingestion_settings=DataFeedIngestionSettings(
                ingestion_begin_time=data_feed.data_start_from,
                data_source_request_concurrency=data_feed.max_concurrency,
                ingestion_retry_delay=data_feed.min_retry_interval_in_seconds,
                ingestion_start_offset=data_feed.start_offset_in_seconds,
                stop_retry_after=data_feed.stop_retry_after_in_seconds,
            ),
            is_admin=data_feed.is_admin,
            metric_ids={
                metric.metric_name: metric.metric_id for metric in data_feed.metrics
            },
            name=data_feed.data_feed_name,
            admins=data_feed.admins,
            data_feed_description=data_feed.data_feed_description,
            missing_data_point_fill_settings=DataFeedMissingDataPointFillSettings(
                fill_type=data_feed.fill_missing_point_type,
                custom_fill_value=data_feed.fill_missing_point_value,
            ),
            rollup_settings=DataFeedRollupSettings(
                rollup_identification_value=data_feed.all_up_identification,
                rollup_type=DataFeedRollupType._from_generated(data_feed.need_rollup),
                auto_rollup_group_by_column_names=data_feed.roll_up_columns,
                rollup_method=data_feed.roll_up_method,
            ),
            viewers=data_feed.viewers,
            access_mode=data_feed.view_mode,
            action_link_template=data_feed.action_link_template,
            schema=DataFeedSchema(
                dimensions=[
                    DataFeedDimension._from_generated(dim)
                    for dim in data_feed.dimension
                ],
                metrics=[
                    DataFeedMetric._from_generated(metric)
                    for metric in data_feed.metrics
                ],
                timestamp_column=data_feed.timestamp_column,
            ),
            source=DATA_FEED_TRANSFORM[data_feed.data_source_type]._from_generated(
                data_feed.data_source_parameter
            ),
            status=data_feed.status,
        )

    def _to_generated_patch(self, data_source_feed_type, kwargs):
        source_param = kwargs.pop("dataSourceParameter", None)
        authentication_type = None
        credential_id = None
        if source_param:
            authentication_type = source_param.authentication_type
            credential_id = source_param.credential_id
            source_param = source_param._to_generated_patch()

        rollup_type = kwargs.pop("needRollup", None)
        if rollup_type:
            DataFeedRollupType._to_generated(rollup_type)
        return data_source_feed_type(
            data_feed_name=kwargs.pop("dataFeedName", None) or self.name,
            data_source_parameter=source_param
            if source_param
            else self.source._to_generated_patch(),
            timestamp_column=kwargs.pop("timestampColumn", None)
            or self.schema.timestamp_column,
            data_start_from=kwargs.pop("dataStartFrom", None)
            or self.ingestion_settings.ingestion_begin_time,
            max_concurrency=kwargs.pop("maxConcurrency", None)
            or self.ingestion_settings.data_source_request_concurrency,
            min_retry_interval_in_seconds=kwargs.pop("minRetryIntervalInSeconds", None)
            or self.ingestion_settings.ingestion_retry_delay,
            start_offset_in_seconds=kwargs.pop("startOffsetInSeconds", None)
            or self.ingestion_settings.ingestion_start_offset,
            stop_retry_after_in_seconds=kwargs.pop("stopRetryAfterInSeconds", None)
            or self.ingestion_settings.stop_retry_after,
            data_feed_description=kwargs.pop("dataFeedDescription", None)
            or self.data_feed_description,
            need_rollup=rollup_type
            or DataFeedRollupType._to_generated(self.rollup_settings.rollup_type)
            if self.rollup_settings
            else None,
            roll_up_method=kwargs.pop("rollUpMethod", None)
            or self.rollup_settings.rollup_method
            if self.rollup_settings
            else None,
            roll_up_columns=kwargs.pop("rollUpColumns", None)
            or self.rollup_settings.auto_rollup_group_by_column_names
            if self.rollup_settings
            else None,
            all_up_identification=kwargs.pop("allUpIdentification", None)
            or self.rollup_settings.rollup_identification_value
            if self.rollup_settings
            else None,
            fill_missing_point_type=kwargs.pop("fillMissingPointType", None)
            or self.missing_data_point_fill_settings.fill_type
            if self.missing_data_point_fill_settings
            else None,
            fill_missing_point_value=kwargs.pop("fillMissingPointValue", None)
            or self.missing_data_point_fill_settings.custom_fill_value
            if self.missing_data_point_fill_settings
            else None,
            viewers=kwargs.pop("viewers", None) or self.viewers,
            view_mode=kwargs.pop("viewMode", None) or self.access_mode,
            admins=kwargs.pop("admins", None) or self.admins,
            status=kwargs.pop("status", None) or self.status,
            action_link_template=kwargs.pop("actionLinkTemplate", None)
            or self.action_link_template,
            authentication_type=authentication_type,
            credential_id=credential_id,
        )


class MetricAnomalyAlertScope(object):
    """MetricAnomalyAlertScope

    :param scope_type: Required. Anomaly scope. Possible values include: "WholeSeries",
     "SeriesGroup", "TopN".
    :type scope_type: str or ~azure.ai.metricsadvisor.models.MetricAnomalyAlertScopeType
    :keyword series_group_in_scope: Dimension specified for series group.
    :paramtype series_group_in_scope: dict[str, str]
    :keyword top_n_group_in_scope:
    :paramtype top_n_group_in_scope: ~azure.ai.metricsadvisor.models.TopNGroupScope
    """

    def __init__(self, scope_type, **kwargs):
        # type: (Union[str, MetricAnomalyAlertScopeType], Any) -> None
        self.scope_type = scope_type
        self.series_group_in_scope = kwargs.get("series_group_in_scope", None)
        self.top_n_group_in_scope = kwargs.get("top_n_group_in_scope", None)

    def __repr__(self):
        return "MetricAnomalyAlertScope(scope_type={}, series_group_in_scope={}, top_n_group_in_scope={})".format(
            self.scope_type, self.series_group_in_scope, repr(self.top_n_group_in_scope)
        )[
            :1024
        ]

    @classmethod
    def _from_generated(cls, config):
        return cls(
            scope_type=MetricAnomalyAlertScopeType._from_generated(
                config.anomaly_scope_type
            ),
            series_group_in_scope=config.dimension_anomaly_scope.dimension
            if config.dimension_anomaly_scope
            else None,
            top_n_group_in_scope=TopNGroupScope(
                top=config.top_n_anomaly_scope.top,
                period=config.top_n_anomaly_scope.period,
                min_top_count=config.top_n_anomaly_scope.min_top_count,
            )
            if config.top_n_anomaly_scope
            else None,
        )


class TopNGroupScope(object):
    """TopNGroupScope.

    :param top: Required. top N, value range : [1, +∞).
    :type top: int
    :param period: Required. point count used to look back, value range : [1, +∞).
    :type period: int
    :param min_top_count: Required. min count should be in top N, value range : [1, +∞)
        should be less than or equal to period.
    :type min_top_count: int
    """

    def __init__(
        self, top, period, min_top_count, **kwargs
    ):  # pylint: disable=unused-argument
        # type: (int, int, int, Any) -> None
        self.top = top
        self.period = period
        self.min_top_count = min_top_count

    def __repr__(self):
        return "TopNGroupScope(top={}, period={}, min_top_count={})".format(
            self.top, self.period, self.min_top_count
        )[:1024]


class SeverityCondition(object):
    """SeverityCondition.

    :param min_alert_severity: Required. min alert severity. Possible values include: "Low",
     "Medium", "High".
    :type min_alert_severity: str or ~azure.ai.metricsadvisor.models.AnomalySeverity
    :param max_alert_severity: Required. max alert severity. Possible values include: "Low",
     "Medium", "High".
    :type max_alert_severity: str or ~azure.ai.metricsadvisor.models.AnomalySeverity
    """

    def __init__(
        self, min_alert_severity, max_alert_severity, **kwargs
    ):  # pylint: disable=unused-argument
        # type: (Union[str, AnomalySeverity], Union[str, AnomalySeverity], Any) -> None
        self.min_alert_severity = min_alert_severity
        self.max_alert_severity = max_alert_severity

    def __repr__(self):
        return "SeverityCondition(min_alert_severity={}, max_alert_severity={})".format(
            self.min_alert_severity, self.max_alert_severity
        )[:1024]


class MetricAnomalyAlertSnoozeCondition(object):
    """MetricAnomalyAlertSnoozeCondition.

    :param auto_snooze: Required. snooze point count, value range : [0, +∞).
    :type auto_snooze: int
    :param snooze_scope: Required. snooze scope. Possible values include: "Metric", "Series".
    :type snooze_scope: str or ~azure.ai.metricsadvisor.models.SnoozeScope
    :param only_for_successive: Required. only snooze for successive anomalies.
    :type only_for_successive: bool
    """

    def __init__(
        self, auto_snooze, snooze_scope, only_for_successive, **kwargs
    ):  # pylint: disable=unused-argument
        # type: (int, Union[str, SnoozeScope], bool, Any) -> None
        self.auto_snooze = auto_snooze
        self.snooze_scope = snooze_scope
        self.only_for_successive = only_for_successive

    def __repr__(self):
        return "MetricAnomalyAlertSnoozeCondition(auto_snooze={}, snooze_scope={}, only_for_successive={})".format(
            self.auto_snooze, self.snooze_scope, self.only_for_successive
        )[
            :1024
        ]


class MetricAnomalyAlertConditions(object):
    """MetricAnomalyAlertConditions

    :keyword metric_boundary_condition:
    :paramtype metric_boundary_condition: ~azure.ai.metricsadvisor.models.MetricBoundaryCondition
    :keyword severity_condition:
    :paramtype severity_condition: ~azure.ai.metricsadvisor.models.SeverityCondition
    """

    def __init__(self, **kwargs):
        self.metric_boundary_condition = kwargs.get("metric_boundary_condition", None)
        self.severity_condition = kwargs.get("severity_condition", None)

    def __repr__(self):
        return "MetricAnomalyAlertConditions(metric_boundary_condition={}, severity_condition={})".format(
            repr(self.metric_boundary_condition), repr(self.severity_condition)
        )[
            :1024
        ]


class MetricBoundaryCondition(object):
    """MetricBoundaryCondition.

    :param direction: Required. value filter direction. Possible values include: "Both", "Down",
     "Up".
    :type direction: str or ~azure.ai.metricsadvisor.models.AnomalyDetectorDirection
    :keyword float lower: lower bound should be specified when direction is Both or Down.
    :keyword float upper: upper bound should be specified when direction is Both or Up.
    :keyword str companion_metric_id: the other metric unique id used for value filter.
    :keyword bool trigger_for_missing: trigger alert when the corresponding point is missing in the other
     metric should be specified only when using other metric to filter.
    """

    def __init__(self, direction, **kwargs):
        # type: (Union[str, AnomalyDetectorDirection], Any) -> None
        self.direction = direction
        self.lower = kwargs.get("lower", None)
        self.upper = kwargs.get("upper", None)
        self.companion_metric_id = kwargs.get("companion_metric_id", None)
        self.trigger_for_missing = kwargs.get("trigger_for_missing", None)

    def __repr__(self):
        return (
            "MetricBoundaryCondition(direction={}, lower={}, upper={}, companion_metric_id={}, "
            "trigger_for_missing={})".format(
                self.direction,
                self.lower,
                self.upper,
                self.companion_metric_id,
                self.trigger_for_missing,
            )[:1024]
        )


class MetricAlertConfiguration(object):
    """MetricAlertConfiguration.

    :param detection_configuration_id: Required. Anomaly detection configuration unique id.
    :type detection_configuration_id: str
    :param alert_scope: Required. Anomaly scope.
    :type alert_scope: ~azure.ai.metricsadvisor.models.MetricAnomalyAlertScope
    :keyword negation_operation: Negation operation.
    :paramtype negation_operation: bool
    :keyword alert_conditions:
    :paramtype alert_conditions: ~azure.ai.metricsadvisor.models.MetricAnomalyAlertConditions
    :keyword alert_snooze_condition:
    :paramtype alert_snooze_condition: ~azure.ai.metricsadvisor.models.MetricAnomalyAlertSnoozeCondition
    """

    def __init__(self, detection_configuration_id, alert_scope, **kwargs):
        # type: (str, MetricAnomalyAlertScope, Any) -> None
        self.detection_configuration_id = detection_configuration_id
        self.alert_scope = alert_scope
        self.negation_operation = kwargs.get("negation_operation", None)
        self.alert_conditions = kwargs.get("alert_conditions", None)
        self.alert_snooze_condition = kwargs.get("alert_snooze_condition", None)

    def __repr__(self):
        return (
            "MetricAlertConfiguration(detection_configuration_id={}, alert_scope={}, negation_operation={}, "
            "alert_conditions={}, alert_snooze_condition={})".format(
                self.detection_configuration_id,
                repr(self.alert_scope),
                self.negation_operation,
                repr(self.alert_conditions),
                repr(self.alert_snooze_condition),
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, config):
        return cls(
            detection_configuration_id=config.anomaly_detection_configuration_id,
            alert_scope=MetricAnomalyAlertScope._from_generated(config),
            negation_operation=config.negation_operation,
            alert_snooze_condition=MetricAnomalyAlertSnoozeCondition(
                auto_snooze=config.snooze_filter.auto_snooze,
                snooze_scope=config.snooze_filter.snooze_scope,
                only_for_successive=config.snooze_filter.only_for_successive,
            )
            if config.snooze_filter
            else None,
            alert_conditions=MetricAnomalyAlertConditions(
                metric_boundary_condition=MetricBoundaryCondition(
                    direction=config.value_filter.direction,
                    lower=config.value_filter.lower,
                    upper=config.value_filter.upper,
                    companion_metric_id=config.value_filter.metric_id,
                    trigger_for_missing=config.value_filter.trigger_for_missing,
                )
                if config.value_filter
                else None,
                severity_condition=SeverityCondition(
                    max_alert_severity=config.severity_filter.max_alert_severity,
                    min_alert_severity=config.severity_filter.min_alert_severity,
                )
                if config.severity_filter
                else None,
            ),
        )

    def _to_generated(self):
        return _MetricAlertingConfiguration(
            anomaly_detection_configuration_id=self.detection_configuration_id,
            anomaly_scope_type=MetricAnomalyAlertScopeType._to_generated(
                self.alert_scope.scope_type
            ),
            dimension_anomaly_scope=_DimensionGroupIdentity(
                dimension=self.alert_scope.series_group_in_scope
            )
            if self.alert_scope.series_group_in_scope
            else None,
            top_n_anomaly_scope=_TopNGroupScope(
                top=self.alert_scope.top_n_group_in_scope.top,
                period=self.alert_scope.top_n_group_in_scope.period,
                min_top_count=self.alert_scope.top_n_group_in_scope.min_top_count,
            )
            if self.alert_scope.top_n_group_in_scope
            else None,
            negation_operation=self.negation_operation,
            severity_filter=_SeverityCondition(
                max_alert_severity=self.alert_conditions.severity_condition.max_alert_severity,
                min_alert_severity=self.alert_conditions.severity_condition.min_alert_severity,
            )
            if self.alert_conditions and self.alert_conditions.severity_condition
            else None,
            snooze_filter=_AlertSnoozeCondition(
                auto_snooze=self.alert_snooze_condition.auto_snooze,
                snooze_scope=self.alert_snooze_condition.snooze_scope,
                only_for_successive=self.alert_snooze_condition.only_for_successive,
            )
            if self.alert_snooze_condition
            else None,
            value_filter=_ValueCondition(
                direction=self.alert_conditions.metric_boundary_condition.direction,
                lower=self.alert_conditions.metric_boundary_condition.lower,
                upper=self.alert_conditions.metric_boundary_condition.upper,
                metric_id=self.alert_conditions.metric_boundary_condition.companion_metric_id,
                trigger_for_missing=self.alert_conditions.metric_boundary_condition.trigger_for_missing,
            )
            if self.alert_conditions and self.alert_conditions.metric_boundary_condition
            else None,
        )


class AnomalyAlertConfiguration(object):
    """AnomalyAlertConfiguration.

    :param str name: Required. anomaly alert configuration name.
    :param list[str] hook_ids: Required. hook unique ids.
    :param metric_alert_configurations: Required. Anomaly alert configurations.
    :type metric_alert_configurations:
     list[~azure.ai.metricsadvisor.models.MetricAlertConfiguration]
    :ivar id: anomaly alert configuration unique id.
    :vartype id: str
    :ivar description: anomaly alert configuration description.
    :vartype description: str
    :ivar cross_metrics_operator: cross metrics operator
     should be specified when setting up multiple metric alert configurations. Possible values
     include: "AND", "OR", "XOR".
    :vartype cross_metrics_operator: str or
     ~azure.ai.metricsadvisor.models.MetricAnomalyAlertConfigurationsOperator
    :keyword list[str] dimensions_to_split_alert: dimensions used to split alert.

    """

    def __init__(self, name, metric_alert_configurations, hook_ids, **kwargs):
        # type: (str, List[MetricAlertConfiguration], List[str], Any) -> None
        self.name = name
        self.hook_ids = hook_ids
        self.metric_alert_configurations = metric_alert_configurations
        self.id = kwargs.get("id", None)
        self.description = kwargs.get("description", None)
        self.cross_metrics_operator = kwargs.get("cross_metrics_operator", None)
        self.dimensions_to_split_alert = kwargs.get("dimensions_to_split_alert", None)

    def __repr__(self):
        return (
            "AnomalyAlertConfiguration(id={}, name={}, description={}, cross_metrics_operator={}, hook_ids={}, "
            "metric_alert_configurations={}, dimensions_to_split_alert={})".format(
                self.id,
                self.name,
                self.description,
                self.cross_metrics_operator,
                self.hook_ids,
                repr(self.metric_alert_configurations),
                self.dimensions_to_split_alert,
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, config):
        return cls(
            id=config.anomaly_alerting_configuration_id,
            name=config.name,
            description=config.description,
            cross_metrics_operator=config.cross_metrics_operator,
            hook_ids=config.hook_ids,
            metric_alert_configurations=[
                MetricAlertConfiguration._from_generated(c)
                for c in config.metric_alerting_configurations
            ],
            dimensions_to_split_alert=config.split_alert_by_dimensions,
        )

    def _to_generated(self):
        return _AnomalyAlertingConfiguration(
            name=self.name,
            metric_alerting_configurations=[
                config._to_generated() for config in self.metric_alert_configurations
            ],
            hook_ids=self.hook_ids,
            cross_metrics_operator=self.cross_metrics_operator,
            description=self.description,
            split_alert_by_dimensions=self.dimensions_to_split_alert,
        )

    def _to_generated_patch(
        self,
        name,
        metric_alert_configurations,
        hook_ids,
        cross_metrics_operator,
        description,
    ):
        metric_alert_configurations = (
            metric_alert_configurations or self.metric_alert_configurations
        )
        return _AnomalyAlertingConfigurationPatch(
            name=name or self.name,
            metric_alerting_configurations=[
                config._to_generated() for config in metric_alert_configurations
            ]
            if metric_alert_configurations
            else None,
            hook_ids=hook_ids or self.hook_ids,
            cross_metrics_operator=cross_metrics_operator
            or self.cross_metrics_operator,
            description=description or self.description,
            split_alert_by_dimensions=self.dimensions_to_split_alert,
        )


class AnomalyDetectionConfiguration(object):
    """AnomalyDetectionConfiguration.


    :param str name: Required. anomaly detection configuration name.
    :param str metric_id: Required. metric unique id.
    :param whole_series_detection_condition: Required.
        Conditions to detect anomalies in all time series of a metric.
    :type whole_series_detection_condition: ~azure.ai.metricsadvisor.models.MetricDetectionCondition
    :ivar str description: anomaly detection configuration description.
    :ivar str id: anomaly detection configuration unique id.
    :ivar series_group_detection_conditions: detection configuration for series group.
    :vartype series_group_detection_conditions:
        list[~azure.ai.metricsadvisor.models.MetricSeriesGroupDetectionCondition]
    :ivar series_detection_conditions: detection configuration for specific series.
    :vartype series_detection_conditions:
        list[~azure.ai.metricsadvisor.models.MetricSingleSeriesDetectionCondition]
    """

    def __init__(self, name, metric_id, whole_series_detection_condition, **kwargs):
        # type: (str, str, MetricDetectionCondition, Any) -> None
        self.name = name
        self.metric_id = metric_id
        self.whole_series_detection_condition = whole_series_detection_condition
        self.id = kwargs.get("id", None)
        self.description = kwargs.get("description", None)
        self.series_group_detection_conditions = kwargs.get(
            "series_group_detection_conditions", None
        )
        self.series_detection_conditions = kwargs.get(
            "series_detection_conditions", None
        )

    def __repr__(self):
        return (
            "AnomalyDetectionConfiguration(id={}, name={}, description={}, metric_id={}, "
            "whole_series_detection_condition={}, series_group_detection_conditions={}, "
            "series_detection_conditions={})".format(
                self.id,
                self.name,
                self.description,
                self.metric_id,
                repr(self.whole_series_detection_condition),
                repr(self.series_group_detection_conditions),
                repr(self.series_detection_conditions),
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, config):
        return cls(
            id=config.anomaly_detection_configuration_id,
            name=config.name,
            description=config.description,
            metric_id=config.metric_id,
            whole_series_detection_condition=MetricDetectionCondition._from_generated(
                config.whole_metric_configuration
            ),
            series_group_detection_conditions=[
                MetricSeriesGroupDetectionCondition._from_generated(conf)
                for conf in config.dimension_group_override_configurations
            ]
            if config.dimension_group_override_configurations
            else None,
            series_detection_conditions=[
                MetricSingleSeriesDetectionCondition._from_generated(conf)
                for conf in config.series_override_configurations
            ]
            if config.series_override_configurations
            else None,
        )

    def _to_generated(self):
        return _AnomalyDetectionConfiguration(
            name=self.name,
            metric_id=self.metric_id,
            description=self.description,
            whole_metric_configuration=self.whole_series_detection_condition._to_generated(),
            dimension_group_override_configurations=[
                group._to_generated()
                for group in self.series_group_detection_conditions
            ]
            if self.series_group_detection_conditions
            else None,
            series_override_configurations=[
                series._to_generated() for series in self.series_detection_conditions
            ]
            if self.series_detection_conditions
            else None,
        )

    def _to_generated_patch(
        self,
        name,
        description,
        whole_series_detection_condition,
        series_group_detection_conditions,
        series_detection_conditions,
    ):
        whole_series_detection_condition = (
            whole_series_detection_condition or self.whole_series_detection_condition
        )
        series_group = (
            series_group_detection_conditions or self.series_group_detection_conditions
        )
        series_detection = (
            series_detection_conditions or self.series_detection_conditions
        )

        return _AnomalyDetectionConfigurationPatch(
            name=name or self.name,
            description=description or self.description,
            whole_metric_configuration=whole_series_detection_condition._to_generated_patch()
            if whole_series_detection_condition
            else None,
            dimension_group_override_configurations=[
                group._to_generated() for group in series_group
            ]
            if series_group
            else None,
            series_override_configurations=[
                series._to_generated() for series in series_detection
            ]
            if series_detection
            else None,
        )


class DataFeedSource(dict):
    """DataFeedSource base class

    :ivar data_source_type: Required. data source type.Constant filled by server.  Possible values
     include: "AzureApplicationInsights", "AzureBlob", "AzureCosmosDB", "AzureDataExplorer",
     "AzureDataLakeStorageGen2", "AzureEventHubs", "AzureLogAnalytics", "AzureTable", "InfluxDB",
     "MongoDB", "MySql", "PostgreSql", "SqlServer".
    :vartype data_source_type: str or ~azure.ai.metricsadvisor.models.DatasourceType
    :ivar authentication_type: authentication type for corresponding data source. Possible values
     include: "Basic", "ManagedIdentity", "AzureSQLConnectionString", "DataLakeGen2SharedKey",
     "ServicePrincipal", "ServicePrincipalInKV". Default is "Basic".
    :vartype authentication_type: str or ~azure.ai.metricsadvisor.models.DatasourceAuthenticationType
    :ivar str credential_id: The datasource credential id.
    """

    def __init__(self, data_source_type, **kwargs):
        # type: (str, **Any) -> None
        super(DataFeedSource, self).__init__(
            data_source_type=data_source_type, **kwargs
        )
        self.data_source_type = data_source_type
        self.authentication_type = kwargs.get("authentication_type", None)
        self.credential_id = kwargs.get("credential_id", None)


class AzureApplicationInsightsDataFeedSource(DataFeedSource):
    """AzureApplicationInsightsDataFeedSource.

    :ivar data_source_type: Required. data source type.Constant filled by server.  Possible values
     include: "AzureApplicationInsights", "AzureBlob", "AzureCosmosDB", "AzureDataExplorer",
     "AzureDataLakeStorageGen2", "AzureEventHubs", "AzureLogAnalytics", "AzureTable", "InfluxDB",
     "MongoDB", "MySql", "PostgreSql", "SqlServer".
    :vartype data_source_type: str or ~azure.ai.metricsadvisor.models.DatasourceType
    :ivar authentication_type: authentication type for corresponding data source. Possible values
     include: "Basic", "ManagedIdentity", "AzureSQLConnectionString", "DataLakeGen2SharedKey",
     "ServicePrincipal", "ServicePrincipalInKV". Default is "Basic".
    :vartype authentication_type: str or ~azure.ai.metricsadvisor.models.DatasourceAuthenticationType
    :keyword str credential_id: The datasource credential id.
    :param str query: Required. Query.
    :keyword str azure_cloud: Azure cloud environment.
    :keyword str application_id: Azure Application Insights ID.
    :keyword str api_key: API Key.
    """

    def __init__(self, query, **kwargs):
        # type: (str, **Any) -> None
        super(AzureApplicationInsightsDataFeedSource, self).__init__(
            data_source_type="AzureApplicationInsights",
            authentication_type="Basic",
            **kwargs
        )
        self.azure_cloud = kwargs.get("azure_cloud", None)
        self.application_id = kwargs.get("application_id", None)
        self.api_key = kwargs.get("api_key", None)
        self.query = query

    def __repr__(self):
        return (
            "AzureApplicationInsightsDataFeedSource(data_source_type={}, azure_cloud={}, application_id={}, "
            "api_key={}, query={}, authentication_type={}, credential_id={})".format(
                self.data_source_type,
                self.azure_cloud,
                self.application_id,
                self.api_key,
                self.query,
                self.authentication_type,
                self.credential_id,
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, source):
        return cls(
            azure_cloud=source.azure_cloud,
            application_id=source.application_id,
            api_key=source.api_key,
            query=source.query,
        )

    def _to_generated(self):
        return _AzureApplicationInsightsParameter(
            azure_cloud=self.azure_cloud,
            application_id=self.application_id,
            api_key=self.api_key,
            query=self.query,
        )

    def _to_generated_patch(self):
        return _AzureApplicationInsightsParameterPatch(
            azure_cloud=self.azure_cloud,
            application_id=self.application_id,
            api_key=self.api_key,
            query=self.query,
        )


class AzureBlobDataFeedSource(DataFeedSource):
    """AzureBlobDataFeedSource.

    :ivar data_source_type: Required. data source type.Constant filled by server.  Possible values
     include: "AzureApplicationInsights", "AzureBlob", "AzureCosmosDB", "AzureDataExplorer",
     "AzureDataLakeStorageGen2", "AzureEventHubs", "AzureLogAnalytics", "AzureTable", "InfluxDB",
     "MongoDB", "MySql", "PostgreSql", "SqlServer".
    :vartype data_source_type: str or ~azure.ai.metricsadvisor.models.DatasourceType
    :ivar authentication_type: authentication type for corresponding data source. Possible values
     include: "Basic", "ManagedIdentity", "AzureSQLConnectionString", "DataLakeGen2SharedKey",
     "ServicePrincipal", "ServicePrincipalInKV". Default is "Basic".
    :vartype authentication_type: str or ~azure.ai.metricsadvisor.models.DatasourceAuthenticationType
    :keyword str credential_id: The datasource credential id.
    :param container: Required. Container.
    :type container: str
    :param blob_template: Required. Blob Template.
    :type blob_template: str
    :keyword str connection_string: Azure Blob connection string.
    :keyword bool msi: If using managed identity authentication.
    """

    def __init__(self, container, blob_template, **kwargs):
        # type: (str, str, **Any) -> None
        super(AzureBlobDataFeedSource, self).__init__(
            data_source_type="AzureBlob", **kwargs
        )
        msi = kwargs.get("msi", False)
        if msi:
            self.authentication_type = "ManagedIdentity"
        else:
            self.authentication_type = "Basic"
            self.connection_string = kwargs.get("connection_string", None)
        self.container = container
        self.blob_template = blob_template

    def __repr__(self):
        return (
            "AzureBlobDataFeedSource(data_source_type={}, connection_string={}, container={}, "
            "blob_template={}, authentication_type={}, credential_id={})".format(
                self.data_source_type,
                self.connection_string,
                self.container,
                self.blob_template,
                self.authentication_type,
                self.credential_id,
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, source):
        return cls(
            connection_string=source.connection_string,
            container=source.container,
            blob_template=source.blob_template,
        )

    def _to_generated(self):
        return _AzureBlobParameter(
            connection_string=self.connection_string,
            container=self.container,
            blob_template=self.blob_template,
        )

    def _to_generated_patch(self):
        return _AzureBlobParameterPatch(
            connection_string=self.connection_string,
            container=self.container,
            blob_template=self.blob_template,
        )


class AzureCosmosDbDataFeedSource(DataFeedSource):
    """AzureCosmosDbDataFeedSource.

    :ivar data_source_type: Required. data source type.Constant filled by server.  Possible values
     include: "AzureApplicationInsights", "AzureBlob", "AzureCosmosDB", "AzureDataExplorer",
     "AzureDataLakeStorageGen2", "AzureEventHubs", "AzureLogAnalytics", "AzureTable", "InfluxDB",
     "MongoDB", "MySql", "PostgreSql", "SqlServer".
    :vartype data_source_type: str or ~azure.ai.metricsadvisor.models.DatasourceType
    :ivar authentication_type: authentication type for corresponding data source. Possible values
     include: "Basic", "ManagedIdentity", "AzureSQLConnectionString", "DataLakeGen2SharedKey",
     "ServicePrincipal", "ServicePrincipalInKV". Default is "Basic".
    :vartype authentication_type: str or ~azure.ai.metricsadvisor.models.DatasourceAuthenticationType
    :keyword str credential_id: The datasource credential id.
    :param sql_query: Required. Query script.
    :type sql_query: str
    :param database: Required. Database name.
    :type database: str
    :param collection_id: Required. Collection id.
    :type collection_id: str
    :keyword str connection_string: Azure CosmosDB connection string.
    """

    def __init__(self, sql_query, database, collection_id, **kwargs):
        # type: (str, str, str, **Any) -> None
        super(AzureCosmosDbDataFeedSource, self).__init__(
            data_source_type="AzureCosmosDB", authentication_type="Basic", **kwargs
        )
        self.connection_string = kwargs.get("connection_string", None)
        self.sql_query = sql_query
        self.database = database
        self.collection_id = collection_id

    def __repr__(self):
        return (
            "AzureCosmosDbDataFeedSource(data_source_type={}, connection_string={}, sql_query={}, database={}, "
            "collection_id={}, authentication_type={}, credential_id={})".format(
                self.data_source_type,
                self.connection_string,
                self.sql_query,
                self.database,
                self.collection_id,
                self.authentication_type,
                self.credential_id,
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, source):
        return cls(
            connection_string=source.connection_string,
            sql_query=source.sql_query,
            database=source.database,
            collection_id=source.collection_id,
        )

    def _to_generated(self):
        return _AzureCosmosDBParameter(
            connection_string=self.connection_string,
            sql_query=self.sql_query,
            database=self.database,
            collection_id=self.collection_id,
        )

    def _to_generated_patch(self):
        return _AzureCosmosDBParameterPatch(
            connection_string=self.connection_string,
            sql_query=self.sql_query,
            database=self.database,
            collection_id=self.collection_id,
        )


class AzureDataExplorerDataFeedSource(DataFeedSource):
    """AzureDataExplorerDataFeedSource.

    :ivar data_source_type: Required. data source type.Constant filled by server.  Possible values
     include: "AzureApplicationInsights", "AzureBlob", "AzureCosmosDB", "AzureDataExplorer",
     "AzureDataLakeStorageGen2", "AzureEventHubs", "AzureLogAnalytics", "AzureTable", "InfluxDB",
     "MongoDB", "MySql", "PostgreSql", "SqlServer".
    :vartype data_source_type: str or ~azure.ai.metricsadvisor.models.DatasourceType
    :ivar authentication_type: authentication type for corresponding data source. Possible values
     include: "Basic", "ManagedIdentity", "AzureSQLConnectionString", "DataLakeGen2SharedKey",
     "ServicePrincipal", "ServicePrincipalInKV". Default is "Basic".
    :vartype authentication_type: str or ~azure.ai.metricsadvisor.models.DatasourceAuthenticationType
    :keyword str credential_id: The datasource credential id.
    :param query: Required. Query script.
    :type query: str
    :keyword str connection_string: Database connection string.
    :keyword bool msi: If using managed identity authentication.
    :keyword str datasource_service_principal_id: Datasource service principal unique id.
    :keyword str datasource_service_principal_in_kv_id: Datasource service principal in key vault unique id.
    """

    def __init__(self, query, **kwargs):
        # type: (str, **Any) -> None
        super(AzureDataExplorerDataFeedSource, self).__init__(
            data_source_type="AzureDataExplorer", **kwargs
        )
        msi = kwargs.get("msi", False)
        datasource_service_principal_id = kwargs.get(
            "datasource_service_principal_id", False
        )
        datasource_service_principal_in_kv_id = kwargs.get(
            "datasource_service_principal_in_kv_id", False
        )
        if msi:
            self.authentication_type = "ManagedIdentity"
        elif datasource_service_principal_id:
            self.authentication_type = "ServicePrincipal"
            self.credential_id = datasource_service_principal_id
        elif datasource_service_principal_in_kv_id:
            self.authentication_type = "ServicePrincipalInKV"
            self.credential_id = datasource_service_principal_in_kv_id
        else:
            self.authentication_type = "Basic"
        self.connection_string = kwargs.get("connection_string", None)
        self.query = query

    def __repr__(self):
        return (
            "AzureDataExplorerDataFeedSource(data_source_type={}, connection_string={}, query={}, "
            "authentication_type={}, credential_id={})".format(
                self.data_source_type,
                self.connection_string,
                self.query,
                self.authentication_type,
                self.credential_id,
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, source):
        return cls(
            connection_string=source.connection_string,
            query=source.query,
        )

    def _to_generated(self):
        return _SQLSourceParameter(
            connection_string=self.connection_string,
            query=self.query,
        )

    def _to_generated_patch(self):
        return _SQLSourceParameterPatch(
            connection_string=self.connection_string,
            query=self.query,
        )


class AzureTableDataFeedSource(DataFeedSource):
    """AzureTableDataFeedSource.

    :ivar data_source_type: Required. data source type.Constant filled by server.  Possible values
     include: "AzureApplicationInsights", "AzureBlob", "AzureCosmosDB", "AzureDataExplorer",
     "AzureDataLakeStorageGen2", "AzureEventHubs", "AzureLogAnalytics", "AzureTable", "InfluxDB",
     "MongoDB", "MySql", "PostgreSql", "SqlServer".
    :vartype data_source_type: str or ~azure.ai.metricsadvisor.models.DatasourceType
    :ivar authentication_type: authentication type for corresponding data source. Possible values
     include: "Basic", "ManagedIdentity", "AzureSQLConnectionString", "DataLakeGen2SharedKey",
     "ServicePrincipal", "ServicePrincipalInKV". Default is "Basic".
    :vartype authentication_type: str or ~azure.ai.metricsadvisor.models.DatasourceAuthenticationType
    :keyword str credential_id: The datasource credential id.
    :param str query: Required. Query script.
    :param str table: Required. Table name.
    :keyword str connection_string: Azure Table connection string.
    """

    def __init__(self, query, table, **kwargs):
        # type: (str, str, **Any) -> None
        super(AzureTableDataFeedSource, self).__init__(
            data_source_type="AzureTable", authentication_type="Basic", **kwargs
        )
        self.connection_string = kwargs.get("connection_string", None)
        self.query = query
        self.table = table

    def __repr__(self):
        return (
            "AzureTableDataFeedSource(data_source_type={}, connection_string={}, query={}, table={}, "
            "authentication_type={}, credential_id={})".format(
                self.data_source_type,
                self.connection_string,
                self.query,
                self.table,
                self.authentication_type,
                self.credential_id,
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, source):
        return cls(
            connection_string=source.connection_string,
            query=source.query,
            table=source.table,
        )

    def _to_generated(self):
        return _AzureTableParameter(
            connection_string=self.connection_string, query=self.query, table=self.table
        )

    def _to_generated_patch(self):
        return _AzureTableParameterPatch(
            connection_string=self.connection_string, query=self.query, table=self.table
        )


class AzureEventHubsDataFeedSource(DataFeedSource):
    """AzureEventHubsDataFeedSource.

    :ivar data_source_type: Required. data source type.Constant filled by server.  Possible values
     include: "AzureApplicationInsights", "AzureBlob", "AzureCosmosDB", "AzureDataExplorer",
     "AzureDataLakeStorageGen2", "AzureEventHubs", "AzureLogAnalytics", "AzureTable", "InfluxDB",
     "MongoDB", "MySql", "PostgreSql", "SqlServer".
    :vartype data_source_type: str or ~azure.ai.metricsadvisor.models.DatasourceType
    :ivar authentication_type: authentication type for corresponding data source. Possible values
     include: "Basic", "ManagedIdentity", "AzureSQLConnectionString", "DataLakeGen2SharedKey",
     "ServicePrincipal", "ServicePrincipalInKV". Default is "Basic".
    :vartype authentication_type: str or ~azure.ai.metricsadvisor.models.DatasourceAuthenticationType
    :keyword str credential_id: The datasource credential id.
    :keyword str connection_string: The connection string of this Azure Event Hubs.
    :param str consumer_group: Required. The consumer group to be used in this data feed.
    """

    def __init__(self, consumer_group, **kwargs):
        # type: (str, **Any) -> None
        super(AzureEventHubsDataFeedSource, self).__init__(
            data_source_type="AzureEventHubs", authentication_type="Basic", **kwargs
        )
        self.connection_string = kwargs.get("connection_string", None)
        self.consumer_group = consumer_group

    def __repr__(self):
        return (
            "AzureEventHubsDataFeedSource(data_source_type={}, connection_string={}, consumer_group={}, "
            "authentication_type={}, credential_id={})".format(
                self.data_source_type,
                self.connection_string,
                self.consumer_group,
                self.authentication_type,
                self.credential_id,
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, source):
        return cls(
            connection_string=source.connection_string,
            consumer_group=source.consumer_group,
        )

    def _to_generated(self):
        return _AzureEventHubsParameter(
            connection_string=self.connection_string,
            consumer_group=self.consumer_group,
        )

    def _to_generated_patch(self):
        return _AzureEventHubsParameterPatch(
            connection_string=self.connection_string,
            consumer_group=self.consumer_group,
        )


class InfluxDbDataFeedSource(DataFeedSource):
    """InfluxDbDataFeedSource.

    :ivar data_source_type: Required. data source type.Constant filled by server.  Possible values
     include: "AzureApplicationInsights", "AzureBlob", "AzureCosmosDB", "AzureDataExplorer",
     "AzureDataLakeStorageGen2", "AzureEventHubs", "AzureLogAnalytics", "AzureTable", "InfluxDB",
     "MongoDB", "MySql", "PostgreSql", "SqlServer".
    :vartype data_source_type: str or ~azure.ai.metricsadvisor.models.DatasourceType
    :ivar authentication_type: authentication type for corresponding data source. Possible values
     include: "Basic", "ManagedIdentity", "AzureSQLConnectionString", "DataLakeGen2SharedKey",
     "ServicePrincipal", "ServicePrincipalInKV". Default is "Basic".
    :vartype authentication_type: str or ~azure.ai.metricsadvisor.models.DatasourceAuthenticationType
    :keyword str credential_id: The datasource credential id.
    :keyword str connection_string: InfluxDB connection string.
    :keyword str database: Database name.
    :keyword str user_name: Database access user.
    :keyword str password: Required. Database access password.
    :param str query: Required. Query script.
    """

    def __init__(self, query, **kwargs):
        # type: (str, **Any) -> None
        super(InfluxDbDataFeedSource, self).__init__(
            data_source_type="InfluxDB", authentication_type="Basic", **kwargs
        )
        self.connection_string = kwargs.get("connection_string", None)
        self.database = kwargs.get("database", None)
        self.user_name = kwargs.get("user_name", None)
        self.password = kwargs.get("password", None)
        self.query = query

    def __repr__(self):
        return (
            "InfluxDbDataFeedSource(data_source_type={}, connection_string={}, database={}, user_name={}, "
            "password={}, query={}, authentication_type={}, credential_id={})".format(
                self.data_source_type,
                self.connection_string,
                self.database,
                self.user_name,
                self.password,
                self.query,
                self.authentication_type,
                self.credential_id,
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, source):
        return cls(
            connection_string=source.connection_string,
            database=source.database,
            user_name=source.user_name,
            password=source.password,
            query=source.query,
        )

    def _to_generated(self):
        return _InfluxDBParameter(
            connection_string=self.connection_string,
            database=self.database,
            user_name=self.user_name,
            password=self.password,
            query=self.query,
        )

    def _to_generated_patch(self):
        return _InfluxDBParameterPatch(
            connection_string=self.connection_string,
            database=self.database,
            user_name=self.user_name,
            password=self.password,
            query=self.query,
        )


class MySqlDataFeedSource(DataFeedSource):
    """MySqlDataFeedSource.

    :ivar data_source_type: Required. data source type.Constant filled by server.  Possible values
     include: "AzureApplicationInsights", "AzureBlob", "AzureCosmosDB", "AzureDataExplorer",
     "AzureDataLakeStorageGen2", "AzureEventHubs", "AzureLogAnalytics", "AzureTable", "InfluxDB",
     "MongoDB", "MySql", "PostgreSql", "SqlServer".
    :vartype data_source_type: str or ~azure.ai.metricsadvisor.models.DatasourceType
    :ivar authentication_type: authentication type for corresponding data source. Possible values
     include: "Basic", "ManagedIdentity", "AzureSQLConnectionString", "DataLakeGen2SharedKey",
     "ServicePrincipal", "ServicePrincipalInKV". Default is "Basic".
    :vartype authentication_type: str or ~azure.ai.metricsadvisor.models.DatasourceAuthenticationType
    :keyword str credential_id: The datasource credential id.
    :keyword str connection_string: Database connection string.
    :param str query: Required. Query script.
    """

    def __init__(self, query, **kwargs):
        # type: (str, **Any) -> None
        super(MySqlDataFeedSource, self).__init__(
            data_source_type="MySql", authentication_type="Basic", **kwargs
        )
        self.connection_string = kwargs.get("connection_string", None)
        self.query = query

    def __repr__(self):
        return (
            "MySqlDataFeedSource(data_source_type={}, connection_string={}, query={}, "
            "authentication_type={}, credential_id={})".format(
                self.data_source_type,
                self.connection_string,
                self.query,
                self.authentication_type,
                self.credential_id,
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, source):
        return cls(
            connection_string=source.connection_string,
            query=source.query,
        )

    def _to_generated(self):
        return _SQLSourceParameter(
            connection_string=self.connection_string, query=self.query
        )

    def _to_generated_patch(self):
        return _SQLSourceParameterPatch(
            connection_string=self.connection_string, query=self.query
        )


class PostgreSqlDataFeedSource(DataFeedSource):
    """PostgreSqlDataFeedSource.

    :ivar data_source_type: Required. data source type.Constant filled by server.  Possible values
     include: "AzureApplicationInsights", "AzureBlob", "AzureCosmosDB", "AzureDataExplorer",
     "AzureDataLakeStorageGen2", "AzureEventHubs", "AzureLogAnalytics", "AzureTable", "InfluxDB",
     "MongoDB", "MySql", "PostgreSql", "SqlServer".
    :vartype data_source_type: str or ~azure.ai.metricsadvisor.models.DatasourceType
    :ivar authentication_type: authentication type for corresponding data source. Possible values
     include: "Basic", "ManagedIdentity", "AzureSQLConnectionString", "DataLakeGen2SharedKey",
     "ServicePrincipal", "ServicePrincipalInKV". Default is "Basic".
    :vartype authentication_type: str or ~azure.ai.metricsadvisor.models.DatasourceAuthenticationType
    :keyword str credential_id: The datasource credential id.
    :keyword str connection_string: Database connection string.
    :param str query: Required. Query script.
    """

    def __init__(self, query, **kwargs):
        # type: (str, **Any) -> None
        super(PostgreSqlDataFeedSource, self).__init__(
            data_source_type="PostgreSql", authentication_type="Basic", **kwargs
        )
        self.connection_string = kwargs.get("connection_string", None)
        self.query = query

    def __repr__(self):
        return (
            "PostgreSqlDataFeedSource(data_source_type={}, connection_string={}, query={}, "
            "authentication_type={}, credential_id={})".format(
                self.data_source_type,
                self.connection_string,
                self.query,
                self.authentication_type,
                self.credential_id,
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, source):
        return cls(
            connection_string=source.connection_string,
            query=source.query,
        )

    def _to_generated(self):
        return _SQLSourceParameter(
            connection_string=self.connection_string, query=self.query
        )

    def _to_generated_patch(self):
        return _SQLSourceParameterPatch(
            connection_string=self.connection_string, query=self.query
        )


class SqlServerDataFeedSource(DataFeedSource):
    """SqlServerDataFeedSource.

    :ivar data_source_type: Required. data source type.Constant filled by server.  Possible values
     include: "AzureApplicationInsights", "AzureBlob", "AzureCosmosDB", "AzureDataExplorer",
     "AzureDataLakeStorageGen2", "AzureEventHubs", "AzureLogAnalytics", "AzureTable", "InfluxDB",
     "MongoDB", "MySql", "PostgreSql", "SqlServer".
    :vartype data_source_type: str or ~azure.ai.metricsadvisor.models.DatasourceType
    :ivar authentication_type: authentication type for corresponding data source. Possible values
     include: "Basic", "ManagedIdentity", "AzureSQLConnectionString", "DataLakeGen2SharedKey",
     "ServicePrincipal", "ServicePrincipalInKV". Default is "Basic".
    :vartype authentication_type: str or ~azure.ai.metricsadvisor.models.DatasourceAuthenticationType
    :keyword str credential_id: The datasource credential id.
    :param str query: Required. Query script.
    :keyword str connection_string: Database connection string.
    :keyword bool msi: If using managed identity authentication.
    :keyword str datasource_service_principal_id: Datasource service principal unique id.
    :keyword str datasource_service_principal_in_kv_id: Datasource service principal in key vault unique id.
    :keyword str datasource_sql_connection_string_id: Datasource sql connection string unique id.
    """

    def __init__(self, query, **kwargs):
        # type: (str, **Any) -> None
        super(SqlServerDataFeedSource, self).__init__(
            data_source_type="SqlServer", **kwargs
        )
        msi = kwargs.get("msi", False)
        datasource_service_principal_id = kwargs.get(
            "datasource_service_principal_id", False
        )
        datasource_service_principal_in_kv_id = kwargs.get(
            "datasource_service_principal_in_kv_id", False
        )
        datasource_sql_connection_string_id = kwargs.get(
            "datasource_sql_connection_string_id", False
        )
        if msi:
            self.authentication_type = "ManagedIdentity"
        elif datasource_service_principal_id:
            self.authentication_type = "ServicePrincipal"
            self.credential_id = datasource_service_principal_id
        elif datasource_service_principal_in_kv_id:
            self.authentication_type = "ServicePrincipalInKV"
            self.credential_id = datasource_service_principal_in_kv_id
        elif datasource_sql_connection_string_id:
            self.authentication_type = "AzureSQLConnectionString"
            self.credential_id = datasource_sql_connection_string_id
        else:
            self.authentication_type = "Basic"
        self.connection_string = kwargs.get("connection_string", None)
        self.query = query

    def __repr__(self):
        return (
            "SqlServerDataFeedSource(data_source_type={}, connection_string={}, query={}, "
            "authentication_type={}, credential_id={})".format(
                self.data_source_type,
                self.connection_string,
                self.query,
                self.authentication_type,
                self.credential_id,
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, source):
        return cls(
            connection_string=source.connection_string,
            query=source.query,
        )

    def _to_generated(self):
        return _SQLSourceParameter(
            connection_string=self.connection_string,
            query=self.query,
        )

    def _to_generated_patch(self):
        return _SQLSourceParameterPatch(
            connection_string=self.connection_string,
            query=self.query,
        )


class AzureDataLakeStorageGen2DataFeedSource(DataFeedSource):
    """AzureDataLakeStorageGen2DataFeedSource.

    :ivar data_source_type: Required. data source type.Constant filled by server.  Possible values
     include: "AzureApplicationInsights", "AzureBlob", "AzureCosmosDB", "AzureDataExplorer",
     "AzureDataLakeStorageGen2", "AzureEventHubs", "AzureLogAnalytics", "AzureTable", "InfluxDB",
     "MongoDB", "MySql", "PostgreSql", "SqlServer".
    :vartype data_source_type: str or ~azure.ai.metricsadvisor.models.DatasourceType
    :ivar authentication_type: authentication type for corresponding data source. Possible values
     include: "Basic", "ManagedIdentity", "AzureSQLConnectionString", "DataLakeGen2SharedKey",
     "ServicePrincipal", "ServicePrincipalInKV". Default is "Basic".
    :vartype authentication_type: str or ~azure.ai.metricsadvisor.models.DatasourceAuthenticationType
    :keyword str credential_id: The datasource credential id.
    :keyword str account_name: Account name.
    :keyword str account_key: Account key.
    :param str file_system_name: Required. File system name (Container).
    :param str directory_template: Required. Directory template.
    :param str file_template: Required. File template.
    :keyword bool msi: If using managed identity authentication.
    :keyword str datasource_service_principal_id: Datasource service principal unique id.
    :keyword str datasource_service_principal_in_kv_id: Datasource service principal in key vault unique id.
    :keyword str datasource_datalake_gen2_shared_key_id: Datasource datalake gen2 shared key unique id.
    """

    def __init__(self, file_system_name, directory_template, file_template, **kwargs):
        # type: (str, str, str, **Any) -> None
        super(AzureDataLakeStorageGen2DataFeedSource, self).__init__(
            data_source_type="AzureDataLakeStorageGen2", **kwargs
        )
        msi = kwargs.get("msi", False)
        datasource_service_principal_id = kwargs.get(
            "datasource_service_principal_id", False
        )
        datasource_service_principal_in_kv_id = kwargs.get(
            "datasource_service_principal_in_kv_id", False
        )
        datasource_datalake_gen2_shared_key_id = kwargs.get(
            "datasource_datalake_gen2_shared_key_id", False
        )
        if msi:
            self.authentication_type = "ManagedIdentity"
        elif datasource_service_principal_id:
            self.authentication_type = "ServicePrincipal"
            self.credential_id = datasource_service_principal_id
        elif datasource_service_principal_in_kv_id:
            self.authentication_type = "ServicePrincipalInKV"
            self.credential_id = datasource_service_principal_in_kv_id
        elif datasource_datalake_gen2_shared_key_id:
            self.authentication_type = "DataLakeGen2SharedKey"
            self.credential_id = datasource_datalake_gen2_shared_key_id
        else:
            self.authentication_type = "Basic"
        self.account_name = kwargs.get("account_name", None)
        self.account_key = kwargs.get("account_key", None)
        self.file_system_name = file_system_name
        self.directory_template = directory_template
        self.file_template = file_template

    def __repr__(self):
        return (
            "AzureDataLakeStorageGen2DataFeedSource(data_source_type={}, account_name={}, account_key={}, "
            "file_system_name={}, directory_template={}, file_template={}, authentication_type={},"
            " credential_id={})".format(
                self.data_source_type,
                self.account_name,
                self.account_key,
                self.file_system_name,
                self.directory_template,
                self.file_template,
                self.authentication_type,
                self.credential_id,
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, source):
        return cls(
            account_name=source.account_name,
            account_key=source.account_key,
            file_system_name=source.file_system_name,
            directory_template=source.directory_template,
            file_template=source.file_template,
        )

    def _to_generated(self):
        return _AzureDataLakeStorageGen2Parameter(
            account_name=self.account_name,
            account_key=self.account_key,
            file_system_name=self.file_system_name,
            directory_template=self.directory_template,
            file_template=self.file_template,
        )

    def _to_generated_patch(self):
        return _AzureDataLakeStorageGen2ParameterPatch(
            account_name=self.account_name,
            account_key=self.account_key,
            file_system_name=self.file_system_name,
            directory_template=self.directory_template,
            file_template=self.file_template,
        )


class AzureLogAnalyticsDataFeedSource(DataFeedSource):
    """AzureLogAnalyticsDataFeedSource.

    :ivar data_source_type: Required. data source type.Constant filled by server.  Possible values
     include: "AzureApplicationInsights", "AzureBlob", "AzureCosmosDB", "AzureDataExplorer",
     "AzureDataLakeStorageGen2", "AzureEventHubs", "AzureLogAnalytics", "AzureTable", "InfluxDB",
     "MongoDB", "MySql", "PostgreSql", "SqlServer".
    :vartype data_source_type: str or ~azure.ai.metricsadvisor.models.DatasourceType
    :ivar authentication_type: authentication type for corresponding data source. Possible values
     include: "Basic", "ManagedIdentity", "AzureSQLConnectionString", "DataLakeGen2SharedKey",
     "ServicePrincipal", "ServicePrincipalInKV". Default is "Basic".
    :vartype authentication_type: str or ~azure.ai.metricsadvisor.models.DatasourceAuthenticationType
    :keyword str credential_id: The datasource credential id.
    :keyword str tenant_id: The tenant id of service principal that have access to this Log
     Analytics.
    :keyword str client_id: The client id of service principal that have access to this Log
     Analytics.
    :keyword str client_secret: The client secret of service principal that have access to this Log Analytics.
    :keyword str datasource_service_principal_id: Datasource service principal unique id.
    :keyword str datasource_service_principal_in_kv_id: Datasource service principal in key vault unique id.
    :param str workspace_id: Required. The workspace id of this Log Analytics.
    :param str query: Required. The KQL (Kusto Query Language) query to fetch data from this Log
     Analytics.
    """

    def __init__(self, workspace_id, query, **kwargs):
        # type: (str, str, **Any) -> None
        super(AzureLogAnalyticsDataFeedSource, self).__init__(
            data_source_type="AzureLogAnalytics", **kwargs
        )
        datasource_service_principal_id = kwargs.get(
            "datasource_service_principal_id", False
        )
        datasource_service_principal_in_kv_id = kwargs.get(
            "datasource_service_principal_in_kv_id", False
        )
        if datasource_service_principal_id:
            self.authentication_type = "ServicePrincipal"
            self.credential_id = datasource_service_principal_id
        elif datasource_service_principal_in_kv_id:
            self.authentication_type = "ServicePrincipalInKV"
            self.credential_id = datasource_service_principal_in_kv_id
        else:
            self.authentication_type = "Basic"
            self.tenant_id = kwargs.get("tenant_id", None)
            self.client_id = kwargs.get("client_id", None)
            self.client_secret = kwargs.get("client_secret", None)
        self.workspace_id = workspace_id
        self.query = query

    def __repr__(self):
        return (
            "AzureLogAnalyticsDataFeedSource(data_source_type={}, tenant_id={}, client_id={}, "
            "client_secret={}, workspace_id={}, query={}, authentication_type={}, credential_id={})".format(
                self.data_source_type,
                self.tenant_id,
                self.client_id,
                self.client_secret,
                self.workspace_id,
                self.query,
                self.authentication_type,
                self.credential_id,
            )[
                :1024
            ]
        )

    @classmethod
    def _from_generated(cls, source):
        return cls(
            tenant_id=source.tenant_id,
            client_id=source.client_id,
            client_secret=source.client_secret,
            workspace_id=source.workspace_id,
            query=source.query,
        )

    def _to_generated(self):
        return _AzureLogAnalyticsParameter(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret,
            workspace_id=self.workspace_id,
            query=self.query,
        )

    def _to_generated_patch(self):
        return _AzureLogAnalyticsParameterPatch(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret,
            workspace_id=self.workspace_id,
            query=self.query,
        )


class MongoDbDataFeedSource(DataFeedSource):
    """MongoDbDataFeedSource.

    :ivar data_source_type: Required. data source type.Constant filled by server.  Possible values
     include: "AzureApplicationInsights", "AzureBlob", "AzureCosmosDB", "AzureDataExplorer",
     "AzureDataLakeStorageGen2", "AzureEventHubs", "AzureLogAnalytics", "AzureTable", "InfluxDB",
     "MongoDB", "MySql", "PostgreSql", "SqlServer".
    :vartype data_source_type: str or ~azure.ai.metricsadvisor.models.DatasourceType
    :ivar authentication_type: authentication type for corresponding data source. Possible values
     include: "Basic", "ManagedIdentity", "AzureSQLConnectionString", "DataLakeGen2SharedKey",
     "ServicePrincipal", "ServicePrincipalInKV". Default is "Basic".
    :vartype authentication_type: str or ~azure.ai.metricsadvisor.models.DatasourceAuthenticationType
    :keyword str credential_id: The datasource credential id.
    :keyword str connection_string: MongoDb connection string.
    :keyword str database: Database name.
    :param str command: Required. Query script.
    """

    def __init__(self, command, **kwargs):
        # type: (str, **Any) -> None
        super(MongoDbDataFeedSource, self).__init__(
            data_source_type="MongoDB", authentication_type="Basic", **kwargs
        )
        self.connection_string = kwargs.get("connection_string", None)
        self.database = kwargs.get("database", None)
        self.command = command

    def __repr__(self):
        return (
            "MongoDbDataFeedSource(data_source_type={}, connection_string={}, database={}, command={}, "
            "authentication_type={}, credential_id={})".format(
                self.data_source_type,
                self.connection_string,
                self.database,
                self.command,
                self.authentication_type,
                self.credential_id,
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, source):
        return cls(
            connection_string=source.connection_string,
            database=source.database,
            command=source.command,
        )

    def _to_generated(self):
        return _MongoDBParameter(
            connection_string=self.connection_string,
            database=self.database,
            command=self.command,
        )

    def _to_generated_patch(self):
        return _MongoDBParameterPatch(
            connection_string=self.connection_string,
            database=self.database,
            command=self.command,
        )


class NotificationHook(dict):
    """NotificationHook.

    :param str name: Hook unique name.
    :ivar str description: Hook description.
    :ivar str external_link: Hook external link.
    :ivar list[str] admins: Hook administrators.
    :ivar str hook_type: Constant filled by server. Possible values include:
        "Webhook", "Email".
    :ivar str id: Hook unique id.
    """

    def __init__(self, name, **kwargs):
        super(NotificationHook, self).__init__(name=name, **kwargs)
        self.id = kwargs.get("id", None)
        self.name = name
        self.description = kwargs.get("description", None)
        self.external_link = kwargs.get("external_link", None)
        self.admins = kwargs.get("admins", None)
        self.hook_type = None

    def __repr__(self):
        return (
            "NotificationHook(id={}, name={}, description={}, external_link={}, admins={}, "
            "hook_type={})".format(
                self.id,
                self.name,
                self.description,
                self.external_link,
                self.admins,
                self.hook_type,
            )[:1024]
        )


class EmailNotificationHook(NotificationHook):
    """EmailNotificationHook.

    :param str name: Hook unique name.
    :param list[str] emails_to_alert: Required. Email TO: list.
    :keyword str description: Hook description.
    :keyword str external_link: Hook external link.
    :ivar list[str] admins: Hook administrators.
    :ivar str hook_type: Constant filled by server - "Email".
    :ivar str id: Hook unique id.
    """

    def __init__(self, name, emails_to_alert, **kwargs):
        # type: (str, List[str], Any) -> None
        super(EmailNotificationHook, self).__init__(name, **kwargs)
        self.hook_type = "Email"  # type: str
        self.emails_to_alert = emails_to_alert

    def __repr__(self):
        return (
            "EmailNotificationHook(id={}, name={}, description={}, external_link={}, admins={}, hook_type={}, "
            "emails_to_alert={})".format(
                self.id,
                self.name,
                self.description,
                self.external_link,
                self.admins,
                self.hook_type,
                self.emails_to_alert,
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, hook):
        return cls(
            emails_to_alert=hook.hook_parameter.to_list,
            name=hook.hook_name,
            description=hook.description,
            external_link=hook.external_link,
            admins=hook.admins,
            id=hook.hook_id,
        )

    def _to_generated(self):
        return _EmailHookInfo(
            hook_name=self.name,
            description=self.description,
            external_link=self.external_link,
            admins=self.admins,
            hook_parameter=_EmailHookParameterPatch(to_list=self.emails_to_alert),
        )

    def _to_generated_patch(self, name, description, external_link, emails_to_alert):
        return _EmailHookInfoPatch(
            hook_name=name or self.name,
            description=description or self.description,
            external_link=external_link or self.external_link,
            admins=self.admins,
            hook_parameter=_EmailHookParameterPatch(
                to_list=emails_to_alert or self.emails_to_alert
            ),
        )


class WebNotificationHook(NotificationHook):
    """WebNotificationHook.

    :param str name: Hook unique name.
    :param str endpoint: Required. API address, will be called when alert is triggered, only support
        POST method via SSL.
    :keyword str username: basic authentication.
    :keyword str password: basic authentication.
    :keyword str certificate_key: client certificate.
    :keyword str certificate_password: client certificate password.
    :keyword str description: Hook description.
    :keyword str external_link: Hook external link.
    :ivar list[str] admins: Hook administrators.
    :ivar str hook_type: Constant filled by server - "Webhook".
    :ivar str id: Hook unique id.
    """

    def __init__(self, name, endpoint, **kwargs):
        # type: (str, str, Any) -> None
        super(WebNotificationHook, self).__init__(name, **kwargs)
        self.hook_type = "Webhook"  # type: str
        self.endpoint = endpoint
        self.username = kwargs.get("username", None)
        self.password = kwargs.get("password", None)
        self.certificate_key = kwargs.get("certificate_key", None)
        self.certificate_password = kwargs.get("certificate_password", None)

    def __repr__(self):
        return (
            "WebNotificationHook(id={}, name={}, description={}, external_link={}, admins={}, hook_type={}, "
            "endpoint={}, username={}, password={}, certificate_key={}, certificate_password={})".format(
                self.id,
                self.name,
                self.description,
                self.external_link,
                self.admins,
                self.hook_type,
                self.endpoint,
                self.username,
                self.password,
                self.certificate_key,
                self.certificate_password,
            )[
                :1024
            ]
        )

    @classmethod
    def _from_generated(cls, hook):
        return cls(
            endpoint=hook.hook_parameter.endpoint,
            username=hook.hook_parameter.username,
            password=hook.hook_parameter.password,
            certificate_key=hook.hook_parameter.certificate_key,
            certificate_password=hook.hook_parameter.certificate_password,
            name=hook.hook_name,
            description=hook.description,
            external_link=hook.external_link,
            admins=hook.admins,
            id=hook.hook_id,
        )

    def _to_generated(self):
        return _WebhookHookInfo(
            hook_name=self.name,
            description=self.description,
            external_link=self.external_link,
            admins=self.admins,
            hook_parameter=_WebhookHookParameterPatch(
                endpoint=self.endpoint,
                username=self.username,
                password=self.password,
                certificate_key=self.certificate_key,
                certificate_password=self.certificate_password,
            ),
        )

    def _to_generated_patch(
        self,
        name,
        description,
        external_link,
        endpoint,
        password,
        username,
        certificate_key,
        certificate_password,
    ):
        return _WebhookHookInfoPatch(
            hook_name=name or self.name,
            description=description or self.description,
            external_link=external_link or self.external_link,
            admins=self.admins,
            hook_parameter=_WebhookHookParameterPatch(
                endpoint=endpoint or self.endpoint,
                username=username or self.username,
                password=password or self.password,
                certificate_key=certificate_key or self.certificate_key,
                certificate_password=certificate_password or self.certificate_password,
            ),
        )


class MetricDetectionCondition(object):
    """MetricDetectionCondition.

    :keyword condition_operator: condition operator
     should be specified when combining multiple detection conditions. Possible values include:
     "AND", "OR".
    :paramtype condition_operator: str or
     ~azure.ai.metricsadvisor.models.DetectionConditionOperator
    :keyword smart_detection_condition:
    :paramtype smart_detection_condition: ~azure.ai.metricsadvisor.models.SmartDetectionCondition
    :keyword hard_threshold_condition:
    :paramtype hard_threshold_condition: ~azure.ai.metricsadvisor.models.HardThresholdCondition
    :keyword change_threshold_condition:
    :paramtype change_threshold_condition: ~azure.ai.metricsadvisor.models.ChangeThresholdCondition
    """

    def __init__(self, **kwargs):
        self.condition_operator = kwargs.get("condition_operator", None)
        self.smart_detection_condition = kwargs.get("smart_detection_condition", None)
        self.hard_threshold_condition = kwargs.get("hard_threshold_condition", None)
        self.change_threshold_condition = kwargs.get("change_threshold_condition", None)

    def __repr__(self):
        return (
            "MetricDetectionCondition(condition_operator={}, smart_detection_condition={}, "
            "hard_threshold_condition={}, change_threshold_condition={})".format(
                self.condition_operator,
                repr(self.smart_detection_condition),
                repr(self.hard_threshold_condition),
                repr(self.change_threshold_condition),
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, condition):
        return cls(
            condition_operator=condition.condition_operator,
            smart_detection_condition=SmartDetectionCondition._from_generated(
                condition.smart_detection_condition
            ),
            hard_threshold_condition=HardThresholdCondition._from_generated(
                condition.hard_threshold_condition
            ),
            change_threshold_condition=ChangeThresholdCondition._from_generated(
                condition.change_threshold_condition
            ),
        )

    def _to_generated(self):
        return _WholeMetricConfiguration(
            condition_operator=self.condition_operator,
            smart_detection_condition=self.smart_detection_condition._to_generated()
            if self.smart_detection_condition
            else None,
            hard_threshold_condition=self.hard_threshold_condition._to_generated()
            if self.hard_threshold_condition
            else None,
            change_threshold_condition=self.change_threshold_condition._to_generated()
            if self.change_threshold_condition
            else None,
        )

    def _to_generated_patch(self):
        return _WholeMetricConfigurationPatch(
            condition_operator=self.condition_operator,
            smart_detection_condition=self.smart_detection_condition._to_generated_patch()
            if self.smart_detection_condition
            else None,
            hard_threshold_condition=self.hard_threshold_condition._to_generated_patch()
            if self.hard_threshold_condition
            else None,
            change_threshold_condition=self.change_threshold_condition._to_generated_patch()
            if self.change_threshold_condition
            else None,
        )


class ChangeThresholdCondition(object):
    """ChangeThresholdCondition.

    :param change_percentage: Required. change percentage, value range : [0, +∞).
    :type change_percentage: float
    :param shift_point: Required. shift point, value range : [1, +∞).
    :type shift_point: int
    :param within_range: Required. if the withinRange = true, detected data is abnormal when the
        value falls in the range, in this case anomalyDetectorDirection must be Both
        if the withinRange = false, detected data is abnormal when the value falls out of the range.
    :type within_range: bool
    :param anomaly_detector_direction: Required. detection direction. Possible values include:
        "Both", "Down", "Up".
    :type anomaly_detector_direction: str or
        ~azure.ai.metricsadvisor.models.AnomalyDetectorDirection
    :param suppress_condition: Required.
    :type suppress_condition: ~azure.ai.metricsadvisor.models.SuppressCondition
    """

    def __init__(
        self,
        change_percentage,  # type: float
        shift_point,  # type: int
        within_range,  # type: bool
        anomaly_detector_direction,  # type: Union[str, AnomalyDetectorDirection]
        suppress_condition,  # type: SuppressCondition
        **kwargs  # type: Any
    ):  # pylint: disable=unused-argument
        # type: (...) -> None
        self.change_percentage = change_percentage
        self.shift_point = shift_point
        self.within_range = within_range
        self.anomaly_detector_direction = anomaly_detector_direction
        self.suppress_condition = suppress_condition

    def __repr__(self):
        return (
            "ChangeThresholdCondition(change_percentage={}, shift_point={}, within_range={}, "
            "anomaly_detector_direction={}, suppress_condition={})".format(
                self.change_percentage,
                self.shift_point,
                self.within_range,
                self.anomaly_detector_direction,
                repr(self.suppress_condition),
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, condition):
        return (
            cls(
                change_percentage=condition.change_percentage,
                shift_point=condition.shift_point,
                within_range=condition.within_range,
                anomaly_detector_direction=condition.anomaly_detector_direction,
                suppress_condition=SuppressCondition._from_generated(
                    condition.suppress_condition
                ),
            )
            if condition
            else None
        )

    def _to_generated(self):
        return _ChangeThresholdCondition(
            change_percentage=self.change_percentage,
            shift_point=self.shift_point,
            within_range=self.within_range,
            anomaly_detector_direction=self.anomaly_detector_direction,
            suppress_condition=_SuppressCondition(
                min_number=self.suppress_condition.min_number,
                min_ratio=self.suppress_condition.min_ratio,
            ),
        )

    def _to_generated_patch(self):
        return _ChangeThresholdConditionPatch(
            change_percentage=self.change_percentage,
            shift_point=self.shift_point,
            within_range=self.within_range,
            anomaly_detector_direction=self.anomaly_detector_direction,
            suppress_condition=_SuppressConditionPatch(
                min_number=self.suppress_condition.min_number,
                min_ratio=self.suppress_condition.min_ratio,
            ),
        )


class SuppressCondition(object):
    """SuppressCondition.

    :param min_number: Required. min point number, value range : [1, +∞).
    :type min_number: int
    :param min_ratio: Required. min point ratio, value range : (0, 100].
    :type min_ratio: float
    """

    def __init__(
        self, min_number, min_ratio, **kwargs
    ):  # pylint: disable=unused-argument
        # type: (int, float, Any) -> None
        self.min_number = min_number
        self.min_ratio = min_ratio

    def __repr__(self):
        return "SuppressCondition(min_number={}, min_ratio={})".format(
            self.min_number, self.min_ratio
        )[:1024]

    @classmethod
    def _from_generated(cls, condition):
        return (
            cls(min_number=condition.min_number, min_ratio=condition.min_ratio)
            if condition
            else None
        )


class SmartDetectionCondition(object):
    """SmartDetectionCondition.

    :param sensitivity: Required. sensitivity, value range : (0, 100].
    :type sensitivity: float
    :param anomaly_detector_direction: Required. detection direction. Possible values include:
     "Both", "Down", "Up".
    :type anomaly_detector_direction: str or
     ~azure.ai.metricsadvisor.models.AnomalyDetectorDirection
    :param suppress_condition: Required.
    :type suppress_condition: ~azure.ai.metricsadvisor.models.SuppressCondition
    """

    def __init__(
        self, sensitivity, anomaly_detector_direction, suppress_condition, **kwargs
    ):  # pylint: disable=unused-argument
        # type: (float, Union[str, AnomalyDetectorDirection], SuppressCondition, Any) -> None
        self.sensitivity = sensitivity
        self.anomaly_detector_direction = anomaly_detector_direction
        self.suppress_condition = suppress_condition

    def __repr__(self):
        return "SmartDetectionCondition(sensitivity={}, anomaly_detector_direction={}, suppress_condition={})".format(
            self.sensitivity,
            self.anomaly_detector_direction,
            repr(self.suppress_condition),
        )[
            :1024
        ]

    @classmethod
    def _from_generated(cls, condition):
        return (
            cls(
                sensitivity=condition.sensitivity,
                anomaly_detector_direction=condition.anomaly_detector_direction,
                suppress_condition=SuppressCondition._from_generated(
                    condition.suppress_condition
                ),
            )
            if condition
            else None
        )

    def _to_generated(self):
        return _SmartDetectionCondition(
            sensitivity=self.sensitivity,
            anomaly_detector_direction=self.anomaly_detector_direction,
            suppress_condition=_SuppressCondition(
                min_number=self.suppress_condition.min_number,
                min_ratio=self.suppress_condition.min_ratio,
            ),
        )

    def _to_generated_patch(self):
        return _SmartDetectionConditionPatch(
            sensitivity=self.sensitivity,
            anomaly_detector_direction=self.anomaly_detector_direction,
            suppress_condition=_SuppressConditionPatch(
                min_number=self.suppress_condition.min_number,
                min_ratio=self.suppress_condition.min_ratio,
            ),
        )


class HardThresholdCondition(object):
    """HardThresholdCondition.

    :param anomaly_detector_direction: Required. detection direction. Possible values include:
        "Both", "Down", "Up".
    :type anomaly_detector_direction: str or
        ~azure.ai.metricsadvisor.models.AnomalyDetectorDirection
    :param suppress_condition: Required.
    :type suppress_condition: ~azure.ai.metricsadvisor.models.SuppressCondition
    :keyword lower_bound: lower bound
        should be specified when anomalyDetectorDirection is Both or Down.
    :paramtype lower_bound: float
    :keyword upper_bound: upper bound
        should be specified when anomalyDetectorDirection is Both or Up.
    :paramtype upper_bound: float
    """

    def __init__(self, anomaly_detector_direction, suppress_condition, **kwargs):
        # type: (Union[str, AnomalyDetectorDirection], SuppressCondition, Any) -> None
        self.anomaly_detector_direction = anomaly_detector_direction
        self.suppress_condition = suppress_condition
        self.lower_bound = kwargs.get("lower_bound", None)
        self.upper_bound = kwargs.get("upper_bound", None)

    def __repr__(self):
        return (
            "HardThresholdCondition(anomaly_detector_direction={}, suppress_condition={}, lower_bound={}, "
            "upper_bound={})".format(
                self.anomaly_detector_direction,
                repr(self.suppress_condition),
                self.lower_bound,
                self.upper_bound,
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, condition):
        return (
            cls(
                anomaly_detector_direction=condition.anomaly_detector_direction,
                suppress_condition=SuppressCondition._from_generated(
                    condition.suppress_condition
                ),
                lower_bound=condition.lower_bound,
                upper_bound=condition.upper_bound,
            )
            if condition
            else None
        )

    def _to_generated(self):
        return _HardThresholdCondition(
            lower_bound=self.lower_bound,
            upper_bound=self.upper_bound,
            anomaly_detector_direction=self.anomaly_detector_direction,
            suppress_condition=_SuppressCondition(
                min_number=self.suppress_condition.min_number,
                min_ratio=self.suppress_condition.min_ratio,
            ),
        )

    def _to_generated_patch(self):
        return _HardThresholdConditionPatch(
            lower_bound=self.lower_bound,
            upper_bound=self.upper_bound,
            anomaly_detector_direction=self.anomaly_detector_direction,
            suppress_condition=_SuppressConditionPatch(
                min_number=self.suppress_condition.min_number,
                min_ratio=self.suppress_condition.min_ratio,
            ),
        )


class MetricSeriesGroupDetectionCondition(MetricDetectionCondition):
    """MetricSeriesGroupAnomalyDetectionConditions.

    :param series_group_key: Required. dimension specified for series group.
    :type series_group_key: dict[str, str]
    :keyword condition_operator: condition operator
        should be specified when combining multiple detection conditions. Possible values include:
        "AND", "OR".
    :paramtype condition_operator: str or
        ~azure.ai.metricsadvisor.models.DetectionConditionOperator
    :keyword smart_detection_condition:
    :paramtype smart_detection_condition: ~azure.ai.metricsadvisor.models.SmartDetectionCondition
    :keyword hard_threshold_condition:
    :paramtype hard_threshold_condition: ~azure.ai.metricsadvisor.models.HardThresholdCondition
    :keyword change_threshold_condition:
    :paramtype change_threshold_condition: ~azure.ai.metricsadvisor.models.ChangeThresholdCondition
    """

    def __init__(self, series_group_key, **kwargs):
        # type: (Dict[str, str], Any) -> None
        super(MetricSeriesGroupDetectionCondition, self).__init__(**kwargs)
        self.series_group_key = series_group_key

    def __repr__(self):
        return (
            "MetricSeriesGroupDetectionCondition(condition_operator={}, smart_detection_condition={}, "
            "hard_threshold_condition={}, change_threshold_condition={}, series_group_key={})".format(
                self.condition_operator,
                repr(self.smart_detection_condition),
                repr(self.hard_threshold_condition),
                repr(self.change_threshold_condition),
                self.series_group_key,
            )[
                :1024
            ]
        )

    @classmethod
    def _from_generated(cls, condition):
        return cls(
            series_group_key=condition.group.dimension,
            condition_operator=condition.condition_operator,
            smart_detection_condition=SmartDetectionCondition._from_generated(
                condition.smart_detection_condition
            ),
            hard_threshold_condition=HardThresholdCondition._from_generated(
                condition.hard_threshold_condition
            ),
            change_threshold_condition=ChangeThresholdCondition._from_generated(
                condition.change_threshold_condition
            ),
        )

    def _to_generated(self):
        return _DimensionGroupConfiguration(
            group=_DimensionGroupIdentity(dimension=self.series_group_key),
            condition_operator=self.condition_operator,
            smart_detection_condition=self.smart_detection_condition._to_generated()
            if self.smart_detection_condition
            else None,
            hard_threshold_condition=self.hard_threshold_condition._to_generated()
            if self.hard_threshold_condition
            else None,
            change_threshold_condition=self.change_threshold_condition._to_generated()
            if self.change_threshold_condition
            else None,
        )


class MetricSingleSeriesDetectionCondition(MetricDetectionCondition):
    """MetricSingleSeriesDetectionCondition.

    :param series_key: Required. dimension specified for series.
    :type series_key: dict[str, str]
    :keyword condition_operator: condition operator
        should be specified when combining multiple detection conditions. Possible values include:
        "AND", "OR".
    :paramtype condition_operator: str or
        ~azure.ai.metricsadvisor.models.DetectionConditionOperator
    :keyword smart_detection_condition:
    :paramtype smart_detection_condition: ~azure.ai.metricsadvisor.models.SmartDetectionCondition
    :keyword hard_threshold_condition:
    :paramtype hard_threshold_condition: ~azure.ai.metricsadvisor.models.HardThresholdCondition
    :keyword change_threshold_condition:
    :paramtype change_threshold_condition: ~azure.ai.metricsadvisor.models.ChangeThresholdCondition
    """

    def __init__(self, series_key, **kwargs):
        # type: (Dict[str, str], Any) -> None
        super(MetricSingleSeriesDetectionCondition, self).__init__(**kwargs)
        self.series_key = series_key

    def __repr__(self):
        return (
            "MetricSingleSeriesDetectionCondition(condition_operator={}, smart_detection_condition={}, "
            "hard_threshold_condition={}, change_threshold_condition={}, series_key={})".format(
                self.condition_operator,
                repr(self.smart_detection_condition),
                repr(self.hard_threshold_condition),
                repr(self.change_threshold_condition),
                self.series_key,
            )[
                :1024
            ]
        )

    @classmethod
    def _from_generated(cls, condition):
        return cls(
            series_key=condition.series.dimension,
            condition_operator=condition.condition_operator,
            smart_detection_condition=SmartDetectionCondition._from_generated(
                condition.smart_detection_condition
            ),
            hard_threshold_condition=HardThresholdCondition._from_generated(
                condition.hard_threshold_condition
            ),
            change_threshold_condition=ChangeThresholdCondition._from_generated(
                condition.change_threshold_condition
            ),
        )

    def _to_generated(self):
        return _SeriesConfiguration(
            series=_SeriesIdentity(dimension=self.series_key),
            condition_operator=self.condition_operator,
            smart_detection_condition=self.smart_detection_condition._to_generated()
            if self.smart_detection_condition
            else None,
            hard_threshold_condition=self.hard_threshold_condition._to_generated()
            if self.hard_threshold_condition
            else None,
            change_threshold_condition=self.change_threshold_condition._to_generated()
            if self.change_threshold_condition
            else None,
        )


class DataFeedMetric(object):
    """DataFeedMetric.

    :param name: Required. metric name.
    :type name: str
    :keyword display_name: metric display name.
    :paramtype display_name: str
    :keyword description: metric description.
    :paramtype description: str
    :ivar id: metric id.
    :vartype id: str
    """

    def __init__(self, name, **kwargs):
        # type: (str, Any) -> None
        self.name = name
        self.id = kwargs.get("id", None)
        self.display_name = kwargs.get("display_name", None)
        self.description = kwargs.get("description", None)

    def __repr__(self):
        return "DataFeedMetric(name={}, id={}, display_name={}, description={})".format(
            self.name, self.id, self.display_name, self.description
        )[:1024]

    @classmethod
    def _from_generated(cls, metric):
        return cls(
            id=metric.metric_id,
            name=metric.metric_name,
            display_name=metric.metric_display_name,
            description=metric.metric_description,
        )

    def _to_generated(self):
        return _Metric(
            metric_name=self.name,
            metric_display_name=self.display_name,
            metric_description=self.description,
        )


class DataFeedDimension(object):
    """DataFeedDimension.

    :param name: Required. dimension name.
    :type name: str
    :keyword display_name: dimension display name.
    :paramtype display_name: str
    """

    def __init__(self, name, **kwargs):
        # type: (str, Any) -> None
        self.name = name
        self.display_name = kwargs.get("display_name", None)

    def __repr__(self):
        return "DataFeedDimension(name={}, display_name={})".format(
            self.name, self.display_name
        )[:1024]

    @classmethod
    def _from_generated(cls, dimension):
        return cls(
            name=dimension.dimension_name,
            display_name=dimension.dimension_display_name,
        )

    def _to_generated(self):
        return _Dimension(
            dimension_name=self.name, dimension_display_name=self.display_name
        )


class DataFeedIngestionProgress(object):
    """DataFeedIngestionProgress.

    :ivar latest_success_timestamp: the timestamp of lastest success ingestion job.
     null indicates not available.
    :vartype latest_success_timestamp: ~datetime.datetime
    :ivar latest_active_timestamp: the timestamp of lastest ingestion job with status update.
     null indicates not available.
    :vartype latest_active_timestamp: ~datetime.datetime
    """

    def __init__(self, **kwargs):
        self.latest_success_timestamp = kwargs.get("latest_success_timestamp")
        self.latest_active_timestamp = kwargs.get("latest_active_timestamp")

    def __repr__(self):
        return "DataFeedIngestionProgress(latest_success_timestamp={}, latest_active_timestamp={})".format(
            self.latest_success_timestamp, self.latest_active_timestamp
        )[
            :1024
        ]

    @classmethod
    def _from_generated(cls, resp):
        return cls(
            latest_success_timestamp=resp.latest_success_timestamp,
            latest_active_timestamp=resp.latest_active_timestamp,
        )


class MetricSeriesData(object):
    """MetricSeriesData.

    :ivar metric_id: metric unique id.
    :vartype metric_id: str
    :ivar series_key: dimension name and value pair.
    :vartype series_key: dict[str, str]
    :ivar timestamps: timestamps of the data related to this time series.
    :vartype timestamps: list[~datetime.datetime]
    :ivar values: values of the data related to this time series.
    :vartype values: list[float]
    """

    def __init__(self, **kwargs):
        self.metric_id = kwargs.get("metric_id", None)
        self.series_key = kwargs.get("series_key", None)
        self.timestamps = kwargs.get("timestamps", None)
        self.values = kwargs.get("values", None)

    def __repr__(self):
        return "MetricSeriesData(metric_id={}, series_key={}, timestamps={}, values={})".format(
            self.metric_id, self.series_key, self.timestamps, self.values
        )[
            :1024
        ]

    @classmethod
    def _from_generated(cls, data):
        return cls(
            metric_id=data.id.metric_id,
            series_key=data.id.dimension,
            timestamps=data.timestamp_list,
            values=data.value_list,
        )


class MetricEnrichedSeriesData(object):
    """MetricEnrichedSeriesData.

    All required parameters must be populated in order to send to Azure.

    :param series_key: Required.
    :type series_key: ~azure.ai.metricsadvisor.models.SeriesIdentity
    :param timestamps: Required. timestamps of the series.
    :type timestamps: list[~datetime.datetime]
    :param values: Required. values of the series.
    :type values: list[float]
    :param is_anomaly: Required. whether points of the series are anomalies.
    :type is_anomaly: list[bool]
    :param periods: Required. period calculated on each point of the series.
    :type periods: list[int]
    :param expected_values: Required. expected values of the series given by smart detector.
    :type expected_values: list[float]
    :param lower_bounds: Required. lower boundary list of the series given by smart
     detector.
    :type lower_bounds: list[float]
    :param upper_bounds: Required. upper boundary list of the series given by smart
     detector.
    :type upper_bounds: list[float]
    """

    def __init__(self, **kwargs):
        self.series_key = kwargs.get("series_key", None)
        self.timestamps = kwargs.get("timestamps", None)
        self.values = kwargs.get("values", None)
        self.is_anomaly = kwargs.get("is_anomaly", None)
        self.periods = kwargs.get("periods", None)
        self.expected_values = kwargs.get("expected_values", None)
        self.lower_bounds = kwargs.get("lower_bounds", None)
        self.upper_bounds = kwargs.get("upper_bounds", None)

    def __repr__(self):
        return (
            "MetricEnrichedSeriesData(series_key={}, timestamps={}, values={}, is_anomaly={}, periods={}, "
            "expected_values={}, lower_bounds={}, upper_bounds={})".format(
                self.series_key,
                self.timestamps,
                self.values,
                self.is_anomaly,
                self.periods,
                self.expected_values,
                self.lower_bounds,
                self.upper_bounds,
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, data):
        return cls(
            series_key=data.series.dimension,
            timestamps=data.timestamp_list,
            values=data.value_list,
            is_anomaly=data.is_anomaly_list,
            periods=data.period_list,
            expected_values=data.expected_value_list,
            lower_bounds=data.lower_boundary_list,
            upper_bounds=data.upper_boundary_list,
        )


class AnomalyAlert(object):
    """AnomalyAlert

    :ivar id: alert id.
    :vartype id: str
    :ivar timestamp: anomaly time.
    :vartype timestamp: ~datetime.datetime
    :ivar created_time: created time.
    :vartype created_time: ~datetime.datetime
    :ivar modified_time: modified time.
    :vartype modified_time: ~datetime.datetime
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.timestamp = kwargs.get("timestamp", None)
        self.created_time = kwargs.get("created_time", None)
        self.modified_time = kwargs.get("modified_time", None)

    def __repr__(self):
        return "AnomalyAlert(id={}, timestamp={}, created_time={}, modified_time={})".format(
            self.id, self.timestamp, self.created_time, self.modified_time
        )[
            :1024
        ]

    @classmethod
    def _from_generated(cls, alert):
        return cls(
            id=alert.alert_id,
            timestamp=alert.timestamp,
            created_time=alert.created_time,
            modified_time=alert.modified_time,
        )


DATA_FEED_TRANSFORM = {
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


class DataPointAnomaly(msrest.serialization.Model):
    """DataPointAnomaly.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar metric_id: metric unique id. Only returned for alerting anomaly result.
    :vartype metric_id: str
    :ivar detection_configuration_id: anomaly detection configuration unique id.
     Only returned for alerting anomaly result.
    :vartype detection_configuration_id: str
    :ivar timestamp: anomaly time.
    :vartype timestamp: ~datetime.datetime
    :ivar created_time: created time. Only returned for alerting result.
    :vartype created_time: ~datetime.datetime
    :ivar modified_time: modified time. Only returned for alerting result.
    :vartype modified_time: ~datetime.datetime
    :ivar dimension: dimension specified for series.
    :vartype dimension: dict[str, str]
    :ivar severity: anomaly severity. Possible values include: "Low", "Medium", "High".
    :vartype anomaly_severity: str or ~azure.ai.metricsadvisor.models.AnomalySeverity
    :vartype severity: str
    :ivar status: anomaly status. only returned for alerting anomaly result. Possible
     values include: "Active", "Resolved".
    :vartype status: str
    """

    _attribute_map = {
        "metric_id": {"key": "metricId", "type": "str"},
        "detection_configuration_id": {
            "key": "detectionConfigurationId",
            "type": "str",
        },
        "timestamp": {"key": "timestamp", "type": "iso-8601"},
        "created_time": {"key": "createdTime", "type": "iso-8601"},
        "modified_time": {"key": "modifiedTime", "type": "iso-8601"},
        "dimension": {"key": "dimension", "type": "{str}"},
        "severity": {"key": "severity", "type": "str"},
        "status": {"key": "status", "type": "str"},
    }

    def __init__(self, **kwargs):
        super(DataPointAnomaly, self).__init__(**kwargs)
        self.metric_id = kwargs.get("metric_id", None)
        self.detection_configuration_id = kwargs.get("detection_configuration_id", None)
        self.timestamp = kwargs.get("timestamp", None)
        self.created_time = kwargs.get("created_time", None)
        self.modified_time = kwargs.get("modified_time", None)
        self.dimension = kwargs.get("dimension", None)
        self.severity = kwargs.get("severity", None)
        self.status = kwargs.get("status", None)

    def __repr__(self):
        return (
            "DataPointAnomaly(metric_id={}, detection_configuration_id={}, timestamp={}, created_time={}, "
            "modified_time={}, dimension={}, severity={}, status={})".format(
                self.metric_id,
                self.detection_configuration_id,
                self.timestamp,
                self.created_time,
                self.modified_time,
                self.dimension,
                self.severity,
                self.status,
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, anomaly_result):
        # type: (AnomalyResult) -> Union[DataPointAnomaly, None]
        if not anomaly_result:
            return None
        severity = None
        status = None
        if anomaly_result.property:
            severity = anomaly_result.property.anomaly_severity
            status = anomaly_result.property.anomaly_status

        return cls(
            metric_id=anomaly_result.metric_id,
            detection_configuration_id=anomaly_result.anomaly_detection_configuration_id,
            timestamp=anomaly_result.timestamp,
            created_time=anomaly_result.created_time,
            modified_time=anomaly_result.modified_time,
            dimension=anomaly_result.dimension,
            severity=severity,
            status=status,
        )


class AnomalyIncident(msrest.serialization.Model):
    """AnomalyIncident.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar metric_id: metric unique id. Only returned for alerting incident result.
    :vartype metric_id: str
    :ivar detection_configuration_id: anomaly detection configuration unique id.
     Only returned for alerting incident result.
    :vartype detection_configuration_id: str
    :ivar id: incident id.
    :vartype id: str
    :ivar start_time: incident start time.
    :vartype start_time: ~datetime.datetime
    :ivar last_time: incident last time.
    :vartype last_time: ~datetime.datetime
    :param dimension_key: dimension specified for series.
    :type dimension_key: dict[str, str]
    :ivar severity: max severity of latest anomalies in the incident. Possible values include:
     "Low", "Medium", "High".
    :vartype severity: str or ~azure.ai.metricsadvisor.models.AnomalySeverity
    :ivar status: incident status
     only return for alerting incident result. Possible values include: "Active", "Resolved".
    :vartype status: str or ~azure.ai.metricsadvisor.models.AnomalyIncidentStatus
    """

    _attribute_map = {
        "metric_id": {"key": "metricId", "type": "str"},
        "detection_configuration_id": {
            "key": "detectionConfigurationId",
            "type": "str",
        },
        "id": {"key": "id", "type": "str"},
        "start_time": {"key": "startTime", "type": "iso-8601"},
        "last_time": {"key": "lastTime", "type": "iso-8601"},
        "dimension_key": {"key": "dimensionKey", "type": "{str}"},
        "severity": {"key": "severity", "type": "str"},
        "status": {"key": "status", "type": "str"},
    }

    def __init__(self, **kwargs):
        super(AnomalyIncident, self).__init__(**kwargs)
        self.metric_id = kwargs.get("metric_id", None)
        self.detection_configuration_id = kwargs.get("detection_configuration_id", None)
        self.id = kwargs.get("id", None)
        self.start_time = kwargs.get("start_time", None)
        self.last_time = kwargs.get("last_time", None)
        self.dimension_key = kwargs.get("dimension_key", None)
        self.severity = kwargs.get("severity", None)
        self.status = kwargs.get("status", None)

    def __repr__(self):
        return (
            "AnomalyIncident(metric_id={}, detection_configuration_id={}, id={}, start_time={}, last_time={}, "
            "dimension_key={}, severity={}, status={})".format(
                self.metric_id,
                self.detection_configuration_id,
                self.id,
                self.start_time,
                self.last_time,
                self.dimension_key,
                self.severity,
                self.status,
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, incident_result):
        # type: (IncidentResult) -> Union[AnomalyIncident, None]
        if not incident_result:
            return None
        dimension_key = (
            incident_result.root_node.dimension if incident_result.root_node else None
        )
        severity = None
        status = None
        if incident_result.property:
            severity = incident_result.property.max_severity
            status = incident_result.property.incident_status
        return cls(
            metric_id=incident_result.metric_id,
            detection_configuration_id=incident_result.anomaly_detection_configuration_id,
            id=incident_result.incident_id,
            start_time=incident_result.start_time,
            last_time=incident_result.last_time,
            dimension_key=dimension_key,
            severity=severity,
            status=status,
        )


class IncidentRootCause(msrest.serialization.Model):
    """Incident Root Cause.

    Variables are only populated by the server, and will be ignored when sending a request.

    :param dimension_key: dimension specified for series group.
    :type dimension_key: dict[str, str]
    :ivar path: drilling down path from query anomaly to root cause.
    :vartype path: list[str]
    :ivar score: score.
    :vartype score: float
    :ivar description: description.
    :vartype description: str
    """

    _attribute_map = {
        "dimension_key": {"key": "dimensionKey", "type": "{str}"},
        "path": {"key": "path", "type": "[str]"},
        "score": {"key": "score", "type": "float"},
        "description": {"key": "description", "type": "str"},
    }

    def __init__(self, **kwargs):
        super(IncidentRootCause, self).__init__(**kwargs)
        self.dimension_key = kwargs.get("dimension_key", None)
        self.path = kwargs.get("path", None)
        self.score = kwargs.get("score", None)
        self.description = kwargs.get("description", None)

    def __repr__(self):
        return "IncidentRootCause(dimension_key={}, path={}, score={}, description={})".format(
            self.dimension_key, self.path, self.score, self.description
        )[
            :1024
        ]

    @classmethod
    def _from_generated(cls, root_cause):
        # type: (RootCause) -> Union[IncidentRootCause, None]
        if not root_cause:
            return None
        dimension_key = (
            root_cause.root_cause.dimension if root_cause.root_cause else None
        )
        return cls(
            dimension_key=dimension_key,
            path=root_cause.path,
            score=root_cause.score,
            description=root_cause.description,
        )


class MetricFeedback(dict):
    """Feedback base class

    Variables are only populated by the server, and will be ignored when sending a request.

    All required parameters must be populated in order to send to Azure.

    :ivar feedback_type: Required. feedback type.Constant filled by server.  Possible values
     include: "Anomaly", "ChangePoint", "Period", "Comment".
    :vartype feedback_type: str or ~azure.ai.metricsadvisor.models.FeedbackType
    :ivar str id: feedback unique id.
    :ivar created_time: feedback created time.
    :vartype created_time: ~datetime.datetime
    :ivar user_principal: user who gives this feedback.
    :vartype user_principal: str
    :ivar str metric_id: Required. metric unique id.
    :ivar dict[str, str] dimension_key: Required. metric dimension filter.
    """

    _attribute_map = {
        "feedback_type": {"key": "feedbackType", "type": "str"},
        "id": {"key": "id", "type": "str"},
        "created_time": {"key": "createdTime", "type": "iso-8601"},
        "user_principal": {"key": "userPrincipal", "type": "str"},
        "metric_id": {"key": "metricId", "type": "str"},
        "dimension_key": {"key": "dimensionKey", "type": "{str}"},
    }

    def __init__(self, feedback_type, metric_id, dimension_key, **kwargs):
        super(MetricFeedback, self).__init__(**kwargs)
        self.feedback_type = feedback_type  # type: str
        self.id = kwargs.get("id", None)
        self.created_time = kwargs.get("created_time", None)
        self.user_principal = kwargs.get("user_principal", None)
        self.metric_id = metric_id
        self.dimension_key = dimension_key

    def __repr__(self):
        return (
            "MetricFeedback(feedback_type={}, id={}, created_time={}, user_principal={}, metric_id={}, "
            "dimension_key={})".format(
                self.feedback_type,
                self.id,
                self.created_time,
                self.user_principal,
                self.metric_id,
                self.dimension_key,
            )[:1024]
        )

    def _to_generated_patch(self):
        pass


class AnomalyFeedback(MetricFeedback):  # pylint:disable=too-many-instance-attributes
    """AnomalyFeedback.

    Variables are only populated by the server, and will be ignored when sending a request.

    All required parameters must be populated in order to send to Azure.

    :ivar feedback_type: Required. feedback type.Constant filled by server.  Possible values
     include: "Anomaly", "ChangePoint", "Period", "Comment".
    :vartype feedback_type: str or ~azure.ai.metricsadvisor.models.FeedbackType
    :ivar str id: feedback unique id.
    :keyword created_time: feedback created time.
    :paramtype created_time: ~datetime.datetime
    :keyword str user_principal: user who gives this feedback.
    :param str metric_id: Required. metric unique id.
    :param dict[str, str] dimension_key: Required. metric dimension filter.
    :param start_time: Required. the start timestamp of feedback timerange.
    :type start_time: ~datetime.datetime
    :param end_time: Required. the end timestamp of feedback timerange, when equals to startTime
     means only one timestamp.
    :type end_time: ~datetime.datetime
    :param value: Required. Possible values include: "AutoDetect", "Anomaly", "NotAnomaly".
    :type value: str or ~azure.ai.metricsadvisor.models.AnomalyValue
    :keyword anomaly_detection_configuration_id: the corresponding anomaly detection configuration of
     this feedback.
    :paramtype anomaly_detection_configuration_id: str
    :keyword anomaly_detection_configuration_snapshot:
    :paramtype anomaly_detection_configuration_snapshot:
     ~azure.ai.metricsadvisor.models.AnomalyDetectionConfiguration
    """

    _attribute_map = {
        "feedback_type": {"key": "feedbackType", "type": "str"},
        "id": {"key": "id", "type": "str"},
        "created_time": {"key": "createdTime", "type": "iso-8601"},
        "user_principal": {"key": "userPrincipal", "type": "str"},
        "metric_id": {"key": "metricId", "type": "str"},
        "dimension_key": {"key": "dimensionKey", "type": "{str}"},
        "start_time": {"key": "startTime", "type": "iso-8601"},
        "end_time": {"key": "endTime", "type": "iso-8601"},
        "value": {"key": "value", "type": "str"},
        "anomaly_detection_configuration_id": {
            "key": "anomalyDetectionConfigurationId",
            "type": "str",
        },
        "anomaly_detection_configuration_snapshot": {
            "key": "anomalyDetectionConfigurationSnapshot",
            "type": "AnomalyDetectionConfiguration",
        },
    }

    def __init__(self, metric_id, dimension_key, start_time, end_time, value, **kwargs):
        super(AnomalyFeedback, self).__init__(
            feedback_type="Anomaly",
            metric_id=metric_id,
            dimension_key=dimension_key,
            **kwargs
        )
        self.start_time = start_time
        self.end_time = end_time
        self.value = value
        self.anomaly_detection_configuration_id = kwargs.get(
            "anomaly_detection_configuration_id", None
        )
        self.anomaly_detection_configuration_snapshot = kwargs.get(
            "anomaly_detection_configuration_snapshot", None
        )

    def __repr__(self):
        return (
            "AnomalyFeedback(feedback_type={}, id={}, created_time={}, user_principal={}, metric_id={}, "
            "dimension_key={}, start_time={}, end_time={}, value={}, anomaly_detection_configuration_id={}, "
            "anomaly_detection_configuration_snapshot={})".format(
                self.feedback_type,
                self.id,
                self.created_time,
                self.user_principal,
                self.metric_id,
                self.dimension_key,
                self.start_time,
                self.end_time,
                self.value,
                self.anomaly_detection_configuration_id,
                self.anomaly_detection_configuration_snapshot,
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, anomaly_feedback):
        # type: (_AnomalyFeedback) -> Union[AnomalyFeedback, None]
        if not anomaly_feedback:
            return None
        dimension_key = anomaly_feedback.dimension_filter.dimension
        value = anomaly_feedback.value.anomaly_value if anomaly_feedback.value else None
        return cls(
            id=anomaly_feedback.feedback_id,
            created_time=anomaly_feedback.created_time,
            user_principal=anomaly_feedback.user_principal,
            metric_id=anomaly_feedback.metric_id,
            dimension_key=dimension_key,
            start_time=anomaly_feedback.start_time,
            end_time=anomaly_feedback.end_time,
            value=value,
            anomaly_detection_configuration_id=anomaly_feedback.anomaly_detection_configuration_id,
            anomaly_detection_configuration_snapshot=anomaly_feedback.anomaly_detection_configuration_snapshot,
        )

    def _to_generated(self):
        # type: (AnomalyFeedback) -> _AnomalyFeedback
        dimension_filter = FeedbackDimensionFilter(dimension=self.dimension_key)
        value = AnomalyFeedbackValue(anomaly_value=self.value)
        return _AnomalyFeedback(
            metric_id=self.metric_id,
            dimension_filter=dimension_filter,
            start_time=self.start_time,
            end_time=self.end_time,
            value=value,
            anomaly_detection_configuration_id=self.anomaly_detection_configuration_id,
            anomaly_detection_configuration_snapshot=self.anomaly_detection_configuration_snapshot,
        )


class ChangePointFeedback(MetricFeedback):
    """ChangePointFeedback.

    Variables are only populated by the server, and will be ignored when sending a request.

    All required parameters must be populated in order to send to Azure.

    :ivar feedback_type: Required. feedback type.Constant filled by server.  Possible values
     include: "Anomaly", "ChangePoint", "Period", "Comment".
    :vartype feedback_type: str or ~azure.ai.metricsadvisor.models.FeedbackType
    :ivar str id: feedback unique id.
    :keyword created_time: feedback created time.
    :paramtype created_time: ~datetime.datetime
    :keyword str user_principal: user who gives this feedback.
    :param str metric_id: Required. metric unique id.
    :param dict[str, str] dimension_key: Required. metric dimension filter.
    :param start_time: Required. the start timestamp of feedback timerange.
    :type start_time: ~datetime.datetime
    :param end_time: Required. the end timestamp of feedback timerange, when equals to startTime
     means only one timestamp.
    :type end_time: ~datetime.datetime
    :param value: Required. Possible values include: "AutoDetect", "ChangePoint", "NotChangePoint".
    :type value: str or ~azure.ai.metricsadvisor.models.ChangePointValue
    """

    _attribute_map = {
        "feedback_type": {"key": "feedbackType", "type": "str"},
        "id": {"key": "id", "type": "str"},
        "created_time": {"key": "createdTime", "type": "iso-8601"},
        "user_principal": {"key": "userPrincipal", "type": "str"},
        "metric_id": {"key": "metricId", "type": "str"},
        "dimension_key": {"key": "dimensionKey", "type": "{str}"},
        "start_time": {"key": "startTime", "type": "iso-8601"},
        "end_time": {"key": "endTime", "type": "iso-8601"},
        "value": {"key": "value", "type": "str"},
    }

    def __init__(self, metric_id, dimension_key, start_time, end_time, value, **kwargs):
        super(ChangePointFeedback, self).__init__(
            feedback_type="ChangePoint",
            metric_id=metric_id,
            dimension_key=dimension_key,
            **kwargs
        )
        self.start_time = start_time
        self.end_time = end_time
        self.value = value

    def __repr__(self):
        return (
            "ChangePointFeedback(feedback_type={}, id={}, created_time={}, user_principal={}, metric_id={}, "
            "dimension_key={}, start_time={}, end_time={}, value={})".format(
                self.feedback_type,
                self.id,
                self.created_time,
                self.user_principal,
                self.metric_id,
                self.dimension_key,
                self.start_time,
                self.end_time,
                self.value,
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, change_point_feedback):
        # type: (_ChangePointFeedback) -> Union[ChangePointFeedback, None]
        if not change_point_feedback:
            return None
        dimension_key = change_point_feedback.dimension_filter.dimension
        value = (
            change_point_feedback.value.change_point_value
            if change_point_feedback.value
            else None
        )
        return cls(
            id=change_point_feedback.feedback_id,
            created_time=change_point_feedback.created_time,
            user_principal=change_point_feedback.user_principal,
            metric_id=change_point_feedback.metric_id,
            dimension_key=dimension_key,
            start_time=change_point_feedback.start_time,
            end_time=change_point_feedback.end_time,
            value=value,
        )

    def _to_generated(self):
        # type: (ChangePointFeedback) -> _ChangePointFeedback
        dimension_filter = FeedbackDimensionFilter(dimension=self.dimension_key)
        value = ChangePointFeedbackValue(change_point_value=self.value)
        return _ChangePointFeedback(
            metric_id=self.metric_id,
            dimension_filter=dimension_filter,
            start_time=self.start_time,
            end_time=self.end_time,
            value=value,
        )


class CommentFeedback(MetricFeedback):
    """CommentFeedback.

    Variables are only populated by the server, and will be ignored when sending a request.

    All required parameters must be populated in order to send to Azure.

    :ivar feedback_type: Required. feedback type.Constant filled by server.  Possible values
     include: "Anomaly", "ChangePoint", "Period", "Comment".
    :vartype feedback_type: str or ~azure.ai.metricsadvisor.models.FeedbackType
    :ivar str id: feedback unique id.
    :keyword created_time: feedback created time.
    :paramtype created_time: ~datetime.datetime
    :keyword str user_principal: user who gives this feedback.
    :param str metric_id: Required. metric unique id.
    :param dict[str, str] dimension_key: Required. metric dimension filter.
    :param start_time: the start timestamp of feedback timerange.
    :type start_time: ~datetime.datetime
    :param end_time: the end timestamp of feedback timerange, when equals to startTime means only
     one timestamp.
    :type end_time: ~datetime.datetime
    :param value: Required. the comment string.
    :type value: str
    """

    _attribute_map = {
        "feedback_type": {"key": "feedbackType", "type": "str"},
        "id": {"key": "id", "type": "str"},
        "created_time": {"key": "createdTime", "type": "iso-8601"},
        "user_principal": {"key": "userPrincipal", "type": "str"},
        "metric_id": {"key": "metricId", "type": "str"},
        "dimension_key": {"key": "dimensionKey", "type": "{str}"},
        "start_time": {"key": "startTime", "type": "iso-8601"},
        "end_time": {"key": "endTime", "type": "iso-8601"},
        "value": {"key": "value", "type": "str"},
    }

    def __init__(self, metric_id, dimension_key, start_time, end_time, value, **kwargs):
        super(CommentFeedback, self).__init__(
            feedback_type="Comment",
            metric_id=metric_id,
            dimension_key=dimension_key,
            **kwargs
        )
        self.start_time = start_time
        self.end_time = end_time
        self.value = value

    def __repr__(self):
        return (
            "CommentFeedback(feedback_type={}, id={}, created_time={}, user_principal={}, metric_id={}, "
            "dimension_key={}, start_time={}, end_time={}, value={})".format(
                self.feedback_type,
                self.id,
                self.created_time,
                self.user_principal,
                self.metric_id,
                self.dimension_key,
                self.start_time,
                self.end_time,
                self.value,
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, comment_feedback):
        # type: (_CommentFeedback) -> Union[CommentFeedback, None]
        if not comment_feedback:
            return None
        dimension_key = comment_feedback.dimension_filter.dimension
        value = comment_feedback.value.comment_value if comment_feedback.value else None
        return cls(
            id=comment_feedback.feedback_id,
            created_time=comment_feedback.created_time,
            user_principal=comment_feedback.user_principal,
            metric_id=comment_feedback.metric_id,
            dimension_key=dimension_key,
            start_time=comment_feedback.start_time,
            end_time=comment_feedback.end_time,
            value=value,
        )

    def _to_generated(self):
        # type: (CommentFeedback) -> _CommentFeedback
        dimension_filter = FeedbackDimensionFilter(dimension=self.dimension_key)
        value = CommentFeedbackValue(comment_value=self.value)
        return _CommentFeedback(
            metric_id=self.metric_id,
            dimension_filter=dimension_filter,
            start_time=self.start_time,
            end_time=self.end_time,
            value=value,
        )


class PeriodFeedback(MetricFeedback):
    """PeriodFeedback.

    Variables are only populated by the server, and will be ignored when sending a request.

    All required parameters must be populated in order to send to Azure.

    :ivar feedback_type: Required. feedback type.Constant filled by server.  Possible values
     include: "Anomaly", "ChangePoint", "Period", "Comment".
    :vartype feedback_type: str or ~azure.ai.metricsadvisor.models.FeedbackType
    :ivar str id: feedback unique id.
    :keyword created_time: feedback created time.
    :paramtype created_time: ~datetime.datetime
    :keyword str user_principal: user who gives this feedback.
    :param str metric_id: Required. metric unique id.
    :param dict[str, str] dimension_key: Required. metric dimension filter.
    :param value: Required.
    :type value: int
    :param period_type: Required. the type of setting period. Possible values include:
     "AutoDetect", "AssignValue".
    :type period_type: str or ~azure.ai.metricsadvisor.models.PeriodType
    """

    _attribute_map = {
        "feedback_type": {"key": "feedbackType", "type": "str"},
        "id": {"key": "id", "type": "str"},
        "created_time": {"key": "createdTime", "type": "iso-8601"},
        "user_principal": {"key": "userPrincipal", "type": "str"},
        "metric_id": {"key": "metricId", "type": "str"},
        "dimension_key": {"key": "dimensionKey", "type": "{str}"},
        "value": {"key": "value", "type": "int"},
        "period_type": {"key": "periodType", "type": "str"},
    }

    def __init__(self, metric_id, dimension_key, value, period_type, **kwargs):
        super(PeriodFeedback, self).__init__(
            feedback_type="Period",
            metric_id=metric_id,
            dimension_key=dimension_key,
            **kwargs
        )
        self.value = value
        self.period_type = period_type

    def __repr__(self):
        return (
            "PeriodFeedback(feedback_type={}, id={}, created_time={}, user_principal={}, metric_id={}, "
            "dimension_key={}, value={}, period_type={})".format(
                self.feedback_type,
                self.id,
                self.created_time,
                self.user_principal,
                self.metric_id,
                self.dimension_key,
                self.value,
                self.period_type,
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, period_feedback):
        # type: (_PeriodFeedback) -> Union[PeriodFeedback, None]
        if not period_feedback:
            return None
        dimension_key = period_feedback.dimension_filter.dimension
        value = period_feedback.value.period_value if period_feedback.value else None
        period_type = (
            period_feedback.value.period_type if period_feedback.value else None
        )
        return cls(
            id=period_feedback.feedback_id,
            created_time=period_feedback.created_time,
            user_principal=period_feedback.user_principal,
            metric_id=period_feedback.metric_id,
            dimension_key=dimension_key,
            value=value,
            period_type=period_type,
        )

    def _to_generated(self):
        # type: (PeriodFeedback) -> _PeriodFeedback
        dimension_filter = FeedbackDimensionFilter(dimension=self.dimension_key)
        value = PeriodFeedbackValue(
            period_type=self.period_type, period_value=self.value
        )
        return _PeriodFeedback(
            metric_id=self.metric_id,
            dimension_filter=dimension_filter,
            value=value,
        )


class DatasourceCredential(dict):
    """DatasourceCredential base class.

    :param credential_type: Required. Type of data source credential.Constant filled by
     server.  Possible values include: "AzureSQLConnectionString", "DataLakeGen2SharedKey",
     "ServicePrincipal", "ServicePrincipalInKV".
    :type credential_type: str or
     ~azure.ai.metricsadvisor.models.DatasourceCredentialType
    :ivar id: Unique id of data source credential.
    :vartype id: str
    :param name: Required. Name of data source credential.
    :type name: str
    :keyword str description: Description of data source credential.
    """

    _attribute_map = {
        "credential_type": {"key": "credentialType", "type": "str"},
        "id": {"key": "id", "type": "str"},
        "name": {"key": "name", "type": "str"},
        "description": {"key": "description", "type": "str"},
    }

    def __init__(self, name, credential_type, **kwargs):
        # type: (str, str, Any) -> None
        super(DatasourceCredential, self).__init__(
            name=name, credential_type=credential_type, **kwargs
        )
        self.credential_type = credential_type
        self.name = name
        self.id = kwargs.get("id", None)
        self.description = kwargs.get("description", None)

    def __repr__(self):
        return "DatasourceCredential(id={}, credential_type={}, name={}, description={})".format(
            self.id, self.credential_type, self.name, self.description
        )[
            :1024
        ]

    def _to_generated_patch(self):
        pass


class DatasourceSqlConnectionString(DatasourceCredential):
    """DatasourceSqlConnectionString.

    All required parameters must be populated in order to send to Azure.

    :ivar credential_type: Required. Type of data source credential.Constant filled by
     server.  Possible values include: "AzureSQLConnectionString", "DataLakeGen2SharedKey",
     "ServicePrincipal", "ServicePrincipalInKV".
    :type credential_type: str or
     ~azure.ai.metricsadvisor.models.DatasourceCredentialType
    :ivar id: Unique id of data source credential.
    :vartype id: str
    :param name: Required. Name of data source credential.
    :type name: str
    :keyword str description: Description of data source credential.
    :param connection_string: Required. The connection string to access the Azure SQL.
    :type connection_string: str
    """

    _attribute_map = {
        "credential_type": {"key": "credentialType", "type": "str"},
        "id": {"key": "id", "type": "str"},
        "name": {"key": "name", "type": "str"},
        "description": {"key": "description", "type": "str"},
        "connection_string": {"key": "connectionString", "type": "str"},
    }

    def __init__(self, name, connection_string, **kwargs):
        # type: (str, str, Any) -> None
        super(DatasourceSqlConnectionString, self).__init__(
            name=name, credential_type="AzureSQLConnectionString", **kwargs
        )
        self.connection_string = connection_string

    def __repr__(self):
        return (
            "DatasourceSqlConnectionString(id={}, credential_type={}, name={}, "
            "connection_string={}, description={})".format(
                self.id,
                self.credential_type,
                self.name,
                self.connection_string,
                self.description,
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, source):
        return cls(
            name=source.data_source_credential_name,
            connection_string=source.parameters.connection_string,
            id=source.data_source_credential_id,
            description=source.data_source_credential_description,
        )

    def _to_generated(self):
        param = _AzureSQLConnectionStringParam(connection_string=self.connection_string)
        return _AzureSQLConnectionStringCredential(
            data_source_credential_type=self.credential_type,
            data_source_credential_name=self.name,
            data_source_credential_description=self.description,
            parameters=param,
        )

    def _to_generated_patch(self):
        param_patch = _AzureSQLConnectionStringParamPatch(
            connection_string=self.connection_string
        )
        return _AzureSQLConnectionStringCredentialPatch(
            data_source_credential_type=self.credential_type,
            data_source_credential_name=self.name,
            data_source_credential_description=self.description,
            parameters=param_patch,
        )


class DatasourceDataLakeGen2SharedKey(DatasourceCredential):
    """DatasourceDataLakeGen2SharedKey.

    All required parameters must be populated in order to send to Azure.

    :ivar credential_type: Required. Type of data source credential.Constant filled by
     server.  Possible values include: "AzureSQLConnectionString", "DataLakeGen2SharedKey",
     "ServicePrincipal", "ServicePrincipalInKV".
    :type credential_type: str or
     ~azure.ai.metricsadvisor.models.DatasourceCredentialType
    :ivar id: Unique id of data source credential.
    :vartype id: str
    :param name: Required. Name of data source credential.
    :type name: str
    :keyword str description: Description of data source credential.
    :param account_key: Required. The account key to access the Azure Data Lake Storage Gen2.
    :type account_key: str
    """

    _attribute_map = {
        "credential_type": {"key": "credentialType", "type": "str"},
        "id": {"key": "id", "type": "str"},
        "name": {"key": "name", "type": "str"},
        "description": {"key": "description", "type": "str"},
        "account_key": {"key": "accountKey", "type": "str"},
    }

    def __init__(self, name, account_key, **kwargs):
        # type: (str, str, Any) -> None
        super(DatasourceDataLakeGen2SharedKey, self).__init__(
            name=name, credential_type="DataLakeGen2SharedKey", **kwargs
        )
        self.account_key = account_key

    def __repr__(self):
        return (
            "DatasourceDataLakeGen2SharedKey(id={}, credential_type={}, name={}, "
            "account_key={}, description={})".format(
                self.id,
                self.credential_type,
                self.name,
                self.account_key,
                self.description,
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, source):
        return cls(
            name=source.data_source_credential_name,
            account_key=source.parameters.account_key,
            id=source.data_source_credential_id,
            description=source.data_source_credential_description,
        )

    def _to_generated(self):
        param = _DataLakeGen2SharedKeyParam(account_key=self.account_key)
        return _DataLakeGen2SharedKeyCredential(
            data_source_credential_type=self.credential_type,
            data_source_credential_name=self.name,
            data_source_credential_description=self.description,
            parameters=param,
        )

    def _to_generated_patch(self):
        param_patch = _DataLakeGen2SharedKeyParamPatch(account_key=self.account_key)
        return _DataLakeGen2SharedKeyCredentialPatch(
            data_source_credential_type=self.credential_type,
            data_source_credential_name=self.name,
            data_source_credential_description=self.description,
            parameters=param_patch,
        )


class DatasourceServicePrincipal(DatasourceCredential):
    """DatasourceServicePrincipal.

    All required parameters must be populated in order to send to Azure.

    :ivar credential_type: Required. Type of data source credential.Constant filled by
     server.  Possible values include: "AzureSQLConnectionString", "DataLakeGen2SharedKey",
     "ServicePrincipal", "ServicePrincipalInKV".
    :type credential_type: str or
     ~azure.ai.metricsadvisor.models.DatasourceCredentialType
    :ivar id: Unique id of data source credential.
    :vartype id: str
    :param name: Required. Name of data source credential.
    :type name: str
    :keyword str description: Description of data source credential.
    :param client_id: Required. The client id of the service principal.
    :type client_id: str
    :param client_secret: Required. The client secret of the service principal.
    :type client_secret: str
    :param tenant_id: Required. The tenant id of the service principal.
    :type tenant_id: str
    """

    _attribute_map = {
        "credential_type": {"key": "credentialType", "type": "str"},
        "id": {"key": "id", "type": "str"},
        "name": {"key": "name", "type": "str"},
        "description": {"key": "description", "type": "str"},
        "client_id": {"key": "clientId", "type": "str"},
        "client_secret": {"key": "clientSecret", "type": "str"},
        "tenant_id": {"key": "tenantId", "type": "str"},
    }

    def __init__(self, name, client_id, client_secret, tenant_id, **kwargs):
        # type: (str, str, str, str, Any) -> None
        super(DatasourceServicePrincipal, self).__init__(
            name=name, credential_type="ServicePrincipal", **kwargs
        )
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id

    def __repr__(self):
        return (
            "DatasourceServicePrincipal(id={}, credential_type={}, name={}, "
            "client_id={}, client_secret={}, tenant_id={}, description={})".format(
                self.id,
                self.credential_type,
                self.name,
                self.client_id,
                self.client_secret,
                self.tenant_id,
                self.description,
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, source):
        return cls(
            name=source.data_source_credential_name,
            client_id=source.parameters.client_id,
            client_secret=source.parameters.client_secret,
            tenant_id=source.parameters.tenant_id,
            id=source.data_source_credential_id,
            description=source.data_source_credential_description,
        )

    def _to_generated(self):
        param = _ServicePrincipalParam(
            client_id=self.client_id,
            client_secret=self.client_secret,
            tenant_id=self.tenant_id,
        )
        return _ServicePrincipalCredential(
            data_source_credential_type=self.credential_type,
            data_source_credential_name=self.name,
            data_source_credential_description=self.description,
            parameters=param,
        )

    def _to_generated_patch(self):
        param_patch = _ServicePrincipalParamPatch(
            client_id=self.client_id,
            client_secret=self.client_secret,
            tenant_id=self.tenant_id,
        )
        return _ServicePrincipalCredentialPatch(
            data_source_credential_type=self.credential_type,
            data_source_credential_name=self.name,
            data_source_credential_description=self.description,
            parameters=param_patch,
        )


class DatasourceServicePrincipalInKeyVault(DatasourceCredential):
    """DatasourceServicePrincipalInKeyVault.

    All required parameters must be populated in order to send to Azure.

    :ivar credential_type: Required. Type of data source credential.Constant filled by
     server.  Possible values include: "AzureSQLConnectionString", "DataLakeGen2SharedKey",
     "ServicePrincipal", "ServicePrincipalInKV".
    :type credential_type: str or
     ~azure.ai.metricsadvisor.models.DatasourceCredentialType
    :ivar id: Unique id of data source credential.
    :vartype id: str
    :param name: Required. Name of data source credential.
    :type name: str
    :keyword str description: Description of data source credential.
    :keyword str key_vault_endpoint: Required. The Key Vault endpoint that storing the service principal.
    :keyword str key_vault_client_id: Required. The Client Id to access the Key Vault.
    :keyword str key_vault_client_secret: Required. The Client Secret to access the Key Vault.
    :keyword str service_principal_id_name_in_kv: Required. The secret name of the service principal's
     client Id in the Key Vault.
    :keyword str service_principal_secret_name_in_kv: Required. The secret name of the service
     principal's client secret in the Key Vault.
    :keyword str tenant_id: Required. The tenant id of your service principal.
    """

    _attribute_map = {
        "credential_type": {"key": "credentialType", "type": "str"},
        "id": {"key": "id", "type": "str"},
        "name": {"key": "name", "type": "str"},
        "description": {"key": "description", "type": "str"},
        "key_vault_endpoint": {"key": "keyVaultEndpoint", "type": "str"},
        "key_vault_client_id": {"key": "keyVaultClientId", "type": "str"},
        "key_vault_client_secret": {"key": "keyVaultClientSecret", "type": "str"},
        "service_principal_id_name_in_kv": {
            "key": "servicePrincipalIdNameInKV",
            "type": "str",
        },
        "service_principal_secret_name_in_kv": {
            "key": "servicePrincipalSecretNameInKV",
            "type": "str",
        },
        "tenant_id": {"key": "tenantId", "type": "str"},
    }

    def __init__(self, name, **kwargs):
        # type: (str, Any) -> None
        if "key_vault_endpoint" not in kwargs:
            raise ValueError("key_vault_endpoint is required.")
        if "key_vault_client_id" not in kwargs:
            raise ValueError("key_vault_client_id is required.")
        if "key_vault_client_secret" not in kwargs:
            raise ValueError("key_vault_client_secret is required.")
        if "service_principal_id_name_in_kv" not in kwargs:
            raise ValueError("service_principal_id_name_in_kv is required.")
        if "service_principal_secret_name_in_kv" not in kwargs:
            raise ValueError("service_principal_secret_name_in_kv is required.")
        if "tenant_id" not in kwargs:
            raise ValueError("tenant_id is required.")
        super(DatasourceServicePrincipalInKeyVault, self).__init__(
            name=name, credential_type="ServicePrincipalInKV", **kwargs
        )
        self.key_vault_endpoint = kwargs["key_vault_endpoint"]
        self.key_vault_client_id = kwargs["key_vault_client_id"]
        self.key_vault_client_secret = kwargs["key_vault_client_secret"]
        self.service_principal_id_name_in_kv = kwargs["service_principal_id_name_in_kv"]
        self.service_principal_secret_name_in_kv = kwargs[
            "service_principal_secret_name_in_kv"
        ]
        self.tenant_id = kwargs["tenant_id"]

    def __repr__(self):
        return (
            "DatasourceServicePrincipalInKeyVault(id={}, credential_type={}, name={}, "
            "key_vault_endpoint={}, key_vault_client_id={}, key_vault_client_secret={}, "
            "service_principal_id_name_in_kv={}, service_principal_secret_name_in_kv={}, tenant_id={}, "
            "description={})".format(
                self.id,
                self.credential_type,
                self.name,
                self.key_vault_endpoint,
                self.key_vault_client_id,
                self.key_vault_client_secret,
                self.service_principal_id_name_in_kv,
                self.service_principal_secret_name_in_kv,
                self.tenant_id,
                self.description,
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, source):
        return cls(
            name=source.data_source_credential_name,
            key_vault_endpoint=source.parameters.key_vault_endpoint,
            key_vault_client_id=source.parameters.key_vault_client_id,
            key_vault_client_secret=source.parameters.key_vault_client_secret,
            service_principal_id_name_in_kv=source.parameters.service_principal_id_name_in_kv,
            service_principal_secret_name_in_kv=source.parameters.service_principal_secret_name_in_kv,
            tenant_id=source.parameters.tenant_id,
            id=source.data_source_credential_id,
            description=source.data_source_credential_description,
        )

    def _to_generated(self):
        param = _ServicePrincipalInKVParam(
            key_vault_endpoint=self.key_vault_endpoint,
            key_vault_client_id=self.key_vault_client_id,
            key_vault_client_secret=self.key_vault_client_secret,
            service_principal_id_name_in_kv=self.service_principal_id_name_in_kv,
            service_principal_secret_name_in_kv=self.service_principal_secret_name_in_kv,
            tenant_id=self.tenant_id,
        )
        return _ServicePrincipalInKVCredential(
            data_source_credential_type=self.credential_type,
            data_source_credential_name=self.name,
            data_source_credential_description=self.description,
            parameters=param,
        )

    def _to_generated_patch(self):
        param_patch = _ServicePrincipalInKVParamPatch(
            key_vault_endpoint=self.key_vault_endpoint,
            key_vault_client_id=self.key_vault_client_id,
            key_vault_client_secret=self.key_vault_client_secret,
            service_principal_id_name_in_kv=self.service_principal_id_name_in_kv,
            service_principal_secret_name_in_kv=self.service_principal_secret_name_in_kv,
            tenant_id=self.tenant_id,
        )
        return _ServicePrincipalInKVCredentialPatch(
            data_source_credential_type=self.credential_type,
            data_source_credential_name=self.name,
            data_source_credential_description=self.description,
            parameters=param_patch,
        )


class DetectionAnomalyFilterCondition(msrest.serialization.Model):
    """DetectionAnomalyFilterCondition.

    :param series_group_key: dimension filter.
    :type series_group_key: dict[str, str]
    :param severity_filter:
    :type severity_filter: ~azure.ai.metricsadvisor.models.SeverityFilterCondition
    """

    _attribute_map = {
        "series_group_key": {"key": "seriesGroupKey", "type": "{str}"},
        "severity_filter": {"key": "severityFilter", "type": "SeverityFilterCondition"},
    }

    def __init__(self, **kwargs):
        super(DetectionAnomalyFilterCondition, self).__init__(**kwargs)
        self.series_group_key = kwargs.get("series_group_key", None)
        self.severity_filter = kwargs.get("severity_filter", None)

    @classmethod
    def _from_generated(cls, source):
        series_group_key = (
            source.dimension_filter.dimension if source.dimension_filter else None
        )
        return cls(
            series_group_key=series_group_key,
            severity_filter=source.severity_filter.key_vault_endpoint,
        )

    def _to_generated(self):
        dimension_filter = _DimensionGroupIdentity(dimension=self.series_group_key)
        return _DetectionAnomalyFilterCondition(
            dimension_filter=dimension_filter, severity_filter=self.severity_filter
        )

################# ADDED GENERATED MODELS ########################

class AnomalySeverity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """min alert severity
    """

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class DatasourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """data source type
    """

    AZURE_APPLICATION_INSIGHTS = "AzureApplicationInsights"
    AZURE_BLOB = "AzureBlob"
    AZURE_COSMOS_DB = "AzureCosmosDB"
    AZURE_DATA_EXPLORER = "AzureDataExplorer"
    AZURE_DATA_LAKE_STORAGE_GEN2 = "AzureDataLakeStorageGen2"
    AZURE_EVENT_HUBS = "AzureEventHubs"
    AZURE_LOG_ANALYTICS = "AzureLogAnalytics"
    AZURE_TABLE = "AzureTable"
    INFLUX_DB = "InfluxDB"
    MONGO_DB = "MongoDB"
    MY_SQL = "MySql"
    POSTGRE_SQL = "PostgreSql"
    SQL_SERVER = "SqlServer"

class DataFeedAccessMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """data feed access mode, default is Private
    """

    PRIVATE = "Private"
    PUBLIC = "Public"

class DataFeedAutoRollupMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """roll up method
    """

    NONE = "None"
    SUM = "Sum"
    MAX = "Max"
    MIN = "Min"
    AVG = "Avg"
    COUNT = "Count"

class DatasourceMissingDataPointFillType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """the type of fill missing point for anomaly detection
    """

    SMART_FILLING = "SmartFilling"
    PREVIOUS_VALUE = "PreviousValue"
    CUSTOM_VALUE = "CustomValue"
    NO_FILLING = "NoFilling"

class AnomalyIncidentStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """incident status

    only return for alerting incident result
    """

    ACTIVE = "Active"
    RESOLVED = "Resolved"

class DataFeedGranularityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """granularity of the time series
    """

    YEARLY = "Yearly"
    MONTHLY = "Monthly"
    WEEKLY = "Weekly"
    DAILY = "Daily"
    HOURLY = "Hourly"
    MINUTELY = "Minutely"
    CUSTOM = "Custom"

class DataFeedStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """data feed status
    """

    ACTIVE = "Active"
    PAUSED = "Paused"

class AlertQueryTimeMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """time mode
    """

    ANOMALY_TIME = "AnomalyTime"
    CREATED_TIME = "CreatedTime"
    MODIFIED_TIME = "ModifiedTime"

class DatasourceCredentialType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of data source credential
    """

    AZURE_SQL_CONNECTION_STRING = "AzureSQLConnectionString"
    DATA_LAKE_GEN2_SHARED_KEY = "DataLakeGen2SharedKey"
    SERVICE_PRINCIPAL = "ServicePrincipal"
    SERVICE_PRINCIPAL_IN_KV = "ServicePrincipalInKV"

class DatasourceAuthenticationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """authentication type for corresponding data source
    """

    BASIC = "Basic"
    MANAGED_IDENTITY = "ManagedIdentity"
    AZURE_SQL_CONNECTION_STRING = "AzureSQLConnectionString"
    DATA_LAKE_GEN2_SHARED_KEY = "DataLakeGen2SharedKey"
    SERVICE_PRINCIPAL = "ServicePrincipal"
    SERVICE_PRINCIPAL_IN_KV = "ServicePrincipalInKV"

class MetricSeriesDefinition(generated_models.MetricSeriesItem):
    ...

class DataFeedIngestionStatus(generated_models.IngestionStatus):
    ...
