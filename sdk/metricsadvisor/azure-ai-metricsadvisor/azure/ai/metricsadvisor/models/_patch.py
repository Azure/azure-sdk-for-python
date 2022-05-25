# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint:disable=protected-access
# pylint:disable=too-many-lines
import datetime
from typing import Any, Tuple, Union, List, Dict, Optional, TYPE_CHECKING
from enum import Enum
import msrest
from azure.core import CaseInsensitiveEnumMeta
from . import _models as generated_models
from . import _enums as generated_enums

if TYPE_CHECKING:
    from .._operations._patch import DataFeedSourceUnion


def get_auth_from_datasource_kwargs(
    *, default_authentication_type: str, check_msi_kwarg: bool = True, **kwargs
) -> Tuple[str, Optional[bool]]:
    msi = False
    if check_msi_kwarg:
        msi = kwargs.pop("msi", False)
    datasource_service_principal_id = kwargs.get("datasource_service_principal_id", False)
    datasource_service_principal_in_kv_id = kwargs.get("datasource_service_principal_in_kv_id", False)
    credential_id: Optional[bool] = None
    if msi:
        authentication_type = "ManagedIdentity"
    elif datasource_service_principal_id:
        authentication_type = "ServicePrincipal"
        credential_id = datasource_service_principal_id
    elif datasource_service_principal_in_kv_id:
        authentication_type = "ServicePrincipalInKV"
        credential_id = datasource_service_principal_in_kv_id
    else:
        authentication_type = default_authentication_type
    return authentication_type, credential_id


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


class DataFeedGranularity:
    """Data feed granularity

    :param granularity_type: Granularity of the time series. Possible values include:
        "Yearly", "Monthly", "Weekly", "Daily", "Hourly", "Minutely", "Secondly", "Custom".
    :type granularity_type: str or ~azure.ai.metricsadvisor.models.DataFeedGranularityType
    :keyword int custom_granularity_value: Must be populated if granularity_type is "Custom".
    """

    def __init__(self, granularity_type: Union[str, generated_enums.DataFeedGranularityType], **kwargs: Any) -> None:
        self.granularity_type = granularity_type
        self.custom_granularity_value = kwargs.get("custom_granularity_value", None)

    def __repr__(self):
        return "DataFeedGranularity(granularity_type={}, custom_granularity_value={})".format(
            self.granularity_type, self.custom_granularity_value
        )[:1024]

    @classmethod
    def _from_generated(cls, granularity_name, granularity_amount):
        return cls(
            granularity_type=granularity_name,
            custom_granularity_value=granularity_amount,
        )


class DataFeedIngestionSettings:
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

    def __init__(self, ingestion_begin_time: datetime.datetime, **kwargs: Any) -> None:
        self.ingestion_begin_time = ingestion_begin_time
        self.ingestion_start_offset = kwargs.get("ingestion_start_offset", 0)
        self.data_source_request_concurrency = kwargs.get("data_source_request_concurrency", -1)
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
            )[:1024]
        )


class DataFeedMissingDataPointFillSettings:
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
        )[:1024]


class DataFeedRollupSettings:
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
        self.rollup_identification_value = kwargs.get("rollup_identification_value", None)
        self.rollup_type = kwargs.get("rollup_type", "AutoRollup")
        self.auto_rollup_group_by_column_names = kwargs.get("auto_rollup_group_by_column_names", None)
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


class DataFeedSchema:
    """Data feed schema

    :param metrics: List of metrics.
    :type metrics: list[~azure.ai.metricsadvisor.models.DataFeedMetric]
    :keyword dimensions: List of dimension.
    :paramtype dimensions: list[~azure.ai.metricsadvisor.models.DataFeedDimension]
    :keyword str timestamp_column: User-defined timestamp column.
        If timestamp_column is None, start time of every time slice will be used as default value.
    """

    def __init__(self, metrics: List["DataFeedMetric"], **kwargs: Any) -> None:
        self.metrics = metrics
        self.dimensions = kwargs.get("dimensions", None)
        self.timestamp_column = kwargs.get("timestamp_column", None)

    def __repr__(self):
        return "DataFeedSchema(metrics={}, dimensions={}, timestamp_column={})".format(
            repr(self.metrics),
            repr(self.dimensions),
            self.timestamp_column,
        )[:1024]


class DataFeed(generated_models.DataFeed):  # pylint:disable=too-many-instance-attributes
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

    def __init__(  # pylint: disable=super-init-not-called
        self,
        name: str,
        source: "DataFeedSourceUnion",
        granularity: DataFeedGranularity,
        schema: DataFeedSchema,
        ingestion_settings: DataFeedIngestionSettings,
        **kwargs: Any
    ) -> None:
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
        self.missing_data_point_fill_settings = kwargs.get("missing_data_point_fill_settings", None)
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
            )[:1024]
        )

    @classmethod
    def _from_generated(cls, data_feed, data_source_parameter, data_source_type):
        return cls(
            created_time=data_feed.created_time,
            granularity=DataFeedGranularity._from_generated(data_feed.granularity_name, data_feed.granularity_amount),
            id=data_feed.id,
            ingestion_settings=DataFeedIngestionSettings(
                ingestion_begin_time=data_feed.data_start_from,
                data_source_request_concurrency=data_feed.max_concurrency,
                ingestion_retry_delay=data_feed.min_retry_interval_in_seconds,
                ingestion_start_offset=data_feed.start_offset_in_seconds,
                stop_retry_after=data_feed.stop_retry_after_in_seconds,
            ),
            is_admin=data_feed.is_admin,
            metric_ids={metric.name: metric.id for metric in data_feed.metrics},
            name=data_feed.name,
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
            access_mode=data_feed.access_mode,
            action_link_template=data_feed.action_link_template,
            schema=DataFeedSchema(
                dimensions=data_feed.dimension,
                metrics=data_feed.metrics,
                timestamp_column=data_feed.timestamp_column,
            ),
            source=TYPE_TO_DATA_SOURCE[data_source_type].deserialize(data_source_parameter),
            status=data_feed.status,
        )

    def _to_generated(self, **kwargs) -> generated_models.DataFeed:
        rollup_type = kwargs.pop("needRollup", None)
        if rollup_type:
            DataFeedRollupType._to_generated(rollup_type)
        retval = generated_models.DataFeed(
            data_source_parameter=kwargs.pop(
                "dataSourceParameter",
                TYPE_TO_DATA_SOURCE[self.source.data_source_type].serialize(self.source),  # type: ignore
            ),
            id=kwargs.pop("id", self.id),
            name=kwargs.pop("dataFeedName", None) or self.name,
            data_feed_description=kwargs.pop("dataFeedDescription", self.data_feed_description),
            granularity_name=kwargs.pop("granularityName", self.granularity.granularity_type),
            granularity_amount=kwargs.pop("granularityAmount", self.granularity.custom_granularity_value),
            metrics=kwargs.pop("metrics", self.schema.metrics),
            dimension=kwargs.pop("dimension", self.schema.dimensions),
            timestamp_column=kwargs.pop("timestampColumn", self.schema.timestamp_column),
            data_start_from=kwargs.pop("dataStartFrom", self.ingestion_settings.ingestion_begin_time),
            start_offset_in_seconds=kwargs.pop("startOffsetInSeconds", self.ingestion_settings.ingestion_start_offset),
            max_concurrency=kwargs.pop("maxConcurrency", self.ingestion_settings.data_source_request_concurrency),
            min_retry_interval_in_seconds=kwargs.pop(
                "minRetryIntervalInSeconds", self.ingestion_settings.ingestion_retry_delay
            ),
            stop_retry_after_in_seconds=kwargs.pop("stopRetryAfterInSeconds", self.ingestion_settings.stop_retry_after),
            need_rollup=rollup_type or self.rollup_settings.rollup_type if self.rollup_settings else None,
            roll_up_method=kwargs.pop("rollUpMethod", None) or self.rollup_settings.rollup_method
            if self.rollup_settings
            else None,
            roll_up_columns=kwargs.pop("rollUpColumns", None) or self.rollup_settings.auto_rollup_group_by_column_names
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
            access_mode=kwargs.pop("viewMode", self.access_mode),
            admins=kwargs.pop("admins", self.admins),
            viewers=kwargs.pop("viewers", self.viewers),
            is_admin=kwargs.pop("isAdmin", self.is_admin),
            status=kwargs.pop("status", self.status),
            created_time=kwargs.pop("createdTime", self.created_time),
            action_link_template=kwargs.pop("actionLinkTemplate", self.action_link_template),
            authentication_type=kwargs.pop("authenticationType", self.source.authentication_type),  # type: ignore
            credential_id=kwargs.pop("credentialId", self.source.credential_id),  # type: ignore
        )
        retval.data_source_type = self.source.data_source_type  # type: ignore
        return retval


