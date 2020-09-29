# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint:disable=protected-access

from typing import List, Union, Dict, Any, cast, TYPE_CHECKING
import datetime

from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    AsyncBearerTokenCredentialPolicy,
    DistributedTracingPolicy,
    RequestIdPolicy,
    ContentDecodePolicy,
    HttpLoggingPolicy,
)
from azure.core.pipeline.transport import AioHttpTransport
from azure.core.exceptions import ClientAuthenticationError
from .._metrics_advisor_key_credential import MetricsAdvisorKeyCredential
from .._metrics_advisor_key_credential_policy import MetricsAdvisorKeyCredentialPolicy
from .._generated.aio._configuration import AzureCognitiveServiceMetricsAdvisorRESTAPIOpenAPIV2Configuration
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
    TimeMode,
    SeriesIdentity,
    FeedbackDimensionFilter,
)
from .._generated.aio import AzureCognitiveServiceMetricsAdvisorRESTAPIOpenAPIV2
from .._helpers import convert_to_sub_feedback
from ..models._models import (
    Incident,
    Anomaly,
    MetricSeriesData,
    Alert,
    IncidentRootCause
)
from .._version import SDK_MONIKER

if TYPE_CHECKING:
    from azure.core.async_paging import AsyncItemPaged
    from .._generated.models import (
        SeriesResult,
        EnrichmentStatus,
        MetricSeriesItem as MetricSeriesDefinition
    )
    from ..models._models import (
        AnomalyFeedback,
        ChangePointFeedback,
        CommentFeedback,
        PeriodFeedback
    )

