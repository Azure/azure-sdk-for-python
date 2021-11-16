# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint:disable=protected-access
# pylint:disable=too-many-lines

from typing import (
    Any,
    List,
    Union,
    cast,
    TYPE_CHECKING,
)
import datetime
import six
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.async_paging import AsyncItemPaged
from .._generated.aio import (
    MetricsAdvisor as _ClientAsync,
)
from .._generated.models import (
    AnomalyAlertingConfiguration as _AnomalyAlertingConfiguration,
    AnomalyDetectionConfiguration as _AnomalyDetectionConfiguration,
    IngestionStatus as DataFeedIngestionStatus,
    IngestionProgressResetOptions as _IngestionProgressResetOptions,
    IngestionStatusQueryOptions as _IngestionStatusQueryOptions,
)
from .._version import SDK_MONIKER
from .._patch import (
    convert_to_generated_data_feed_type,
    construct_alert_config_dict,
    construct_detection_config_dict,
    construct_hook_dict,
    construct_data_feed_dict,
    convert_datetime,
    get_authentication_policy,
    convert_to_datasource_credential,
    DATA_FEED,
    DATA_FEED_PATCH,
    DataFeedSourceUnion,
    DatasourceCredentialUnion,
    MetricsAdvisorKeyCredential,
    convert_to_sub_feedback,
    convert_datetime,
    get_authentication_policy,
)
from ..models import (
    DataFeed,
    EmailNotificationHook,
    WebNotificationHook,
    AnomalyAlertConfiguration,
    AnomalyDetectionConfiguration,
    DataFeedIngestionProgress,
    DataFeedGranularityType,
    MetricAlertConfiguration,
    DataFeedGranularity,
    DataFeedSchema,
    DataFeedIngestionSettings,
    NotificationHook,
    MetricDetectionCondition,
)
if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential

from typing import List, Union, Dict, Any, cast, TYPE_CHECKING, overload
import datetime

from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.async_paging import AsyncItemPaged
from .._generated.models import (
    MetricFeedbackFilter,
    DetectionSeriesQuery,
    AlertingResultQuery,
    DetectionAnomalyResultQuery,
    AnomalyDimensionQuery,
    DetectionIncidentResultQuery,
    MetricDimensionQueryOptions,
    MetricDataQueryOptions,
    MetricSeriesQueryOptions,
    EnrichmentStatusQueryOption,
    TimeMode as AlertQueryTimeMode,
    SeriesIdentity,
    FeedbackDimensionFilter,
    DimensionGroupIdentity,
)
from .._generated.aio import MetricsAdvisor as _ClientAsync
from ..models._models import (
    AnomalyIncident,
    DataPointAnomaly,
    MetricSeriesData,
    AnomalyAlert,
    IncidentRootCause,
    MetricEnrichedSeriesData,
)
from .._version import SDK_MONIKER

if TYPE_CHECKING:
    from .._generated.models import (
        EnrichmentStatus,
        MetricSeriesItem as MetricSeriesDefinition,
    )
    from ..models._models import MetricFeedback

