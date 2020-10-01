# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=protected-access

from typing import List, Union, Dict, Any, cast, TYPE_CHECKING
import datetime  # pylint:disable=unused-import

from azure.core.tracing.decorator import distributed_trace
from ._metrics_advisor_key_credential import MetricsAdvisorKeyCredential
from ._metrics_advisor_key_credential_policy import MetricsAdvisorKeyCredentialPolicy
from ._generated.models import (
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
    SeriesIdentity,
    FeedbackDimensionFilter,
)
from ._generated import AzureCognitiveServiceMetricsAdvisorRESTAPIOpenAPIV2
from ._helpers import convert_to_sub_feedback
from .models._models import (
    Incident,
    Anomaly,
    MetricSeriesData,
    Alert,
    IncidentRootCause
)
from ._version import SDK_MONIKER

if TYPE_CHECKING:
    from ._generated.models import (
        SeriesResult,
        EnrichmentStatus,
        MetricSeriesItem as MetricSeriesDefinition,
        TimeMode,
    )
    from .models._models import (
        AnomalyFeedback,
        ChangePointFeedback,
        CommentFeedback,
        PeriodFeedback
    )

    from azure.core.paging import ItemPaged

class MetricsAdvisorClient(object):
    """Represents an client that calls restful API of Azure Metrics Advisor service.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and hostname,
        for example: https://:code:`<resource-name>`.cognitiveservices.azure.com).
    :param credential: An instance of ~azure.ai.metricsadvisor.MetricsAdvisorKeyCredential.
        Requires both subscription key and API key.
    :type credential: ~azure.ai.metricsadvisor.MetricsAdvisorKeyCredential
    :keyword Pipeline pipeline: If omitted, the standard pipeline is used.
    :keyword HttpTransport transport: If omitted, the standard pipeline is used.
    :keyword list[HTTPPolicy] policies: If omitted, the standard pipeline is used.

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

        self._client = AzureCognitiveServiceMetricsAdvisorRESTAPIOpenAPIV2(
            endpoint=endpoint,
            sdk_moniker=SDK_MONIKER,
            authentication_policy=MetricsAdvisorKeyCredentialPolicy(credential),
            **kwargs
        )

    def __repr__(self):
        # type: () -> str
        return "<MetricsAdvisorClient [endpoint={}]>".format(
            repr(self._endpoint)
        )[:1024]

    def __enter__(self):
        # type: () -> MetricsAdvisorClient
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        self._client.__exit__(*args)  # pylint:disable=no-member

    def close(self):
        # type: () -> None
        """Close the :class:`~azure.ai.metricsadvisor.MetricsAdvisorClient` session.
        """
        return self._client.close()

    @distributed_trace
    def add_feedback(self, feedback, **kwargs):
        # type: (Union[AnomalyFeedback, ChangePointFeedback, CommentFeedback, PeriodFeedback], Any) -> None

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

        return self._client.create_metric_feedback(
            body=feedback._to_generated(),
            **kwargs)

    @distributed_trace
    def get_feedback(self, feedback_id, **kwargs):
        # type: (str, Any) -> Union[AnomalyFeedback, ChangePointFeedback, CommentFeedback, PeriodFeedback]

        """Get a metric feedback by its id.

        :param str feedback_id: the id of the feedback.
        :return: The feedback object
        :rtype: ~azure.ai.metricsadvisor.models.AnomalyFeedback or
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

        return convert_to_sub_feedback(self._client.get_metric_feedback(
            feedback_id=feedback_id,
            **kwargs))

    @distributed_trace
    def list_feedbacks(self, metric_id, **kwargs):
        # type: (str, Any) -> ItemPaged[Union[AnomalyFeedback, ChangePointFeedback, CommentFeedback, PeriodFeedback]]

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
        :rtype: ~azure.core.paging.ItemPaged[
            Union[AnomalyFeedback, ChangePointFeedback, CommentFeedback, PeriodFeedback]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_feedback.py
                :start-after: [START list_feedback]
                :end-before: [END list_feedback]
                :language: python
                :dedent: 4
                :caption: List feedback on the given metric.
        """

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
            **kwargs)

    @distributed_trace
    def list_incident_root_causes(self, detection_configuration_id, incident_id, **kwargs):
        # type: (str, str, Any) -> ItemPaged[IncidentRootCause]

        """Query root cause for incident.

        :param detection_configuration_id: anomaly detection configuration unique id.
        :type detection_configuration_id: str
        :param incident_id: incident id.
        :type incident_id: str
        :return: Pageable of root cause for incident
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.metricsadvisor.models.IncidentRootCause]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        return self._client.get_root_cause_of_incident_by_anomaly_detection_configuration(  # type: ignore
            configuration_id=detection_configuration_id,
            incident_id=incident_id,
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
        # type: (...) -> ItemPaged[SeriesResult]
        """Query series enriched by anomaly detection.

        :param str detection_configuration_id: anomaly alerting configuration unique id.
        :param series: List of dimensions specified for series.
        :type series: ~azure.ai.metricsadvisor.models.SeriesIdentity or list[dict[str, str]]
        :param ~datetime.datetime start_time: start time filter under chosen time mode.
        :param ~datetime.datetime end_time: end time filter under chosen time mode.
        :return: Pageable of SeriesResult
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.metricsadvisor.models.SeriesResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

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
            **kwargs)

    @distributed_trace
    def list_alerts_for_alert_configuration(self, alert_configuration_id, start_time, end_time, time_mode, **kwargs):
        # type: (str, datetime.datetime, datetime.datetime, Union[str, TimeMode], Any) -> ItemPaged[Alert]

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
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.metricsadvisor.models.Alert]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_anomaly_alert_configuration.py
                :start-after: [START list_alerts_for_alert_config]
                :end-before: [END list_alerts_for_alert_config]
                :language: python
                :dedent: 4
                :caption: Query anomaly detection results.
        """

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
            cls=kwargs.pop("cls", lambda alerts: [Alert._from_generated(alert) for alert in alerts]),
            **kwargs)

    @distributed_trace
    def list_anomalies_for_alert(self, alert_configuration_id, alert_id, **kwargs):
        # type: (str, str, Any) -> ItemPaged[Anomaly]

        """Query anomalies under a specific alert.

        :param alert_configuration_id: anomaly alert configuration unique id.
        :type alert_configuration_id: str
        :param alert_id: alert id.
        :type alert_id: str
        :keyword int skip:
        :return: Anomalies under a specific alert.
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.metricsadvisor.models.Anomaly]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_anomaly_alert_configuration.py
                :start-after: [START list_anomalies_for_alert]
                :end-before: [END list_anomalies_for_alert]
                :language: python
                :dedent: 4
                :caption: Query anomalies using alert id.
        """

        skip = kwargs.pop('skip', None)

        return self._client.get_anomalies_from_alert_by_anomaly_alerting_configuration(  # type: ignore
            configuration_id=alert_configuration_id,
            alert_id=alert_id,
            skip=skip,
            cls=lambda objs: [Anomaly._from_generated(x) for x in objs],
            **kwargs)

    @distributed_trace
    def list_anomalies_for_detection_configuration(self, detection_configuration_id, start_time, end_time, **kwargs):
        # type: (str, datetime.datetime, datetime.datetime, Any) -> ItemPaged[Anomaly]

        """Query anomalies under anomaly detection configuration.

        :param detection_configuration_id: anomaly detection configuration unique id.
        :type detection_configuration_id: str
        :param ~datetime.datetime start_time: start time filter under chosen time mode.
        :param ~datetime.datetime end_time: end time filter under chosen time mode.
        :keyword int skip:
        :keyword filter:
        :paramtype filter: ~azure.ai.metricsadvisor.models.DetectionAnomalyFilterCondition
        :return: Anomalies under anomaly detection configuration.
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.metricsadvisor.models.Anomaly]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

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
            **kwargs)

    @distributed_trace
    def list_dimension_values_for_detection_configuration(
            self, detection_configuration_id,
            dimension_name,
            start_time,
            end_time,
            **kwargs
    ):
        # type: (str, str, datetime.datetime, datetime.datetime, Any) -> ItemPaged[str]

        """Query dimension values of anomalies.

        :param detection_configuration_id: anomaly detection configuration unique id.
        :type detection_configuration_id: str
        :param str dimension_name: dimension to query.
        :param ~datetime.datetime start_time: start time filter under chosen time mode.
        :param ~datetime.datetime end_time: end time filter under chosen time mode.
        :keyword int skip:
        :keyword str dimension_name: The dimension name to query.
        :paramtype dimension_filter: ~azure.ai.metricsadvisor.models.DimensionGroupIdentity
        :return: Dimension values of anomalies.
        :rtype: ~azure.core.paging.ItemPaged[str]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

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
            **kwargs)

    @distributed_trace
    def list_incidents_for_alert(self, alert_configuration_id, alert_id, **kwargs):
        # type: (str, str, Any) -> ItemPaged[Incident]

        """Query incidents under a specific alert.

        :param alert_configuration_id: anomaly alerting configuration unique id.
        :type alert_configuration_id: str
        :param alert_id: alert id.
        :type alert_id: str
        :keyword int skip:
        :return: Incidents under a specific alert.
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.metricsadvisor.models.Incident]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        skip = kwargs.pop('skip', None)

        return self._client.get_incidents_from_alert_by_anomaly_alerting_configuration(  # type: ignore
            configuration_id=alert_configuration_id,
            alert_id=alert_id,
            skip=skip,
            cls=lambda objs: [Incident._from_generated(x) for x in objs],
            **kwargs)

    @distributed_trace
    def list_incidents_for_detection_configuration(self, detection_configuration_id, start_time, end_time, **kwargs):
        # type: (str, datetime.datetime, datetime.datetime, Any) -> ItemPaged[Incident]

        """Query incidents under a specific alert.

        :param detection_configuration_id: anomaly detection configuration unique id.
        :type detection_configuration_id: str
        :param ~datetime.datetime start_time: start time filter under chosen time mode.
        :param ~datetime.datetime end_time: end time filter under chosen time mode.
        :keyword filter:
        :paramtype filter: ~azure.ai.metricsadvisor.models.DetectionIncidentFilterCondition
        :return: Incidents under a specific alert.
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.metricsadvisor.models.Incident]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

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
            **kwargs)

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
        """

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
            **kwargs)

    @distributed_trace
    def list_metrics_series_data(self, metric_id, start_time, end_time, series_to_filter, **kwargs):
        # type: (str, datetime.datetime, datetime.datetime, List[Dict[str, str]], Any) -> ItemPaged[MetricSeriesData]

        """Get time series data from metric.

        :param metric_id: metric unique id.
        :type metric_id: str
        :param ~datetime.datetime start_time: start time filter under chosen time mode.
        :param ~datetime.datetime end_time: end time filter under chosen time mode.
        :param series_to_filter: query specific series.
        :type series_to_filter: list[dict[str, str]]
        :return: Time series data from metric.
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.metricsadvisor.models.MetricSeriesData]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        metric_data_query_options = MetricDataQueryOptions(
            start_time=start_time,
            end_time=end_time,
            series=series_to_filter,
        )

        return self._client.get_metric_data(  # type: ignore
            metric_id=metric_id,
            body=metric_data_query_options,
            cls=kwargs.pop("cls", lambda result: [MetricSeriesData._from_generated(series) for series in result]),
            **kwargs)

    @distributed_trace
    def list_metric_series_definitions(self, metric_id, active_since, **kwargs):
        # type: (str, datetime.datetime, Any) -> ItemPaged[MetricSeriesDefinition]

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
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.metricsadvisor.models.MetricSeriesDefinition]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

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
            **kwargs)

    @distributed_trace
    def list_metric_enrichment_status(self, metric_id, start_time, end_time, **kwargs):
        # type: (str, datetime.datetime, datetime.datetime, Any) -> ItemPaged[EnrichmentStatus]

        """Query anomaly detection status.

        :param metric_id: filter feedbacks by metric id.
        :type metric_id: str
        :param ~datetime.datetime start_time: start time filter under chosen time mode.
        :param ~datetime.datetime end_time: end time filter under chosen time mode.
        :keyword int skip:
        :return: Anomaly detection status.
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.metricsadvisor.models.EnrichmentStatus]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        skip = kwargs.pop('skip', None)
        enrichment_status_query_option = EnrichmentStatusQueryOption(
            start_time=start_time,
            end_time=end_time,
        )

        return self._client.get_enrichment_status_by_metric(  # type: ignore
            metric_id=metric_id,
            skip=skip,
            body=enrichment_status_query_option,
            **kwargs)