class MetricAnomalyAlertScope:
    """MetricAnomalyAlertScope

    :param scope_type: Required. Anomaly scope. Possible values include: "WholeSeries",
     "SeriesGroup", "TopN".
    :type scope_type: str or ~azure.ai.metricsadvisor.models.MetricAnomalyAlertScopeType
    :keyword series_group_in_scope: Dimension specified for series group.
    :paramtype series_group_in_scope: dict[str, str]
    :keyword top_n_group_in_scope:
    :paramtype top_n_group_in_scope: ~azure.ai.metricsadvisor.models.TopNGroupScope
    """

    def __init__(self, scope_type: Union[str, "MetricAnomalyAlertScopeType"], **kwargs: Any) -> None:
        self.scope_type = scope_type
        self.series_group_in_scope = kwargs.get("series_group_in_scope", None)
        self.top_n_group_in_scope = kwargs.get("top_n_group_in_scope", None)

    def __repr__(self):
        return "MetricAnomalyAlertScope(scope_type={}, series_group_in_scope={}, top_n_group_in_scope={})".format(
            self.scope_type, self.series_group_in_scope, repr(self.top_n_group_in_scope)
        )[:1024]

    @classmethod
    def _from_generated(cls, config):
        return cls(
            scope_type=MetricAnomalyAlertScopeType._from_generated(config.anomaly_scope_type),
            series_group_in_scope=config.dimension_anomaly_scope.dimension if config.dimension_anomaly_scope else None,
            top_n_group_in_scope=TopNGroupScope(
                top=config.top_n_anomaly_scope.top,
                period=config.top_n_anomaly_scope.period,
                min_top_count=config.top_n_anomaly_scope.min_top_count,
            )
            if config.top_n_anomaly_scope
            else None,
        )


class TopNGroupScope(generated_models.TopNGroupScope):
    """TopNGroupScope.

    :param top: Required. top N, value range : [1, +∞).
    :type top: int
    :param period: Required. point count used to look back, value range : [1, +∞).
    :type period: int
    :param min_top_count: Required. min count should be in top N, value range : [1, +∞)
        should be less than or equal to period.
    :type min_top_count: int
    """

    def __init__(self, top: int, period: int, min_top_count: int, **kwargs: Any):
        super().__init__(top=top, period=period, min_top_count=min_top_count, **kwargs)

    def __repr__(self):
        return "TopNGroupScope(top={}, period={}, min_top_count={})".format(self.top, self.period, self.min_top_count)[
            :1024
        ]


class SeverityCondition(generated_models.SeverityCondition):
    """SeverityCondition.

    :param min_alert_severity: Required. min alert severity. Possible values include: "Low",
     "Medium", "High".
    :type min_alert_severity: str or ~azure.ai.metricsadvisor.models.AnomalySeverity
    :param max_alert_severity: Required. max alert severity. Possible values include: "Low",
     "Medium", "High".
    :type max_alert_severity: str or ~azure.ai.metricsadvisor.models.AnomalySeverity
    """

    def __init__(
        self,
        min_alert_severity: Union[str, "generated_enums.AnomalySeverity"],
        max_alert_severity: Union[str, "generated_enums.AnomalySeverity"],
        **kwargs: Any
    ) -> None:
        super().__init__(min_alert_severity=min_alert_severity, max_alert_severity=max_alert_severity)

    def __repr__(self):
        return "SeverityCondition(min_alert_severity={}, max_alert_severity={})".format(
            self.min_alert_severity, self.max_alert_severity
        )[:1024]


class MetricAnomalyAlertSnoozeCondition(generated_models.MetricAnomalyAlertSnoozeCondition):
    """MetricAnomalyAlertSnoozeCondition.

    :param auto_snooze: Required. snooze point count, value range : [0, +∞).
    :type auto_snooze: int
    :param snooze_scope: Required. snooze scope. Possible values include: "Metric", "Series".
    :type snooze_scope: str or ~azure.ai.metricsadvisor.models.SnoozeScope
    :param only_for_successive: Required. only snooze for successive anomalies.
    :type only_for_successive: bool
    """

    def __init__(
        self,
        auto_snooze: int,
        snooze_scope: Union[str, "generated_enums.SnoozeScope"],
        only_for_successive: bool,
        **kwargs: Any
    ) -> None:
        super().__init__(
            auto_snooze=auto_snooze, snooze_scope=snooze_scope, only_for_successive=only_for_successive, **kwargs
        )

    def __repr__(self):
        return "MetricAnomalyAlertSnoozeCondition(auto_snooze={}, snooze_scope={}, only_for_successive={})".format(
            self.auto_snooze, self.snooze_scope, self.only_for_successive
        )[:1024]


class MetricAnomalyAlertConditions:
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
        )[:1024]

    @classmethod
    def _from_generated(cls, config: generated_models.MetricAlertConfiguration):
        return cls(
            metric_boundary_condition=config.value_filter,
            severity_condition=config.severity_filter,
        )


class MetricBoundaryCondition(generated_models.MetricBoundaryCondition):
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

    def __init__(self, direction: Union[str, "generated_enums.AnomalyDetectorDirection"], **kwargs: Any) -> None:
        super().__init__(direction=direction, **kwargs)

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


class MetricAlertConfiguration(generated_models.MetricAlertConfiguration):
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

    def __init__(  # pylint: disable=super-init-not-called
        self, detection_configuration_id: str, alert_scope: MetricAnomalyAlertScope, **kwargs: Any
    ) -> None:
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
    def _from_generated(cls, config: generated_models.MetricAlertConfiguration):
        return cls(
            detection_configuration_id=config.detection_configuration_id,
            alert_scope=MetricAnomalyAlertScope._from_generated(config),
            negation_operation=config.negation_operation,
            alert_snooze_condition=config.alert_snooze_condition,
            alert_conditions=MetricAnomalyAlertConditions._from_generated(config),
        )

    def _to_generated(self) -> generated_models.MetricAlertConfiguration:
        return generated_models.MetricAlertConfiguration(
            detection_configuration_id=self.detection_configuration_id,
            anomaly_scope_type=MetricAnomalyAlertScopeType._to_generated(self.alert_scope.scope_type),
            dimension_anomaly_scope=generated_models.DimensionGroupIdentity(
                dimension=self.alert_scope.series_group_in_scope
            )
            if self.alert_scope.series_group_in_scope
            else None,
            top_n_anomaly_scope=self.alert_scope.top_n_group_in_scope,
            negation_operation=self.negation_operation,
            severity_filter=self.alert_conditions.severity_condition if self.alert_conditions else None,
            alert_snooze_condition=self.alert_snooze_condition,
            value_filter=self.alert_conditions.metric_boundary_condition if self.alert_conditions else None,
        )


