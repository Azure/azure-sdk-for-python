# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any
from azure.core.pipeline.policies import SansIOHTTPPolicy

_API_KEY_HEADER_NAME = "Ocp-Apim-Subscription-Key"
_X_API_KEY_HEADER_NAME = "x-api-key"
from typing import Any
import six

# pylint: disable=protected-access

from typing import List, Union, Dict, Any, cast, TYPE_CHECKING, overload
from azure.core.exceptions import (
    map_error,
    HttpResponseError,
    ClientAuthenticationError,
    ResourceNotFoundError,
    ResourceExistsError,
)
from azure.core.paging import ItemPaged
from azure.core.tracing.decorator import distributed_trace
from ..models._models import (
    AnomalyIncident,
    DataPointAnomaly,
    MetricSeriesData,
    AnomalyAlert,
    IncidentRootCause,
    MetricEnrichedSeriesData,
    AnomalyFeedback,
    ChangePointFeedback,
    CommentFeedback,
    PeriodFeedback,
)
from .._version import SDK_MONIKER

if TYPE_CHECKING:
    import datetime
    from .models import (
        EnrichmentStatus,
        MetricSeriesItem as MetricSeriesDefinition,
        TimeMode as AlertQueryTimeMode,
    )
    from ..models._models import MetricFeedback
    from azure.core.paging import ItemPaged

FeedbackUnion = Union[
    AnomalyFeedback,
    ChangePointFeedback,
    CommentFeedback,
    PeriodFeedback,
]

from typing import Any, List, Union, cast, TYPE_CHECKING
import datetime
import six
from azure.core.tracing.decorator import distributed_trace
from .models import (
    AnomalyAlertingConfiguration as _AnomalyAlertingConfiguration,
    AzureApplicationInsightsDataFeed as _AzureApplicationInsightsDataFeed,
    AzureBlobDataFeed as _AzureBlobDataFeed,
    AzureCosmosDBDataFeed as _AzureCosmosDBDataFeed,
    AzureDataExplorerDataFeed as _AzureDataExplorerDataFeed,
    AzureTableDataFeed as _AzureTableDataFeed,
    AzureLogAnalyticsDataFeed as _AzureLogAnalyticsDataFeed,
    InfluxDBDataFeed as _InfluxDBDataFeed,
    MySqlDataFeed as _MySqlDataFeed,
    PostgreSqlDataFeed as _PostgreSqlDataFeed,
    MongoDBDataFeed as _MongoDBDataFeed,
    SQLServerDataFeed as _SQLServerDataFeed,
    AzureDataLakeStorageGen2DataFeed as _AzureDataLakeStorageGen2DataFeed,
    AzureDataLakeStorageGen2DataFeedPatch as _AzureDataLakeStorageGen2DataFeedPatch,
    AzureEventHubsDataFeed as _AzureEventHubsDataFeed,
    AzureEventHubsDataFeedPatch as _AzureEventHubsDataFeedPatch,
    AzureApplicationInsightsDataFeedPatch as _AzureApplicationInsightsDataFeedPatch,
    AzureBlobDataFeedPatch as _AzureBlobDataFeedPatch,
    AzureCosmosDBDataFeedPatch as _AzureCosmosDBDataFeedPatch,
    AzureDataExplorerDataFeedPatch as _AzureDataExplorerDataFeedPatch,
    AzureTableDataFeedPatch as _AzureTableDataFeedPatch,
    AzureLogAnalyticsDataFeedPatch as _AzureLogAnalyticsDataFeedPatch,
    InfluxDBDataFeedPatch as _InfluxDBDataFeedPatch,
    MySqlDataFeedPatch as _MySqlDataFeedPatch,
    PostgreSqlDataFeedPatch as _PostgreSqlDataFeedPatch,
    MongoDBDataFeedPatch as _MongoDBDataFeedPatch,
    SQLServerDataFeedPatch as _SQLServerDataFeedPatch,
    AnomalyDetectionConfiguration as _AnomalyDetectionConfiguration,
    IngestionProgressResetOptions as _IngestionProgressResetOptions,
    IngestionStatusQueryOptions as _IngestionStatusQueryOptions,
)
from .._version import SDK_MONIKER
from ..models._models import (
    DataFeed,
    EmailNotificationHook,
    WebNotificationHook,
    AnomalyAlertConfiguration,
    AnomalyDetectionConfiguration,
    DataFeedIngestionProgress,
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
    DatasourceSqlConnectionString,
    DatasourceDataLakeGen2SharedKey,
    DatasourceServicePrincipal,
    DatasourceServicePrincipalInKeyVault,
    DatasourceCredential,
)

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

DatasourceCredentialUnion = Union[
    DatasourceSqlConnectionString,
    DatasourceDataLakeGen2SharedKey,
    DatasourceServicePrincipal,
    DatasourceServicePrincipalInKeyVault,
]

DATA_FEED = {
    "SqlServer": _SQLServerDataFeed,
    "AzureApplicationInsights": _AzureApplicationInsightsDataFeed,
    "AzureBlob": _AzureBlobDataFeed,
    "AzureCosmosDB": _AzureCosmosDBDataFeed,
    "AzureDataExplorer": _AzureDataExplorerDataFeed,
    "AzureTable": _AzureTableDataFeed,
    "AzureLogAnalytics": _AzureLogAnalyticsDataFeed,
    "InfluxDB": _InfluxDBDataFeed,
    "MySql": _MySqlDataFeed,
    "PostgreSql": _PostgreSqlDataFeed,
    "MongoDB": _MongoDBDataFeed,
    "AzureDataLakeStorageGen2": _AzureDataLakeStorageGen2DataFeed,
    "AzureEventHubs": _AzureEventHubsDataFeed,
}


