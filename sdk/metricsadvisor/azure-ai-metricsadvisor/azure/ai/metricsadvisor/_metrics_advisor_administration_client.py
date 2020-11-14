# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=protected-access
# pylint: disable=too-many-lines

from typing import (
    Any,
    List,
    Union,
    cast,
    TYPE_CHECKING
)
import datetime
import six
from azure.core.tracing.decorator import distributed_trace
from ._generated._azure_cognitive_service_metrics_advisor_restapi_open_ap_iv2 \
    import AzureCognitiveServiceMetricsAdvisorRESTAPIOpenAPIV2 as _Client
from ._generated.models import (
    AnomalyAlertingConfiguration as _AnomalyAlertingConfiguration,
    AzureApplicationInsightsDataFeed as _AzureApplicationInsightsDataFeed,
    AzureBlobDataFeed as _AzureBlobDataFeed,
    AzureCosmosDBDataFeed as _AzureCosmosDBDataFeed,
    AzureDataExplorerDataFeed as _AzureDataExplorerDataFeed,
    AzureTableDataFeed as _AzureTableDataFeed,
    HttpRequestDataFeed as _HttpRequestDataFeed,
    InfluxDBDataFeed as _InfluxDBDataFeed,
    MySqlDataFeed as _MySqlDataFeed,
    PostgreSqlDataFeed as _PostgreSqlDataFeed,
    MongoDBDataFeed as _MongoDBDataFeed,
    SQLServerDataFeed as _SQLServerDataFeed,
    AzureDataLakeStorageGen2DataFeed as _AzureDataLakeStorageGen2DataFeed,
    AzureDataLakeStorageGen2DataFeedPatch as _AzureDataLakeStorageGen2DataFeedPatch,
    ElasticsearchDataFeed as _ElasticsearchDataFeed,
    ElasticsearchDataFeedPatch as _ElasticsearchDataFeedPatch,
    AzureApplicationInsightsDataFeedPatch as _AzureApplicationInsightsDataFeedPatch,
    AzureBlobDataFeedPatch as _AzureBlobDataFeedPatch,
    AzureCosmosDBDataFeedPatch as _AzureCosmosDBDataFeedPatch,
    AzureDataExplorerDataFeedPatch as _AzureDataExplorerDataFeedPatch,
    AzureTableDataFeedPatch as _AzureTableDataFeedPatch,
    HttpRequestDataFeedPatch as _HttpRequestDataFeedPatch,
    InfluxDBDataFeedPatch as _InfluxDBDataFeedPatch,
    MySqlDataFeedPatch as _MySqlDataFeedPatch,
    PostgreSqlDataFeedPatch as _PostgreSqlDataFeedPatch,
    MongoDBDataFeedPatch as _MongoDBDataFeedPatch,
    SQLServerDataFeedPatch as _SQLServerDataFeedPatch,
    AnomalyDetectionConfiguration as _AnomalyDetectionConfiguration,
    IngestionProgressResetOptions as _IngestionProgressResetOptions,
    IngestionStatusQueryOptions as _IngestionStatusQueryOptions,
)
from ._version import SDK_MONIKER
from ._metrics_advisor_key_credential_policy import MetricsAdvisorKeyCredentialPolicy
from ._helpers import (
    convert_to_generated_data_feed_type,
    construct_alert_config_dict,
    construct_detection_config_dict,
    construct_hook_dict,
    construct_data_feed_dict,
    convert_datetime
)
from .models._models import (
    DataFeed,
    EmailNotificationHook,
    WebNotificationHook,
    AnomalyAlertConfiguration,
    AnomalyDetectionConfiguration,
    DataFeedIngestionProgress,
    AzureApplicationInsightsDataFeed,
    AzureBlobDataFeed,
    AzureCosmosDBDataFeed,
    AzureDataExplorerDataFeed,
    AzureTableDataFeed,
    HttpRequestDataFeed,
    InfluxDBDataFeed,
    MySqlDataFeed,
    PostgreSqlDataFeed,
    SQLServerDataFeed,
    MongoDBDataFeed,
    AzureDataLakeStorageGen2DataFeed,
    ElasticsearchDataFeed
)