class AnomalyAlertConfiguration(generated_models.AnomalyAlertConfiguration):
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

    def __init__(
        self, name: str, metric_alert_configurations: List[MetricAlertConfiguration], hook_ids: List[str], **kwargs: Any
    ) -> None:
        super().__init__(
            name=name, hook_ids=hook_ids, metric_alert_configurations=metric_alert_configurations, **kwargs
        )

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
    def _from_generated(cls, config: generated_models.AnomalyAlertConfiguration):
        return cls(
            id=config.id,
            name=config.name,
            description=config.description,
            cross_metrics_operator=config.cross_metrics_operator,
            hook_ids=config.hook_ids,
            metric_alert_configurations=[
                MetricAlertConfiguration._from_generated(c) for c in config.metric_alert_configurations
            ],
            dimensions_to_split_alert=config.dimensions_to_split_alert,
        )

    def _to_generated(self, **kwargs):
        metric_alert_configurations = kwargs.pop("metricAlertingConfigurations", self.metric_alert_configurations)
        return generated_models.AnomalyAlertConfiguration(
            name=kwargs.pop("name", self.name),
            metric_alert_configurations=[
                config._to_generated() for config in metric_alert_configurations
            ],  # type: ignore
            hook_ids=kwargs.pop("hookIds", self.hook_ids),
            cross_metrics_operator=kwargs.pop("crossMetricsOperator", self.cross_metrics_operator),
            description=kwargs.pop("description", self.description),
            dimensions_to_split_alert=self.dimensions_to_split_alert,
        )


class AnomalyDetectionConfiguration(generated_models.AnomalyDetectionConfiguration):
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

    def __init__(
        self, name: str, metric_id: str, whole_series_detection_condition: "MetricDetectionCondition", **kwargs: Any
    ) -> None:
        super().__init__(
            name=name, metric_id=metric_id, whole_series_detection_condition=whole_series_detection_condition, **kwargs
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

    def __init__(self, data_source_type: str, **kwargs: Any) -> None:
        super().__init__(data_source_type=data_source_type, **kwargs)  # type: ignore
        self.data_source_type = data_source_type
        self.authentication_type = kwargs.get("authentication_type", None)
        self.credential_id = kwargs.get("credential_id", None)


class AzureApplicationInsightsDataFeedSource(generated_models.AzureApplicationInsightsDataFeedSource, DataFeedSource):
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

    def __init__(self, query: str, **kwargs: Any) -> None:
        super().__init__(
            query=query, data_source_type="AzureApplicationInsights", authentication_type="Basic", **kwargs
        )
        self.data_source_type = "AzureApplicationInsights"
        self.authentication_type = "Basic"
        self.credential_id = kwargs.get("credential_id", None)

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


class AzureBlobDataFeedSource(generated_models.AzureBlobDataFeedSource, dict):
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

    def __init__(self, container: str, blob_template: str, **kwargs: Any) -> None:
        msi = kwargs.get("msi", False)
        super().__init__(container=container, blob_template=blob_template, **kwargs)
        self.data_source_type = "AzureBlob"
        self.authentication_type = "ManagedIdentity" if msi else "Basic"
        self.credential_id = kwargs.get("credential_id", None)

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


class AzureCosmosDbDataFeedSource(generated_models.AzureCosmosDbDataFeedSource, dict):
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

    def __init__(self, sql_query: str, database: str, collection_id: str, **kwargs: Any) -> None:
        super().__init__(sql_query=sql_query, database=database, collection_id=collection_id, **kwargs)
        self.data_source_type = "AzureCosmosDB"
        self.authentication_type = "Basic"
        self.credential_id = kwargs.get("credential_id", None)

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


class AzureDataExplorerDataFeedSource(generated_models.AzureDataExplorerDataFeedSource, dict):
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

    def __init__(self, query: str, **kwargs: Any) -> None:
        super().__init__(query=query, **kwargs)
        authentication_type, credential_id = get_auth_from_datasource_kwargs(
            default_authentication_type="Basic", **kwargs
        )
        self.data_source_type = "AzureDataExplorer"
        self.authentication_type = authentication_type
        self.credential_id = credential_id

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


class AzureTableDataFeedSource(generated_models.AzureTableDataFeedSource, dict):
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

    def __init__(self, query: str, table: str, **kwargs: Any) -> None:
        super().__init__(query=query, table=table, **kwargs)
        self.data_source_type = "AzureTable"
        self.authentication_type = "Basic"
        self.credential_id = kwargs.get("credential_id", None)

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


class AzureEventHubsDataFeedSource(generated_models.AzureEventHubsDataFeedSource, dict):
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

    def __init__(self, consumer_group: str, **kwargs: Any) -> None:
        super().__init__(consumer_group=consumer_group, **kwargs)
        self.data_source_type = "AzureEventHubs"
        self.authentication_type = "Basic"
        self.credential_id = kwargs.get("credential_id", None)

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


class InfluxDbDataFeedSource(generated_models.InfluxDbDataFeedSource, dict):
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

    def __init__(self, query: str, **kwargs: Any) -> None:
        super().__init__(query=query, **kwargs)
        self.data_source_type = "InfluxDB"
        self.authentication_type = "Basic"
        self.credential_id = kwargs.get("credential_id", None)

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


class MySqlDataFeedSource(generated_models.AzureDataExplorerDataFeedSource, dict):
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

    def __init__(self, query: str, **kwargs: Any) -> None:
        super().__init__(query=query, **kwargs)
        self.data_source_type = "MySql"
        self.authentication_type = "Basic"
        self.credential_id = kwargs.get("credential_id", None)

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


class PostgreSqlDataFeedSource(generated_models.AzureDataExplorerDataFeedSource, dict):
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

    def __init__(self, query: str, **kwargs: Any) -> None:
        super().__init__(query=query, **kwargs)
        self.data_source_type = "PostgreSql"
        self.authentication_type = "Basic"
        self.credential_id = kwargs.get("credential_id", None)

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


class SqlServerDataFeedSource(generated_models.AzureDataExplorerDataFeedSource, dict):
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

    def __init__(self, query: str, **kwargs: Any) -> None:
        super().__init__(query=query, **kwargs)
        datasource_sql_connection_string_id = kwargs.get("datasource_sql_connection_string_id", False)
        authentication_type, credential_id = get_auth_from_datasource_kwargs(
            default_authentication_type="AzureSQLConnectionString" if datasource_sql_connection_string_id else "Basic"
        )
        if credential_id is None and datasource_sql_connection_string_id:
            credential_id = datasource_sql_connection_string_id
        self.data_source_type = "SqlServer"
        self.authentication_type = authentication_type
        self.credential_id = credential_id

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


class AzureDataLakeStorageGen2DataFeedSource(generated_models.AzureDataLakeStorageGen2DataFeedSource, dict):
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

    def __init__(self, file_system_name: str, directory_template: str, file_template: str, **kwargs: Any) -> None:
        super().__init__(
            file_system_name=file_system_name,
            directory_template=directory_template,
            file_template=file_template,
            **kwargs
        )
        datasource_datalake_gen2_shared_key_id = kwargs.get("datasource_datalake_gen2_shared_key_id", False)
        authentication_type, credential_id = get_auth_from_datasource_kwargs(
            default_authentication_type="DataLakeGen2SharedKey" if datasource_datalake_gen2_shared_key_id else "Basic",
        )
        if credential_id is None and datasource_datalake_gen2_shared_key_id:
            credential_id = datasource_datalake_gen2_shared_key_id
        self.data_source_type = "AzureDataLakeStorageGen2"
        self.authentication_type = authentication_type
        self.credential_id = credential_id

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


class AzureLogAnalyticsDataFeedSource(generated_models.AzureLogAnalyticsDataFeedSource, dict):
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

    def __init__(self, workspace_id: str, query: str, **kwargs: Any) -> None:
        authentication_type, credential_id = get_auth_from_datasource_kwargs(
            default_authentication_type="Basic",
            check_msi_kwarg=False,
        )
        tenant_id = None
        client_id = None
        client_secret = None
        if authentication_type == "Basic":
            tenant_id = kwargs.get("tenant_id", None)
            client_id = kwargs.get("client_id", None)
            client_secret = kwargs.get("client_secret", None)
        super().__init__(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
            workspace_id=workspace_id,
            query=query,
            **kwargs
        )
        self.data_source_type = "AzureLogAnalytics"
        self.authentication_type = authentication_type
        self.credential_id = credential_id

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
            )[:1024]
        )