DATA_FEED_PATCH = {
    "SqlServer": _SQLServerDataFeedPatch,
    "AzureApplicationInsights": _AzureApplicationInsightsDataFeedPatch,
    "AzureBlob": _AzureBlobDataFeedPatch,
    "AzureCosmosDB": _AzureCosmosDBDataFeedPatch,
    "AzureDataExplorer": _AzureDataExplorerDataFeedPatch,
    "AzureTable": _AzureTableDataFeedPatch,
    "AzureEventHubs": _AzureEventHubsDataFeedPatch,
    "InfluxDB": _InfluxDBDataFeedPatch,
    "MySql": _MySqlDataFeedPatch,
    "PostgreSql": _PostgreSqlDataFeedPatch,
    "MongoDB": _MongoDBDataFeedPatch,
    "AzureDataLakeStorageGen2": _AzureDataLakeStorageGen2DataFeedPatch,
    "AzureLogAnalytics": _AzureLogAnalyticsDataFeedPatch,
}

from typing import Union, TYPE_CHECKING
import datetime
import six
from msrest import Serializer
from azure.core.exceptions import HttpResponseError
from ..models import (
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
    DatasourceServicePrincipalInKeyVault,
)

if TYPE_CHECKING:
    from .models import MetricFeedback


def construct_alert_config_dict(update_kwargs):

    if "metricAlertingConfigurations" in update_kwargs:
        update_kwargs["metricAlertingConfigurations"] = (
            [
                config._to_generated()
                for config in update_kwargs["metricAlertingConfigurations"]
            ]
            if update_kwargs["metricAlertingConfigurations"]
            else None
        )

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
            [
                group._to_generated()
                for group in update_kwargs["dimensionGroupOverrideConfigurations"]
            ]
            if update_kwargs["dimensionGroupOverrideConfigurations"]
            else None
        )
    if "seriesOverrideConfigurations" in update_kwargs:
        update_kwargs["seriesOverrideConfigurations"] = (
            [
                series._to_generated()
                for series in update_kwargs["seriesOverrideConfigurations"]
            ]
            if update_kwargs["seriesOverrideConfigurations"]
            else None
        )

    return update_kwargs


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
            update_kwargs["hookParameter"]["certificateKey"] = update_kwargs.pop(
                "certificateKey"
            )
        if "certificatePassword" in update_kwargs:
            update_kwargs["hookParameter"]["certificatePassword"] = update_kwargs.pop(
                "certificatePassword"
            )

    return update_kwargs


def construct_data_feed_dict(update_kwargs):
    if "dataStartFrom" in update_kwargs:
        update_kwargs["dataStartFrom"] = Serializer.serialize_iso(
            update_kwargs["dataStartFrom"]
        )

    if "dataSourceParameter" in update_kwargs:
        update_kwargs["authenticationType"] = update_kwargs[
            "dataSourceParameter"
        ].authentication_type
        update_kwargs["credentialId"] = update_kwargs[
            "dataSourceParameter"
        ].credential_id
        update_kwargs["dataSourceParameter"] = update_kwargs[
            "dataSourceParameter"
        ]._to_generated_patch()
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
        dimension=[dimension._to_generated() for dimension in schema.dimensions]
        if schema.dimensions
        else None,
        timestamp_column=schema.timestamp_column,
        data_start_from=ingestion_settings.ingestion_begin_time,
        max_concurrency=ingestion_settings.data_source_request_concurrency,
        min_retry_interval_in_seconds=ingestion_settings.ingestion_retry_delay,
        start_offset_in_seconds=ingestion_settings.ingestion_start_offset,
        stop_retry_after_in_seconds=ingestion_settings.stop_retry_after,
        data_feed_description=data_feed_description,
        need_rollup=DataFeedRollupType._to_generated(rollup_settings.rollup_type)
        if rollup_settings
        else None,
        roll_up_method=rollup_settings.rollup_method if rollup_settings else None,
        roll_up_columns=rollup_settings.auto_rollup_group_by_column_names
        if rollup_settings
        else None,
        all_up_identification=rollup_settings.rollup_identification_value
        if rollup_settings
        else None,
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


class MetricsAdvisorKeyCredential(object):
    """Credential type used for authenticating to an Azure Metrics Advisor service.

    :param str subscription_key: The subscription key
    :param str api_key: The api key
    :raises: TypeError
    """

    def __init__(self, subscription_key, api_key):
        # type: (str, str) -> None
        if not (
            isinstance(subscription_key, six.string_types)
            and isinstance(api_key, six.string_types)
        ):
            raise TypeError("key must be a string.")
        self._subscription_key = subscription_key  # type: str
        self._api_key = api_key  # type: str

    @property
    def subscription_key(self):
        # type: () -> str
        """The value of the subscription key.

        :rtype: str
        """
        return self._subscription_key

    @property
    def api_key(self):
        # type: () -> str
        """The value of the api key.

        :rtype: str
        """
        return self._api_key

    def update_key(self, **kwargs):
        # type: (**Any) -> None
        """Update the subscription key or the api key.

        This can be used when you've regenerated your service keys and want
        to update long-lived clients.

        :keyword str subscription_key: The subscription key
        :keyword str api_key: The api key
        :raises: ValueError or TypeError
        """
        subscription_key = kwargs.pop("subscription_key", None)
        api_key = kwargs.pop("api_key", None)
        if len(kwargs) > 0:
            raise TypeError(
                "Got an unexpected keyword argument: {}".format(list(kwargs.keys())[0])
            )
        if subscription_key:
            if not isinstance(subscription_key, six.string_types):
                raise TypeError(
                    "The subscription_key used for updating must be a string."
                )
            self._subscription_key = subscription_key
        if api_key:
            if not isinstance(api_key, six.string_types):
                raise TypeError("The api_key used for updating must be a string.")
            self._api_key = api_key