if TYPE_CHECKING:
    from azure.core.paging import ItemPaged
    from ._metrics_advisor_key_credential import MetricsAdvisorKeyCredential
    from ._generated.models import IngestionStatus as DataFeedIngestionStatus
    from .models._models import (
        MetricAlertConfiguration,
        DataFeedGranularity,
        DataFeedGranularityType,
        DataFeedSchema,
        DataFeedIngestionSettings,
        NotificationHook,
        MetricDetectionCondition
    )

DataFeedSourceUnion = Union[
    AzureApplicationInsightsDataFeed,
    AzureBlobDataFeed,
    AzureCosmosDBDataFeed,
    AzureDataExplorerDataFeed,
    AzureTableDataFeed,
    HttpRequestDataFeed,
    InfluxDBDataFeed,
    MySqlDataFeed,
    PostgreSqlDataFeed,
    SQLServerDataFeed,
    MongoDBDataFeed,
    AzureDataLakeStorageGen2DataFeed,
    ElasticsearchDataFeed
]

DATA_FEED = {
    "SqlServer": _SQLServerDataFeed,
    "AzureApplicationInsights": _AzureApplicationInsightsDataFeed,
    "AzureBlob": _AzureBlobDataFeed,
    "AzureCosmosDB": _AzureCosmosDBDataFeed,
    "AzureDataExplorer": _AzureDataExplorerDataFeed,
    "AzureTable": _AzureTableDataFeed,
    "HttpRequest": _HttpRequestDataFeed,
    "InfluxDB": _InfluxDBDataFeed,
    "MySql": _MySqlDataFeed,
    "PostgreSql": _PostgreSqlDataFeed,
    "MongoDB": _MongoDBDataFeed,
    "AzureDataLakeStorageGen2": _AzureDataLakeStorageGen2DataFeed,
    "Elasticsearch": _ElasticsearchDataFeed
}


DATA_FEED_PATCH = {
    "SqlServer": _SQLServerDataFeedPatch,
    "AzureApplicationInsights": _AzureApplicationInsightsDataFeedPatch,
    "AzureBlob": _AzureBlobDataFeedPatch,
    "AzureCosmosDB": _AzureCosmosDBDataFeedPatch,
    "AzureDataExplorer": _AzureDataExplorerDataFeedPatch,
    "AzureTable": _AzureTableDataFeedPatch,
    "HttpRequest": _HttpRequestDataFeedPatch,
    "InfluxDB": _InfluxDBDataFeedPatch,
    "MySql": _MySqlDataFeedPatch,
    "PostgreSql": _PostgreSqlDataFeedPatch,
    "MongoDB": _MongoDBDataFeedPatch,
    "AzureDataLakeStorageGen2": _AzureDataLakeStorageGen2DataFeedPatch,
    "Elasticsearch": _ElasticsearchDataFeedPatch
}