class MongoDbDataFeedSource(generated_models.MongoDbDataFeedSource, dict):
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

    def __init__(self, command: str, **kwargs: Any) -> None:
        super().__init__(command=command, **kwargs)
        self.data_source_type = "MongoDB"
        self.authentication_type = "Basic"
        self.credential_id = kwargs.get("credential_id", None)

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


class NotificationHook(generated_models.NotificationHook):
    """NotificationHook.

    :param str name: Hook unique name.
    :ivar str description: Hook description.
    :ivar str external_link: Hook external link.
    :ivar list[str] admins: Hook administrators.
    :ivar str hook_type: Constant filled by server. Possible values include:
        "Webhook", "Email".
    :ivar str id: Hook unique id.
    """

    _subtype_map = {"hook_type": {"Email": "EmailNotificationHook", "Webhook": "WebNotificationHook"}}

    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)

    def __repr__(self):
        return "NotificationHook(id={}, name={}, description={}, external_link={}, admins={}, " "hook_type={})".format(
            self.id,
            self.name,
            self.description,
            self.external_link,
            self.admins,
            self.hook_type,
        )[:1024]


class EmailNotificationHook(NotificationHook, generated_models.EmailNotificationHook):
    """EmailNotificationHook.

    :param str name: Hook unique name.
    :param list[str] emails_to_alert: Required. Email TO: list.
    :keyword str description: Hook description.
    :keyword str external_link: Hook external link.
    :ivar list[str] admins: Hook administrators.
    :ivar str hook_type: Constant filled by server - "Email".
    :ivar str id: Hook unique id.
    """

    def __init__(self, name: str, emails_to_alert: List[str], **kwargs: Any) -> None:
        super().__init__(name, emails_to_alert=emails_to_alert, **kwargs)

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


class WebNotificationHook(NotificationHook, generated_models.WebNotificationHook):
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

    def __init__(self, name: str, endpoint: str, **kwargs: Any) -> None:
        super().__init__(name, endpoint=endpoint, **kwargs)

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
            )[:1024]
        )


class MetricDetectionCondition(generated_models.MetricDetectionCondition):
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


class ChangeThresholdCondition(generated_models.ChangeThresholdCondition):
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
        change_percentage: float,
        shift_point: int,
        within_range: bool,
        anomaly_detector_direction: Union[str, "generated_enums.AnomalyDetectorDirection"],
        suppress_condition: "SuppressCondition",
        **kwargs: Any
    ) -> None:
        super().__init__(
            change_percentage=change_percentage,
            shift_point=shift_point,
            within_range=within_range,
            anomaly_detector_direction=anomaly_detector_direction,
            suppress_condition=suppress_condition,
            **kwargs
        )

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


class SuppressCondition(generated_models.SuppressCondition):
    """SuppressCondition.

    :param min_number: Required. min point number, value range : [1, +∞).
    :type min_number: int
    :param min_ratio: Required. min point ratio, value range : (0, 100].
    :type min_ratio: float
    """

    def __init__(self, min_number: int, min_ratio: float, **kwargs: Any) -> None:
        super().__init__(min_number=min_number, min_ratio=min_ratio, **kwargs)

    def __repr__(self):
        return "SuppressCondition(min_number={}, min_ratio={})".format(self.min_number, self.min_ratio)[:1024]


class SmartDetectionCondition(generated_models.SmartDetectionCondition):
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
        self,
        sensitivity: float,
        anomaly_detector_direction: Union[str, "generated_enums.AnomalyDetectorDirection"],
        suppress_condition: "SuppressCondition",
        **kwargs: Any
    ) -> None:
        super().__init__(
            sensitivity=sensitivity,
            anomaly_detector_direction=anomaly_detector_direction,
            suppress_condition=suppress_condition,
            **kwargs
        )

    def __repr__(self):
        return "SmartDetectionCondition(sensitivity={}, anomaly_detector_direction={}, suppress_condition={})".format(
            self.sensitivity,
            self.anomaly_detector_direction,
            repr(self.suppress_condition),
        )[:1024]


class HardThresholdCondition(generated_models.HardThresholdCondition):
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

    def __init__(
        self,
        anomaly_detector_direction: Union[str, "generated_enums.AnomalyDetectorDirection"],
        suppress_condition: "SuppressCondition",
        **kwargs: Any
    ) -> None:
        super().__init__(
            anomaly_detector_direction=anomaly_detector_direction, suppress_condition=suppress_condition, **kwargs
        )

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


class MetricSeriesGroupDetectionCondition(
    generated_models.MetricSeriesGroupDetectionCondition, MetricDetectionCondition
):
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

    def __init__(self, series_group_key: Dict[str, str], **kwargs: Any) -> None:
        super().__init__(series_group_key=series_group_key, **kwargs)

    def __repr__(self):
        return (
            "MetricSeriesGroupDetectionCondition(condition_operator={}, smart_detection_condition={}, "
            "hard_threshold_condition={}, change_threshold_condition={}, series_group_key={})".format(
                self.condition_operator,
                repr(self.smart_detection_condition),
                repr(self.hard_threshold_condition),
                repr(self.change_threshold_condition),
                self.series_group_key,
            )[:1024]
        )


class MetricSingleSeriesDetectionCondition(
    generated_models.MetricSingleSeriesDetectionCondition, MetricDetectionCondition
):
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

    def __init__(self, series_key: Dict[str, str], **kwargs: Any) -> None:
        super().__init__(series_key=series_key, **kwargs)

    def __repr__(self):
        return (
            "MetricSingleSeriesDetectionCondition(condition_operator={}, smart_detection_condition={}, "
            "hard_threshold_condition={}, change_threshold_condition={}, series_key={})".format(
                self.condition_operator,
                repr(self.smart_detection_condition),
                repr(self.hard_threshold_condition),
                repr(self.change_threshold_condition),
                self.series_key,
            )[:1024]
        )


class DataFeedMetric(generated_models.DataFeedMetric):
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

    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__(name=name, **kwargs)

    def __repr__(self):
        return "DataFeedMetric(name={}, id={}, display_name={}, description={})".format(
            self.name, self.id, self.display_name, self.description
        )[:1024]


class DataFeedDimension(generated_models.DataFeedDimension):
    """DataFeedDimension.

    :param name: Required. dimension name.
    :type name: str
    :keyword display_name: dimension display name.
    :paramtype display_name: str
    """

    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__(name=name, **kwargs)

    def __repr__(self):
        return "DataFeedDimension(name={}, display_name={})".format(self.name, self.display_name)[:1024]


class DataFeedIngestionProgress(generated_models.DataFeedIngestionProgress):
    """DataFeedIngestionProgress.

    :ivar latest_success_timestamp: the timestamp of lastest success ingestion job.
     null indicates not available.
    :vartype latest_success_timestamp: ~datetime.datetime
    :ivar latest_active_timestamp: the timestamp of lastest ingestion job with status update.
     null indicates not available.
    :vartype latest_active_timestamp: ~datetime.datetime
    """

    def __repr__(self):
        return "DataFeedIngestionProgress(latest_success_timestamp={}, latest_active_timestamp={})".format(
            self.latest_success_timestamp, self.latest_active_timestamp
        )[:1024]