class MetricsAdvisorKeyCredentialPolicy(SansIOHTTPPolicy):
    """Adds a key header for the provided credential.

    :param credential: The credential used to authenticate requests.
    :type credential: ~azure.core.credentials.AzureKeyCredential
    :param str name: The name of the key header used for the credential.
    :raises: ValueError or TypeError
    """

    def __init__(self, credential, **kwargs):  # pylint: disable=unused-argument
        # type: (MetricsAdvisorKeyCredential, Any) -> None
        super(MetricsAdvisorKeyCredentialPolicy, self).__init__()
        self._credential = credential

    def on_request(self, request):
        request.http_request.headers[
            _API_KEY_HEADER_NAME
        ] = self._credential.subscription_key
        request.http_request.headers[_X_API_KEY_HEADER_NAME] = self._credential.api_key

class MetricsAdvisorClientCustomization(object):
    """Represents an client that calls restful API of Azure Metrics Advisor service.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and hostname,
        for example: https://:code:`<resource-name>`.cognitiveservices.azure.com).
    :param credential: An instance of ~azure.ai.metricsadvisor.MetricsAdvisorKeyCredential.
        which requires both subscription key and API key. Or an object which can provide an access
        token for the vault, such as a credential from :mod:`azure.identity`
    :type credential: ~azure.ai.metricsadvisor.MetricsAdvisorKeyCredential or ~azure.core.credentials.TokenCredential

    """

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, MetricsAdvisorKeyCredential, Any) -> None
        try:
            if not endpoint.lower().startswith("http"):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Base URL must be a string.")
        authentication_policy = get_authentication_policy(credential)
        self._endpoint = endpoint
        super(MetricsAdvisorClientCustomization, self).__init__(
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

class MetricsAdvisorClientOperationsMixinCustomization:

    @distributed_trace
    def add_feedback(self, feedback, **kwargs):
        # type: (FeedbackUnion, Any) -> None

        """Create a new metric feedback.

        :param feedback: metric feedback.
        :type feedback: ~azure.ai.metricsadvisor.models.AnomalyFeedback or
            ~azure.ai.metricsadvisor.models.ChangePointFeedback or
            ~azure.ai.metricsadvisor.models.CommentFeedback or
            ~azure.ai.metricsadvisor.models.PeriodFeedback
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_feedback.py
                :start-after: [START add_feedback]
                :end-before: [END add_feedback]
                :language: python
                :dedent: 4
                :caption: Add new feedback.
        """

        return super().add_feedback(
            body=feedback._to_generated(), **kwargs
        )
    add_feedback.metadata = {'url': '/feedback/metric'}  # type: ignore

    @distributed_trace
    def get_feedback(self, feedback_id, **kwargs):
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

            .. literalinclude:: ../samples/sample_feedback.py
                :start-after: [START get_feedback]
                :end-before: [END get_feedback]
                :language: python
                :dedent: 4
                :caption: Get a metric feedback by its id.
        """

        return convert_to_sub_feedback(
            super().get_feedback(feedback_id=feedback_id, **kwargs)
        )
    get_feedback.metadata = {'url': '/feedback/metric/{feedbackId}'}  # type: ignore

    @distributed_trace
    def list_feedback(self, metric_id, **kwargs):
        # type: (str, Any) -> ItemPaged[Union[MetricFeedback, FeedbackUnion]]

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
        :rtype: ~azure.core.paging.ItemPaged[
            Union[MetricFeedback, AnomalyFeedback, ChangePointFeedback, CommentFeedback, PeriodFeedback]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_feedback.py
                :start-after: [START list_feedback]
                :end-before: [END list_feedback]
                :language: python
                :dedent: 4
                :caption: List feedback on the given metric.
        """

        skip = kwargs.pop("skip", None)
        dimension_filter = None
        dimension_key = kwargs.pop("dimension_key", None)
        if dimension_key:
            from .models import FeedbackDimensionFilter
            dimension_filter = FeedbackDimensionFilter(dimension=dimension_key)
        feedback_type = kwargs.pop("feedback_type", None)
        start_time = kwargs.pop("start_time", None)
        end_time = kwargs.pop("end_time", None)
        converted_start_time = convert_datetime(start_time) if start_time else None
        converted_end_time = convert_datetime(end_time) if end_time else None
        time_mode = kwargs.pop("time_mode", None)
        from .models import MetricFeedbackFilter
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
            cls=kwargs.pop(
                "cls", lambda result: [convert_to_sub_feedback(x) for x in result]
            ),
            **kwargs
        )
    list_feedback.metadata = {'url': '/feedback/metric/query'}  # type: ignore

    @distributed_trace
    def list_incident_root_causes(
        self, detection_configuration_id, incident_id, **kwargs
    ):
        # type: (str, str, Any) -> ItemPaged[IncidentRootCause]

        """Query root cause for incident.

        :param detection_configuration_id: anomaly detection configuration unique id.
        :type detection_configuration_id: str
        :param incident_id: incident id.
        :type incident_id: str
        :return: Pageable of root cause for incident
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.metricsadvisor.models.IncidentRootCause]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_incidents.py
                :start-after: [START list_incident_root_cause]
                :end-before: [END list_incident_root_cause]
                :language: python
                :dedent: 4
                :caption: Query incident root causes.
        """

        return super().list_incident_root_causes(  # type: ignore
            configuration_id=detection_configuration_id,
            incident_id=incident_id,
            cls=kwargs.pop(
                "cls",
                lambda result: [IncidentRootCause._from_generated(x) for x in result],
            ),
            **kwargs
        )
    list_incident_root_causes.metadata = {'url': '/enrichment/anomalyDetection/configurations/{configurationId}/incidents/{incidentId}/rootCause'}  # type: ignore

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
        """Query series enriched by anomaly detection.

        :param str detection_configuration_id: anomaly alerting configuration unique id.
        :param series: List of dimensions specified for series.
        :type series: ~azure.ai.metricsadvisor.models.SeriesIdentity or list[dict[str, str]]
        :param Union[str, datetime.datetime] start_time: start time filter under chosen time mode.
        :param Union[str, datetime.datetime] end_time: end time filter under chosen time mode.
        :return: Pageable of MetricEnrichedSeriesData
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.metricsadvisor.models.MetricEnrichedSeriesData]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_queries.py
                :start-after: [START list_metric_enriched_series_data]
                :end-before: [END list_metric_enriched_series_data]
                :language: python
                :dedent: 4
                :caption: Query metric enriched series data.
        """
        from .models import SeriesIdentity
        series_list = [
            SeriesIdentity(dimension=dimension)
            for dimension in series
            if isinstance(dimension, dict)
        ] or series

        series_list = cast(List[SeriesIdentity], series_list)
        converted_start_time = convert_datetime(start_time)
        converted_end_time = convert_datetime(end_time)
        from .models import DetectionSeriesQuery
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
                lambda series: [
                    MetricEnrichedSeriesData._from_generated(data) for data in series
                ],
            ),
            **kwargs
        )
    list_metric_enriched_series_data.metadata = {'url': '/enrichment/anomalyDetection/configurations/{configurationId}/series/query'}  # type: ignore

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
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.metricsadvisor.models.AnomalyAlert]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_alert_configuration.py
                :start-after: [START list_alerts]
                :end-before: [END list_alerts]
                :language: python
                :dedent: 4
                :caption: Query anomaly detection results.
        """

        skip = kwargs.pop("skip", None)
        converted_start_time = convert_datetime(start_time)
        converted_end_time = convert_datetime(end_time)
        from .models import AlertingResultQuery
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
                lambda alerts: [
                    AnomalyAlert._from_generated(alert) for alert in alerts
                ],
            ),
            **kwargs
        )
    list_alerts.metadata = {'url': '/alert/anomaly/configurations/{configurationId}/alerts/query'}  # type: ignore

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

    def _list_anomalies_for_detection_configuration(
        self, detection_configuration_id, start_time, end_time, **kwargs
    ):
        # type: (...) -> ItemPaged[DataPointAnomaly]

        skip = kwargs.pop("skip", None)
        condition = kwargs.pop("filter", None)
        filter_condition = condition._to_generated() if condition else None
        converted_start_time = convert_datetime(start_time)
        converted_end_time = convert_datetime(end_time)
        from .models import DetectionAnomalyResultQuery
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

    @overload
    def list_anomalies(
        self,
        alert_configuration_id,  # type: str
        alert_id,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[DataPointAnomaly]
        """Query anomalies under a specific alert.

        :param alert_configuration_id: anomaly alert configuration unique id.
        :type alert_configuration_id: str
        :param alert_id: alert id.
        :type alert_id: str
        :keyword int skip:
        :return: Anomalies under a specific alert.
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.metricsadvisor.models.DataPointAnomaly]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_alert_configuration.py
                :start-after: [START list_anomalies_for_alert]
                :end-before: [END list_anomalies_for_alert]
                :language: python
                :dedent: 4
                :caption: Query anomalies using alert id.
        """

    @overload
    def list_anomalies(
        self,
        detection_configuration_id,  # type: str
        start_time,  # type: Union[str, datetime.datetime]
        end_time,  # type: Union[str, datetime.datetime]
        **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[DataPointAnomaly]
        """Query anomalies under a detection configuration.

        :param detection_configuration_id: anomaly detection configuration unique id.
        :type detection_configuration_id: str
        :param Union[str, datetime.datetime] start_time: start time filter under chosen time mode.
        :param Union[str, datetime.datetime] end_time: end time filter under chosen time mode.
        :keyword int skip:
        :keyword filter:
        :paramtype filter: ~azure.ai.metricsadvisor.models.DetectionAnomalyFilterCondition
        :return: Anomalies under anomaly detection configuration.
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.metricsadvisor.models.DataPointAnomaly]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def list_anomalies(self, **kwargs):
        # type: (Any) -> ItemPaged[DataPointAnomaly]
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
        # type: (str, str, Union[str, datetime.datetime], Union[str, datetime.datetime], Any) -> ItemPaged[str]

        """Query dimension values of anomalies.

        :param detection_configuration_id: anomaly detection configuration unique id.
        :type detection_configuration_id: str
        :param str dimension_name: dimension to query.
        :param Union[str, datetime.datetime] start_time: start time filter under chosen time mode.
        :param Union[str, datetime.datetime] end_time: end time filter under chosen time mode.
        :keyword int skip:
        :keyword Dict[str, str] dimension_filter: filter specfic dimension name and values.
        :return: Dimension values of anomalies.
        :rtype: ~azure.core.paging.ItemPaged[str]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_queries.py
                :start-after: [START list_anomaly_dimension_values]
                :end-before: [END list_anomaly_dimension_values]
                :language: python
                :dedent: 4
                :caption: Query dimension values.
        """

        skip = kwargs.pop("skip", None)
        dimension = kwargs.pop("dimension_filter", None)
        from .models import DimensionGroupIdentity
        dimension_filter = DimensionGroupIdentity(dimension=dimension) if dimension else None
        converted_start_time = convert_datetime(start_time)
        converted_end_time = convert_datetime(end_time)
        from .models import AnomalyDimensionQuery
        anomaly_dimension_query = AnomalyDimensionQuery(
            start_time=converted_start_time,
            end_time=converted_end_time,
            dimension_name=dimension_name,
            dimension_filter=dimension_filter,
        )

        return super().list_anomaly_dimension_values(  # type: ignore
            configuration_id=detection_configuration_id,
            skip=skip,
            body=anomaly_dimension_query,
            **kwargs
        )
    list_anomaly_dimension_values.metadata = {'url': '/enrichment/anomalyDetection/configurations/{configurationId}/anomalies/dimension/query'}  # type: ignore

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

    def _list_incidents_for_detection_configuration(
        self, detection_configuration_id, start_time, end_time, **kwargs
    ):
        # type: (str, Union[str, datetime.datetime], Union[str, datetime.datetime], Any) -> ItemPaged[AnomalyIncident]

        condition = kwargs.pop("filter", None)
        filter_condition = condition._to_generated() if condition else None
        converted_start_time = convert_datetime(start_time)
        converted_end_time = convert_datetime(end_time)
        from .models import DetectionIncidentResultQuery
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

    @overload
    def list_incidents(
        self,
        alert_configuration_id,  # type: str
        alert_id,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[AnomalyIncident]
        """Query incidents under a specific alert.

        :param alert_configuration_id: anomaly alerting configuration unique id.
        :type alert_configuration_id: str
        :param alert_id: alert id.
        :type alert_id: str
        :keyword int skip:
        :return: AnomalyIncidents under a specific alert.
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.metricsadvisor.models.AnomalyIncident]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_incidents.py
                :start-after: [START list_incidents_for_alert]
                :end-before: [END list_incidents_for_alert]
                :language: python
                :dedent: 4
                :caption: Query incidents for alert.
        """

    @overload
    def list_incidents(
        self,
        detection_configuration_id,  # type: str
        start_time,  # type: Union[str, datetime.datetime]
        end_time,  # type: Union[str, datetime.datetime]
        **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[AnomalyIncident]
        """Query incidents under a detection configuration.

        :param detection_configuration_id: anomaly detection configuration unique id.
        :type detection_configuration_id: str
        :param Union[str, datetime.datetime] start_time: start time filter under chosen time mode.
        :param Union[str, datetime.datetime] end_time: end time filter under chosen time mode.
        :keyword filter:
        :paramtype filter: ~azure.ai.metricsadvisor.models.DetectionIncidentFilterCondition
        :return: AnomalyIncidents under a specific alert.
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.metricsadvisor.models.AnomalyIncident]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_incidents.py
                :start-after: [START list_incidents_for_detection_configuration]
                :end-before: [END list_incidents_for_detection_configuration]
                :language: python
                :dedent: 4
                :caption: Query incidents for detection configuration.
        """

    @distributed_trace
    def list_incidents(self, **kwargs):
        # type: (Any) -> ItemPaged[AnomalyIncident]

        """Query incidents under a specific alert or detection configuration.

        :keyword str alert_configuration_id: anomaly alerting configuration unique id.
        :keyword str alert_id: alert id.
        :keyword str detection_configuration_id: anomaly detection configuration unique id.
        :keyword Union[str, datetime.datetime] start_time: start time filter under chosen time mode.
        :keyword Union[str, datetime.datetime] end_time: end time filter under chosen time mode.
        :keyword int skip:
        :keyword filter:
        :paramtype filter: ~azure.ai.metricsadvisor.models.DetectionAnomalyFilterCondition
        :return: AnomalyIncidents under a specific alert or detection configuration.
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
        # type: (str, str, Any) -> ItemPaged[str]

        """List dimension from certain metric.

        :param metric_id: metric unique id.
        :type metric_id: str
        :param dimension_name: the dimension name
        :type dimension_name: str
        :keyword int skip:
        :keyword dimension_value_filter: dimension value to be filtered.
        :paramtype dimension_value_filter: str
        :return: Dimension from certain metric.
        :rtype: ~azure.core.paging.ItemPaged[str]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_queries.py
                :start-after: [START list_metric_dimension_values]
                :end-before: [END list_metric_dimension_values]
                :language: python
                :dedent: 4
                :caption: Query metric dimension values.
        """

        skip = kwargs.pop("skip", None)
        dimension_value_filter = kwargs.pop("dimension_value_filter", None)
        from .models import MetricDimensionQueryOptions
        metric_dimension_query_options = MetricDimensionQueryOptions(
            dimension_name=dimension_name,
            dimension_value_filter=dimension_value_filter,
        )

        return super().list_metric_dimension_values(  # type: ignore
            metric_id=metric_id,
            body=metric_dimension_query_options,
            skip=skip,
            **kwargs
        )
    list_metric_dimension_values.metadata = {'url': '/metrics/{metricId}/dimension/query'}  # type: ignore

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

        """Get time series data from metric.

        :param metric_id: metric unique id.
        :type metric_id: str
        :param series_keys: query specific series.
        :type series_keys: list[dict[str, str]]
        :param Union[str, datetime.datetime] start_time: start time filter under chosen time mode.
        :param Union[str, datetime.datetime] end_time: end time filter under chosen time mode.
        :return: Time series data from metric.
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.metricsadvisor.models.MetricSeriesData]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_queries.py
                :start-after: [START list_metric_series_data]
                :end-before: [END list_metric_series_data]
                :language: python
                :dedent: 4
                :caption: Query metrics series data.
        """

        converted_start_time = convert_datetime(start_time)
        converted_end_time = convert_datetime(end_time)
        from .models import MetricDataQueryOptions
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
                lambda result: [
                    MetricSeriesData._from_generated(series) for series in result
                ],
            ),
            **kwargs
        )
    list_metric_series_data.metadata = {'url': '/metrics/{metricId}/data/query'}  # type: ignore

    @distributed_trace
    def list_metric_series_definitions(self, metric_id, active_since, **kwargs):
        # type: (str, datetime.datetime, Any) -> ItemPaged[MetricSeriesDefinition]

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
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.metricsadvisor.models.MetricSeriesDefinition]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_queries.py
                :start-after: [START list_metric_series_definitions]
                :end-before: [END list_metric_series_definitions]
                :language: python
                :dedent: 4
                :caption: Query metric series definitions.
        """
        from .operations._metrics_advisor_client_operations import build_list_metric_series_definitions_request
        from ._vendor import _convert_request
        skip = kwargs.pop("skip", None)
        dimension_filter = kwargs.pop("dimension_filter", None)
        from .models import MetricSeriesQueryOptions
        body = MetricSeriesQueryOptions(
            active_since=active_since,
            dimension_filter=dimension_filter,
        )
        maxpagesize = None
        content_type = kwargs.pop('content_type', "application/json")  # type: Optional[str]

        cls = kwargs.pop('cls', None)  # type: ClsType["_models.MetricSeriesList"]
        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}))
        def prepare_request(next_link=None):
            if not next_link:
                _json = self._serialize.body(body, 'MetricSeriesQueryOptions')

                request = build_list_metric_series_definitions_request(
                    metric_id=metric_id,
                    content_type=content_type,
                    json=_json,
                    skip=skip,
                    maxpagesize=maxpagesize,
                    template_url=self.list_metric_series_definitions.metadata['url'],
                )
                request = _convert_request(request)
                path_format_arguments = {
                    "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, 'str', skip_quote=True),
                }
                request.url = self._client.format_url(request.url, **path_format_arguments)

            else:
                _json = self._serialize.body(body, 'MetricSeriesQueryOptions')

                request = build_list_metric_series_definitions_request(
                    metric_id=metric_id,
                    content_type=content_type,
                    json=_json,
                    skip=skip,
                    maxpagesize=maxpagesize,
                    template_url=next_link,
                )
                request = _convert_request(request)
                path_format_arguments = {
                    "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, 'str', skip_quote=True),
                    "nextLink": self._serialize.url("next_link", next_link, "str", skip_quote=True)
                }
                request.url = self._client.format_url("{nextLink}", **path_format_arguments)
            return request

        def extract_data(pipeline_response):
            deserialized = self._deserialize("MetricSeriesList", pipeline_response)
            list_of_elem = deserialized.value
            if cls:
                list_of_elem = cls(list_of_elem)
            return deserialized.next_link or None, iter(list_of_elem)

        def get_next(next_link=None):
            request = prepare_request(next_link)

            pipeline_response = self._client._pipeline.run(request, stream=False, **kwargs)
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                error = self._deserialize.failsafe_deserialize(_models.ErrorCode, pipeline_response)
                raise HttpResponseError(response=response, model=error)

            return pipeline_response


        return ItemPaged(
            get_next, extract_data
        )
    list_metric_series_definitions.metadata = {'url': '/metrics/{metricId}/series/query'}  # type: ignore

    @distributed_trace
    def list_metric_enrichment_status(self, metric_id, start_time, end_time, **kwargs):
        # type: (str, Union[str, datetime.datetime], Union[str, datetime.datetime], Any) -> ItemPaged[EnrichmentStatus]

        """Query anomaly detection status.

        :param metric_id: filter feedbacks by metric id.
        :type metric_id: str
        :param Union[str, datetime.datetime] start_time: start time filter under chosen time mode.
        :param Union[str, datetime.datetime] end_time: end time filter under chosen time mode.
        :keyword int skip:
        :return: Anomaly detection status.
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.metricsadvisor.models.EnrichmentStatus]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_queries.py
                :start-after: [START list_metric_enrichment_status]
                :end-before: [END list_metric_enrichment_status]
                :language: python
                :dedent: 4
                :caption: Query metric enrichment status.
        """

        skip = kwargs.pop("skip", None)
        converted_start_time = convert_datetime(start_time)
        converted_end_time = convert_datetime(end_time)
        from .models import EnrichmentStatusQueryOption
        enrichment_status_query_option = EnrichmentStatusQueryOption(
            start_time=converted_start_time,
            end_time=converted_end_time,
        )

        return super().list_metric_enrichment_status(  # type: ignore
            metric_id=metric_id,
            skip=skip,
            body=enrichment_status_query_option,
            **kwargs
        )
    list_metric_enrichment_status.metadata = {'url': '/metrics/{metricId}/status/enrichment/anomalyDetection/query'}  # type: ignore