class MetricsAdvisorAdministrationClient(object):  # pylint:disable=too-many-public-methods
    """MetricsAdvisorAdministrationClient is used to create and manage data feeds.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and hostname,
        for example: https://:code:`<resource-name>`.cognitiveservices.azure.com).
    :param credential: An instance of ~azure.ai.metricsadvisor.MetricsAdvisorKeyCredential.
        Requires both subscription key and API key.
    :type credential: ~azure.ai.metricsadvisor.MetricsAdvisorKeyCredential

    .. admonition:: Example:

        .. literalinclude:: ../samples/sample_authentication.py
            :start-after: [START administration_client_with_metrics_advisor_credential]
            :end-before: [END administration_client_with_metrics_advisor_credential]
            :language: python
            :dedent: 4
            :caption: Authenticate MetricsAdvisorAdministrationClient with a MetricsAdvisorKeyCredential
    """
    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, MetricsAdvisorKeyCredential, Any) -> None

        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Base URL must be a string.")

        if not credential:
            raise ValueError("Missing credential")

        self._endpoint = endpoint

        self._client = _Client(
            endpoint=endpoint,
            sdk_moniker=SDK_MONIKER,
            authentication_policy=MetricsAdvisorKeyCredentialPolicy(credential),
            **kwargs
        )

    def __repr__(self):
        # type: () -> str
        return "<MetricsAdvisorAdministrationClient [endpoint={}]>".format(
            repr(self._endpoint)
        )[:1024]

    def close(self):
        # type: () -> None
        """Close the :class:`~azure.ai.metricsadvisor.MetricsAdvisorAdministrationClient` session.
        """
        return self._client.close()

    def __enter__(self):
        # type: () -> MetricsAdvisorAdministrationClient
        self._client.__enter__()  # pylint: disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        self._client.__exit__(*args)  # pylint: disable=no-member

    @distributed_trace
    def create_alert_configuration(
            self, name,  # type: str
            metric_alert_configurations,  # type: List[MetricAlertConfiguration]
            hook_ids,  # type: List[str]
            **kwargs  # type: Any
    ):  # type: (...) -> AnomalyAlertConfiguration
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

            .. literalinclude:: ../samples/sample_alert_configuration.py
                :start-after: [START create_alert_config]
                :end-before: [END create_alert_config]
                :language: python
                :dedent: 4
                :caption: Create an anomaly alert configuration
        """

        cross_metrics_operator = kwargs.pop("cross_metrics_operator", None)
        response_headers = self._client.create_anomaly_alerting_configuration(  # type: ignore
            _AnomalyAlertingConfiguration(
                name=name,
                metric_alerting_configurations=[
                    config._to_generated() for config in metric_alert_configurations
                ],
                hook_ids=hook_ids,
                cross_metrics_operator=cross_metrics_operator,
                description=kwargs.pop("description", None)
            ),
            cls=lambda pipeline_response, _, response_headers: response_headers,
            **kwargs
        )

        config_id = response_headers["Location"].split("configurations/")[1]
        return self.get_alert_configuration(config_id)

    @distributed_trace
    def create_data_feed(
            self, name,  # type: str
            source,  # type: DataFeedSourceUnion
            granularity,  # type: Union[str, DataFeedGranularityType, DataFeedGranularity]
            schema,  # type: Union[List[str], DataFeedSchema]
            ingestion_settings,  # type: Union[datetime.datetime, DataFeedIngestionSettings]
            **kwargs  # type: Any
    ):  # type: (...) -> DataFeed
        """Create a new data feed.

        :param str name: Name for the data feed.
        :param source: The source of the data feed
        :type source: Union[AzureApplicationInsightsDataFeed, AzureBlobDataFeed, AzureCosmosDBDataFeed,
            AzureDataExplorerDataFeed, AzureDataLakeStorageGen2DataFeed, AzureTableDataFeed, HttpRequestDataFeed,
            InfluxDBDataFeed, MySqlDataFeed, PostgreSqlDataFeed, SQLServerDataFeed, MongoDBDataFeed,
            ElasticsearchDataFeed]
        :param granularity: Granularity type. If using custom granularity, you must instantiate a DataFeedGranularity.
        :type granularity: Union[str, ~azure.ai.metricsadvisor.models.DataFeedGranularityType,
            ~azure.ai.metricsadvisor.models.DataFeedGranularity]
        :param schema: Data feed schema. Can be passed as a list of metric names as strings or as a DataFeedSchema
            object if additional configuration is needed.
        :type schema: Union[list[str], ~azure.ai.metricsadvisor.models.DataFeedSchema]
        :param ingestion_settings: The data feed ingestions settings. Can be passed as a datetime to use for the
            ingestion begin time or as a DataFeedIngestionSettings object if additional configuration is needed.
        :type ingestion_settings: Union[~datetime.datetime, ~azure.ai.metricsadvisor.models.DataFeedIngestionSettings]
        :keyword options: Data feed options.
        :paramtype options: ~azure.ai.metricsadvisor.models.DataFeedOptions
        :return: DataFeed
        :rtype: ~azure.ai.metricsadvisor.models.DataFeed
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_data_feeds.py
                :start-after: [START create_data_feed]
                :end-before: [END create_data_feed]
                :language: python
                :dedent: 4
                :caption: Create a data feed
        """

        options = kwargs.pop("options", None)
        data_feed_type = DATA_FEED[source.data_source_type]
        data_feed_detail = convert_to_generated_data_feed_type(
            generated_feed_type=data_feed_type,
            name=name,
            source=source,
            granularity=granularity,
            schema=schema,
            ingestion_settings=ingestion_settings,
            options=options
        )

        response_headers = self._client.create_data_feed(  # type: ignore
            data_feed_detail,
            cls=lambda pipeline_response, _, response_headers: response_headers,
            **kwargs
        )
        data_feed_id = response_headers["Location"].split("dataFeeds/")[1]
        return self.get_data_feed(data_feed_id)

    @distributed_trace
    def create_hook(
            self, hook,  # type: Union[EmailNotificationHook, WebNotificationHook]
            **kwargs  # type: Any
    ):  # type: (...) -> Union[NotificationHook, EmailNotificationHook, WebNotificationHook]
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

            .. literalinclude:: ../samples/sample_hooks.py
                :start-after: [START create_hook]
                :end-before: [END create_hook]
                :language: python
                :dedent: 4
                :caption: Create a notification hook
        """

        hook_request = None
        if hook.hook_type == "Email":
            hook_request = hook._to_generated()

        if hook.hook_type == "Webhook":
            hook_request = hook._to_generated()

        response_headers = self._client.create_hook(  # type: ignore
            hook_request,  # type: ignore
            cls=lambda pipeline_response, _, response_headers: response_headers,
            **kwargs
        )
        hook_id = response_headers["Location"].split("hooks/")[1]
        return self.get_hook(hook_id)

    @distributed_trace
    def create_detection_configuration(
            self, name,  # type: str
            metric_id,  # type: str
            whole_series_detection_condition,  # type: MetricDetectionCondition
            **kwargs  # type: Any
    ):  # type: (...) -> AnomalyDetectionConfiguration
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

            .. literalinclude:: ../samples/sample_detection_configuration.py
                :start-after: [START create_detection_config]
                :end-before: [END create_detection_config]
                :language: python
                :dedent: 4
                :caption: Create an anomaly detection configuration
        """

        description = kwargs.pop("description", None)
        series_group_detection_conditions = kwargs.pop("series_group_detection_conditions", None)
        series_detection_conditions = kwargs.pop("series_detection_conditions", None)
        config = _AnomalyDetectionConfiguration(
            name=name,
            metric_id=metric_id,
            description=description,
            whole_metric_configuration=whole_series_detection_condition._to_generated(),
            dimension_group_override_configurations=[
                group._to_generated() for group in series_group_detection_conditions
            ] if series_group_detection_conditions else None,
            series_override_configurations=[
                series._to_generated() for series in series_detection_conditions]
            if series_detection_conditions else None,
        )

        response_headers = self._client.create_anomaly_detection_configuration(  # type: ignore
            config,
            cls=lambda pipeline_response, _, response_headers: response_headers,
            **kwargs
        )
        config_id = response_headers["Location"].split("configurations/")[1]
        return self.get_detection_configuration(config_id)

    @distributed_trace
    def get_data_feed(self, data_feed_id, **kwargs):
        # type: (str, Any) -> DataFeed
        """Get a data feed by its id.

        :param data_feed_id: The data feed unique id.
        :type data_feed_id: str
        :return: DataFeed
        :rtype: ~azure.ai.metricsadvisor.models.DataFeed
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_data_feeds.py
                :start-after: [START get_data_feed]
                :end-before: [END get_data_feed]
                :language: python
                :dedent: 4
                :caption: Get a single data feed by its ID
        """

        data_feed = self._client.get_data_feed_by_id(
            data_feed_id,
            **kwargs
        )
        return DataFeed._from_generated(data_feed)

    @distributed_trace
    def get_alert_configuration(self, alert_configuration_id, **kwargs):
        # type: (str, Any) -> AnomalyAlertConfiguration
        """Get a single anomaly alert configuration.

        :param alert_configuration_id: anomaly alert configuration unique id.
        :type alert_configuration_id: str
        :return: AnomalyAlertConfiguration
        :rtype: ~azure.ai.metricsadvisor.models.AnomalyAlertConfiguration
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_alert_configuration.py
                :start-after: [START get_alert_config]
                :end-before: [END get_alert_config]
                :language: python
                :dedent: 4
                :caption: Get a single anomaly alert configuration by its ID
        """

        config = self._client.get_anomaly_alerting_configuration(alert_configuration_id, **kwargs)
        return AnomalyAlertConfiguration._from_generated(config)

    @distributed_trace
    def get_detection_configuration(self, detection_configuration_id, **kwargs):
        # type: (str, Any) -> AnomalyDetectionConfiguration
        """Get a single anomaly detection configuration.

        :param detection_configuration_id: anomaly detection configuration unique id.
        :type detection_configuration_id: str
        :return: AnomalyDetectionConfiguration
        :rtype: ~azure.ai.metricsadvisor.models.AnomalyDetectionConfiguration
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_detection_configuration.py
                :start-after: [START get_detection_config]
                :end-before: [END get_detection_config]
                :language: python
                :dedent: 4
                :caption: Get a single anomaly detection configuration by its ID
        """

        config = self._client.get_anomaly_detection_configuration(detection_configuration_id, **kwargs)
        return AnomalyDetectionConfiguration._from_generated(config)

    @distributed_trace
    def get_hook(
        self,
        hook_id,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> Union[NotificationHook, EmailNotificationHook, WebNotificationHook]
        """Get a web or email hook by its id.

        :param hook_id: Hook unique ID.
        :type hook_id: str
        :return: EmailNotificationHook or WebNotificationHook
        :rtype: Union[~azure.ai.metricsadvisor.models.NotificationHook,
            ~azure.ai.metricsadvisor.models.EmailNotificationHook,
            ~azure.ai.metricsadvisor.models.WebNotificationHook]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_hooks.py
                :start-after: [START get_hook]
                :end-before: [END get_hook]
                :language: python
                :dedent: 4
                :caption: Get a notification hook by its ID
        """

        hook = self._client.get_hook(hook_id, **kwargs)
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
        """Get last successful data ingestion job timestamp by data feed.

        :param data_feed_id: The data feed unique id.
        :type data_feed_id: str
        :return: DataFeedIngestionProgress, containing `latest_success_timestamp`
            and `latest_active_timestamp`
        :rtype: ~azure.ai.metricsadvisor.models.DataFeedIngestionProgress
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_ingestion.py
                :start-after: [START get_data_feed_ingestion_progress]
                :end-before: [END get_data_feed_ingestion_progress]
                :language: python
                :dedent: 4
                :caption: Get the progress of data feed ingestion
        """
        ingestion_process = self._client.get_ingestion_progress(data_feed_id, **kwargs)
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

            .. literalinclude:: ../samples/sample_ingestion.py
                :start-after: [START refresh_data_feed_ingestion]
                :end-before: [END refresh_data_feed_ingestion]
                :language: python
                :dedent: 4
                :caption: Refresh data feed ingestion over a period of time
        """
        converted_start_time = convert_datetime(start_time)
        converted_end_time = convert_datetime(end_time)
        self._client.reset_data_feed_ingestion_status(
            data_feed_id,
            body=_IngestionProgressResetOptions(
                start_time=converted_start_time,
                end_time=converted_end_time
            ),
            **kwargs
        )

    @distributed_trace
    def delete_alert_configuration(self, alert_configuration_id, **kwargs):
        # type: (str, Any) -> None
        """Delete an anomaly alert configuration by its ID.

        :param alert_configuration_id: anomaly alert configuration unique id.
        :type alert_configuration_id: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_alert_configuration.py
                :start-after: [START delete_alert_config]
                :end-before: [END delete_alert_config]
                :language: python
                :dedent: 4
                :caption: Delete an anomaly alert configuration by its ID
        """

        self._client.delete_anomaly_alerting_configuration(alert_configuration_id, **kwargs)

    @distributed_trace
    def delete_detection_configuration(self, detection_configuration_id, **kwargs):
        # type: (str, Any) -> None
        """Delete an anomaly detection configuration by its ID.

        :param detection_configuration_id: anomaly detection configuration unique id.
        :type detection_configuration_id: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_detection_configuration.py
                :start-after: [START delete_detection_config]
                :end-before: [END delete_detection_config]
                :language: python
                :dedent: 4
                :caption: Delete an anomaly detection configuration by its ID
        """

        self._client.delete_anomaly_detection_configuration(detection_configuration_id, **kwargs)

    @distributed_trace
    def delete_data_feed(self, data_feed_id, **kwargs):
        # type: (str, Any) -> None
        """Delete a data feed by its ID.

        :param data_feed_id: The data feed unique id.
        :type data_feed_id: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_data_feeds.py
                :start-after: [START delete_data_feed]
                :end-before: [END delete_data_feed]
                :language: python
                :dedent: 4
                :caption: Delete a data feed by its ID
        """

        self._client.delete_data_feed(data_feed_id, **kwargs)

    @distributed_trace
    def delete_hook(self, hook_id, **kwargs):
        # type: (str, Any) -> None
        """Delete a web or email hook by its ID.

        :param hook_id: Hook unique ID.
        :type hook_id: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_hooks.py
                :start-after: [START delete_hook]
                :end-before: [END delete_hook]
                :language: python
                :dedent: 4
                :caption: Delete a hook by its ID
        """

        self._client.delete_hook(hook_id, **kwargs)

    @distributed_trace
    def update_data_feed(
            self, data_feed,  # type: Union[str, DataFeed]
            **kwargs  # type: Any
    ):  # type: (...) -> DataFeed
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
        :paramtype fill_type: str or ~azure.ai.metricsadvisor.models.DataSourceMissingDataPointFillType
        :keyword float custom_fill_value: The value of fill missing point for anomaly detection
            if "CustomValue" fill type is specified.
        :keyword list[str] admin_emails: Data feed administrator emails.
        :keyword str data_feed_description: Data feed description.
        :keyword list[str] viewer_emails: Data feed viewer emails.
        :keyword access_mode: Data feed access mode. Possible values include:
            "Private", "Public". Default value: "Private".
        :paramtype access_mode: str or ~azure.ai.metricsadvisor.models.DataFeedAccessMode
        :keyword str action_link_template: action link for alert.
        :keyword status: Data feed status. Possible values include: "Active", "Paused".
        :paramtype status: str or ~azure.ai.metricsadvisor.models.DataFeedStatus
        :keyword source: The source of the data feed for update
        :paramtype source: Union[AzureApplicationInsightsDataFeed, AzureBlobDataFeed, AzureCosmosDBDataFeed,
            AzureDataExplorerDataFeed, AzureDataLakeStorageGen2DataFeed, AzureTableDataFeed, HttpRequestDataFeed,
            InfluxDBDataFeed, MySqlDataFeed, PostgreSqlDataFeed, SQLServerDataFeed, MongoDBDataFeed,
            ElasticsearchDataFeed]
        :return: DataFeed
        :rtype: ~azure.ai.metricsadvisor.models.DataFeed
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_data_feeds.py
                :start-after: [START update_data_feed]
                :end-before: [END update_data_feed]
                :language: python
                :dedent: 4
                :caption: Update an existing data feed
        """

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
        update_kwargs["admins"] = kwargs.pop("admin_emails", unset)
        update_kwargs["viewers"] = kwargs.pop("viewer_emails", unset)
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

        self._client.update_data_feed(data_feed_id, data_feed_patch, **kwargs)
        return self.get_data_feed(data_feed_id)

    @distributed_trace
    def update_alert_configuration(
        self,
        alert_configuration,  # type: Union[str, AnomalyAlertConfiguration]
        **kwargs  # type: Any
    ):
        # type: (...) -> AnomalyAlertConfiguration
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
        :return: AnomalyAlertConfiguration
        :rtype: ~azure.ai.metricsadvisor.models.AnomalyAlertConfiguration
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_alert_configuration.py
                :start-after: [START update_alert_config]
                :end-before: [END update_alert_config]
                :language: python
                :dedent: 4
                :caption: Update an existing anomaly alert configuration
        """

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

        self._client.update_anomaly_alerting_configuration(
            alert_configuration_id,
            alert_configuration_patch,
            **kwargs
        )
        return self.get_alert_configuration(alert_configuration_id)

    @distributed_trace
    def update_detection_configuration(
        self,
        detection_configuration,  # type: Union[str, AnomalyDetectionConfiguration]
        **kwargs  # type: Any
    ):
        # type: (...) -> AnomalyDetectionConfiguration
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

            .. literalinclude:: ../samples/sample_detection_configuration.py
                :start-after: [START update_detection_config]
                :end-before: [END update_detection_config]
                :language: python
                :dedent: 4
                :caption: Update an existing anomaly detection configuration
        """

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
                series_detection_conditions=update.pop("seriesOverrideConfigurations", None)
            )

        self._client.update_anomaly_detection_configuration(
            detection_configuration_id,
            detection_config_patch,
            **kwargs
        )
        return self.get_detection_configuration(detection_configuration_id)

    @distributed_trace
    def update_hook(
        self,
        hook,  # type: Union[str, EmailNotificationHook, WebNotificationHook]
        **kwargs  # type: Any
    ):
        # type: (...) -> Union[NotificationHook, EmailNotificationHook, WebNotificationHook]
        """Update a hook. Either pass the entire EmailNotificationHook or WebNotificationHook object with the chosen
        updates, or the ID to your hook configuration with the updates passed via keyword arguments.
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
        :return: EmailNotificationHook or WebNotificationHook
        :rtype: Union[~azure.ai.metricsadvisor.models.NotificationHook,
            ~azure.ai.metricsadvisor.models.EmailNotificationHook,
            ~azure.ai.metricsadvisor.models.WebNotificationHook]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_hooks.py
                :start-after: [START update_hook]
                :end-before: [END update_hook]
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
        update_kwargs["endpoint"] = kwargs.pop('endpoint', unset)
        update_kwargs["username"] = kwargs.pop('username', unset)
        update_kwargs["password"] = kwargs.pop('password', unset)
        update_kwargs["certificateKey"] = kwargs.pop('certificate_key', unset)
        update_kwargs["certificatePassword"] = kwargs.pop('certificate_password', unset)

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
                    certificate_password=update.pop("certificatePassword", None)
                )

        self._client.update_hook(
            hook_id,
            hook_patch,
            **kwargs
        )
        return self.get_hook(hook_id)

    @distributed_trace
    def list_hooks(
        self,
        **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[Union[NotificationHook, EmailNotificationHook, WebNotificationHook]]
        """List all hooks.

        :keyword str hook_name: filter hook by its name.
        :keyword int skip:
        :return: Pageable containing EmailNotificationHook and WebNotificationHook
        :rtype: ~azure.core.paging.ItemPaged[Union[~azure.ai.metricsadvisor.models.NotificationHook,
            ~azure.ai.metricsadvisor.models.EmailNotificationHook, ~azure.ai.metricsadvisor.models.WebNotificationHook]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_hooks.py
                :start-after: [START list_hooks]
                :end-before: [END list_hooks]
                :language: python
                :dedent: 4
                :caption: List all of the notification hooks under the account
        """
        hook_name = kwargs.pop('hook_name', None)
        skip = kwargs.pop('skip', None)

        def _convert_to_hook_type(hook):
            if hook.hook_type == "Email":
                return EmailNotificationHook._from_generated(hook)
            return WebNotificationHook._from_generated(hook)

        return self._client.list_hooks(  # type: ignore
            hook_name=hook_name,
            skip=skip,
            cls=kwargs.pop("cls", lambda hooks: [_convert_to_hook_type(hook) for hook in hooks]),
            **kwargs
        )

    @distributed_trace
    def list_data_feeds(
        self,
        **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[DataFeed]
        """List all data feeds.

        :keyword str data_feed_name: filter data feed by its name.
        :keyword data_source_type: filter data feed by its source type.
        :paramtype data_source_type: str or ~azure.ai.metricsadvisor.models.DataSourceType
        :keyword granularity_type: filter data feed by its granularity.
        :paramtype granularity_type: str or ~azure.ai.metricsadvisor.models.DataFeedGranularityType
        :keyword status: filter data feed by its status.
        :paramtype status: str or ~azure.ai.metricsadvisor.models.DataFeedStatus
        :keyword str creator: filter data feed by its creator.
        :keyword int skip:
        :return: Pageable of DataFeed
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.metricsadvisor.models.DataFeed]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_data_feeds.py
                :start-after: [START list_data_feeds]
                :end-before: [END list_data_feeds]
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
        """Query all anomaly alert configurations for specific anomaly detection configuration.

        :param detection_configuration_id: anomaly detection configuration unique id.
        :type detection_configuration_id: str
        :return: Pageable of AnomalyAlertConfiguration
        :rtype: ~azure.core.paging.ItemPaged[AnomalyAlertConfiguration]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_alert_configuration.py
                :start-after: [START list_alert_configs]
                :end-before: [END list_alert_configs]
                :language: python
                :dedent: 4
                :caption: List all anomaly alert configurations for specific anomaly detection configuration
        """
        return self._client.get_anomaly_alerting_configurations_by_anomaly_detection_configuration(  # type: ignore
            detection_configuration_id,
            cls=kwargs.pop("cls", lambda confs: [
                AnomalyAlertConfiguration._from_generated(conf) for conf in confs
            ]),
            **kwargs
        )

    @distributed_trace
    def list_detection_configurations(
        self,
        metric_id,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[AnomalyDetectionConfiguration]
        """Query all anomaly detection configurations for specific metric.

        :param metric_id: metric unique id.
        :type metric_id: str
        :return: Pageable of AnomalyDetectionConfiguration
        :rtype: ~azure.core.paging.ItemPaged[AnomalyDetectionConfiguration]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_detection_configuration.py
                :start-after: [START list_detection_configs]
                :end-before: [END list_detection_configs]
                :language: python
                :dedent: 4
                :caption: List all anomaly detection configurations for a specific metric
        """
        return self._client.get_anomaly_detection_configurations_by_metric(  # type: ignore
            metric_id,
            cls=kwargs.pop("cls", lambda confs: [
                AnomalyDetectionConfiguration._from_generated(conf) for conf in confs
            ]),
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
        """Get data ingestion status by data feed.

        :param str data_feed_id: The data feed unique id.
        :param start_time: Required. the start point of time range to query data ingestion status.
        :type start_time: Union[str, ~datetime.datetime]
        :param end_time: Required. the end point of time range to query data ingestion status.
        :type end_time: Union[str, ~datetime.datetime]
        :keyword int skip:
        :return: Pageable of DataFeedIngestionStatus
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.metricsadvisor.models.DataFeedIngestionStatus]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_ingestion.py
                :start-after: [START list_data_feed_ingestion_status]
                :end-before: [END list_data_feed_ingestion_status]
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
                start_time=converted_start_time,
                end_time=converted_end_time
            ),
            skip=skip,
            **kwargs
        )
