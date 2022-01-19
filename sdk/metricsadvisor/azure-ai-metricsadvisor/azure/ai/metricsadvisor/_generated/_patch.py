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
import datetime
from typing import Any, List, Union
from azure.core.tracing.decorator import distributed_trace
from azure.core.paging import ItemPaged
from ._metrics_advisor_client import MetricsAdvisorClientGenerated
from ._version import SDK_MONIKER
from .models import *
from .models._patch import DataFeedSourceUnion

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

class MetricsAdvisorAdministrationClient:  # pylint:disable=too-many-public-methods

    """MetricsAdvisorAdministrationClient is used to create and manage data feeds.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and hostname,
        for example: https://:code:`<resource-name>`.cognitiveservices.azure.com).
    :param credential: An instance of ~azure.ai.metricsadvisor.MetricsAdvisorKeyCredential.
        which requires both subscription key and API key. Or an object which can provide an access
        token for the Metrics Advisor service, such as a credential from :mod:`azure.identity`
    :type credential: ~azure.ai.metricsadvisor.MetricsAdvisorKeyCredential or ~azure.core.credentials.TokenCredential

    .. admonition:: Example:

        .. literalinclude:: ../samples/sample_authentication.py
            :start-after: [START administration_client_with_metrics_advisor_credential]
            :end-before: [END administration_client_with_metrics_advisor_credential]
            :language: python
            :dedent: 4
            :caption: Authenticate MetricsAdvisorAdministrationClient with a MetricsAdvisorKeyCredential
    """

    def __init__(self, endpoint: str, credential: MetricsAdvisorKeyCredential, **kwargs: Any) -> None:

        try:
            if not endpoint.lower().startswith("http"):
                endpoint = "https://" + endpoint
            endpoint = endpoint.rstrip("/")
        except AttributeError:
            raise ValueError("Base URL must be a string.")

        self._endpoint = endpoint
        authentication_policy = get_authentication_policy(credential)
        self._client = MetricsAdvisorClientGenerated(
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

    def close(self):
        # type: () -> None
        """Close the :class:`~azure.ai.metricsadvisor.MetricsAdvisorAdministrationClient` session."""
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

            .. literalinclude:: ../samples/sample_alert_configuration.py
                :start-after: [START create_alert_config]
                :end-before: [END create_alert_config]
                :language: python
                :dedent: 4
                :caption: Create an anomaly alert configuration
        """
        return self._client.create_alert_configuration(
            name=name,
            metric_alert_configurations=metric_alert_configurations,
            hook_ids=hook_ids,
            **kwargs
        )

    @distributed_trace
    def create_data_feed(
        self,
        name: str,
        source: DataFeedSourceUnion,
        granularity: Union[str, DataFeedGranularityType, DataFeedGranularity],
        schema: Union[List[str], DataFeedSchema],
        ingestion_settings: Union[datetime.datetime, DataFeedIngestionSettings],
        **kwargs  # type: Any
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

            .. literalinclude:: ../samples/sample_data_feeds.py
                :start-after: [START create_data_feed]
                :end-before: [END create_data_feed]
                :language: python
                :dedent: 4
                :caption: Create a data feed
        """
        return self._client.create_data_feed(
            name=name,
            source=source,
            granularity=granularity,
            schema=schema,
            ingestion_settings=ingestion_settings,
            **kwargs
        )

    @distributed_trace
    def create_hook(
        self,
        hook: Union[EmailNotificationHook, WebNotificationHook],
        **kwargs: Any
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
            .. literalinclude:: ../samples/sample_hooks.py
                :start-after: [START create_hook]
                :end-before: [END create_hook]
                :language: python
                :dedent: 4
                :caption: Create a notification hook
        """
        return self._client.create_hook(
            hook=hook, **kwargs
        )

    @distributed_trace
    def create_detection_configuration(
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

            .. literalinclude:: ../samples/sample_detection_configuration.py
                :start-after: [START create_detection_config]
                :end-before: [END create_detection_config]
                :language: python
                :dedent: 4
                :caption: Create an anomaly detection configuration
        """
        return self._client.create_detection_configuration(
            name=name,
            metric_id=metric_id,
            whole_series_detection_condition=whole_series_detection_condition,
            **kwargs
        )

    @distributed_trace
    def get_data_feed(self, data_feed_id: str, **kwargs: Any) -> DataFeed:
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
        return self._client.get_data_feed(
            data_feed_id=data_feed_id,
            **kwargs
        )

    @distributed_trace
    def get_alert_configuration(
        self, alert_configuration_id: str, **kwargs: Any
    ) -> AnomalyAlertConfiguration:
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
        return self._client.get_alert_configuration(
            alert_configuration_id=alert_configuration_id,
            **kwargs
        )

    @distributed_trace
    def get_detection_configuration(
        self, detection_configuration_id: str, **kwargs: Any
    ) -> AnomalyDetectionConfiguration:
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
        return self._client.get_detection_configuration(
            detection_configuration_id=detection_configuration_id,
            **kwargs
        )

    @distributed_trace
    def get_hook(
        self,
        hook_id: str,  # type
        **kwargs: Any
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

            .. literalinclude:: ../samples/sample_hooks.py
                :start-after: [START get_hook]
                :end-before: [END get_hook]
                :language: python
                :dedent: 4
                :caption: Get a notification hook by its ID
        """
        return self._client.get_hook(hook_id=hook_id, **kwargs)

    @distributed_trace
    def get_data_feed_ingestion_progress(
        self,
        data_feed_id: str,
        **kwargs: Any
    ) -> DataFeedIngestionProgress:
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
        return self._client.get_data_feed_ingestion_progress(
            data_feed_id=data_feed_id,
            **kwargs
        )

    @distributed_trace
    def refresh_data_feed_ingestion(
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

            .. literalinclude:: ../samples/sample_ingestion.py
                :start-after: [START refresh_data_feed_ingestion]
                :end-before: [END refresh_data_feed_ingestion]
                :language: python
                :dedent: 4
                :caption: Refresh data feed ingestion over a period of time
        """
        return self._client.refresh_data_feed_ingestion(
            data_feed_id=data_feed_id,
            start_time=start_time,
            end_time=end_time,
            **kwargs
        )

    @distributed_trace
    def delete_alert_configuration(
        self, *alert_configuration_id: *str, **kwargs: Any
    ) -> None:
        """Delete an anomaly alert configuration by its ID.

        :param str alert_configuration_id: anomaly alert configuration unique id.
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
        return self._client.delete_alert_configuration(
            *alert_configuration_id, **kwargs
        )

    @distributed_trace
    def delete_detection_configuration(
        self, *detection_configuration_id: *str, **kwargs: Any
    ) -> None:
        """Delete an anomaly detection configuration by its ID.

        :param str detection_configuration_id: anomaly detection configuration unique id.
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
        return self._client.delete_detection_configuration(
            *detection_configuration_id, **kwargs
        )

    @distributed_trace
    def delete_data_feed(self, *data_feed_id: *str, **kwargs: Any) -> None:
        """Delete a data feed by its ID.

        :param str data_feed_id: The data feed unique id.
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
        return self._client.delete_data_feed(
            *data_feed_id, **kwargs
        )

    @distributed_trace
    def delete_hook(self, *hook_id: *str, **kwargs: Any) -> None:
        """Delete a web or email hook by its ID.
        :param str hook_id: Hook unique ID.
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
        return self._client.delete_hook(
            *hook_id, **kwargs
        )

    @distributed_trace
    def update_data_feed(
        self,
        data_feed: Union[str, DataFeed],
        **kwargs: Any
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

            .. literalinclude:: ../samples/sample_data_feeds.py
                :start-after: [START update_data_feed]
                :end-before: [END update_data_feed]
                :language: python
                :dedent: 4
                :caption: Update an existing data feed
        """
        return self._client.update_data_feed(
            data_feed=data_feed,
            **kwargs
        )

    @distributed_trace
    def update_alert_configuration(
        self,
        alert_configuration: Union[str, AnomalyAlertConfiguration],
        **kwargs: Any
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

            .. literalinclude:: ../samples/sample_alert_configuration.py
                :start-after: [START update_alert_config]
                :end-before: [END update_alert_config]
                :language: python
                :dedent: 4
                :caption: Update an existing anomaly alert configuration
        """
        return self._client.update_alert_configuration(
            alert_configuration=alert_configuration,
            **kwargs
        )

    @distributed_trace
    def update_detection_configuration(
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
        return self._client.update_detection_configuration(
            detection_configuration=detection_configuration,
            **kwargs
        )

    @distributed_trace
    def update_hook(
        self,
        hook: Union[str, EmailNotificationHook, WebNotificationHook],
        **kwargs: Any
    ) -> Union[NotificationHook, EmailNotificationHook, WebNotificationHook]:
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
        return self._client.update_hook(
            hook=hook, **kwargs
        )

    @distributed_trace
    def list_hooks(
        self, **kwargs: Any
    ) -> ItemPaged[Union[NotificationHook, EmailNotificationHook, WebNotificationHook]]:
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
        return self._client.list_hooks(**kwargs)

    @distributed_trace
    def list_data_feeds(
        self, **kwargs: Any
    ) -> ItemPaged[DataFeed]:
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
        return self._client.list_data_feeds(**kwargs)

    @distributed_trace
    def list_alert_configurations(
        self,
        detection_configuration_id: str,
        **kwargs: Any
    ) -> ItemPaged[AnomalyAlertConfiguration]:
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
        return self._client.list_alert_configurations(
            detection_configuration_id=detection_configuration_id,
            **kwargs
        )

    @distributed_trace
    def list_detection_configurations(
        self,
        metric_id: str,
        **kwargs: Any
    ) -> ItemPaged[AnomalyDetectionConfiguration]:
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
        return self._client.list_detection_configurations(
            metric_id=metric_id, **kwargs
        )

    @distributed_trace
    def list_data_feed_ingestion_status(
        self,
        data_feed_id: str,
        start_time: Union[str, datetime.datetime],
        end_time: Union[str, datetime.datetime],
        **kwargs: Any
    ) -> ItemPaged[DataFeedIngestionStatus]:
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
        return self._client.list_data_feed_ingestion_status(
            data_feed_id=data_feed_id,
            start_time=start_time,
            end_time=end_time,
            **kwargs
        )

    @distributed_trace
    def get_datasource_credential(
        self,
        credential_id: str,  # type
        **kwargs: Any
    ) -> DatasourceCredentialUnion:
        """Get a datasource credential

        :param str credential_id: Data source credential entity unique ID.
        :return: The datasource credential
        :rtype: Union[~azure.ai.metricsadvisor.models.DatasourceCredential,
            ~azure.ai.metricsadvisor.models.DatasourceSqlConnectionString,
            ~azure.ai.metricsadvisor.models.DatasourceDataLakeGen2SharedKey,
            ~azure.ai.metricsadvisor.models.DatasourceServicePrincipal,
            ~azure.ai.metricsadvisor.models.DatasourceServicePrincipalInKeyVault]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_datasource_credentials.py
                :start-after: [START get_datasource_credential]
                :end-before: [END get_datasource_credential]
                :language: python
                :dedent: 4
                :caption: Get a datasource credential by its ID
        """
        return self._client.get_datasource_credential(
            credential_id=credential_id, **kwargs
        )

    @distributed_trace
    def create_datasource_credential(
        self,
        datasource_credential: DatasourceCredentialUnion,
        **kwargs: Any
    ) -> DatasourceCredentialUnion:
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

            .. literalinclude:: ../samples/sample_datasource_credentials.py
                :start-after: [START create_datasource_credential]
                :end-before: [END create_datasource_credential]
                :language: python
                :dedent: 4
                :caption: Create a datasource credential
        """
        return self._client.create_datasource_credential(
            datasource_credential=datasource_credential,
            *kwargs
        )

    @distributed_trace
    def list_datasource_credentials(
        self, **kwargs: Any
    ) -> ItemPaged[DatasourceCredential]:
        """List all credential entities.

        :param skip: for paging, skipped number.
        :type skip: int
        :return: Pageable containing datasource credential
        :rtype: ~azure.core.paging.ItemPaged[Union[~azure.ai.metricsadvisor.models.DatasourceCredential,
            ~azure.ai.metricsadvisor.models.DatasourceSqlConnectionString,
            ~azure.ai.metricsadvisor.models.DatasourceDataLakeGen2SharedKey,
            ~azure.ai.metricsadvisor.models.DatasourceServicePrincipal,
            ~azure.ai.metricsadvisor.models.DatasourceServicePrincipalInKeyVault]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_datasource_credentials.py
                :start-after: [START list_datasource_credentials]
                :end-before: [END list_datasource_credentials]
                :language: python
                :dedent: 4
                :caption: List all of the datasource credentials under the account
        """
        return self._client.list_datasource_credentials(**kwargs)

    @distributed_trace
    def update_datasource_credential(
        self,
        datasource_credential: DatasourceCredential,
        **kwargs: Any
    ) -> DatasourceCredential:
        """Update a datasource credential.

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

            .. literalinclude:: ../samples/sample_datasource_credentials.py
                :start-after: [START update_datasource_credential]
                :end-before: [END update_datasource_credential]
                :language: python
                :dedent: 4
                :caption: Update an existing datasource credential
        """
        return self._client.update_datasource_credential(
            datasource_credential=datasource_credential, **kwargs
        )

    @distributed_trace
    def delete_datasource_credential(
        self, *credential_id: *str, **kwargs: Any
    ) -> None:
        """Delete a datasource credential by its ID.

        :param str credential_id: Datasource credential unique ID.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_datasource_credentials.py
                :start-after: [START delete_datasource_credential]
                :end-before: [END delete_datasource_credential]
                :language: python
                :dedent: 4
                :caption: Delete a datasource credential by its ID
        """
        return self._client.delete_datasource_credential(
            *credential_id, **kwargs
        )

__all__ = ["MetricsAdvisorAdministrationClient"]