class MetricsAdvisorAdministrationClient(
    object
):  # pylint:disable=too-many-public-methods
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

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, MetricsAdvisorKeyCredential, Any) -> None

        try:
            if not endpoint.lower().startswith("http"):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Base URL must be a string.")

        self._endpoint = endpoint
        authentication_policy = get_authentication_policy(credential)
        from ._metrics_advisor_client import MetricsAdvisorClient as _Client
        self._client = _Client(
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
        name,  # type: str
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
        response_headers = super().create_alert_configuration(  # type: ignore
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

        response_headers = super().create_data_feed(  # type: ignore
            data_feed_detail,
            cls=lambda pipeline_response, _, response_headers: response_headers,
            **kwargs
        )
        data_feed_id = response_headers["Location"].split("dataFeeds/")[1]
        return self.get_data_feed(data_feed_id)

    @distributed_trace
    def create_hook(
        self,
        hook,  # type: Union[EmailNotificationHook, WebNotificationHook]
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

        response_headers = super().create_hook(  # type: ignore
            hook_request,  # type: ignore
            cls=lambda pipeline_response, _, response_headers: response_headers,
            **kwargs
        )
        hook_id = response_headers["Location"].split("hooks/")[1]
        return super().get_hook(hook_id)

    @distributed_trace
    def create_detection_configuration(
        self,
        name,  # type: str
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

        response_headers = super().create_detection_configuration(  # type: ignore
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

        data_feed = super().get_data_feed(data_feed_id, **kwargs)
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

        config = super().get_alert_configuration(
            alert_configuration_id, **kwargs
        )
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

        config = super().get_detection_configuration(
            detection_configuration_id, **kwargs
        )
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
        super().refresh_data_feed_ingestion(
            data_feed_id,
            body=_IngestionProgressResetOptions(
                start_time=converted_start_time, end_time=converted_end_time
            ),
            **kwargs
        )

    @distributed_trace
    def delete_alert_configuration(self, *alert_configuration_id, **kwargs):
        # type: (*str, Any) -> None
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
        if len(alert_configuration_id) != 1:
            raise TypeError("Alert configuration requires exactly one id.")

        super().delete_alert_configuration(
            alert_configuration_id[0], **kwargs
        )

    @distributed_trace
    def delete_detection_configuration(self, *detection_configuration_id, **kwargs):
        # type: (*str, Any) -> None
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
        if len(detection_configuration_id) != 1:
            raise TypeError("Detection configuration requires exactly one id.")

        super().delete_detection_configuration(
            detection_configuration_id[0], **kwargs
        )

    @distributed_trace
    def delete_data_feed(self, *data_feed_id, **kwargs):
        # type: (*str, Any) -> None
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
        if len(data_feed_id) != 1:
            raise TypeError("Data feed requires exactly one id.")

        super().delete_data_feed(data_feed_id[0], **kwargs)

    @distributed_trace
    def delete_hook(self, *hook_id, **kwargs):
        # type: (*str, Any) -> None
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
        if len(hook_id) != 1:
            raise TypeError("Hook requires exactly one id.")

        super().delete_hook(hook_id[0], **kwargs)

    @distributed_trace
    def update_data_feed(
        self,
        data_feed,  # type: Union[str, DataFeed]
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

        return DataFeed._from_generated(
            super().update_data_feed(data_feed_id, data_feed_patch, **kwargs)
        )

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

        return AnomalyAlertConfiguration._from_generated(
            super().update_alert_configuration(
                alert_configuration_id, alert_configuration_patch, **kwargs
            )
        )

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

        return AnomalyDetectionConfiguration._from_generated(
            super().update_detection_configuration(
                detection_configuration_id, detection_config_patch, **kwargs
            )
        )

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
        hook_name = kwargs.pop("hook_name", None)
        skip = kwargs.pop("skip", None)

        def _convert_to_hook_type(hook):
            if hook.hook_type == "Email":
                return EmailNotificationHook._from_generated(hook)
            return WebNotificationHook._from_generated(hook)

        return super().list_hooks(  # type: ignore
            hook_name=hook_name,
            skip=skip,
            cls=kwargs.pop(
                "cls", lambda hooks: [_convert_to_hook_type(hook) for hook in hooks]
            ),
            **kwargs
        )

    @distributed_trace
    def list_data_feeds(
        self, **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[DataFeed]
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
            cls=kwargs.pop(
                "cls", lambda feeds: [DataFeed._from_generated(feed) for feed in feeds]
            ),
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
        return super().list_alert_configurations(  # type: ignore
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
        return super().list_detection_configurations(  # type: ignore
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

        return super().list_data_feed_ingestion_status(  # type: ignore
            data_feed_id=data_feed_id,
            body=_IngestionStatusQueryOptions(
                start_time=converted_start_time, end_time=converted_end_time
            ),
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

        datasource_credential = super().get_datasource_credential(credential_id, **kwargs)
        return convert_to_datasource_credential(datasource_credential)

    @distributed_trace
    def create_datasource_credential(
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

            .. literalinclude:: ../samples/sample_datasource_credentials.py
                :start-after: [START create_datasource_credential]
                :end-before: [END create_datasource_credential]
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
        return super().list_datasource_credentials(  # type: ignore
            cls=kwargs.pop(
                "cls",
                lambda credentials: [
                    convert_to_datasource_credential(credential)
                    for credential in credentials
                ],
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

        datasource_credential_request = None
        if datasource_credential.credential_type in [
            "AzureSQLConnectionString",
            "DataLakeGen2SharedKey",
            "ServicePrincipal",
            "ServicePrincipalInKV",
        ]:
            datasource_credential_request = datasource_credential._to_generated_patch()

        updated_datasource_credential = super().update_datasource_credential(  # type: ignore
            datasource_credential.id,
            datasource_credential_request,  # type: ignore
            **kwargs
        )

        return convert_to_datasource_credential(updated_datasource_credential)

    @distributed_trace
    def delete_datasource_credential(self, *credential_id, **kwargs):
        # type: (*str, Any) -> None
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
        if len(credential_id) != 1:
            raise TypeError("Credential requires exactly one id.")

        super().delete_datasource_credential(credential_id=credential_id[0], **kwargs)


##################### MODELS #####################



class MetricFeedbackCustomization(dict):
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
        super().__init__(
            metric_id=metric_id,
            dimension_filter=dimension_key,
            **kwargs
        )
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

    # "AnomalyFeedback",
    # "ChangePointFeedback",
    # "CommentFeedback",
    # "PeriodFeedback",
    # "FeedbackQueryTimeMode",
    # "RootCause",
    # "AnomalyAlertConfiguration",
    # "DetectionAnomalyFilterCondition",
    # "DimensionGroupIdentity",
    # "AnomalyIncident",
    # "DetectionIncidentFilterCondition",
    # "AnomalyDetectionConfiguration",
    # "MetricAnomalyAlertConfigurationsOperator",
    # "DataFeedStatus",
    # "DataFeedGranularity",
    # "DataFeedIngestionSettings",
    # "DataFeedMissingDataPointFillSettings",
    # "DataFeedRollupSettings",
    # "DataFeedSchema",
    # "DataFeedDimension",
    # "DataFeedMetric",
    # "DataFeed",
    # "TopNGroupScope",
    # "MetricAnomalyAlertScope",
    # "MetricAlertConfiguration",
    # "SnoozeScope",
    # "AnomalySeverity",
    # "MetricAnomalyAlertSnoozeCondition",
    # "MetricBoundaryCondition",
    # "AzureApplicationInsightsDataFeedSource",
    # "AzureBlobDataFeedSource",
    # "AzureCosmosDbDataFeedSource",
    # "AzureTableDataFeedSource",
    # "AzureLogAnalyticsDataFeedSource",
    # "InfluxDbDataFeedSource",
    # "SqlServerDataFeedSource",
    # "MongoDbDataFeedSource",
    # "MySqlDataFeedSource",
    # "PostgreSqlDataFeedSource",
    # "AzureDataExplorerDataFeedSource",
    # "MetricDetectionCondition",
    # "MetricSeriesGroupDetectionCondition",
    # "MetricSingleSeriesDetectionCondition",
    # "SeverityCondition",
    # "DatasourceType",
    # "AnomalyDetectorDirection",
    # "NotificationHook",
    # "EmailNotificationHook",
    # "WebNotificationHook",
    # "DataFeedIngestionProgress",
    # "DetectionConditionOperator",
    # "MetricAnomalyAlertConditions",
    # "EnrichmentStatus",
    # "DataFeedGranularityType",
    # "DataPointAnomaly",
    # "AnomalyIncidentStatus",
    # "MetricSeriesData",
    # "MetricSeriesDefinition",
    # "AnomalyAlert",
    # "DataFeedAccessMode",
    # "DataFeedRollupType",
    # "DataFeedAutoRollupMethod",
    # "DatasourceMissingDataPointFillType",
    # "DataFeedIngestionStatus",
    # "SmartDetectionCondition",
    # "SuppressCondition",
    # "ChangeThresholdCondition",
    # "HardThresholdCondition",
    # "SeriesIdentity",
    # "AzureDataLakeStorageGen2DataFeedSource",
    # "AzureEventHubsDataFeedSource",
    # "AnomalyValue",
    # "ChangePointValue",
    # "PeriodType",
    # "FeedbackType",
    # "AlertQueryTimeMode",
    # "IncidentRootCause",
    # "SeverityFilterCondition",
    # "MetricEnrichedSeriesData",
    # "DatasourceSqlConnectionString",
    # "DatasourceDataLakeGen2SharedKey",
    # "DatasourceServicePrincipal",
    # "DatasourceServicePrincipalInKeyVault",
    # "DatasourceCredentialType",
    # "DatasourceAuthenticationType",
    # "DatasourceCredential",
    # "DataFeedSource",

def patch_sdk():
    pass