class MetricSeriesData(generated_models.MetricSeriesData):
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

    def __repr__(self):
        return "MetricSeriesData(metric_id={}, series_key={}, timestamps={}, values={})".format(
            self.metric_id, self.series_key, self.timestamps, self.values
        )[:1024]


class MetricEnrichedSeriesData(generated_models.MetricEnrichedSeriesData):
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


class AnomalyAlert(generated_models.AnomalyAlert):
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

    def __repr__(self):
        return "AnomalyAlert(id={}, timestamp={}, created_time={}, modified_time={})".format(
            self.id, self.timestamp, self.created_time, self.modified_time
        )[:1024]


TYPE_TO_DATA_SOURCE = {
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


class DataPointAnomaly(generated_models.DataPointAnomaly):
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


class AnomalyIncident(generated_models.AnomalyIncident):
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
        super().__init__(**kwargs)
        self.dimension_key = kwargs.get("dimension_key", None)
        self.path = kwargs.get("path", None)
        self.score = kwargs.get("score", None)
        self.description = kwargs.get("description", None)

    def __repr__(self):
        return "IncidentRootCause(dimension_key={}, path={}, score={}, description={})".format(
            self.dimension_key, self.path, self.score, self.description
        )[:1024]

    @classmethod
    def _from_generated(cls, root_cause: generated_models.IncidentRootCause) -> Union["IncidentRootCause", None]:
        if not root_cause:
            return None
        dimension_key = root_cause.root_cause.dimension if root_cause.root_cause else None
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
        "id": {"key": "feedbackId", "type": "str"},
        "created_time": {"key": "createdTime", "type": "iso-8601"},
        "user_principal": {"key": "userPrincipal", "type": "str"},
        "metric_id": {"key": "metricId", "type": "str"},
        "dimension_key": {"key": "dimensionFilter.dimension", "type": "{str}"},
    }

    def __init__(self, feedback_type, metric_id, dimension_key, **kwargs):
        super().__init__(**kwargs)
        self.feedback_type = feedback_type  # type: str
        self.id = None
        self.created_time = None
        self.user_principal = None
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

    _validation = {
        "feedback_type": {"required": True},
        "id": {"readonly": True},
        "created_time": {"readonly": True},
        "user_principal": {"readonly": True},
        "metric_id": {"required": True},
        "dimension_key": {"required": True},
        "start_time": {"required": True},
        "end_time": {"required": True},
        "value": {"required": True},
    }

    _attribute_map = {
        "feedback_type": {"key": "feedbackType", "type": "str"},
        "id": {"key": "feedbackId", "type": "str"},
        "created_time": {"key": "createdTime", "type": "iso-8601"},
        "user_principal": {"key": "userPrincipal", "type": "str"},
        "metric_id": {"key": "metricId", "type": "str"},
        "dimension_key": {"key": "dimensionFilter.dimension", "type": "{str}"},
        "start_time": {"key": "startTime", "type": "iso-8601"},
        "end_time": {"key": "endTime", "type": "iso-8601"},
        "anomaly_detection_configuration_id": {"key": "anomalyDetectionConfigurationId", "type": "str"},
        "anomaly_detection_configuration_snapshot": {
            "key": "anomalyDetectionConfigurationSnapshot",
            "type": "AnomalyDetectionConfiguration",
        },
        "value": {"key": "value.anomalyValue", "type": "str"},
    }

    def __init__(self, metric_id, dimension_key, start_time, end_time, value, **kwargs):
        super(AnomalyFeedback, self).__init__(
            feedback_type="Anomaly", metric_id=metric_id, dimension_key=dimension_key, **kwargs
        )
        self.start_time = start_time
        self.end_time = end_time
        self.value = value
        self.anomaly_detection_configuration_id = kwargs.get("anomaly_detection_configuration_id", None)
        self.anomaly_detection_configuration_snapshot = kwargs.get("anomaly_detection_configuration_snapshot", None)

    @classmethod
    def _from_generated(cls, anomaly_feedback: generated_models.AnomalyFeedback) -> Optional["AnomalyFeedback"]:
        if not anomaly_feedback:
            return None
        dimension_key = anomaly_feedback.dimension_key
        return cls(
            id=anomaly_feedback.id,
            created_time=anomaly_feedback.created_time,
            user_principal=anomaly_feedback.user_principal,
            metric_id=anomaly_feedback.metric_id,
            dimension_key=dimension_key,
            start_time=anomaly_feedback.start_time,
            end_time=anomaly_feedback.end_time,
            value=anomaly_feedback.value,
            anomaly_detection_configuration_id=anomaly_feedback.anomaly_detection_configuration_id,
            anomaly_detection_configuration_snapshot=anomaly_feedback.anomaly_detection_configuration_snapshot,
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

    _validation = {
        "feedback_type": {"required": True},
        "id": {"readonly": True},
        "created_time": {"readonly": True},
        "user_principal": {"readonly": True},
        "metric_id": {"required": True},
        "dimension_key": {"required": True},
        "start_time": {"required": True},
        "end_time": {"required": True},
        "value": {"required": True},
    }

    _attribute_map = {
        "feedback_type": {"key": "feedbackType", "type": "str"},
        "id": {"key": "feedbackId", "type": "str"},
        "created_time": {"key": "createdTime", "type": "iso-8601"},
        "user_principal": {"key": "userPrincipal", "type": "str"},
        "metric_id": {"key": "metricId", "type": "str"},
        "dimension_key": {"key": "dimensionFilter.dimension", "type": "{str}"},
        "start_time": {"key": "startTime", "type": "iso-8601"},
        "end_time": {"key": "endTime", "type": "iso-8601"},
        "value": {"key": "value.changePointValue", "type": "str"},
    }

    def __init__(self, metric_id, dimension_key, start_time, end_time, value, **kwargs):
        super(ChangePointFeedback, self).__init__(
            feedback_type="ChangePoint", metric_id=metric_id, dimension_key=dimension_key, **kwargs
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
    def _from_generated(
        cls, change_point_feedback: generated_models.ChangePointFeedback
    ) -> Optional["ChangePointFeedback"]:
        if not change_point_feedback:
            return None
        dimension_key = change_point_feedback.dimension_key
        return cls(
            id=change_point_feedback.id,
            created_time=change_point_feedback.created_time,
            user_principal=change_point_feedback.user_principal,
            metric_id=change_point_feedback.metric_id,
            dimension_key=dimension_key,
            start_time=change_point_feedback.start_time,
            end_time=change_point_feedback.end_time,
            value=change_point_feedback.value,
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

    _validation = {
        "feedback_type": {"required": True},
        "id": {"readonly": True},
        "created_time": {"readonly": True},
        "user_principal": {"readonly": True},
        "metric_id": {"required": True},
        "dimension_key": {"required": True},
        "value": {"required": True},
    }

    _attribute_map = {
        "feedback_type": {"key": "feedbackType", "type": "str"},
        "id": {"key": "feedbackId", "type": "str"},
        "created_time": {"key": "createdTime", "type": "iso-8601"},
        "user_principal": {"key": "userPrincipal", "type": "str"},
        "metric_id": {"key": "metricId", "type": "str"},
        "dimension_key": {"key": "dimensionFilter.dimension", "type": "{str}"},
        "start_time": {"key": "startTime", "type": "iso-8601"},
        "end_time": {"key": "endTime", "type": "iso-8601"},
        "value": {"key": "value.commentValue", "type": "str"},
    }

    def __init__(self, metric_id, dimension_key, start_time, end_time, value, **kwargs):
        super(CommentFeedback, self).__init__(
            feedback_type="Comment", metric_id=metric_id, dimension_key=dimension_key, **kwargs
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
    def _from_generated(cls, comment_feedback: generated_models.CommentFeedback) -> Optional["CommentFeedback"]:
        if not comment_feedback:
            return None
        dimension_key = comment_feedback.dimension_key
        return cls(
            id=comment_feedback.id,
            created_time=comment_feedback.created_time,
            user_principal=comment_feedback.user_principal,
            metric_id=comment_feedback.metric_id,
            dimension_key=dimension_key,
            start_time=comment_feedback.start_time,
            end_time=comment_feedback.end_time,
            value=comment_feedback.value,
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

    _validation = {
        "feedback_type": {"required": True},
        "id": {"readonly": True},
        "created_time": {"readonly": True},
        "user_principal": {"readonly": True},
        "metric_id": {"required": True},
        "dimension_key": {"required": True},
        "period_type": {"required": True},
        "value": {"required": True},
    }

    _attribute_map = {
        "feedback_type": {"key": "feedbackType", "type": "str"},
        "id": {"key": "feedbackId", "type": "str"},
        "created_time": {"key": "createdTime", "type": "iso-8601"},
        "user_principal": {"key": "userPrincipal", "type": "str"},
        "metric_id": {"key": "metricId", "type": "str"},
        "dimension_key": {"key": "dimensionFilter.dimension", "type": "{str}"},
        "period_type": {"key": "value.periodType", "type": "str"},
        "value": {"key": "value.periodValue", "type": "int"},
    }

    def __init__(self, metric_id, dimension_key, value, period_type, **kwargs):
        super(PeriodFeedback, self).__init__(
            feedback_type="Period", metric_id=metric_id, dimension_key=dimension_key, **kwargs
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
    def _from_generated(cls, period_feedback: generated_models.PeriodFeedback) -> Optional["PeriodFeedback"]:
        if not period_feedback:
            return None
        dimension_key = period_feedback.dimension_key
        return cls(
            id=period_feedback.id,
            created_time=period_feedback.created_time,
            user_principal=period_feedback.user_principal,
            metric_id=period_feedback.metric_id,
            dimension_key=dimension_key,
            value=period_feedback.value,
            period_type=period_feedback.period_type,
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

    _validation = {
        "credential_type": {"required": True},
        "id": {"readonly": True},
        "name": {"required": True},
    }

    _attribute_map = {
        "credential_type": {"key": "dataSourceCredentialType", "type": "str"},
        "id": {"key": "dataSourceCredentialId", "type": "str"},
        "name": {"key": "dataSourceCredentialName", "type": "str"},
        "description": {"key": "dataSourceCredentialDescription", "type": "str"},
    }

    def __init__(self, name: str, credential_type: str, **kwargs: Any) -> None:
        super().__init__(name=name, credential_type=credential_type, id=id, **kwargs)
        self.credential_type = credential_type
        self.id = None
        self.name = name
        self.description = kwargs.pop("description", None)

    def __repr__(self):
        return "DatasourceCredential(id={}, credential_type={}, name={}, description={})".format(
            self.id, self.credential_type, self.name, self.description
        )[:1024]


class DatasourceSqlConnectionString(generated_models.DatasourceSqlConnectionString, DatasourceCredential):
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

    def __init__(self, name: str, connection_string: str, **kwargs: Any) -> None:
        super().__init__(name=name, connection_string=connection_string, **kwargs)

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


class DatasourceDataLakeGen2SharedKey(generated_models.DatasourceDataLakeGen2SharedKey, DatasourceCredential):
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

    def __init__(self, name: str, account_key: str, **kwargs: Any) -> None:
        super().__init__(name=name, account_key=account_key, **kwargs)

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


class DatasourceServicePrincipal(generated_models.DatasourceServicePrincipal, DatasourceCredential):
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

    def __init__(self, name: str, client_id: str, client_secret: str, tenant_id: str, **kwargs: Any) -> None:
        super().__init__(name=name, client_id=client_id, client_secret=client_secret, tenant_id=tenant_id, **kwargs)

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


class DatasourceServicePrincipalInKeyVault(generated_models.DatasourceServicePrincipalInKeyVault, DatasourceCredential):
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

    def __init__(
        self,
        name: str,
        *,
        key_vault_endpoint: str,
        key_vault_client_id: str,
        key_vault_client_secret: str,
        service_principal_id_name_in_kv: str,
        service_principal_secret_name_in_kv: str,
        tenant_id: str,
        **kwargs: Any
    ) -> None:
        super().__init__(
            name=name,
            key_vault_endpoint=key_vault_endpoint,
            key_vault_client_id=key_vault_client_id,
            key_vault_client_secret=key_vault_client_secret,
            service_principal_id_name_in_kv=service_principal_id_name_in_kv,
            service_principal_secret_name_in_kv=service_principal_secret_name_in_kv,
            tenant_id=tenant_id,
            **kwargs
        )

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
        super().__init__(**kwargs)
        self.series_group_key = kwargs.get("series_group_key", None)
        self.severity_filter = kwargs.get("severity_filter", None)


class AlertingResultQuery(msrest.serialization.Model):
    """AlertingResultQuery.

    All required parameters must be populated in order to send to Azure.

    :ivar start_time: Required. start time.
    :vartype start_time: ~datetime.datetime
    :ivar end_time: Required. end time.
    :vartype end_time: ~datetime.datetime
    :ivar time_mode: Required. time mode. Possible values include: "AnomalyTime", "CreatedTime",
     "ModifiedTime".
    :vartype time_mode: str or ~azure.ai.metricsadvisor.models.AlertQueryTimeMode
    """

    _validation = {
        "start_time": {"required": True},
        "end_time": {"required": True},
        "time_mode": {"required": True},
    }

    _attribute_map = {
        "start_time": {"key": "startTime", "type": "iso-8601"},
        "end_time": {"key": "endTime", "type": "iso-8601"},
        "time_mode": {"key": "timeMode", "type": "str"},
    }

    def __init__(self, *, start_time: datetime.datetime, end_time: datetime.datetime, time_mode: str, **kwargs):
        super(AlertingResultQuery, self).__init__(**kwargs)
        self.start_time = start_time
        self.end_time = end_time
        self.time_mode = time_mode


class MetricDataQueryOptions(msrest.serialization.Model):
    """MetricDataQueryOptions.

    All required parameters must be populated in order to send to Azure.

    :ivar start_time: Required. start time of query a time series data, and format should be
     yyyy-MM-ddThh:mm:ssZ. The maximum number of data points (series number * time range) is 10000.
    :vartype start_time: ~datetime.datetime
    :ivar end_time: Required. start time of query a time series data, and format should be
     yyyy-MM-ddThh:mm:ssZ. The maximum number of data points (series number * time range) is 10000.
    :vartype end_time: ~datetime.datetime
    :ivar series: Required. query specific series. The maximum number of series is 100.
    :vartype series: list[dict[str, str]]
    """

    _validation = {
        "start_time": {"required": True},
        "end_time": {"required": True},
        "series": {"required": True},
    }

    _attribute_map = {
        "start_time": {"key": "startTime", "type": "iso-8601"},
        "end_time": {"key": "endTime", "type": "iso-8601"},
        "series": {"key": "series", "type": "[{str}]"},
    }

    def __init__(
        self, *, start_time: datetime.datetime, end_time: datetime.datetime, series: List[Dict[str, str]], **kwargs
    ):
        super(MetricDataQueryOptions, self).__init__(**kwargs)
        self.start_time = start_time
        self.end_time = end_time
        self.series = series


class MetricDimensionQueryOptions(msrest.serialization.Model):
    """MetricDimensionQueryOptions.

    All required parameters must be populated in order to send to Azure.

    :ivar dimension_name: Required. dimension name.
    :vartype dimension_name: str
    :ivar dimension_value_filter: dimension value to be filtered.
    :vartype dimension_value_filter: str
    """

    _validation = {
        "dimension_name": {"required": True},
    }

    _attribute_map = {
        "dimension_name": {"key": "dimensionName", "type": "str"},
        "dimension_value_filter": {"key": "dimensionValueFilter", "type": "str"},
    }

    def __init__(self, *, dimension_name: str, dimension_value_filter: Optional[str] = None, **kwargs):
        super(MetricDimensionQueryOptions, self).__init__(**kwargs)
        self.dimension_name = dimension_name
        self.dimension_value_filter = dimension_value_filter


class MetricSeriesQueryOptions(msrest.serialization.Model):
    """MetricSeriesQueryOptions.

    All required parameters must be populated in order to send to Azure.

    :ivar active_since: Required. query series ingested after this time, the format should be
     yyyy-MM-ddTHH:mm:ssZ.
    :vartype active_since: ~datetime.datetime
    :ivar dimension_filter: filter specific dimension name and values.
    :vartype dimension_filter: dict[str, list[str]]
    """

    _validation = {
        "active_since": {"required": True},
    }

    _attribute_map = {
        "active_since": {"key": "activeSince", "type": "iso-8601"},
        "dimension_filter": {"key": "dimensionFilter", "type": "{[str]}"},
    }

    def __init__(
        self, *, active_since: datetime.datetime, dimension_filter: Optional[Dict[str, List[str]]] = None, **kwargs
    ):
        super(MetricSeriesQueryOptions, self).__init__(**kwargs)
        self.active_since = active_since
        self.dimension_filter = dimension_filter


class AlertQueryTimeMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """time mode"""

    ANOMALY_TIME = "AnomalyTime"
    CREATED_TIME = "CreatedTime"
    MODIFIED_TIME = "ModifiedTime"


class AnomalyDimensionQuery(msrest.serialization.Model):
    """AnomalyDimensionQuery.

    All required parameters must be populated in order to send to Azure.

    :ivar start_time: Required. start time.
    :vartype start_time: ~datetime.datetime
    :ivar end_time: Required. end time.
    :vartype end_time: ~datetime.datetime
    :ivar dimension_name: Required. dimension to query.
    :vartype dimension_name: str
    :ivar dimension_filter:
    :vartype dimension_filter: ~azure.ai.metricsadvisor.models.DimensionGroupIdentity
    """

    _validation = {
        "start_time": {"required": True},
        "end_time": {"required": True},
        "dimension_name": {"required": True},
    }

    _attribute_map = {
        "start_time": {"key": "startTime", "type": "iso-8601"},
        "end_time": {"key": "endTime", "type": "iso-8601"},
        "dimension_name": {"key": "dimensionName", "type": "str"},
        "dimension_filter": {"key": "dimensionFilter", "type": "DimensionGroupIdentity"},
    }

    def __init__(
        self,
        *,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        dimension_name: str,
        dimension_filter=None,
        **kwargs
    ):
        super(AnomalyDimensionQuery, self).__init__(**kwargs)
        self.start_time = start_time
        self.end_time = end_time
        self.dimension_name = dimension_name
        self.dimension_filter = dimension_filter


class DetectionAnomalyResultQuery(msrest.serialization.Model):
    """DetectionAnomalyResultQuery.

    All required parameters must be populated in order to send to Azure.

    :ivar start_time: Required. start time.
    :vartype start_time: ~datetime.datetime
    :ivar end_time: Required. end time.
    :vartype end_time: ~datetime.datetime
    :ivar filter:
    :vartype filter: ~azure.ai.metricsadvisor.models.DetectionAnomalyFilterCondition
    """

    _validation = {
        "start_time": {"required": True},
        "end_time": {"required": True},
    }

    _attribute_map = {
        "start_time": {"key": "startTime", "type": "iso-8601"},
        "end_time": {"key": "endTime", "type": "iso-8601"},
        "filter": {"key": "filter", "type": "DetectionAnomalyFilterCondition"},
    }

    def __init__(
        self,
        *,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        filter: Optional["DetectionAnomalyFilterCondition"] = None,  # pylint: disable=redefined-builtin
        **kwargs
    ):
        super(DetectionAnomalyResultQuery, self).__init__(**kwargs)
        self.start_time = start_time
        self.end_time = end_time
        self.filter = filter


class DetectionIncidentResultQuery(msrest.serialization.Model):
    """DetectionIncidentResultQuery.

    All required parameters must be populated in order to send to Azure.

    :ivar start_time: Required. start time.
    :vartype start_time: ~datetime.datetime
    :ivar end_time: Required. end time.
    :vartype end_time: ~datetime.datetime
    :ivar filter:
    :vartype filter: ~azure.ai.metricsadvisor.models.DetectionIncidentFilterCondition
    """

    _validation = {
        "start_time": {"required": True},
        "end_time": {"required": True},
    }

    _attribute_map = {
        "start_time": {"key": "startTime", "type": "iso-8601"},
        "end_time": {"key": "endTime", "type": "iso-8601"},
        "filter": {"key": "filter", "type": "DetectionIncidentFilterCondition"},
    }

    def __init__(
        self,
        *,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        filter=None,  # pylint: disable=redefined-builtin
        **kwargs
    ):
        super(DetectionIncidentResultQuery, self).__init__(**kwargs)
        self.start_time = start_time
        self.end_time = end_time
        self.filter = filter


class DetectionSeriesQuery(msrest.serialization.Model):
    """DetectionSeriesQuery.

    All required parameters must be populated in order to send to Azure.

    :ivar start_time: Required. This is inclusive. The maximum number of data points (series number
     * time range) is 10000.
    :vartype start_time: ~datetime.datetime
    :ivar end_time: Required. This is exclusive. The maximum number of data points (series number *
     time range) is 10000.
    :vartype end_time: ~datetime.datetime
    :ivar series: Required. The series to be queried. The identity must be able to define one
     single time series instead of a group of time series. The maximum number of series is 100.
    :vartype series: list[~azure.ai.metricsadvisor.models.SeriesIdentity]
    """

    _validation = {
        "start_time": {"required": True},
        "end_time": {"required": True},
        "series": {"required": True, "unique": True},
    }

    _attribute_map = {
        "start_time": {"key": "startTime", "type": "iso-8601"},
        "end_time": {"key": "endTime", "type": "iso-8601"},
        "series": {"key": "series", "type": "[SeriesIdentity]"},
    }

    def __init__(self, *, start_time: datetime.datetime, end_time: datetime.datetime, series, **kwargs):
        super(DetectionSeriesQuery, self).__init__(**kwargs)
        self.start_time = start_time
        self.end_time = end_time
        self.series = series


class EnrichmentStatusQueryOption(msrest.serialization.Model):
    """EnrichmentStatusQueryOption.

    All required parameters must be populated in order to send to Azure.

    :ivar start_time: Required. the start point of time range to query anomaly detection status.
    :vartype start_time: ~datetime.datetime
    :ivar end_time: Required. the end point of time range to query anomaly detection status.
    :vartype end_time: ~datetime.datetime
    """

    _validation = {
        "start_time": {"required": True},
        "end_time": {"required": True},
    }

    _attribute_map = {
        "start_time": {"key": "startTime", "type": "iso-8601"},
        "end_time": {"key": "endTime", "type": "iso-8601"},
    }

    def __init__(self, *, start_time: datetime.datetime, end_time: datetime.datetime, **kwargs):
        super(EnrichmentStatusQueryOption, self).__init__(**kwargs)
        self.start_time = start_time
        self.end_time = end_time


class FeedbackQueryTimeMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """time mode to filter feedback"""

    METRIC_TIMESTAMP = "MetricTimestamp"
    FEEDBACK_CREATED_TIME = "FeedbackCreatedTime"


class IngestionProgressResetOptions(msrest.serialization.Model):
    """IngestionProgressResetOptions.

    All required parameters must be populated in order to send to Azure.

    :ivar start_time: Required. the start point of time range to reset data ingestion status.
    :vartype start_time: ~datetime.datetime
    :ivar end_time: Required. the end point of time range to reset data ingestion status.
    :vartype end_time: ~datetime.datetime
    """

    _validation = {
        "start_time": {"required": True},
        "end_time": {"required": True},
    }

    _attribute_map = {
        "start_time": {"key": "startTime", "type": "iso-8601"},
        "end_time": {"key": "endTime", "type": "iso-8601"},
    }

    def __init__(self, *, start_time: datetime.datetime, end_time: datetime.datetime, **kwargs):
        super(IngestionProgressResetOptions, self).__init__(**kwargs)
        self.start_time = start_time
        self.end_time = end_time


class IngestionStatusQueryOptions(msrest.serialization.Model):
    """IngestionStatusQueryOptions.

    All required parameters must be populated in order to send to Azure.

    :ivar start_time: Required. the start point of time range to query data ingestion status.
    :vartype start_time: ~datetime.datetime
    :ivar end_time: Required. the end point of time range to query data ingestion status.
    :vartype end_time: ~datetime.datetime
    """

    _validation = {
        "start_time": {"required": True},
        "end_time": {"required": True},
    }

    _attribute_map = {
        "start_time": {"key": "startTime", "type": "iso-8601"},
        "end_time": {"key": "endTime", "type": "iso-8601"},
    }

    def __init__(self, *, start_time: datetime.datetime, end_time: datetime.datetime, **kwargs):
        super(IngestionStatusQueryOptions, self).__init__(**kwargs)
        self.start_time = start_time
        self.end_time = end_time


class SeriesIdentity(msrest.serialization.Model):
    """SeriesIdentity.

    All required parameters must be populated in order to send to Azure.
    :param dimension: Required. dimension specified for series.
    :type dimension: dict[str, str]
    """

    _validation = {
        "dimension": {"required": True},
    }

    _attribute_map = {
        "dimension": {"key": "dimension", "type": "{str}"},
    }

    def __init__(self, *, dimension: Dict[str, str], **kwargs):
        super(SeriesIdentity, self).__init__(**kwargs)
        self.dimension = dimension


class FeedbackDimensionFilter(msrest.serialization.Model):
    _validation = {
        "dimension": {"required": True},
    }

    _attribute_map = {
        "dimension": {"key": "dimension", "type": "{str}"},
    }

    def __init__(self, *, dimension: Dict[str, str], **kwargs):
        super(FeedbackDimensionFilter, self).__init__(**kwargs)
        self.dimension = dimension


class MetricFeedbackFilter(msrest.serialization.Model):
    """MetricFeedbackFilter.

    All required parameters must be populated in order to send to Azure.

    :param metric_id: Required. filter feedbacks by metric id.
    :type metric_id: str
    :param dimension_filter:
    :type dimension_filter: ~azure.ai.metricsadvisor.models.FeedbackDimensionFilter
    :param feedback_type: filter feedbacks by type. Possible values include: "Anomaly",
     "ChangePoint", "Period", "Comment".
    :type feedback_type: str or ~azure.ai.metricsadvisor.models.FeedbackType
    :param start_time: start time filter under chosen time mode.
    :type start_time: ~datetime.datetime
    :param end_time: end time filter under chosen time mode.
    :type end_time: ~datetime.datetime
    :param time_mode: time mode to filter feedback. Possible values include: "MetricTimestamp",
     "FeedbackCreatedTime".
    :type time_mode: str or ~azure.ai.metricsadvisor.models.FeedbackQueryTimeMode
    """

    _validation = {
        "metric_id": {"required": True},
    }

    _attribute_map = {
        "metric_id": {"key": "metricId", "type": "str"},
        "dimension_filter": {"key": "dimensionFilter", "type": "FeedbackDimensionFilter"},
        "feedback_type": {"key": "feedbackType", "type": "str"},
        "start_time": {"key": "startTime", "type": "iso-8601"},
        "end_time": {"key": "endTime", "type": "iso-8601"},
        "time_mode": {"key": "timeMode", "type": "str"},
    }

    def __init__(
        self,
        *,
        metric_id: str,
        dimension_filter: Optional[FeedbackDimensionFilter] = None,
        feedback_type: Optional[Union[str, "generated_enums.FeedbackType"]] = None,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
        time_mode: Optional[Union[str, "FeedbackQueryTimeMode"]] = None,
        **kwargs
    ):
        super(MetricFeedbackFilter, self).__init__(**kwargs)
        self.metric_id = metric_id
        self.dimension_filter = dimension_filter
        self.feedback_type = feedback_type
        self.start_time = start_time
        self.end_time = end_time
        self.time_mode = time_mode


class ErrorCode(msrest.serialization.Model):
    """ErrorCode.
    :param message:
    :type message: str
    :param code:
    :type code: str
    """

    _attribute_map = {
        "message": {"key": "message", "type": "str"},
        "code": {"key": "code", "type": "str"},
    }

    def __init__(self, *, message: Optional[str] = None, code: Optional[str] = None, **kwargs):
        super(ErrorCode, self).__init__(**kwargs)
        self.message = message
        self.code = code


__all__ = [
    "MetricFeedback",
    "AnomalyFeedback",
    "ChangePointFeedback",
    "CommentFeedback",
    "PeriodFeedback",
    "DataFeedGranularity",
    "DataFeedIngestionSettings",
    "DataFeedMissingDataPointFillSettings",
    "DataFeedRollupSettings",
    "DataFeedSchema",
    "DataFeed",
    "MetricAnomalyAlertScope",
    "MetricAlertConfiguration",
    "AzureApplicationInsightsDataFeedSource",
    "AzureBlobDataFeedSource",
    "AzureCosmosDbDataFeedSource",
    "AzureTableDataFeedSource",
    "AzureLogAnalyticsDataFeedSource",
    "InfluxDbDataFeedSource",
    "SqlServerDataFeedSource",
    "MongoDbDataFeedSource",
    "MySqlDataFeedSource",
    "PostgreSqlDataFeedSource",
    "AzureDataExplorerDataFeedSource",
    "AnomalyAlertConfiguration",
    "NotificationHook",
    "EmailNotificationHook",
    "WebNotificationHook",
    "TopNGroupScope",
    "SeverityCondition",
    "MetricAnomalyAlertSnoozeCondition",
    "MetricBoundaryCondition",
    "MetricDetectionCondition",
    "MetricSeriesGroupDetectionCondition",
    "SmartDetectionCondition",
    "HardThresholdCondition",
    "SuppressCondition",
    "ChangeThresholdCondition",
    "MetricSingleSeriesDetectionCondition",
    "DataFeedDimension",
    "DataFeedMetric",
    "DataFeedIngestionProgress",
    "AnomalyDetectionConfiguration",
    "MetricAnomalyAlertConditions",
    "AnomalyIncident",
    "DataPointAnomaly",
    "MetricSeriesData",
    "AnomalyAlert",
    "AzureDataLakeStorageGen2DataFeedSource",
    "AzureEventHubsDataFeedSource",
    "MetricAnomalyAlertScopeType",
    "DataFeedRollupType",
    "IncidentRootCause",
    "MetricEnrichedSeriesData",
    "DatasourceSqlConnectionString",
    "DatasourceDataLakeGen2SharedKey",
    "DatasourceServicePrincipal",
    "DatasourceServicePrincipalInKeyVault",
    "DatasourceCredential",
    "DataFeedSource",
    "DetectionAnomalyFilterCondition",
    "AlertQueryTimeMode",
    "FeedbackQueryTimeMode",
    "SeriesIdentity",
    "AlertQueryTimeMode",
]


def patch_sdk():
    pass