class MetricsAdvisorClient(object):
    """Represents an client that calls restful API of Azure Metrics Advisor service.

        :param str endpoint: Url to the Azure Metrics Advisor service endpoint
        :param credential: credential Used to authenticate requests to the service.
        :type credential: azure.ai.metricsadvisor.MetricsAdvisorKeyCredential
        :keyword Pipeline pipeline: If omitted, the standard pipeline is used.
        :keyword HttpTransport transport: If omitted, the standard pipeline is used.
        :keyword list[HTTPPolicy] policies: If omitted, the standard pipeline is used.

    """
    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, MetricsAdvisorKeyCredential, dict) -> None
        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Base URL must be a string.")

        if not credential:
            raise ValueError("Missing credential")

        self._config = AzureCognitiveServiceMetricsAdvisorRESTAPIOpenAPIV2Configuration(endpoint=endpoint, **kwargs)
        self._endpoint = endpoint
        self._credential = credential
        self._config.user_agent_policy = UserAgentPolicy(
            base_user_agent=None, sdk_moniker=SDK_MONIKER, **kwargs
        )

        pipeline = kwargs.get("pipeline")

        if pipeline is None:
            aad_mode = not isinstance(credential, MetricsAdvisorKeyCredential)
            pipeline = self._create_pipeline(
                credential=credential,
                aad_mode=aad_mode,
                endpoint=endpoint,
                **kwargs)

        self._client = AzureCognitiveServiceMetricsAdvisorRESTAPIOpenAPIV2(
            endpoint=endpoint, pipeline=pipeline
        )

    def __repr__(self):
        # type: () -> str
        return "<MetricsAdvisorClient [endpoint={}]>".format(
            repr(self._endpoint)
        )[:1024]

    async def __aenter__(self):
        # type: () -> MetricsAdvisorClient
        await self._client.__aenter__()  # pylint:disable=no-member
        return self

    async def __aexit__(self, *args):
        # type: (*Any) -> None
        await self._client.__aexit__(*args)  # pylint:disable=no-member

    async def close(self) -> None:
        """Close the :class:`~azure.ai.metricsadvisor.aio.MetricsAdvisorClient` session.
        """
        await self._client.__aexit__()

    def _create_pipeline(self, credential, endpoint=None, aad_mode=False, **kwargs):
        transport = kwargs.get('transport')
        policies = kwargs.get('policies')

        if policies is None:  # [] is a valid policy list
            if aad_mode:
                scope = endpoint.strip("/") + "/.default"
                if hasattr(credential, "get_token"):
                    credential_policy = AsyncBearerTokenCredentialPolicy(credential, scope)
                else:
                    raise TypeError("Please provide an instance from azure-identity "
                                    "or a class that implement the 'get_token protocol")
            else:
                credential_policy = MetricsAdvisorKeyCredentialPolicy(credential)
            policies = [
                RequestIdPolicy(**kwargs),
                self._config.headers_policy,
                self._config.user_agent_policy,
                self._config.proxy_policy,
                ContentDecodePolicy(**kwargs),
                self._config.redirect_policy,
                self._config.retry_policy,
                credential_policy,
                self._config.logging_policy,  # HTTP request/response log
                DistributedTracingPolicy(**kwargs),
                self._config.http_logging_policy or HttpLoggingPolicy(**kwargs)
            ]

        if not transport:
            transport = AioHttpTransport(**kwargs)

        return AsyncPipeline(transport, policies)

    @distributed_trace_async
    async def add_feedback(self, feedback, **kwargs):
        # type: (Union[AnomalyFeedback, ChangePointFeedback, CommentFeedback, PeriodFeedback], Any) -> None

        """Create a new metric feedback.

        :param feedback: metric feedback.
        :type feedback: ~azure.ai.metriscadvisor.models.AnomalyFeedback or
            ~azure.ai.metriscadvisor.models.ChangePointFeedback or
            ~azure.ai.metriscadvisor.models.CommentFeedback or
            ~azure.ai.metriscadvisor.models.PeriodFeedback.
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_feedback_async.py
                :start-after: [START add_feedback_async]
                :end-before: [END add_feedback_async]
                :language: python
                :dedent: 4
                :caption: Add new feedback.
        """
        error_map = {
            401: ClientAuthenticationError
        }

        return await self._client.create_metric_feedback(
            body=feedback._to_generated(),
            error_map=error_map,
            **kwargs)

    @distributed_trace_async
    async def get_feedback(self, feedback_id, **kwargs):
        # type: (str, Any) -> Union[AnomalyFeedback, ChangePointFeedback, CommentFeedback, PeriodFeedback]

        """Get a metric feedback by its id.

        :param str feedback_id: the id of the feedback.
        :return: The feedback object
        :rtype: ~azure.ai.metriscadvisor.models.AnomalyFeedback or
            ~azure.ai.metriscadvisor.models.ChangePointFeedback or
            ~azure.ai.metriscadvisor.models.CommentFeedback or
            ~azure.ai.metriscadvisor.models.PeriodFeedback.
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_feedback_async.py
                :start-after: [START get_feedback_async]
                :end-before: [END get_feedback_async]
                :language: python
                :dedent: 4
                :caption: Get a metric feedback by its id.
        """
        error_map = {
            401: ClientAuthenticationError
        }

        feedback = await self._client.get_metric_feedback(
            feedback_id=feedback_id,
            error_map=error_map,
            **kwargs)

        return convert_to_sub_feedback(feedback)

    @distributed_trace
    def list_feedbacks(
        self, metric_id,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> AsyncItemPaged[Union[AnomalyFeedback, ChangePointFeedback, CommentFeedback, PeriodFeedback]]

        """List feedback on the given metric.

        :param str metric_id: filter feedbacks by metric id
        :keyword int skip:
        :keyword dimension_key: filter specfic dimension name and values
        :paramtype dimension_key: dict[str, str]
        :keyword feedback_type: filter feedbacks by type. Possible values include: "Anomaly",
                "ChangePoint", "Period", "Comment".
        :paramtype feedback_type: str or ~azure.ai.metricsadvisor.models.FeedbackType
        :keyword ~datetime.datetime start_time: start time filter under chosen time mode.
        :keyword ~datetime.datetime end_time: end time filter under chosen time mode.
        :keyword time_mode: time mode to filter feedback. Possible values include: "MetricTimestamp",
                "FeedbackCreatedTime".
        :paramtype time_mode: str or ~azure.ai.metricsadvisor.models.FeedbackQueryTimeMode
        :return: Pageable list of MetricFeedback
        :rtype: ~azure.core.paging.AsyncItemPaged[~azure.ai.metricsadvisor.models.MetricFeedback]
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_feedback_async.py
                :start-after: [START list_feedback_async]
                :end-before: [END list_feedback_async]
                :language: python
                :dedent: 4
                :caption: List feedback on the given metric.
        """
        error_map = {
            401: ClientAuthenticationError
        }

        skip = kwargs.pop('skip', None)
        dimension_filter = None
        dimension_key = kwargs.pop('dimension_key', None)
        if dimension_key:
            dimension_filter = FeedbackDimensionFilter(dimension=dimension_key)
        feedback_type = kwargs.pop('feedback_type', None)
        start_time = kwargs.pop('start_time', None)
        end_time = kwargs.pop('end_time', None)
        time_mode = kwargs.pop('time_mode', None)
        feedback_filter = MetricFeedbackFilter(
            metric_id=metric_id,
            dimension_filter=dimension_filter,
            feedback_type=feedback_type,
            start_time=start_time,
            end_time=end_time,
            time_mode=time_mode,
        )

        return self._client.list_metric_feedbacks(  # type: ignore
            skip=skip,
            body=feedback_filter,
            cls=kwargs.pop("cls", lambda result: [
                convert_to_sub_feedback(x) for x in result
            ]),
            error_map=error_map,
            **kwargs)

    @distributed_trace
    def list_incident_root_causes(self, detection_configuration_id, incident_id, **kwargs):
        # type: (str, str, Any) -> AsyncItemPaged[IncidentRootCause]

        """Query root cause for incident.

        :param detection_configuration_id: anomaly detection configuration unique id.
        :type detection_configuration_id: str
        :param incident_id: incident id.
        :type incident_id: str
        :return: Pageable of root cause for incident
        :rtype: AsyncItemPaged[~azure.ai.metriscadvisor.models.IncidentRootCause]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        error_map = {
            401: ClientAuthenticationError
        }
        return self._client.get_root_cause_of_incident_by_anomaly_detection_configuration(  # type: ignore
            configuration_id=detection_configuration_id,
            incident_id=incident_id,
            error_map=error_map,
            cls=kwargs.pop("cls", lambda result: [
                IncidentRootCause._from_generated(x) for x in result
            ]),
            **kwargs
        )

    @distributed_trace
    def list_metric_enriched_series_data(
        self, detection_configuration_id,  # type: str
        series,  # type: Union[List[SeriesIdentity], List[Dict[str, str]]]
        start_time,  # type: datetime.datetime
        end_time,  # type: datetime.datetime
        **kwargs  # type: Any
    ):
        # type: (...) -> AsyncItemPaged[SeriesResult]
        """Query series enriched by anomaly detection.

        :param str detection_configuration_id: anomaly alerting configuration unique id.
        :param series: List of dimensions specified for series.
        :type series: ~azure.ai.metricsadvisor.models.SeriesIdentity or list[dict[str, str]]
        :param ~datetime.datetime start_time: start time filter under chosen time mode.
        :param ~datetime.datetime end_time: end time filter under chosen time mode.
        :return: Pageable of SeriesResult
        :rtype: AsyncItemPaged[~azure.ai.metricsadvisor.models.SeriesResult]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        error_map = {
            401: ClientAuthenticationError
        }

        series_list = [
                SeriesIdentity(dimension=dimension)
                for dimension in series
                if isinstance(dimension, dict)
            ] or series

        series_list = cast(List[SeriesIdentity], series_list)
        detection_series_query = DetectionSeriesQuery(
            start_time=start_time,
            end_time=end_time,
            series=series_list
        )

        return self._client.get_series_by_anomaly_detection_configuration(  # type: ignore
            configuration_id=detection_configuration_id,
            body=detection_series_query,
            error_map=error_map,
            **kwargs)

    @distributed_trace
    def list_alerts_for_alert_configuration(self, alert_configuration_id, start_time, end_time, time_mode, **kwargs):
        # type: (str, datetime.datetime, datetime.datetime, Union[str, TimeMode], Any) -> AsyncItemPaged[Alert]
        """Query alerts under anomaly alert configuration.

        :param alert_configuration_id: anomaly alert configuration unique id.
        :type alert_configuration_id: str
        :param ~datetime.datetime start_time: start time.
        :param ~datetime.datetime end_time: end time.
        :param time_mode: time mode. Possible values include: "AnomalyTime", "CreatedTime",
                "ModifiedTime".
        :type time_mode: str or ~azure.ai.metricsadvisor.models.TimeMode
        :keyword int skip:
        :return: Alerts under anomaly alert configuration.
        :rtype: ~azure.core.paging.AsyncItemPaged[~azure.ai.metricsadvisor.models.Alert]
        :raises: ~azure.core.exceptions.HttpResponseError
        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_anomaly_alert_configuration_async.py
                :start-after: [START list_alerts_for_alert_config_async]
                :end-before: [END list_alerts_for_alert_config_async]
                :language: python
                :dedent: 4
                :caption: Query anomaly detection results.
        """
        error_map = {
            401: ClientAuthenticationError
        }

        skip = kwargs.pop('skip', None)

        alerting_result_query = AlertingResultQuery(
            start_time=start_time,
            end_time=end_time,
            time_mode=time_mode,
        )

        return self._client.get_alerts_by_anomaly_alerting_configuration(  # type: ignore
            configuration_id=alert_configuration_id,
            skip=skip,
            body=alerting_result_query,
            error_map=error_map,
            cls=kwargs.pop("cls", lambda alerts: [Alert._from_generated(alert) for alert in alerts]),
            **kwargs)

    @distributed_trace
    def list_anomalies_for_alert(self, alert_configuration_id, alert_id, **kwargs):
        # type: (str, str, Any) -> AsyncItemPaged[Anomaly]

        """Query anomalies under a specific alert.

        :param alert_configuration_id: anomaly alert configuration unique id.
        :type alert_configuration_id: str
        :param alert_id: alert id.
        :type alert_id: str
        :keyword int skip:
        :return: Anomalies under a specific alert.
        :rtype: ~azure.core.paging.AsyncItemPaged[~azure.ai.metricsadvisor.models.Anomaly]
        :raises: ~azure.core.exceptions.HttpResponseError
        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_anomaly_alert_configuration_async.py
                :start-after: [START list_anomalies_for_alert_async]
                :end-before: [END list_anomalies_for_alert_async]
                :language: python
                :dedent: 4
                :caption: Query anomalies using alert id.
        """
        error_map = {
            401: ClientAuthenticationError
        }

        skip = kwargs.pop('skip', None)

        return self._client.get_anomalies_from_alert_by_anomaly_alerting_configuration(  # type: ignore
            configuration_id=alert_configuration_id,
            alert_id=alert_id,
            skip=skip,
            cls=lambda objs: [Anomaly._from_generated(x) for x in objs],
            error_map=error_map,
            **kwargs)

    @distributed_trace
    def list_anomalies_for_detection_configuration(self, detection_configuration_id, start_time, end_time, **kwargs):
        # type: (str, datetime.datetime, datetime.datetime, Any) -> AsyncItemPaged[Anomaly]

        """Query anomalies under anomaly detection configuration.

        :param detection_configuration_id: anomaly detection configuration unique id.
        :type detection_configuration_id: str
        :param ~datetime.datetime start_time: start time filter under chosen time mode.
        :param ~datetime.datetime end_time: end time filter under chosen time mode.
        :keyword int skip:
        :keyword filter:
        :paramtype filter: ~azure.ai.metricsadvisor.models.DetectionAnomalyFilterCondition
        :return: Anomalies under anomaly detection configuration.
        :rtype: ~azure.core.paging.AsyncItemPaged[~azure.ai.metricsadvisor.models.Anomaly]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        error_map = {
            401: ClientAuthenticationError
        }

        skip = kwargs.pop('skip', None)
        filter_condition = kwargs.pop('filter', None)
        detection_anomaly_result_query = DetectionAnomalyResultQuery(
            start_time=start_time,
            end_time=end_time,
            filter=filter_condition,
        )

        return self._client.get_anomalies_by_anomaly_detection_configuration(  # type: ignore
            configuration_id=detection_configuration_id,
            skip=skip,
            body=detection_anomaly_result_query,
            cls=lambda objs: [Anomaly._from_generated(x) for x in objs],
            error_map=error_map,
            **kwargs)

    @distributed_trace
    def list_dimension_values_for_detection_configuration(
            self, detection_configuration_id,
            dimension_name,
            start_time,
            end_time,
            **kwargs
    ):
        # type: (str, str, datetime.datetime, datetime.datetime, Any) -> AsyncItemPaged[str]

        """Query dimension values of anomalies.

        :param detection_configuration_id: anomaly detection configuration unique id.
        :type detection_configuration_id: str
        :param str dimension_name: dimension to query.
        :param ~datetime.datetime start_time: start time filter under chosen time mode.
        :param ~datetime.datetime end_time: end time filter under chosen time mode.
        :keyword int skip:
        :keyword dimension_name: str
        :paramtype dimension_filter: ~azure.ai.metricsadvisor.models.DimensionGroupIdentity
        :return: Dimension values of anomalies.
        :rtype: ~azure.core.paging.AsyncItemPaged[str]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        error_map = {
            401: ClientAuthenticationError
        }

        skip = kwargs.pop('skip', None)
        dimension_filter = kwargs.pop('dimension_filter', None)
        anomaly_dimension_query = AnomalyDimensionQuery(
            start_time=start_time,
            end_time=end_time,
            dimension_name=dimension_name,
            dimension_filter=dimension_filter,
        )

        return self._client.get_dimension_of_anomalies_by_anomaly_detection_configuration(  # type: ignore
            configuration_id=detection_configuration_id,
            skip=skip,
            body=anomaly_dimension_query,
            error_map=error_map,
            **kwargs)

    @distributed_trace
    def list_incidents_for_alert(self, alert_configuration_id, alert_id, **kwargs):
        # type: (str, str, Any) -> AsyncItemPaged[Incident]

        """Query incidents under a specific alert.

        :param alert_configuration_id: anomaly alerting configuration unique id.
        :type alert_configuration_id: str
        :param alert_id: alert id.
        :type alert_id: str
        :keyword int skip:
        :return: Incidents under a specific alert.
        :rtype: ~azure.core.paging.AsyncItemPaged[~azure.ai.metriscadvisor.models.Incident]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        error_map = {
            401: ClientAuthenticationError
        }

        skip = kwargs.pop('skip', None)

        return self._client.get_incidents_from_alert_by_anomaly_alerting_configuration(  # type: ignore
            configuration_id=alert_configuration_id,
            alert_id=alert_id,
            skip=skip,
            cls=lambda objs: [Incident._from_generated(x) for x in objs],
            error_map=error_map,
            **kwargs)

    @distributed_trace
    def list_incidents_for_detection_configuration(self, detection_configuration_id, start_time, end_time, **kwargs):
        # type: (str, datetime.datetime, datetime.datetime, Any) -> AsyncItemPaged[Incident]

        """Query incidents under a specific alert.

        :param detection_configuration_id: anomaly alerting configuration unique id.
        :type detection_configuration_id: str
        :param ~datetime.datetime start_time: start time filter under chosen time mode.
        :param ~datetime.datetime end_time: end time filter under chosen time mode.
        :keyword filter:
        :paramtype filter: ~azure.ai.metricsadvisor.models.DetectionIncidentFilterCondition
        :return: Incidents under a specific alert.
        :rtype: ~azure.core.paging.AsyncItemPaged[~azure.ai.metriscadvisor.models.Incident]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        error_map = {
            401: ClientAuthenticationError
        }

        filter_condition = kwargs.pop('filter', None)

        detection_incident_result_query = DetectionIncidentResultQuery(
            start_time=start_time,
            end_time=end_time,
            filter=filter_condition,
        )

        return self._client.get_incidents_by_anomaly_detection_configuration(  # type: ignore
            configuration_id=detection_configuration_id,
            body=detection_incident_result_query,
            cls=lambda objs: [Incident._from_generated(x) for x in objs],
            error_map=error_map,
            **kwargs)

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
        :rtype: ~azure.core.paging.AsyncItemPaged[str]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        error_map = {
            401: ClientAuthenticationError
        }

        skip = kwargs.pop('skip', None)
        dimension_value_filter = kwargs.pop('dimension_value_filter', None)

        metric_dimension_query_options = MetricDimensionQueryOptions(
            dimension_name=dimension_name,
            dimension_value_filter=dimension_value_filter,
        )

        return self._client.get_metric_dimension(  # type: ignore
            metric_id=metric_id,
            body=metric_dimension_query_options,
            skip=skip,
            error_map=error_map,
            **kwargs)

    @distributed_trace
    def list_metrics_series_data(
        self, metric_id,  # type: str
        start_time,  # type: datetime.datetime
        end_time,  # type: datetime.datetime
        series_to_filter,  # type: List[Dict[str, str]]
        **kwargs  # type: Any
    ):
        # type: (...) -> AsyncItemPaged[MetricSeriesData]

        """Get time series data from metric.

        :param metric_id: metric unique id.
        :type metric_id: str
        :param ~datetime.datetime start_time: start time filter under chosen time mode.
        :param ~datetime.datetime end_time: end time filter under chosen time mode.
        :param series_to_filter: query specific series.
        :type series_to_filter: list[dict[str, str]]
        :return: Time series data from metric.
        :rtype: AsyncItemPaged[~azure.ai.metriscadvisor.models.MetricSeriesData]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        error_map = {
            401: ClientAuthenticationError
        }

        metric_data_query_options = MetricDataQueryOptions(
            start_time=start_time,
            end_time=end_time,
            series=series_to_filter,
        )

        return self._client.get_metric_data(  # type: ignore
            metric_id=metric_id,
            body=metric_data_query_options,
            error_map=error_map,
            cls=kwargs.pop("cls", lambda result: [MetricSeriesData._from_generated(series) for series in result]),
            **kwargs)

    @distributed_trace
    def list_metric_series_definitions(self, metric_id, active_since, **kwargs):
        # type: (str, datetime.datetime, Any) -> AsyncItemPaged[MetricSeriesDefinition]

        """List series (dimension combinations) from metric.

        :param metric_id: metric unique id.
        :type metric_id: str
        :param active_since: Required. query series ingested after this time, the format should be
         yyyy-MM-ddTHH:mm:ssZ.
        :type active_since: ~datetime.datetime
        :keyword int skip:
        :keyword ~datetime.datetime active_since: query series ingested after this time, the format should be
                 yyyy-MM-ddTHH:mm:ssZ.
        :keyword dimension_filter: filter specfic dimension name and values.
        :paramtype dimension_filter: dict[str, list[str]]
        :return: Series (dimension combinations) from metric.
        :rtype: ~azure.core.paging.AsyncItemPaged[~azure.ai.metriscadvisor.models.MetricSeriesDefinition]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        error_map = {
            401: ClientAuthenticationError
        }

        skip = kwargs.pop('skip', None)
        dimension_filter = kwargs.pop('dimension_filter', None)

        metric_series_query_options = MetricSeriesQueryOptions(
            active_since=active_since,
            dimension_filter=dimension_filter,
        )

        return self._client.get_metric_series(  # type: ignore
            metric_id=metric_id,
            body=metric_series_query_options,
            skip=skip,
            error_map=error_map,
            **kwargs)

    @distributed_trace
    def list_metric_enrichment_status(self, metric_id, start_time, end_time, **kwargs):
        # type: (str, datetime.datetime, datetime.datetime, Any) -> AsyncItemPaged[EnrichmentStatus]

        """Query anomaly detection status.

        :param metric_id: filter feedbacks by metric id.
        :type metric_id: str
        :param ~datetime.datetime start_time: start time filter under chosen time mode.
        :param ~datetime.datetime end_time: end time filter under chosen time mode.
        :keyword int skip:
        :return: Anomaly detection status.
        :rtype: ~azure.core.paging.AsyncItemPaged[~azure.ai.metriscadvisor.models.EnrichmentStatus]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        error_map = {
            401: ClientAuthenticationError
        }

        skip = kwargs.pop('skip', None)
        enrichment_status_query_option = EnrichmentStatusQueryOption(
            start_time=start_time,
            end_time=end_time,
        )

        return self._client.get_enrichment_status_by_metric(  # type: ignore
            metric_id=metric_id,
            skip=skip,
            body=enrichment_status_query_option,
            error_map=error_map,
            **kwargs)