class MetricsAdvisorAdministrationClient(
    object
):  # pylint:disable=too-many-public-methods
    """MetricsAdvisorAdministrationClient is used to create and manage data feeds.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and hostname,
        for example: https://:code:`<resource-name>`.cognitiveservices.azure.com).
    :param credential: An instance of ~azure.ai.metricsadvisor.MetricsAdvisorKeyCredential.
        which requires both subscription key and API key. Or an object which can provide an access
        token for the vault, such as a credential from :mod:`azure.identity`
    :type credential: ~azure.ai.metricsadvisor.MetricsAdvisorKeyCredential or ~azure.core.credentials.TokenCredential

    .. admonition:: Example:

        .. literalinclude:: ../samples/async_samples/sample_authentication_async.py
            :start-after: [START administration_client_with_metrics_advisor_credential_async]
            :end-before: [END administration_client_with_metrics_advisor_credential_async]
            :language: python
            :dedent: 4
            :caption: Authenticate MetricsAdvisorAdministrationClient with a MetricsAdvisorKeyCredential
    """

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, Union[MetricsAdvisorKeyCredential, AsyncTokenCredential], **Any) -> None
        try:
            if not endpoint.lower().startswith("http"):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Base URL must be a string.")

        self._endpoint = endpoint
        authentication_policy = get_authentication_policy(credential)
        self._client = _ClientAsync(
            endpoint=endpoint,
            credential=credential,  # type: ignore
            sdk_moniker=SDK_MONIKER,
            authentication_policy=authentication_policy,
            **kwargs
        )

    def __repr__(self):
        # type: () -> str
        return "<MetricsAdvisorAdministrationClient [endpoint={}]>".format(
            repr(self._endpoint)
        )[:1024]

    async def __aenter__(self) -> "MetricsAdvisorAdministrationClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self._client.__aexit__(*args)

    async def close(self) -> None:
        """Close the :class:`~azure.ai.metricsadvisor.aio.MetricsAdvisorAdministrationClient` session."""
        await self._client.__aexit__()

    @distributed_trace_async
    async def create_alert_configuration(
        self,
        name: str,
        metric_alert_configurations: List[MetricAlertConfiguration],
        hook_ids: List[str],
        **kwargs: Any
    ) -> AnomalyAlertConfiguration:
        """Create an anomaly alert configuration.

        :param str name: Name for the anomaly alert configuration.
        :param metric_alert_configurations: Anomaly alert configurations.
        :type metric_alert_configurations: list[~azure.ai.metricsadvisor.models.MetricAlertConfiguration]
        :param list[str] hook_ids: Unique hook IDs.
        :keyword cross_metrics_operator: Cross metrics operator should be specified when setting up multiple metric
            alert configurations. Possible values include: "AND", "OR", "XOR".
        :paramtype cross_metrics_operator: str or
            ~azure.ai.metricsadvisor.models.MetricAnomalyAlertConfigurationsOperator
        :keyword str description: Anomaly alert configuration description.
        :return: AnomalyAlertConfiguration
        :rtype: ~azure.ai.metricsadvisor.models.AnomalyAlertConfiguration
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_alert_configuration_async.py
                :start-after: [START create_alert_config_async]
                :end-before: [END create_alert_config_async]
                :language: python
                :dedent: 4
                :caption: Create an anomaly alert configuration
        """

        cross_metrics_operator = kwargs.pop("cross_metrics_operator", None)
        response_headers = await self._client.create_anomaly_alerting_configuration(
            _AnomalyAlertingConfiguration(
                name=name,
                metric_alerting_configurations=[
                    config._to_generated() for config in metric_alert_configurations
                ],
                hook_ids=hook_ids,
                cross_metrics_operator=cross_metrics_operator,
                description=kwargs.pop("description", None),
            ),
            cls=lambda pipeline_response, _, response_headers: response_headers,
            **kwargs
        )
        response_headers = cast(dict, response_headers)
        config_id = response_headers["Location"].split("configurations/")[1]
        return await self.get_alert_configuration(config_id)

    @distributed_trace_async
    async def create_data_feed(
        self,
        name: str,
        source: DataFeedSourceUnion,
        granularity: Union[str, DataFeedGranularityType, DataFeedGranularity],
        schema: Union[List[str], DataFeedSchema],
        ingestion_settings: Union[datetime.datetime, DataFeedIngestionSettings],
        **kwargs: Any
    ) -> DataFeed:
        """Create a new data feed.

        :param str name: Name for the data feed.
        :param source: The source of the data feed
        :type source: Union[AzureApplicationInsightsDataFeedSource, AzureBlobDataFeedSource,
            AzureCosmosDbDataFeedSource, AzureDataExplorerDataFeedSource, AzureDataLakeStorageGen2DataFeedSource,
            AzureTableDataFeedSource, AzureLogAnalyticsDataFeedSource, InfluxDbDataFeedSource, MySqlDataFeedSource,
            PostgreSqlDataFeedSource, SqlServerDataFeedSource, MongoDbDataFeedSource, AzureEventHubsDataFeedSource]
        :param granularity: Granularity type. If using custom granularity, you must instantiate a DataFeedGranularity.
        :type granularity: Union[str, ~azure.ai.metricsadvisor.models.DataFeedGranularityType,
            ~azure.ai.metricsadvisor.models.DataFeedGranularity]
        :param schema: Data feed schema. Can be passed as a list of metric names as strings or as a DataFeedSchema
            object if additional configuration is needed.
        :type schema: Union[list[str], ~azure.ai.metricsadvisor.models.DataFeedSchema]
        :param ingestion_settings: The data feed ingestions settings. Can be passed as a datetime to use for the
            ingestion begin time or as a DataFeedIngestionSettings object if additional configuration is needed.
        :type ingestion_settings: Union[~datetime.datetime, ~azure.ai.metricsadvisor.models.DataFeedIngestionSettings]
        :keyword list[str] admins: Data feed administrators.
        :keyword str data_feed_description: Data feed description.
        :keyword missing_data_point_fill_settings: The fill missing point type and value.
        :paramtype missing_data_point_fill_settings:
            ~azure.ai.metricsadvisor.models.DataFeedMissingDataPointFillSettings
        :keyword rollup_settings: The rollup settings.
        :paramtype rollup_settings:
            ~azure.ai.metricsadvisor.models.DataFeedRollupSettings
        :keyword list[str] viewers: Data feed viewers.
        :keyword access_mode: Data feed access mode. Possible values include:
            "Private", "Public". Default value: "Private".
        :paramtype access_mode: str or ~azure.ai.metricsadvisor.models.DataFeedAccessMode
        :keyword str action_link_template: action link for alert.
        :return: DataFeed
        :rtype: ~azure.ai.metricsadvisor.models.DataFeed
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_data_feeds_async.py
                :start-after: [START create_data_feed_async]
                :end-before: [END create_data_feed_async]
                :language: python
                :dedent: 4
                :caption: Create a data feed
        """

        admins = kwargs.pop("admins", None)
        data_feed_description = kwargs.pop("data_feed_description", None)
        missing_data_point_fill_settings = kwargs.pop(
            "missing_data_point_fill_settings", None
        )
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

        response_headers = await self._client.create_data_feed(
            data_feed_detail,
            cls=lambda pipeline_response, _, response_headers: response_headers,
            **kwargs
        )
        response_headers = cast(dict, response_headers)
        data_feed_id = response_headers["Location"].split("dataFeeds/")[1]
        return await self.get_data_feed(data_feed_id)

    @distributed_trace_async
    async def create_hook(
        self, hook: Union[EmailNotificationHook, WebNotificationHook], **kwargs: Any
    ) -> Union[NotificationHook, EmailNotificationHook, WebNotificationHook]:
        """Create a new email or web hook.

        :param hook: An email or web hook to create
        :type hook: Union[~azure.ai.metricsadvisor.models.EmailNotificationHook,
            ~azure.ai.metricsadvisor.models.WebNotificationHook]
        :return: EmailNotificationHook or WebNotificationHook
        :rtype: Union[~azure.ai.metricsadvisor.models.NotificationHook,
            ~azure.ai.metricsadvisor.models.EmailNotificationHook,
            ~azure.ai.metricsadvisor.models.WebNotificationHook]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_hooks_async.py
                :start-after: [START create_hook_async]
                :end-before: [END create_hook_async]
                :language: python
                :dedent: 4
                :caption: Create a notification hook
        """

        hook_request = None
        if hook.hook_type == "Email":
            hook_request = hook._to_generated()

        if hook.hook_type == "Webhook":
            hook_request = hook._to_generated()

        response_headers = await self._client.create_hook(
            hook_request,  # type: ignore
            cls=lambda pipeline_response, _, response_headers: response_headers,
            **kwargs
        )
        response_headers = cast(dict, response_headers)
        hook_id = response_headers["Location"].split("hooks/")[1]
        return await self.get_hook(hook_id)

    @distributed_trace_async
    async def create_detection_configuration(
        self,
        name: str,
        metric_id: str,
        whole_series_detection_condition: MetricDetectionCondition,
        **kwargs: Any
    ) -> AnomalyDetectionConfiguration:
        """Create anomaly detection configuration.

        :param str name: The name for the anomaly detection configuration
        :param str metric_id: Required. metric unique id.
        :param whole_series_detection_condition: Required.
            Conditions to detect anomalies in all time series of a metric.
        :type whole_series_detection_condition: ~azure.ai.metricsadvisor.models.MetricDetectionCondition
        :keyword str description: anomaly detection configuration description.
        :keyword series_group_detection_conditions: detection configuration for series group.
        :paramtype series_group_detection_conditions:
         list[~azure.ai.metricsadvisor.models.MetricSeriesGroupDetectionCondition]
        :keyword series_detection_conditions: detection configuration for specific series.
        :paramtype series_detection_conditions:
            list[~azure.ai.metricsadvisor.models.MetricSingleSeriesDetectionCondition]
        :return: AnomalyDetectionConfiguration
        :rtype: ~azure.ai.metricsadvisor.models.AnomalyDetectionConfiguration
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_detection_configuration_async.py
                :start-after: [START create_detection_config_async]
                :end-before: [END create_detection_config_async]
                :language: python
                :dedent: 4
                :caption: Create an anomaly detection configuration
        """

        description = kwargs.pop("description", None)
        series_group_detection_conditions = kwargs.pop(
            "series_group_detection_conditions", None
        )
        series_detection_conditions = kwargs.pop("series_detection_conditions", None)
        config = _AnomalyDetectionConfiguration(
            name=name,
            metric_id=metric_id,
            description=description,
            whole_metric_configuration=whole_series_detection_condition._to_generated(),
            dimension_group_override_configurations=[
                group._to_generated() for group in series_group_detection_conditions
            ]
            if series_group_detection_conditions
            else None,
            series_override_configurations=[
                series._to_generated() for series in series_detection_conditions
            ]
            if series_detection_conditions
            else None,
        )

        response_headers = await self._client.create_anomaly_detection_configuration(
            config,
            cls=lambda pipeline_response, _, response_headers: response_headers,
            **kwargs
        )
        response_headers = cast(dict, response_headers)
        config_id = response_headers["Location"].split("configurations/")[1]
        return await self.get_detection_configuration(config_id)

    @distributed_trace_async
    async def get_data_feed(self, data_feed_id: str, **kwargs: Any) -> DataFeed:
        """Get a data feed by its id.

        :param data_feed_id: The data feed unique id.
        :type data_feed_id: str
        :return: DataFeed
        :rtype: ~azure.ai.metricsadvisor.models.DataFeed
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_data_feeds_async.py
                :start-after: [START get_data_feed_async]
                :end-before: [END get_data_feed_async]
                :language: python
                :dedent: 4
                :caption: Get a data feed by its ID
        """

        data_feed = await self._client.get_data_feed_by_id(data_feed_id, **kwargs)
        return DataFeed._from_generated(data_feed)

    @distributed_trace_async
    async def get_alert_configuration(
        self, alert_configuration_id: str, **kwargs: Any
    ) -> AnomalyAlertConfiguration:
        """Get a single anomaly alert configuration.

        :param alert_configuration_id: anomaly alert configuration unique id.
        :type alert_configuration_id: str
        :return: AnomalyAlertConfiguration
        :rtype: ~azure.ai.metricsadvisor.models.AnomalyAlertConfiguration
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_alert_configuration_async.py
                :start-after: [START get_alert_config_async]
                :end-before: [END get_alert_config_async]
                :language: python
                :dedent: 4
                :caption: Get a single anomaly alert configuration by its ID
        """

        config = await self._client.get_anomaly_alerting_configuration(
            alert_configuration_id, **kwargs
        )
        return AnomalyAlertConfiguration._from_generated(config)

    @distributed_trace_async
    async def get_detection_configuration(
        self, detection_configuration_id: str, **kwargs: Any
    ) -> AnomalyDetectionConfiguration:
        """Get a single anomaly detection configuration.

        :param detection_configuration_id: anomaly detection configuration unique id.
        :type detection_configuration_id: str
        :return: AnomalyDetectionConfiguration
        :rtype: ~azure.ai.metricsadvisor.models.AnomalyDetectionConfiguration
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_detection_configuration_async.py
                :start-after: [START get_detection_config_async]
                :end-before: [END get_detection_config_async]
                :language: python
                :dedent: 4
                :caption: Get a single anomaly detection configuration by its ID
        """

        config = await self._client.get_anomaly_detection_configuration(
            detection_configuration_id, **kwargs
        )
        return AnomalyDetectionConfiguration._from_generated(config)

    @distributed_trace_async
    async def get_hook(
        self, hook_id: str, **kwargs: Any
    ) -> Union[NotificationHook, EmailNotificationHook, WebNotificationHook]:
        """Get a web or email hook by its id.

        :param hook_id: Hook unique ID.
        :type hook_id: str
        :return: EmailNotificationHook or WebNotificationHook
        :rtype: Union[~azure.ai.metricsadvisor.models.NotificationHook,
            ~azure.ai.metricsadvisor.models.EmailNotificationHook,
            ~azure.ai.metricsadvisor.models.WebNotificationHook]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_hooks_async.py
                :start-after: [START get_hook_async]
                :end-before: [END get_hook_async]
                :language: python
                :dedent: 4
                :caption: Get a notification hook by its ID
        """

        hook = await self._client.get_hook(hook_id, **kwargs)
        if hook.hook_type == "Email":
            return EmailNotificationHook._from_generated(hook)
        return WebNotificationHook._from_generated(hook)

    @distributed_trace_async
    async def get_data_feed_ingestion_progress(
        self, data_feed_id: str, **kwargs: Any
    ) -> DataFeedIngestionProgress:
        """Get last successful data ingestion job timestamp by data feed.

        :param data_feed_id: The data feed unique id.
        :type data_feed_id: str
        :return: DataFeedIngestionProgress, containing `latest_success_timestamp`
            and `latest_active_timestamp`
        :rtype: ~azure.ai.metricsadvisor.models.DataFeedIngestionProgress
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_ingestion_async.py
                :start-after: [START get_data_feed_ingestion_progress_async]
                :end-before: [END get_data_feed_ingestion_progress_async]
                :language: python
                :dedent: 4
                :caption: Get the progress of data feed ingestion
        """
        ingestion_process = await self._client.get_ingestion_progress(
            data_feed_id, **kwargs
        )
        return DataFeedIngestionProgress._from_generated(ingestion_process)

    @distributed_trace_async
    async def refresh_data_feed_ingestion(
        self,
        data_feed_id: str,
        start_time: Union[str, datetime.datetime],
        end_time: Union[str, datetime.datetime],
        **kwargs: Any
    ) -> None:
        """Refreshes data ingestion by data feed to backfill data.

        :param data_feed_id: The data feed unique id.
        :type data_feed_id: str
        :param start_time: The start point of time range to refresh data ingestion.
        :type start_time: Union[str, ~datetime.datetime]
        :param end_time: The end point of time range to refresh data ingestion.
        :type end_time: Union[str, ~datetime.datetime]
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_ingestion_async.py
                :start-after: [START refresh_data_feed_ingestion_async]
                :end-before: [END refresh_data_feed_ingestion_async]
                :language: python
                :dedent: 4
                :caption: Refresh data feed ingestion over a period of time
        """
        converted_start_time = convert_datetime(start_time)
        converted_end_time = convert_datetime(end_time)
        await self._client.reset_data_feed_ingestion_status(
            data_feed_id,
            body=_IngestionProgressResetOptions(
                start_time=converted_start_time, end_time=converted_end_time
            ),
            **kwargs
        )

    @distributed_trace_async
    async def delete_alert_configuration(
        self, *alert_configuration_id: str, **kwargs: Any
    ) -> None:
        """Delete an anomaly alert configuration by its ID.

        :param str alert_configuration_id: anomaly alert configuration unique id.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_alert_configuration_async.py
                :start-after: [START delete_alert_config_async]
                :end-before: [END delete_alert_config_async]
                :language: python
                :dedent: 4
                :caption: Delete an anomaly alert configuration by its ID
        """
        if len(alert_configuration_id) != 1:
            raise TypeError("Alert configuration requires exactly one id.")

        await self._client.delete_anomaly_alerting_configuration(
            alert_configuration_id[0], **kwargs
        )

    @distributed_trace_async
    async def delete_detection_configuration(
        self, *detection_configuration_id: str, **kwargs: Any
    ) -> None:
        """Delete an anomaly detection configuration by its ID.

        :param str detection_configuration_id: anomaly detection configuration unique id.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_detection_configuration_async.py
                :start-after: [START delete_detection_config_async]
                :end-before: [END delete_detection_config_async]
                :language: python
                :dedent: 4
                :caption: Delete an anomaly detection configuration by its ID
        """
        if len(detection_configuration_id) != 1:
            raise TypeError("Detection configuration requires exactly one id.")

        await self._client.delete_anomaly_detection_configuration(
            detection_configuration_id[0], **kwargs
        )

    @distributed_trace_async
    async def delete_data_feed(self, *data_feed_id: str, **kwargs: Any) -> None:
        """Delete a data feed by its ID.

        :param str data_feed_id: The data feed unique id.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_data_feeds_async.py
                :start-after: [START delete_data_feed_async]
                :end-before: [END delete_data_feed_async]
                :language: python
                :dedent: 4
                :caption: Delete a data feed by its ID
        """
        if len(data_feed_id) != 1:
            raise TypeError("Data feed requires exactly one id.")

        await self._client.delete_data_feed(data_feed_id[0], **kwargs)

    @distributed_trace_async
    async def delete_hook(self, *hook_id: str, **kwargs: Any) -> None:
        """Delete a web or email hook by its ID.

        :param str hook_id: Hook unique ID.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_hooks_async.py
                :start-after: [START delete_hook_async]
                :end-before: [END delete_hook_async]
                :language: python
                :dedent: 4
                :caption: Delete a hook by its ID
        """
        if len(hook_id) != 1:
            raise TypeError("Hook requires exactly one id.")

        await self._client.delete_hook(hook_id[0], **kwargs)

    @distributed_trace_async
    async def update_data_feed(
        self, data_feed: Union[str, DataFeed], **kwargs: Any
    ) -> DataFeed:
        """Update a data feed. Either pass the entire DataFeed object with the chosen updates
        or the ID to your data feed with updates passed via keyword arguments. If you pass both
        the DataFeed object and keyword arguments, the keyword arguments will take precedence.

        :param data_feed: The data feed with updates or the data feed ID.
        :type data_feed: ~azure.ai.metricsadvisor.models.DataFeed or str
        :keyword str name: The name to update the data feed.
        :keyword str timestamp_column: User-defined timestamp column name.
        :keyword ~datetime.datetime ingestion_begin_time: Ingestion start time.
        :keyword int data_source_request_concurrency: The max concurrency of data ingestion queries against
            user data source. Zero (0) means no limitation.
        :keyword int ingestion_retry_delay: The min retry interval for failed data ingestion tasks, in seconds.
        :keyword int ingestion_start_offset: The time that the beginning of data ingestion task will delay
            for every data slice according to this offset, in seconds.
        :keyword int stop_retry_after: Stop retry data ingestion after the data slice first
            schedule time in seconds.
        :keyword str rollup_identification_value: The identification value for the row of calculated
            all-up value.
        :keyword rollup_type: Mark if the data feed needs rollup. Possible values include: "NoRollup",
            "AutoRollup", "AlreadyRollup". Default value: "AutoRollup".
        :paramtype rollup_type: str or ~azure.ai.metricsadvisor.models.DataFeedRollupType
        :keyword list[str] auto_rollup_group_by_column_names: Roll up columns.
        :keyword rollup_method: Roll up method. Possible values include: "None", "Sum", "Max", "Min",
            "Avg", "Count".
        :paramtype rollup_method: str or ~azure.ai.metricsadvisor.models.DataFeedAutoRollupMethod
        :keyword fill_type: The type of fill missing point for anomaly detection. Possible
            values include: "SmartFilling", "PreviousValue", "CustomValue", "NoFilling". Default value:
            "SmartFilling".
        :paramtype fill_type: str or ~azure.ai.metricsadvisor.models.DatasourceMissingDataPointFillType
        :keyword float custom_fill_value: The value of fill missing point for anomaly detection
            if "CustomValue" fill type is specified.
        :keyword list[str] admins: Data feed administrators.
        :keyword str data_feed_description: Data feed description.
        :keyword list[str] viewers: Data feed viewers.
        :keyword access_mode: Data feed access mode. Possible values include:
            "Private", "Public". Default value: "Private".
        :paramtype access_mode: str or ~azure.ai.metricsadvisor.models.DataFeedAccessMode
        :keyword str action_link_template: action link for alert.
        :keyword status: Data feed status. Possible values include: "Active", "Paused".
        :paramtype status: str or ~azure.ai.metricsadvisor.models.DataFeedStatus
        :keyword source: The source of the data feed for update
        :paramtype source: Union[AzureApplicationInsightsDataFeedSource, AzureBlobDataFeedSource,
            AzureCosmosDbDataFeedSource, AzureDataExplorerDataFeedSource, AzureDataLakeStorageGen2DataFeedSource,
            AzureTableDataFeedSource, AzureLogAnalyticsDataFeedSource, InfluxDbDataFeedSource, MySqlDataFeedSource,
            PostgreSqlDataFeedSource, SqlServerDataFeedSource, MongoDbDataFeedSource, AzureEventHubsDataFeedSource]
        :rtype: ~azure.ai.metricsadvisor.models.DataFeed
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_data_feeds_async.py
                :start-after: [START update_data_feed_async]
                :end-before: [END update_data_feed_async]
                :language: python
                :dedent: 4
                :caption: Update an existing data feed
        """

        unset = object()
        update_kwargs = {}
        update_kwargs["dataFeedName"] = kwargs.pop("name", unset)
        update_kwargs["dataFeedDescription"] = kwargs.pop(
            "data_feed_description", unset
        )
        update_kwargs["timestampColumn"] = kwargs.pop("timestamp_column", unset)
        update_kwargs["dataStartFrom"] = kwargs.pop("ingestion_begin_time", unset)
        update_kwargs["startOffsetInSeconds"] = kwargs.pop(
            "ingestion_start_offset", unset
        )
        update_kwargs["maxConcurrency"] = kwargs.pop(
            "data_source_request_concurrency", unset
        )
        update_kwargs["minRetryIntervalInSeconds"] = kwargs.pop(
            "ingestion_retry_delay", unset
        )
        update_kwargs["stopRetryAfterInSeconds"] = kwargs.pop("stop_retry_after", unset)
        update_kwargs["needRollup"] = kwargs.pop("rollup_type", unset)
        update_kwargs["rollUpMethod"] = kwargs.pop("rollup_method", unset)
        update_kwargs["rollUpColumns"] = kwargs.pop(
            "auto_rollup_group_by_column_names", unset
        )
        update_kwargs["allUpIdentification"] = kwargs.pop(
            "rollup_identification_value", unset
        )
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
            data_feed_patch = data_feed._to_generated_patch(
                data_feed_patch_type, update
            )

        data_feed_detail = await self._client.update_data_feed(
            data_feed_id, data_feed_patch, **kwargs
        )
        return DataFeed._from_generated(data_feed_detail)

    @distributed_trace_async
    async def update_alert_configuration(
        self, alert_configuration: Union[str, AnomalyAlertConfiguration], **kwargs: Any
    ) -> AnomalyAlertConfiguration:
        """Update anomaly alerting configuration. Either pass the entire AnomalyAlertConfiguration object
        with the chosen updates or the ID to your alert configuration with updates passed via keyword arguments.
        If you pass both the AnomalyAlertConfiguration object and keyword arguments, the keyword arguments
        will take precedence.

        :param alert_configuration: AnomalyAlertConfiguration object or the ID to the alert configuration.
        :type alert_configuration: str or ~azure.ai.metricsadvisor.models.AnomalyAlertConfiguration
        :keyword str name: Name for the anomaly alert configuration.
        :keyword metric_alert_configurations: Anomaly alert configurations.
        :paramtype metric_alert_configurations: list[~azure.ai.metricsadvisor.models.MetricAlertConfiguration]
        :keyword list[str] hook_ids: Unique hook IDs.
        :keyword cross_metrics_operator: Cross metrics operator should be specified when setting up multiple metric
            alert configurations. Possible values include: "AND", "OR", "XOR".
        :paramtype cross_metrics_operator: str or
            ~azure.ai.metricsadvisor.models.MetricAnomalyAlertConfigurationsOperator
        :keyword str description: Anomaly alert configuration description.
        :rtype: ~azure.ai.metricsadvisor.models.AnomalyAlertConfiguration
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_alert_configuration_async.py
                :start-after: [START update_alert_config_async]
                :end-before: [END update_alert_config_async]
                :language: python
                :dedent: 4
                :caption: Update an existing anomaly alert configuration
        """

        unset = object()
        update_kwargs = {}
        update_kwargs["name"] = kwargs.pop("name", unset)
        update_kwargs["hookIds"] = kwargs.pop("hook_ids", unset)
        update_kwargs["crossMetricsOperator"] = kwargs.pop(
            "cross_metrics_operator", unset
        )
        update_kwargs["metricAlertingConfigurations"] = kwargs.pop(
            "metric_alert_configurations", unset
        )
        update_kwargs["description"] = kwargs.pop("description", unset)

        update = {key: value for key, value in update_kwargs.items() if value != unset}
        if isinstance(alert_configuration, six.string_types):
            alert_configuration_id = alert_configuration
            alert_configuration_patch = construct_alert_config_dict(update)

        else:
            alert_configuration_id = alert_configuration.id
            alert_configuration_patch = alert_configuration._to_generated_patch(
                name=update.pop("name", None),
                metric_alert_configurations=update.pop(
                    "metricAlertingConfigurations", None
                ),
                hook_ids=update.pop("hookIds", None),
                cross_metrics_operator=update.pop("crossMetricsOperator", None),
                description=update.pop("description", None),
            )
        alerting_config = await self._client.update_anomaly_alerting_configuration(
            alert_configuration_id, alert_configuration_patch, **kwargs
        )

        return AnomalyAlertConfiguration._from_generated(alerting_config)

    @distributed_trace_async
    async def update_detection_configuration(
        self,
        detection_configuration: Union[str, AnomalyDetectionConfiguration],
        **kwargs: Any
    ) -> AnomalyDetectionConfiguration:
        """Update anomaly metric detection configuration. Either pass the entire AnomalyDetectionConfiguration object
        with the chosen updates or the ID to your detection configuration with updates passed via keyword arguments.
        If you pass both the AnomalyDetectionConfiguration object and keyword arguments, the keyword arguments
        will take precedence.

        :param detection_configuration: AnomalyDetectionConfiguration object or the ID to the detection
            configuration.
        :type detection_configuration: str or ~azure.ai.metricsadvisor.models.AnomalyDetectionConfiguration
        :keyword str name: The name for the anomaly detection configuration
        :keyword str metric_id: metric unique id.
        :keyword whole_series_detection_condition: Required.
            Conditions to detect anomalies in all time series of a metric.
        :paramtype whole_series_detection_condition: ~azure.ai.metricsadvisor.models.MetricDetectionCondition
        :keyword str description: anomaly detection configuration description.
        :keyword series_group_detection_conditions: detection configuration for series group.
        :paramtype series_group_detection_conditions:
         list[~azure.ai.metricsadvisor.models.MetricSeriesGroupDetectionCondition]
        :keyword series_detection_conditions: detection configuration for specific series.
        :paramtype series_detection_conditions:
            list[~azure.ai.metricsadvisor.models.MetricSingleSeriesDetectionCondition]
        :return: AnomalyDetectionConfiguration
        :rtype: ~azure.ai.metricsadvisor.models.AnomalyDetectionConfiguration
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_detection_configuration_async.py
                :start-after: [START update_detection_config_async]
                :end-before: [END update_detection_config_async]
                :language: python
                :dedent: 4
                :caption: Update an existing anomaly detection configuration
        """

        unset = object()
        update_kwargs = {}
        update_kwargs["name"] = kwargs.pop("name", unset)
        update_kwargs["wholeMetricConfiguration"] = kwargs.pop(
            "whole_series_detection_condition", unset
        )
        update_kwargs["dimensionGroupOverrideConfigurations"] = kwargs.pop(
            "series_group_detection_conditions", unset
        )
        update_kwargs["seriesOverrideConfigurations"] = kwargs.pop(
            "series_detection_conditions", unset
        )
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
                whole_series_detection_condition=update.pop(
                    "wholeMetricConfiguration", None
                ),
                series_group_detection_conditions=update.pop(
                    "dimensionGroupOverrideConfigurations", None
                ),
                series_detection_conditions=update.pop(
                    "seriesOverrideConfigurations", None
                ),
            )
        detection_config = await self._client.update_anomaly_detection_configuration(
            detection_configuration_id, detection_config_patch, **kwargs
        )

        return AnomalyDetectionConfiguration._from_generated(detection_config)

    @distributed_trace_async
    async def update_hook(
        self,
        hook: Union[str, EmailNotificationHook, WebNotificationHook],
        **kwargs: Any
    ) -> Union[NotificationHook, EmailNotificationHook, WebNotificationHook]:
        """Update a hook. Either pass the entire EmailNotificationHook or WebNotificationHook object with the
        chosen updates, or the ID to your hook configuration with the updates passed via keyword arguments.
        If you pass both the hook object and keyword arguments, the keyword arguments will take precedence.

        :param hook: An email or web hook or the ID to the hook. If an ID is passed, you must pass `hook_type`.
        :type hook: Union[str, ~azure.ai.metricsadvisor.models.EmailNotificationHook,
            ~azure.ai.metricsadvisor.models.WebNotificationHook]
        :keyword str hook_type: The hook type. Possible values are "Email" or "Web". Must be passed if only the
            hook ID is provided.
        :keyword str name: Hook unique name.
        :keyword str description: Hook description.
        :keyword str external_link: Hook external link.
        :keyword list[str] emails_to_alert: Email TO: list. Only should be passed to update EmailNotificationHook.
        :keyword str endpoint: API address, will be called when alert is triggered, only support
            POST method via SSL. Only should be passed to update WebNotificationHook.
        :keyword str username: basic authentication. Only should be passed to update WebNotificationHook.
        :keyword str password: basic authentication. Only should be passed to update WebNotificationHook.
        :keyword str certificate_key: client certificate. Only should be passed to update WebNotificationHook.
        :keyword str certificate_password: client certificate password. Only should be passed to update
            WebNotificationHook.
        :rtype: Union[~azure.ai.metricsadvisor.models.NotificationHook,
            ~azure.ai.metricsadvisor.models.EmailNotificationHook,
            ~azure.ai.metricsadvisor.models.WebNotificationHook]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_hooks_async.py
                :start-after: [START update_hook_async]
                :end-before: [END update_hook_async]
                :language: python
                :dedent: 4
                :caption: Update an existing notification hook
        """

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

        updated_hook = await self._client.update_hook(hook_id, hook_patch, **kwargs)
        if updated_hook.hook_type == "Email":
            return EmailNotificationHook._from_generated(updated_hook)
        return WebNotificationHook._from_generated(updated_hook)

    @distributed_trace
    def list_hooks(
        self, **kwargs: Any
    ) -> AsyncItemPaged[
        Union[NotificationHook, EmailNotificationHook, WebNotificationHook]
    ]:
        """List all hooks.

        :keyword str hook_name: filter hook by its name.
        :keyword int skip:
        :return: Pageable containing EmailNotificationHook and WebNotificationHook
        :rtype: ~azure.core.async_paging.AsyncItemPaged[Union[~azure.ai.metricsadvisor.models.NotificationHook,
            ~azure.ai.metricsadvisor.models.EmailNotificationHook, ~azure.ai.metricsadvisor.models.WebNotificationHook]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_hooks_async.py
                :start-after: [START list_hooks_async]
                :end-before: [END list_hooks_async]
                :language: python
                :dedent: 4
                :caption: List all the notification hooks under an account
        """
        hook_name = kwargs.pop("hook_name", None)
        skip = kwargs.pop("skip", None)

        def _convert_to_hook_type(hook):
            if hook.hook_type == "Email":
                return EmailNotificationHook._from_generated(hook)
            return WebNotificationHook._from_generated(hook)

        return self._client.list_hooks(  # type: ignore
            hook_name=hook_name,
            skip=skip,
            cls=kwargs.pop(
                "cls", lambda hooks: [_convert_to_hook_type(hook) for hook in hooks]
            ),
            **kwargs
        )

    @distributed_trace
    def list_data_feeds(self, **kwargs: Any) -> AsyncItemPaged[DataFeed]:
        """List all data feeds.

        :keyword str data_feed_name: filter data feed by its name.
        :keyword data_source_type: filter data feed by its source type.
        :paramtype data_source_type: str or ~azure.ai.metricsadvisor.models.DatasourceType
        :keyword granularity_type: filter data feed by its granularity.
        :paramtype granularity_type: str or ~azure.ai.metricsadvisor.models.DataFeedGranularityType
        :keyword status: filter data feed by its status.
        :paramtype status: str or ~azure.ai.metricsadvisor.models.DataFeedStatus
        :keyword str creator: filter data feed by its creator.
        :keyword int skip:
        :return: Pageable of DataFeed
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.ai.metricsadvisor.models.DataFeed]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_data_feeds_async.py
                :start-after: [START list_data_feeds_async]
                :end-before: [END list_data_feeds_async]
                :language: python
                :dedent: 4
                :caption: List data feeds under an account.
        """

        data_feed_name = kwargs.pop("data_feed_name", None)
        data_source_type = kwargs.pop("data_source_type", None)
        granularity_type = kwargs.pop("granularity_type", None)
        status = kwargs.pop("status", None)
        creator = kwargs.pop("creator", None)
        skip = kwargs.pop("skip", None)

        return self._client.list_data_feeds(  # type: ignore
            data_feed_name=data_feed_name,
            data_source_type=data_source_type,
            granularity_name=granularity_type,
            status=status,
            creator=creator,
            skip=skip,
            cls=kwargs.pop(
                "cls", lambda feeds: [DataFeed._from_generated(feed) for feed in feeds]
            ),
            **kwargs
        )

    @distributed_trace
    def list_alert_configurations(
        self, detection_configuration_id: str, **kwargs: Any
    ) -> AsyncItemPaged[AnomalyAlertConfiguration]:
        """Query all anomaly alert configurations for specific anomaly detection configuration.

        :param detection_configuration_id: anomaly detection configuration unique id.
        :type detection_configuration_id: str
        :return: Pageable of AnomalyAlertConfiguration
        :rtype: ~azure.core.async_paging.AsyncItemPaged[AnomalyAlertConfiguration]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_alert_configuration_async.py
                :start-after: [START list_alert_configs_async]
                :end-before: [END list_alert_configs_async]
                :language: python
                :dedent: 4
                :caption: List all anomaly alert configurations for specific anomaly detection configuration
        """
        return self._client.get_anomaly_alerting_configurations_by_anomaly_detection_configuration(  # type: ignore
            detection_configuration_id,
            cls=kwargs.pop(
                "cls",
                lambda confs: [
                    AnomalyAlertConfiguration._from_generated(conf) for conf in confs
                ],
            ),
            **kwargs
        )

    @distributed_trace
    def list_detection_configurations(
        self, metric_id: str, **kwargs: Any
    ) -> AsyncItemPaged[AnomalyDetectionConfiguration]:
        """Query all anomaly detection configurations for specific metric.

        :param metric_id: metric unique id.
        :type metric_id: str
        :return: Pageable of AnomalyDetectionConfiguration
        :rtype: ~azure.core.async_paging.AsyncItemPaged[AnomalyDetectionConfiguration]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_detection_configuration_async.py
                :start-after: [START list_detection_configs_async]
                :end-before: [END list_detection_configs_async]
                :language: python
                :dedent: 4
                :caption: List all anomaly detection configurations for a specific metric
        """
        return self._client.get_anomaly_detection_configurations_by_metric(  # type: ignore
            metric_id,
            cls=kwargs.pop(
                "cls",
                lambda confs: [
                    AnomalyDetectionConfiguration._from_generated(conf)
                    for conf in confs
                ],
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
        # type: (...) -> AsyncItemPaged[DataFeedIngestionStatus]
        """Get data ingestion status by data feed.

        :param str data_feed_id: The data feed unique id.
        :param start_time: Required. the start point of time range to query data ingestion status.
        :type start_time: Union[str, ~datetime.datetime]
        :param end_time: Required. the end point of time range to query data ingestion status.
        :type end_time: Union[str, ~datetime.datetime]
        :keyword int skip:
        :return: Pageable of DataFeedIngestionStatus
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.ai.metricsadvisor.models.DataFeedIngestionStatus]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_ingestion_async.py
                :start-after: [START list_data_feed_ingestion_status_async]
                :end-before: [END list_data_feed_ingestion_status_async]
                :language: python
                :dedent: 4
                :caption: List the data feed ingestion statuses by data feed ID
        """

        skip = kwargs.pop("skip", None)
        converted_start_time = convert_datetime(start_time)
        converted_end_time = convert_datetime(end_time)

        return self._client.get_data_feed_ingestion_status(  # type: ignore
            data_feed_id=data_feed_id,
            body=_IngestionStatusQueryOptions(
                start_time=converted_start_time, end_time=converted_end_time
            ),
            skip=skip,
            **kwargs
        )

    @distributed_trace_async
    async def get_datasource_credential(
        self,
        credential_id,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> DatasourceCredentialUnion
        """Get a datasource credential

        :param str credential_id: Datasource credential unique ID.
        :return: The datasource credential
        :rtype: Union[~azure.ai.metricsadvisor.models.DatasourceCredential,
            ~azure.ai.metricsadvisor.models.DatasourceSqlConnectionString,
            ~azure.ai.metricsadvisor.models.DatasourceDataLakeGen2SharedKey,
            ~azure.ai.metricsadvisor.models.DatasourceServicePrincipal,
            ~azure.ai.metricsadvisor.models.DatasourceServicePrincipalInKeyVault]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_datasource_credentials_async.py
                :start-after: [START get_datasource_credential_async]
                :end-before: [END get_datasource_credential_async]
                :language: python
                :dedent: 4
                :caption: Get a datasource credential by its ID
        """

        datasource_credential = await self._client.get_credential(
            credential_id, **kwargs
        )
        return convert_to_datasource_credential(datasource_credential)

    @distributed_trace_async
    async def create_datasource_credential(
        self,
        datasource_credential,  # type: DatasourceCredentialUnion
        **kwargs  # type: Any
    ):
        # type: (...) -> DatasourceCredentialUnion
        """Create a new datasource credential.

        :param datasource_credential: The datasource credential to create
        :type datasource_credential: Union[~azure.ai.metricsadvisor.models.DatasourceSqlConnectionString,
            ~azure.ai.metricsadvisor.models.DatasourceDataLakeGen2SharedKey,
            ~azure.ai.metricsadvisor.models.DatasourceServicePrincipal,
            ~azure.ai.metricsadvisor.models.DatasourceServicePrincipalInKeyVault]
        :return: The created datasource credential
        :rtype: Union[~azure.ai.metricsadvisor.models.DatasourceSqlConnectionString,
            ~azure.ai.metricsadvisor.models.DatasourceDataLakeGen2SharedKey,
            ~azure.ai.metricsadvisor.models.DatasourceServicePrincipal,
            ~azure.ai.metricsadvisor.models.DatasourceServicePrincipalInKeyVault]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_datasource_credentials_async.py
                :start-after: [START create_datasource_credential_async]
                :end-before: [END create_datasource_credential_async]
                :language: python
                :dedent: 4
                :caption: Create a datasource credential
        """

        datasource_credential_request = None
        if datasource_credential.credential_type in [
            "AzureSQLConnectionString",
            "DataLakeGen2SharedKey",
            "ServicePrincipal",
            "ServicePrincipalInKV",
        ]:
            datasource_credential_request = datasource_credential._to_generated()

        response_headers = await self._client.create_credential(  # type: ignore
            datasource_credential_request,  # type: ignore
            cls=lambda pipeline_response, _, response_headers: response_headers,
            **kwargs
        )
        credential_id = response_headers["Location"].split("credentials/")[1]  # type: ignore
        return await self.get_datasource_credential(credential_id)

    @distributed_trace
    def list_datasource_credentials(
        self, **kwargs  # type: Any
    ):
        # type: (...) -> AsyncItemPaged[DatasourceCredentialUnion]
        """List all datasource credential.

        :param skip: for paging, skipped number.
        :type skip: int
        :return: Pageable containing datasource credentials
        :rtype: ~azure.core.paging.AsyncItemPaged[Union[
            ~azure.ai.metricsadvisor.models.DatasourceCredential,
            ~azure.ai.metricsadvisor.models.DatasourceSqlConnectionString,
            ~azure.ai.metricsadvisor.models.DatasourceDataLakeGen2SharedKey,
            ~azure.ai.metricsadvisor.models.DatasourceServicePrincipal,
            ~azure.ai.metricsadvisor.models.DatasourceServicePrincipalInKeyVault]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_datasource_credentials_async.py
                :start-after: [START list_datasource_credentials_async]
                :end-before: [END list_datasource_credentials_async]
                :language: python
                :dedent: 4
                :caption: List all of the datasource credentials under the account
        """
        return self._client.list_credentials(  # type: ignore
            cls=kwargs.pop(
                "cls",
                lambda credentials: [
                    convert_to_datasource_credential(credential)
                    for credential in credentials
                ],
            ),
            **kwargs
        )

    @distributed_trace_async
    async def update_datasource_credential(
        self,
        datasource_credential,  # type: DatasourceCredentialUnion
        **kwargs  # type: Any
    ):
        # type: (...) -> DatasourceCredentialUnion
        """Update a credential entity.

        :param datasource_credential: The new datasource credential object
        :type datasource_credential: Union[~azure.ai.metricsadvisor.models.DatasourceSqlConnectionString,
            ~azure.ai.metricsadvisor.models.DatasourceDataLakeGen2SharedKey,
            ~azure.ai.metricsadvisor.models.DatasourceServicePrincipal,
            ~azure.ai.metricsadvisor.models.DatasourceServicePrincipalInKeyVault]
        :rtype: Union[~azure.ai.metricsadvisor.models.DatasourceSqlConnectionString,
            ~azure.ai.metricsadvisor.models.DatasourceDataLakeGen2SharedKey,
            ~azure.ai.metricsadvisor.models.DatasourceServicePrincipal,
            ~azure.ai.metricsadvisor.models.DatasourceServicePrincipalInKeyVault]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_datasource_credentials_async.py
                :start-after: [START update_datasource_credential_async]
                :end-before: [END update_datasource_credential_async]
                :language: python
                :dedent: 4
                :caption: Update an existing datasource credential
        """

        datasource_credential_request = None
        if datasource_credential.credential_type in [
            "AzureSQLConnectionString",
            "DataLakeGen2SharedKey",
            "ServicePrincipal",
            "ServicePrincipalInKV",
        ]:
            datasource_credential_request = datasource_credential._to_generated_patch()

        updated_datasource_credential = await self._client.update_credential(  # type: ignore
            datasource_credential.id,
            datasource_credential_request,  # type: ignore
            **kwargs
        )

        return convert_to_datasource_credential(updated_datasource_credential)

    @distributed_trace_async
    async def delete_datasource_credential(
        self, *credential_id: str, **kwargs: Any
    ) -> None:
        """Delete a datasource credential by its ID.

        ::param str credential_id: Datasource credential unique ID.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_datasource_credentials_async.py
                :start-after: [START delete_datasource_credential_async]
                :end-before: [END delete_datasource_credential_async]
                :language: python
                :dedent: 4
                :caption: Delete a datasource credential by its ID
        """
        if len(credential_id) != 1:
            raise TypeError("Credential requires exactly one id.")

        await self._client.delete_credential(credential_id=credential_id[0], **kwargs)


class MetricsAdvisorClient(object):
    """Represents an client that calls restful API of Azure Metrics Advisor service.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and hostname,
        for example: https://:code:`<resource-name>`.cognitiveservices.azure.com).
    :param credential: An instance of ~azure.ai.metricsadvisor.MetricsAdvisorKeyCredential.
        which requires both subscription key and API key. Or an object which can provide an access
        token for the vault, such as a credential from :mod:`azure.identity`
    :type credential: ~azure.ai.metricsadvisor.MetricsAdvisorKeyCredential or ~azure.core.credentials.TokenCredential

    """

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, Union[MetricsAdvisorKeyCredential, AsyncTokenCredential], **Any) -> None
        try:
            if not endpoint.lower().startswith("http"):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Base URL must be a string.")

        self._endpoint = endpoint
        authentication_policy = get_authentication_policy(credential)
        self._client = _ClientAsync(
            endpoint=endpoint,
            credential=credential,  # type: ignore
            sdk_moniker=SDK_MONIKER,
            authentication_policy=authentication_policy,
            **kwargs
        )

    def __repr__(self):
        # type: () -> str
        return "<MetricsAdvisorClient [endpoint={}]>".format(repr(self._endpoint))[
            :1024
        ]

    async def __aenter__(self):
        # type: () -> MetricsAdvisorClient
        await self._client.__aenter__()  # pylint:disable=no-member
        return self

    async def __aexit__(self, *args):
        # type: (*Any) -> None
        await self._client.__aexit__(*args)  # pylint:disable=no-member

    async def close(self) -> None:
        """Close the :class:`~azure.ai.metricsadvisor.aio.MetricsAdvisorClient` session."""
        await self._client.__aexit__()

    @distributed_trace_async
    async def add_feedback(self, feedback, **kwargs):
        # type: (FeedbackUnion, Any) -> None

        """Create a new metric feedback.

        :param feedback: metric feedback.
        :type feedback: ~azure.ai.metricsadvisor.models.AnomalyFeedback or
            ~azure.ai.metricsadvisor.models.ChangePointFeedback or
            ~azure.ai.metricsadvisor.models.CommentFeedback or
            ~azure.ai.metricsadvisor.models.PeriodFeedback
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_feedback_async.py
                :start-after: [START add_feedback_async]
                :end-before: [END add_feedback_async]
                :language: python
                :dedent: 4
                :caption: Add new feedback.
        """

        return await self._client.create_metric_feedback(
            body=feedback._to_generated(), **kwargs
        )

    @distributed_trace_async
    async def get_feedback(self, feedback_id, **kwargs):
        # type: (str, Any) -> Union[MetricFeedback, FeedbackUnion]

        """Get a metric feedback by its id.

        :param str feedback_id: the id of the feedback.
        :return: The feedback object
        :rtype: ~azure.ai.metricsadvisor.models.MetricFeedback or
            ~azure.ai.metricsadvisor.models.AnomalyFeedback or
            ~azure.ai.metricsadvisor.models.ChangePointFeedback or
            ~azure.ai.metricsadvisor.models.CommentFeedback or
            ~azure.ai.metricsadvisor.models.PeriodFeedback
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_feedback_async.py
                :start-after: [START get_feedback_async]
                :end-before: [END get_feedback_async]
                :language: python
                :dedent: 4
                :caption: Get a metric feedback by its id.
        """

        feedback = await self._client.get_metric_feedback(
            feedback_id=feedback_id, **kwargs
        )

        return convert_to_sub_feedback(feedback)

    @distributed_trace
    def list_feedback(
        self,
        metric_id,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> AsyncItemPaged[Union[MetricFeedback, FeedbackUnion]]

        """List feedback on the given metric.

        :param str metric_id: filter feedbacks by metric id
        :keyword int skip:
        :keyword dimension_key: filter specfic dimension name and values
        :paramtype dimension_key: dict[str, str]
        :keyword feedback_type: filter feedbacks by type. Possible values include: "Anomaly",
                "ChangePoint", "Period", "Comment".
        :paramtype feedback_type: str or ~azure.ai.metricsadvisor.models.FeedbackType
        :keyword Union[str, datetime.datetime] start_time: start time filter under chosen time mode.
        :keyword Union[str, datetime.datetime] end_time: end time filter under chosen time mode.
        :keyword time_mode: time mode to filter feedback. Possible values include: "MetricTimestamp",
                "FeedbackCreatedTime".
        :paramtype time_mode: str or ~azure.ai.metricsadvisor.models.FeedbackQueryTimeMode
        :return: Pageable list of MetricFeedback
        :rtype: ~azure.core.async_paging.AsyncItemPaged[
            Union[MetricFeedback, AnomalyFeedback, ChangePointFeedback, CommentFeedback, PeriodFeedback]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_feedback_async.py
                :start-after: [START list_feedback_async]
                :end-before: [END list_feedback_async]
                :language: python
                :dedent: 4
                :caption: List feedback on the given metric.
        """

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

        return self._client.list_metric_feedbacks(  # type: ignore
            skip=skip,
            body=feedback_filter,
            cls=kwargs.pop(
                "cls", lambda result: [convert_to_sub_feedback(x) for x in result]
            ),
            **kwargs
        )

    @distributed_trace
    def list_incident_root_causes(
        self, detection_configuration_id, incident_id, **kwargs
    ):
        # type: (str, str, Any) -> AsyncItemPaged[IncidentRootCause]

        """Query root cause for incident.

        :param detection_configuration_id: anomaly detection configuration unique id.
        :type detection_configuration_id: str
        :param incident_id: incident id.
        :type incident_id: str
        :return: Pageable of root cause for incident
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.ai.metricsadvisor.models.IncidentRootCause]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_incidents_async.py
                :start-after: [START list_incident_root_cause_async]
                :end-before: [END list_incident_root_cause_async]
                :language: python
                :dedent: 4
                :caption: Query incident root causes.
        """

        return self._client.get_root_cause_of_incident_by_anomaly_detection_configuration(  # type: ignore
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
        # type: (...) -> AsyncItemPaged[MetricEnrichedSeriesData]
        """Query series enriched by anomaly detection.

        :param str detection_configuration_id: anomaly alerting configuration unique id.
        :param series: List of dimensions specified for series.
        :type series: ~azure.ai.metricsadvisor.models.SeriesIdentity or list[dict[str, str]]
        :param Union[str, datetime.datetime] start_time: start time filter under chosen time mode.
        :param Union[str, datetime.datetime] end_time: end time filter under chosen time mode.
        :return: Pageable of MetricEnrichedSeriesData
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.ai.metricsadvisor.models.MetricEnrichedSeriesData]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_queries_async.py
                :start-after: [START list_metric_enriched_series_data_async]
                :end-before: [END list_metric_enriched_series_data_async]
                :language: python
                :dedent: 4
                :caption: Query metric enriched series data.
        """

        series_list = [
            SeriesIdentity(dimension=dimension)
            for dimension in series
            if isinstance(dimension, dict)
        ] or series

        series_list = cast(List[SeriesIdentity], series_list)
        converted_start_time = convert_datetime(start_time)
        converted_end_time = convert_datetime(end_time)
        detection_series_query = DetectionSeriesQuery(
            start_time=converted_start_time,
            end_time=converted_end_time,
            series=series_list,
        )

        return self._client.get_series_by_anomaly_detection_configuration(  # type: ignore
            configuration_id=detection_configuration_id,
            body=detection_series_query,
            cls=kwargs.pop(
                "cls",
                lambda series: [
                    MetricEnrichedSeriesData._from_generated(data) for data in series
                ],
            ),
            **kwargs
        )

    @distributed_trace
    def list_alerts(
        self,
        alert_configuration_id,  # type: str
        start_time,  # type: Union[str, datetime.datetime]
        end_time,  # type: Union[str, datetime.datetime]
        time_mode,  # type: Union[str, AlertQueryTimeMode]
        **kwargs  # type: Any
    ):
        # type: (...) -> AsyncItemPaged[AnomalyAlert]
        """Query alerts under anomaly alert configuration.

        :param alert_configuration_id: anomaly alert configuration unique id.
        :type alert_configuration_id: str
        :param Union[str, datetime.datetime] start_time: start time.
        :param Union[str, datetime.datetime] end_time: end time.
        :param time_mode: time mode. Possible values include: "AnomalyTime", "CreatedTime",
                "ModifiedTime".
        :type time_mode: str or ~azure.ai.metricsadvisor.models.AlertQueryTimeMode
        :keyword int skip:
        :return: AnomalyAlerts under anomaly alert configuration.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.ai.metricsadvisor.models.AnomalyAlert]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_alert_configuration_async.py
                :start-after: [START list_alerts_async]
                :end-before: [END list_alerts_async]
                :language: python
                :dedent: 4
                :caption: Query anomaly detection results.
        """

        skip = kwargs.pop("skip", None)
        converted_start_time = convert_datetime(start_time)
        converted_end_time = convert_datetime(end_time)

        alerting_result_query = AlertingResultQuery(
            start_time=converted_start_time,
            end_time=converted_end_time,
            time_mode=time_mode,
        )

        return self._client.get_alerts_by_anomaly_alerting_configuration(  # type: ignore
            configuration_id=alert_configuration_id,
            skip=skip,
            body=alerting_result_query,
            cls=kwargs.pop(
                "cls",
                lambda alerts: [
                    AnomalyAlert._from_generated(alert) for alert in alerts
                ],
            ),
            **kwargs
        )

    def _list_anomalies_for_alert(self, alert_configuration_id, alert_id, **kwargs):
        # type: (str, str, Any) -> AsyncItemPaged[DataPointAnomaly]

        skip = kwargs.pop("skip", None)

        return self._client.get_anomalies_from_alert_by_anomaly_alerting_configuration(  # type: ignore
            configuration_id=alert_configuration_id,
            alert_id=alert_id,
            skip=skip,
            cls=lambda objs: [DataPointAnomaly._from_generated(x) for x in objs],
            **kwargs
        )

    def _list_anomalies_for_detection_configuration(
        self,
        detection_configuration_id,  # type: str
        start_time,  # type: Union[str, datetime.datetime]
        end_time,  # type: Union[str, datetime.datetime]
        **kwargs  # type: Any
    ):
        # type: (...) -> AsyncItemPaged[DataPointAnomaly]

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

        return self._client.get_anomalies_by_anomaly_detection_configuration(  # type: ignore
            configuration_id=detection_configuration_id,
            skip=skip,
            body=detection_anomaly_result_query,
            cls=lambda objs: [DataPointAnomaly._from_generated(x) for x in objs],
            **kwargs
        )

    @overload
    def list_anomalies(
        self, alert_configuration_id: str, alert_id: str, **kwargs: Any
    ) -> AsyncItemPaged[DataPointAnomaly]:
        """Query anomalies under a specific alert.

        :param alert_configuration_id: anomaly alert configuration unique id.
        :type alert_configuration_id: str
        :param alert_id: alert id.
        :type alert_id: str
        :keyword int skip:
        :return: Anomalies under a specific alert.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.ai.metricsadvisor.models.DataPointAnomaly]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_alert_configuration_async.py
                :start-after: [START list_anomalies_for_alert_async]
                :end-before: [END list_anomalies_for_alert_async]
                :language: python
                :dedent: 4
                :caption: Query anomalies using alert id.
        """

    @overload
    def list_anomalies(
        self,
        detection_configuration_id: str,
        start_time: Union[str, datetime.datetime],
        end_time: Union[str, datetime.datetime],
        **kwargs: Any
    ) -> AsyncItemPaged[DataPointAnomaly]:
        """Query anomalies under a detection configuration.

        :param detection_configuration_id: anomaly detection configuration unique id.
        :type detection_configuration_id: str
        :param Union[str, datetime.datetime] start_time: start time filter under chosen time mode.
        :param Union[str, datetime.datetime] end_time: end time filter under chosen time mode.
        :keyword int skip:
        :keyword filter:
        :paramtype filter: ~azure.ai.metricsadvisor.models.DetectionAnomalyFilterCondition
        :return: Anomalies under anomaly detection configuration.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.ai.metricsadvisor.models.DataPointAnomaly]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def list_anomalies(self, **kwargs):
        # type: (Any) -> AsyncItemPaged[DataPointAnomaly]
        """Query anomalies under a specific alert or detection configuration.

        :keyword str alert_configuration_id: anomaly alert configuration unique id.
        :keyword str alert_id: alert id.
        :keyword str detection_configuration_id: anomaly detection configuration unique id.
        :keyword Union[str, datetime.datetime] start_time: start time filter under chosen time mode.
        :keyword Union[str, datetime.datetime] end_time: end time filter under chosen time mode.
        :keyword int skip:
        :keyword filter:
        :paramtype filter: ~azure.ai.metricsadvisor.models.DetectionAnomalyFilterCondition
        :return: Anomalies under a specific alert or detection configuration.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.ai.metricsadvisor.models.DataPointAnomaly]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
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
    def list_anomaly_dimension_values(
        self, detection_configuration_id, dimension_name, start_time, end_time, **kwargs
    ):
        # type: (str, str, Union[str, datetime.datetime], Union[str, datetime.datetime], Any) -> AsyncItemPaged[str]

        """Query dimension values of anomalies.

        :param detection_configuration_id: anomaly detection configuration unique id.
        :type detection_configuration_id: str
        :param str dimension_name: dimension to query.
        :param Union[str, datetime.datetime] start_time: start time filter under chosen time mode.
        :param Union[str, datetime.datetime] end_time: end time filter under chosen time mode.
        :keyword int skip:
        :keyword Dict[str, str] dimension_filter: filter specfic dimension name and values.
        :return: Dimension values of anomalies.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[str]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_queries_async.py
                :start-after: [START list_anomaly_dimension_values_async]
                :end-before: [END list_anomaly_dimension_values_async]
                :language: python
                :dedent: 4
                :caption: Query dimension values.
        """

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

        return self._client.get_dimension_of_anomalies_by_anomaly_detection_configuration(  # type: ignore
            configuration_id=detection_configuration_id,
            skip=skip,
            body=anomaly_dimension_query,
            **kwargs
        )

    def _list_incidents_for_alert(self, alert_configuration_id, alert_id, **kwargs):
        # type: (str, str, Any) -> AsyncItemPaged[AnomalyIncident]

        skip = kwargs.pop("skip", None)

        return self._client.get_incidents_from_alert_by_anomaly_alerting_configuration(  # type: ignore
            configuration_id=alert_configuration_id,
            alert_id=alert_id,
            skip=skip,
            cls=lambda objs: [AnomalyIncident._from_generated(x) for x in objs],
            **kwargs
        )

    def _list_incidents_for_detection_configuration(
        self,
        detection_configuration_id: str,
        start_time: Union[str, datetime.datetime],
        end_time: Union[str, datetime.datetime],
        **kwargs: Any
    ) -> AsyncItemPaged[AnomalyIncident]:

        condition = kwargs.pop("filter", None)
        filter_condition = condition._to_generated() if condition else None
        converted_start_time = convert_datetime(start_time)
        converted_end_time = convert_datetime(end_time)

        detection_incident_result_query = DetectionIncidentResultQuery(
            start_time=converted_start_time,
            end_time=converted_end_time,
            filter=filter_condition,
        )

        return self._client.get_incidents_by_anomaly_detection_configuration(  # type: ignore
            configuration_id=detection_configuration_id,
            body=detection_incident_result_query,
            cls=lambda objs: [AnomalyIncident._from_generated(x) for x in objs],
            **kwargs
        )

    @overload
    def list_incidents(
        self, alert_configuration_id: str, alert_id: str, **kwargs: Any
    ) -> AsyncItemPaged[AnomalyIncident]:

        """Query incidents under a specific alert.

        :param alert_configuration_id: anomaly alerting configuration unique id.
        :type alert_configuration_id: str
        :param alert_id: alert id.
        :type alert_id: str
        :keyword int skip:
        :return: AnomalyIncidents under a specific alert.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.ai.metricsadvisor.models.AnomalyIncident]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_incidents_async.py
                :start-after: [START list_incidents_for_alert_async]
                :end-before: [END list_incidents_for_alert_async]
                :language: python
                :dedent: 4
                :caption: Query incidents for alert.
        """

    @overload
    def list_incidents(
        self,
        detection_configuration_id: str,
        start_time: Union[str, datetime.datetime],
        end_time: Union[str, datetime.datetime],
        **kwargs: Any
    ) -> AsyncItemPaged[AnomalyIncident]:

        """Query incidents under a detection configuration.

        :param detection_configuration_id: anomaly detection configuration unique id.
        :type detection_configuration_id: str
        :param Union[str, datetime.datetime] start_time: start time filter under chosen time mode.
        :param Union[str, datetime.datetime] end_time: end time filter under chosen time mode.
        :keyword filter:
        :paramtype filter: ~azure.ai.metricsadvisor.models.DetectionIncidentFilterCondition
        :return: AnomalyIncidents under a specific alert or detection configuration.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.ai.metricsadvisor.models.AnomalyIncident]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_incidents_async.py
                :start-after: [START list_incidents_for_detection_configuration_async]
                :end-before: [END list_incidents_for_detection_configuration_async]
                :language: python
                :dedent: 4
                :caption: Query incidents for detection configuration.
        """

    @distributed_trace
    def list_incidents(self, **kwargs):
        # type: (Any) -> AsyncItemPaged[AnomalyIncident]

        """Query incidents under a specific alert or detection configuration.

        :keyword str alert_configuration_id: anomaly alerting configuration unique id.
        :keyword str alert_id: alert id.
        :keyword str detection_configuration_id: anomaly detection configuration unique id.
        :keyword Union[str, datetime.datetime] start_time: start time filter under chosen time mode.
        :keyword Union[str, datetime.datetime] end_time: end time filter under chosen time mode.
        :keyword int skip:
        :keyword filter:
        :paramtype filter: ~azure.ai.metricsadvisor.models.DetectionAnomalyFilterCondition
        :return: AnomalyIncidents under a specific alert.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.ai.metricsadvisor.models.AnomalyIncident]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
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
        # type: (str, str, Any) -> AsyncItemPaged[str]

        """List dimension from certain metric.

        :param metric_id: metric unique id.
        :type metric_id: str
        :param dimension_name: the dimension name
        :type dimension_name: str
        :keyword int skip:
        :keyword dimension_value_filter: dimension value to be filtered.
        :paramtype dimension_value_filter: str
        :return: Dimension from certain metric.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[str]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_queries_async.py
                :start-after: [START list_metric_dimension_values_async]
                :end-before: [END list_metric_dimension_values_async]
                :language: python
                :dedent: 4
                :caption: Query metric dimension values.
        """

        skip = kwargs.pop("skip", None)
        dimension_value_filter = kwargs.pop("dimension_value_filter", None)

        metric_dimension_query_options = MetricDimensionQueryOptions(
            dimension_name=dimension_name,
            dimension_value_filter=dimension_value_filter,
        )

        return self._client.get_metric_dimension(  # type: ignore
            metric_id=metric_id,
            body=metric_dimension_query_options,
            skip=skip,
            **kwargs
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
        # type: (...) -> AsyncItemPaged[MetricSeriesData]

        """Get time series data from metric.

        :param metric_id: metric unique id.
        :type metric_id: str
        :param series_keys: query specific series.
        :type series_keys: list[dict[str, str]]
        :param Union[str, datetime.datetime] start_time: start time filter under chosen time mode.
        :param Union[str, datetime.datetime] end_time: end time filter under chosen time mode.
        :return: Time series data from metric.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.ai.metricsadvisor.models.MetricSeriesData]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_queries_async.py
                :start-after: [START list_metric_series_data_async]
                :end-before: [END list_metric_series_data_async]
                :language: python
                :dedent: 4
                :caption: Query metrics series data.
        """

        converted_start_time = convert_datetime(start_time)
        converted_end_time = convert_datetime(end_time)

        metric_data_query_options = MetricDataQueryOptions(
            start_time=converted_start_time,
            end_time=converted_end_time,
            series=series_keys,
        )

        return self._client.get_metric_data(  # type: ignore
            metric_id=metric_id,
            body=metric_data_query_options,
            cls=kwargs.pop(
                "cls",
                lambda result: [
                    MetricSeriesData._from_generated(series) for series in result
                ],
            ),
            **kwargs
        )

    @distributed_trace
    def list_metric_series_definitions(self, metric_id, active_since, **kwargs):
        # type: (str, datetime.datetime, Any) -> AsyncItemPaged[MetricSeriesDefinition]

        """List series (dimension combinations) from metric.

        :param metric_id: metric unique id.
        :type metric_id: str
        :param active_since: Required. query series ingested after this time, the format should be
         yyyy-MM-ddTHH:mm:ssZ.
        :type active_since: datetime.datetime
        :keyword int skip:
        :keyword dimension_filter: filter specfic dimension name and values.
        :paramtype dimension_filter: dict[str, list[str]]
        :return: Series (dimension combinations) from metric.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.ai.metricsadvisor.models.MetricSeriesDefinition]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_queries_async.py
                :start-after: [START list_metric_series_definitions_async]
                :end-before: [END list_metric_series_definitions_async]
                :language: python
                :dedent: 4
                :caption: Query metric series definitions.
        """

        skip = kwargs.pop("skip", None)
        dimension_filter = kwargs.pop("dimension_filter", None)

        metric_series_query_options = MetricSeriesQueryOptions(
            active_since=active_since,
            dimension_filter=dimension_filter,
        )

        return self._client.get_metric_series(  # type: ignore
            metric_id=metric_id, body=metric_series_query_options, skip=skip, **kwargs
        )

    @distributed_trace
    def list_metric_enrichment_status(
        self,
        metric_id,  # type: str
        start_time,  # type: Union[str, datetime.datetime]
        end_time,  # type: Union[str, datetime.datetime]
        **kwargs  # type: Any
    ):
        # type: (...) -> AsyncItemPaged[EnrichmentStatus]

        """Query anomaly detection status.

        :param metric_id: filter feedbacks by metric id.
        :type metric_id: str
        :param Union[str, datetime.datetime] start_time: start time filter under chosen time mode.
        :param Union[str, datetime.datetime] end_time: end time filter under chosen time mode.
        :keyword int skip:
        :return: Anomaly detection status.
        :rtype: ~azure.core.async_paging.AsyncItemPaged[~azure.ai.metricsadvisor.models.EnrichmentStatus]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_queries_async.py
                :start-after: [START list_metric_enrichment_status_async]
                :end-before: [END list_metric_enrichment_status_async]
                :language: python
                :dedent: 4
                :caption: Query metric enrichment status.
        """

        skip = kwargs.pop("skip", None)
        converted_start_time = convert_datetime(start_time)
        converted_end_time = convert_datetime(end_time)
        enrichment_status_query_option = EnrichmentStatusQueryOption(
            start_time=converted_start_time,
            end_time=converted_end_time,
        )

        return self._client.get_enrichment_status_by_metric(  # type: ignore
            metric_id=metric_id,
            skip=skip,
            body=enrichment_status_query_option,
            **kwargs
        )

