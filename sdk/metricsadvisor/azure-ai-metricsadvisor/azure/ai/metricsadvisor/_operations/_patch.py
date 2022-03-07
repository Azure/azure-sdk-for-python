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
import functools
import six
import datetime
from typing import Any, Callable, List, Tuple, Union, cast, overload, Dict, Optional
from azure.core.tracing.decorator import distributed_trace
from azure.core.rest import HttpRequest
from ._operations import *
from ._operations import MetricsAdvisorClientOperationsMixin as _MetricsAdvisorClientOperationsMixin
from ..models import *
from ..models import _models_py3 as generated_models
from ..models._patch import (
    AlertingResultQuery,
    MetricDataQueryOptions,
    AnomalyDimensionQuery,
    DetectionAnomalyResultQuery,
    DetectionIncidentResultQuery,
    DetectionSeriesQuery,
    EnrichmentStatusQueryOption,
    IngestionProgressResetOptions,
    IngestionStatusQueryOptions,
    MetricDimensionQueryOptions,
    MetricFeedbackFilter,
    MetricSeriesQueryOptions,
    ErrorCode,
)
from msrest import Serializer
from azure.core.paging import ItemPaged
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    map_error,
)


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

UpdateHelperRetval = Tuple[str, Union[JSONType, DataFeed], Any]

########################### HELPERS ###########################


class OperationMixinHelpers:
    def _convert_to_sub_feedback(self, feedback):
        # type: (MetricFeedback) -> Union[AnomalyFeedback, ChangePointFeedback, CommentFeedback, PeriodFeedback]
        if feedback.feedback_type == "Anomaly":
            return AnomalyFeedback.from_dict(feedback.serialize())
        if feedback.feedback_type == "ChangePoint":
            return ChangePointFeedback.from_dict(feedback.serialize())  # type: ignore
        if feedback.feedback_type == "Comment":
            return CommentFeedback.from_dict(feedback.serialize())  # type: ignore
        if feedback.feedback_type == "Period":
            return PeriodFeedback.from_dict(feedback.serialize())  # type: ignore
        raise HttpResponseError("Invalid feedback type returned in the response.")

    def _construct_data_feed(self, **kwargs):
        granularity = kwargs.pop("granularity", None)
        schema = kwargs.pop("schema", None)
        ingestion_settings = kwargs.pop("ingestion_settings", None)
        if isinstance(granularity, (DataFeedGranularityType, str)):
            granularity = DataFeedGranularity(
                granularity_type=granularity,
            )
        if isinstance(schema, list):
            schema = DataFeedSchema(metrics=[DataFeedMetric(name=metric_name) for metric_name in schema])
        if isinstance(ingestion_settings, (datetime.datetime, str)):
            ingestion_settings = DataFeedIngestionSettings(ingestion_begin_time=ingestion_settings)
        return DataFeed(granularity=granularity, schema=schema, ingestion_settings=ingestion_settings, **kwargs)

    def _deserialize_anomaly_detection_configuration(self, pipeline_response, **kwargs) -> AnomalyAlertConfiguration:
        cls = kwargs.pop("cls", None)
        response_json = pipeline_response.http_response.json()
        try:
            response_json["metricAlertingConfigurations"] = [
                self._deserialize(generated_models.MetricAlertConfiguration, m)
                for m in response_json["metricAlertingConfigurations"]
            ]
        except KeyError:
            raise ValueError(response_json)
        deserialized = self._deserialize(generated_models.AnomalyAlertConfiguration, response_json)
        if cls:
            return cls(pipeline_response, deserialized, {})

        return AnomalyAlertConfiguration._from_generated(deserialized)

    def _update_detection_configuration_helper(
        self, detection_configuration, **kwargs
    ) -> Tuple[str, Union[JSONType, AnomalyDetectionConfiguration], Any]:

        unset = object()
        update_kwargs = {}
        update_kwargs["name"] = kwargs.pop("name", unset)
        update_kwargs["wholeMetricConfiguration"] = kwargs.pop("whole_series_detection_condition", unset)
        update_kwargs["dimensionGroupOverrideConfigurations"] = kwargs.pop("series_group_detection_conditions", unset)
        update_kwargs["seriesOverrideConfigurations"] = kwargs.pop("series_detection_conditions", unset)
        update_kwargs["description"] = kwargs.pop("description", unset)

        update = {key: value for key, value in update_kwargs.items() if value != unset}
        if isinstance(detection_configuration, str):
            detection_configuration_id = detection_configuration
            detection_config_patch = update
            for key in update.keys():
                if key in kwargs:
                    kwargs.pop(key)
        else:
            detection_configuration_id = detection_configuration.id
            detection_config_patch = AnomalyDetectionConfiguration(
                name=update.pop("name", detection_configuration.name),
                metric_id=detection_configuration.metric_id,
                id=detection_configuration.id,
                description=update.pop("description", detection_configuration.description),
                whole_series_detection_condition=update.pop(
                    "whole_series_detection_condition", detection_configuration.whole_series_detection_condition
                ),
                series_group_detection_conditions=update.pop(
                    "series_group_detection_conditions", detection_configuration.series_group_detection_conditions
                ),
                series_detection_conditions=update.pop(
                    "series_detection_conditions", detection_configuration.series_detection_conditions
                ),
            )
        return detection_configuration_id, detection_config_patch, kwargs

    def _update_data_feed_helper(self, data_feed: Union[str, DataFeed], **kwargs) -> UpdateHelperRetval:
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

        if isinstance(data_feed, str):
            data_feed_id = data_feed
            if "dataStartFrom" in update:
                update["dataStartFrom"] = Serializer.serialize_iso(update["dataStartFrom"])
            data_feed_patch = update

        else:
            data_feed_id = data_feed.id
            data_feed_patch = data_feed._to_generated()
        return data_feed_id, data_feed_patch, kwargs

    def _list_metric_enriched_series_data_requests(
        self,
        detection_configuration_id,  # type: str
        series,  # type: Union[List[SeriesIdentity], List[Dict[str, str]]]
        start_time,  # type: Union[str, datetime.datetime]
        end_time,  # type: Union[str, datetime.datetime]
        **kwargs  # type: Any
    ) -> Tuple[HttpRequest, HttpRequest, Any]:
        series_list = [
            SeriesIdentity(dimension=dimension) for dimension in series if isinstance(dimension, dict)
        ] or series

        series_list = cast(List[SeriesIdentity], series_list)
        converted_start_time = self._convert_datetime(start_time)
        converted_end_time = self._convert_datetime(end_time)
        detection_series_query = DetectionSeriesQuery(
            start_time=converted_start_time,
            end_time=converted_end_time,
            series=series_list,
        )
        content_type = kwargs.pop("content_type", "application/json")  # type: Optional[str]
        initial_request = build_list_metric_enriched_series_data_request(
            configuration_id=detection_configuration_id,
            json=detection_series_query.serialize(),
            content_type=content_type,
        )
        next_request = build_list_metric_enriched_series_data_request(
            configuration_id=detection_configuration_id,
            json=detection_series_query.serialize(),
            content_type=content_type,
        )
        return initial_request, next_request, kwargs

    def _list_feedback_requests(self, metric_id: str, **kwargs) -> Tuple[HttpRequest, HttpRequest, Any]:
        dimension_filter = None
        dimension_key = kwargs.pop("dimension_key", None)
        if dimension_key:
            dimension_filter = FeedbackDimensionFilter(dimension_key=dimension_key)
        feedback_type = kwargs.pop("feedback_type", None)
        start_time = kwargs.pop("start_time", None)
        end_time = kwargs.pop("end_time", None)
        converted_start_time = self._convert_datetime(start_time) if start_time else None
        converted_end_time = self._convert_datetime(end_time) if end_time else None
        time_mode = kwargs.pop("time_mode", None)
        feedback_filter = MetricFeedbackFilter(
            metric_id=metric_id,
            dimension_filter=dimension_filter,
            feedback_type=feedback_type,
            start_time=converted_start_time,
            end_time=converted_end_time,
            time_mode=time_mode,
        )
        return (
            build_list_feedback_request(json=feedback_filter.serialize(), skip=kwargs.pop("skip", None)),
            build_list_feedback_request(),
            kwargs,
        )

    def _list_data_feed_ingestion_status_requests(
        self, data_feed_id, start_time, end_time, **kwargs
    ) -> Tuple[HttpRequest, HttpRequest, Any]:
        skip = kwargs.pop("skip", None)
        converted_start_time = self._convert_datetime(start_time)
        converted_end_time = self._convert_datetime(end_time)
        body = IngestionStatusQueryOptions(start_time=converted_start_time, end_time=converted_end_time)
        content_type = kwargs.pop("content_type", "application/json")  # type: Optional[str]
        initial_request = build_list_data_feed_ingestion_status_request(
            data_feed_id=data_feed_id, json=body.serialize(), content_type=content_type, skip=skip
        )
        next_request = build_list_data_feed_ingestion_status_request(
            data_feed_id=data_feed_id, json=body.serialize(), content_type=content_type
        )
        return initial_request, next_request, kwargs

    def _list_metric_series_definitions_requests(self, metric_id, active_since, **kwargs):
        dimension_filter = kwargs.pop("dimension_filter", None)
        metric_series_query_options = MetricSeriesQueryOptions(
            active_since=active_since,
            dimension_filter=dimension_filter,
        )
        content_type = kwargs.pop("content_type", "application/json")
        initial_request = build_list_metric_series_definitions_request(
            metric_id=metric_id,
            content_type=content_type,
            json=metric_series_query_options.serialize(),
            skip=kwargs.pop("skip", None),
            maxpagesize=kwargs.pop("maxpagesize", None),
        )
        next_request = build_list_metric_series_definitions_request(
            metric_id=metric_id,
            content_type=content_type,
            json=metric_series_query_options.serialize(),
        )
        return initial_request, next_request, kwargs

    def _list_alerts_requests(
        self,
        alert_configuration_id: str,
        start_time: Union[str, datetime.datetime],
        end_time: Union[str, datetime.datetime],
        time_mode: Union[str, AlertQueryTimeMode],
        **kwargs: Any
    ) -> Tuple[HttpRequest, HttpRequest, Any]:
        skip = kwargs.pop("skip", None)
        converted_start_time = self._convert_datetime(start_time)
        converted_end_time = self._convert_datetime(end_time)
        content_type = kwargs.pop("content_type", "application/json")

        alerting_result_query = AlertingResultQuery(
            start_time=converted_start_time,
            end_time=converted_end_time,
            time_mode=time_mode,
        )
        initial_request = build_list_alerts_request(
            configuration_id=alert_configuration_id,
            skip=skip,
            json=alerting_result_query.serialize(),
            content_type=content_type,
        )
        next_request = build_list_alerts_request(
            configuration_id=alert_configuration_id,
            json=alerting_result_query.serialize(),
            content_type=content_type,
        )
        return initial_request, next_request, kwargs

    def _list_anomalies_for_detection_configuration_requests(
        self,
        detection_configuration_id,  # type: str
        start_time,  # type: Union[str, datetime.datetime]
        end_time,  # type: Union[str, datetime.datetime]
        **kwargs  # type: Any
    ) -> Tuple[HttpRequest, HttpRequest, Any]:
        skip = kwargs.pop("skip", None)
        converted_start_time = self._convert_datetime(start_time)
        converted_end_time = self._convert_datetime(end_time)
        detection_anomaly_result_query = DetectionAnomalyResultQuery(
            start_time=converted_start_time,
            end_time=converted_end_time,
            filter=kwargs.pop("filter", None),
        )
        content_type = kwargs.pop("content_type", "application/json")
        initial_request = build_get_anomalies_by_anomaly_detection_configuration_request(
            configuration_id=detection_configuration_id,
            skip=skip,
            json=detection_anomaly_result_query.serialize(),
            content_type=content_type,
        )
        next_request = build_get_anomalies_by_anomaly_detection_configuration_request(
            configuration_id=detection_configuration_id,
            json=detection_anomaly_result_query.serialize(),
            content_type=content_type,
        )
        return initial_request, next_request, kwargs

    def _list_anomaly_dimension_values_requests(
        self, detection_configuration_id, dimension_name, start_time, end_time, **kwargs
    ) -> Tuple[HttpRequest, HttpRequest, Any]:
        skip = kwargs.pop("skip", None)
        dimension = kwargs.pop("dimension_filter", None)
        dimension_filter = DimensionGroupIdentity(dimension=dimension) if dimension else None
        converted_start_time = self._convert_datetime(start_time)
        converted_end_time = self._convert_datetime(end_time)
        anomaly_dimension_query = AnomalyDimensionQuery(
            start_time=converted_start_time,
            end_time=converted_end_time,
            dimension_name=dimension_name,
            dimension_filter=dimension_filter,
        )
        content_type = kwargs.pop("content_type", "application/json")
        initial_request = build_list_anomaly_dimension_values_request(
            configuration_id=detection_configuration_id,
            skip=skip,
            json=anomaly_dimension_query.serialize(),
            content_type=content_type,
        )
        next_request = build_list_anomaly_dimension_values_request(
            configuration_id=detection_configuration_id,
            json=anomaly_dimension_query.serialize(),
            content_type=content_type,
        )
        return initial_request, next_request, kwargs

    def _list_incidents_for_detection_configuration_requests(
        self,
        detection_configuration_id: str,
        start_time: Union[str, datetime.datetime],
        end_time: Union[str, datetime.datetime],
        **kwargs: Any
    ) -> Tuple[HttpRequest, HttpRequest, Any]:
        condition = kwargs.pop("filter", None)
        filter_condition = condition._to_generated() if condition else None
        converted_start_time = self._convert_datetime(start_time)
        converted_end_time = self._convert_datetime(end_time)
        content_type = kwargs.pop("content_type", "application/json")
        detection_incident_result_query = DetectionIncidentResultQuery(
            start_time=converted_start_time,
            end_time=converted_end_time,
            filter=filter_condition,
        )
        initial_request = build_get_incidents_by_anomaly_detection_configuration_request(
            configuration_id=detection_configuration_id,
            json=detection_incident_result_query.serialize(),
            content_type=content_type,
        )
        next_request = build_get_incidents_by_anomaly_detection_configuration_request(
            configuration_id=detection_configuration_id,
            json=detection_incident_result_query.serialize(),
            content_type=content_type,
        )
        return initial_request, next_request, kwargs

    def _list_metric_dimension_values_requests(
        self, metric_id, dimension_name, **kwargs
    ) -> Tuple[HttpRequest, HttpRequest, Any]:
        skip = kwargs.pop("skip", None)
        dimension_value_filter = kwargs.pop("dimension_value_filter", None)
        content_type = kwargs.pop("content_type", "application/json")
        metric_dimension_query_options = MetricDimensionQueryOptions(
            dimension_name=dimension_name,
            dimension_value_filter=dimension_value_filter,
        )
        initial_request = build_list_metric_dimension_values_request(
            metric_id=metric_id,
            json=metric_dimension_query_options.serialize(),
            skip=skip,
            content_type=content_type,
        )
        next_request = build_list_metric_dimension_values_request(
            metric_id=metric_id,
            json=metric_dimension_query_options.serialize(),
            content_type=content_type,
        )
        return initial_request, next_request, kwargs

    def _list_metric_series_data_requests(
        self,
        metric_id,  # type: str
        series_keys,  # type: List[Dict[str, str]]
        start_time,  # type: Union[str, datetime.datetime]
        end_time,  # type: Union[str, datetime.datetime]
        **kwargs  # type: Any
    ) -> Tuple[HttpRequest, HttpRequest, Any]:
        converted_start_time = self._convert_datetime(start_time)
        converted_end_time = self._convert_datetime(end_time)

        metric_data_query_options = MetricDataQueryOptions(
            start_time=converted_start_time,
            end_time=converted_end_time,
            series=series_keys,
        )
        initial_request = build_list_metric_series_data_request(
            metric_id=metric_id,
            json=metric_data_query_options.serialize(),
            content_type=kwargs.pop("content_type", "application/json"),
        )
        next_request = build_list_metric_series_data_request(metric_id=metric_id)
        return initial_request, next_request, kwargs

    def _list_metric_enrichment_status_requests(
        self,
        metric_id,  # type: str
        start_time,  # type: Union[str, datetime.datetime]
        end_time,  # type: Union[str, datetime.datetime]
        **kwargs  # type: Any
    ) -> Tuple[HttpRequest, HttpRequest, Any]:
        skip = kwargs.pop("skip", None)
        converted_start_time = self._convert_datetime(start_time)
        converted_end_time = self._convert_datetime(end_time)
        enrichment_status_query_option = EnrichmentStatusQueryOption(
            start_time=converted_start_time,
            end_time=converted_end_time,
        )
        initial_request = build_list_metric_enrichment_status_request(
            metric_id=metric_id,
            json=enrichment_status_query_option.serialize(),
            skip=skip,
            content_type=kwargs.pop("content_type", "application/json"),
        )
        next_request = build_list_metric_enrichment_status_request(metric_id=metric_id)
        return initial_request, next_request, kwargs

    def _list_incidents_for_alert_requests(
        self,
        alert_configuration_id: str,
        alert_id: str,
        *,
        skip: Optional[int] = None,
        maxpagesize: Optional[int] = None,
        **kwargs: Any
    ) -> Tuple[HttpRequest, HttpRequest, Any]:
        initial_request = build_list_incidents_for_alert_request(
            alert_configuration_id=alert_configuration_id,
            alert_id=alert_id,
            skip=skip,
            maxpagesize=maxpagesize,
        )
        next_request = build_list_incidents_for_alert_request(
            alert_configuration_id=alert_configuration_id,
            alert_id=alert_id,
        )
        return initial_request, next_request, kwargs

    def _list_anomalies_for_alert_requests(
        self, alert_configuration_id: str, alert_id: str, **kwargs: Any
    ) -> Tuple[HttpRequest, HttpRequest, Any]:
        initial_request = build_list_anomalies_for_alert_request(
            alert_configuration_id=alert_configuration_id,
            alert_id=alert_id,
            skip=kwargs.pop("skip", None),
        )
        next_request = build_list_anomalies_for_alert_request(
            alert_configuration_id=alert_configuration_id, alert_id=alert_id
        )
        return initial_request, next_request, kwargs

    def _list_incident_root_causes_requests(self, detection_configuration_id: str, incident_id: str, **kwargs):
        initial_request = build_list_incident_root_causes_request(
            detection_configuration_id=detection_configuration_id,
            incident_id=incident_id,
        )
        return initial_request, initial_request, kwargs

    def _list_hooks_requests(self, **kwargs):
        hook_name = kwargs.pop("hook_name", None)
        skip = kwargs.pop("skip", None)
        initial_request = build_list_hooks_request(hook_name=hook_name, skip=skip)
        return initial_request, build_list_hooks_request(), kwargs

    def _update_alert_configuration_helper(
        self, alert_configuration: Union[str, AnomalyAlertConfiguration], **kwargs
    ) -> Tuple[HttpRequest, Any]:
        unset = object()
        update_kwargs = {}
        update_kwargs["name"] = kwargs.pop("name", unset)
        update_kwargs["hookIds"] = kwargs.pop("hook_ids", unset)
        update_kwargs["crossMetricsOperator"] = kwargs.pop("cross_metrics_operator", unset)
        update_kwargs["metricAlertingConfigurations"] = kwargs.pop("metric_alert_configurations", unset)
        update_kwargs["description"] = kwargs.pop("description", unset)

        update = {key: value for key, value in update_kwargs.items() if value != unset}
        if isinstance(alert_configuration, str):
            alert_configuration_id = alert_configuration
            if "metricAlertingConfigurations" in update:
                update["metricAlertingConfigurations"] = (
                    [config._to_generated() for config in update["metricAlertingConfigurations"]]
                    if update["metricAlertingConfigurations"]
                    else None
                )
            alert_configuration_patch = update

        else:
            alert_configuration_id = alert_configuration.id
            alert_configuration_patch = alert_configuration._to_generated()
        content_type = kwargs.pop("content_type", "application/merge-patch+json")  # type: Optional[str]

        _json = self._serialize.body(alert_configuration_patch, "AnomalyAlertingConfiguration")

        request = build_update_alert_configuration_request(
            configuration_id=alert_configuration_id,
            content_type=content_type,
            json=_json,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)
        return request, kwargs

    def _update_alert_configuration_deserialize(self, pipeline_response, **kwargs: Any):
        cls = kwargs.pop("cls", None)  # type: ClsType["_models.AnomalyAlertConfiguration"]
        error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop("error_map", {}))
        response = pipeline_response.http_response

        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            error = self._deserialize.failsafe_deserialize(_models.ErrorCode, pipeline_response)
            raise HttpResponseError(response=response, model=error)

        deserialized = self._deserialize(generated_models.AnomalyAlertConfiguration, pipeline_response)

        if cls:
            return cls(pipeline_response, deserialized, {})

        return deserialized

    def _get_feedback_request(self, feedback_id: str) -> HttpRequest:
        request = build_get_feedback_request(
            feedback_id=feedback_id,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)
        return request

    def _get_feedback_deserialize(self, pipeline_response, **kwargs) -> MetricFeedback:
        cls = kwargs.pop("cls", None)
        error_map = kwargs.pop("error_map", None)
        response = pipeline_response.http_response
        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            error = self._deserialize.failsafe_deserialize(ErrorCode, pipeline_response)
            raise HttpResponseError(response=response, model=error)

        deserialized = self._convert_to_sub_feedback(
            self._deserialize(generated_models.MetricFeedback, pipeline_response)
        )

        if cls:
            return cls(pipeline_response, deserialized, {})

        return deserialized

    def _update_hook_helper(
        self, hook: Union[str, EmailNotificationHook, WebNotificationHook], **kwargs: Any
    ) -> Tuple[str, Union[JSONType, NotificationHook], Any]:
        hook_patch = {}
        hook_type = kwargs.pop("hook_type", None)
        hook_kwarg_names = [
            "name",
            "description",
            "external_link",
            "emails_to_alert",
            "endpoint",
            "username",
            "password",
            "certificate_key",
            "certificate_password",
            "hook_type",
        ]
        specific_kwargs = {}
        passed_kwargs = {k: v for k, v in kwargs.items() if k in hook_kwarg_names}
        if isinstance(hook, str):
            hook_id = hook
            if hook_type is None:
                raise ValueError("hook_type must be passed with a hook ID.")
            hook_class = EmailNotificationHook if hook_type.lower() == "email" else WebNotificationHook
            hook_patch = hook_class.from_dict(passed_kwargs).serialize()

        else:
            hook_id = hook.id
            hook_patch = hook.serialize()
        if hook_patch["hookType"] == "Email" and "emails_to_alert" in passed_kwargs:
            specific_kwargs = {"toList": "emails_to_alert"}
        elif hook_patch["hookType"] == "Webhook":
            specific_kwargs = {
                "endpoint": "endpoint",
                "password": "password",
                "username": "username",
                "certificateKey": "certificate_key",
                "certificatePassword": "certificate_password",
            }
        shared_kwargs = {
            "externalLink": "external_link",
            "description": "description",
            "hookName": "name"
        }
        for rest_name, attr_name in shared_kwargs.items():
            hook_patch[rest_name] = passed_kwargs.pop(
                attr_name, hook_patch.get(rest_name)
            )
        hook_patch['hookParameter'] = hook_patch.get("hookParameter", {})
        for rest_name, attr_name in specific_kwargs.items():
            hook_patch["hookParameter"][rest_name] = passed_kwargs.pop(
                attr_name, hook_patch["hookParameter"].get(rest_name)
            )
        for k in hook_kwarg_names:
            if k in kwargs:
                kwargs.pop(k)
        return hook_id, hook_patch, kwargs

    def _convert_datetime(self, date_time):
        # type: (Union[str, datetime.datetime]) -> datetime.datetime
        if isinstance(date_time, datetime.datetime):
            return date_time
        if isinstance(date_time, str):
            try:
                return datetime.datetime.strptime(date_time, "%Y-%m-%d")
            except ValueError:
                try:
                    return datetime.datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%SZ")
                except ValueError:
                    return datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
        raise TypeError("Bad datetime type")

    def _get_paging_prepare_request(
        self, initial_request: HttpRequest, next_request: HttpRequest, next_link=None, **kwargs
    ) -> Callable:
        def prepare_request(next_link=None):
            path_format_arguments = {
                "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
            }
            if not next_link:
                request = initial_request
                request.url = self._client.format_url(request.url, **path_format_arguments)
            else:
                request = next_request
                request.url = self._client.format_url(next_link, **path_format_arguments)
            return request

        return prepare_request


def _extract_data_default(deserializer, pipeline_response):
    response_json = pipeline_response.http_response.json()
    list_of_elem = [deserializer(l) for l in response_json["value"]]
    return response_json.get("@nextLink", None) or None, iter(list_of_elem)


class MetricsAdvisorClientOperationsMixin(_MetricsAdvisorClientOperationsMixin, OperationMixinHelpers):
    def _paging_helper(
        self, *, extract_data=None, initial_request: HttpRequest, next_request: HttpRequest, deserializer=None, **kwargs
    ) -> ItemPaged:
        extract_data = extract_data or functools.partial(_extract_data_default, deserializer)
        error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop("error_map", {}))

        prepare_request = self._get_paging_prepare_request(
            initial_request=initial_request, next_request=next_request, **kwargs
        )

        def get_next(next_link=None):
            request = prepare_request(next_link)

            pipeline_response = self._client._pipeline.run(  # pylint: disable=protected-access
                request, stream=False, **kwargs
            )
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                error = self._deserialize.failsafe_deserialize(ErrorCode, pipeline_response)
                raise HttpResponseError(response=response, model=error)

            return pipeline_response

        return ItemPaged(get_next, extract_data)

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
                metric_alert_configurations=[m._to_generated() for m in metric_alert_configurations],
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
        data_feed = self._construct_data_feed(
            name=name,
            source=source,
            granularity=granularity,
            schema=schema,
            ingestion_settings=ingestion_settings,
            **kwargs
        )
        for attr in dir(data_feed):
            if attr in kwargs:
                kwargs.pop(attr)
        response_headers = super().create_data_feed(  # type: ignore
            data_feed._to_generated(), cls=lambda pipeline_response, _, response_headers: response_headers, **kwargs
        )
        data_feed_id = response_headers["Location"].split("dataFeeds/")[1]
        return self.get_data_feed(data_feed_id)

    @distributed_trace
    def create_hook(
        self,
        hook,  # type: Union[EmailNotificationHook, WebNotificationHook]
        **kwargs  # type: Any
    ):  # type: (...) -> Union[NotificationHook, EmailNotificationHook, WebNotificationHook]
        response_headers = super().create_hook(  # type: ignore
            hook, cls=lambda pipeline_response, _, response_headers: response_headers, **kwargs  # type: ignore
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
        config = AnomalyDetectionConfiguration(
            name=name,
            metric_id=metric_id,
            description=kwargs.pop("description", None),
            whole_series_detection_condition=whole_series_detection_condition,
            **kwargs
        )
        for attr in dir(config):
            if attr in kwargs:
                kwargs.pop(attr)
        response_headers = super().create_detection_configuration(  # type: ignore
            config, cls=lambda pipeline_response, _, response_headers: response_headers, **kwargs
        )
        config_id = response_headers["Location"].split("configurations/")[1]
        return self.get_detection_configuration(config_id)

    @distributed_trace
    def get_data_feed(self, data_feed_id, **kwargs):
        # type: (str, Any) -> DataFeed
        cls = kwargs.pop("cls", None)
        error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop("error_map", {}))

        request = build_get_data_feed_request(
            data_feed_id=data_feed_id,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)

        pipeline_response = self._client._pipeline.run(  # pylint: disable=protected-access
            request, stream=False, **kwargs
        )
        response = pipeline_response.http_response

        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            error = self._deserialize.failsafe_deserialize(ErrorCode, pipeline_response)
            raise HttpResponseError(response=response, model=error)

        deserialized = self._deserialize(generated_models.DataFeed, pipeline_response)

        if cls:
            return cls(pipeline_response, deserialized, {})
        json_response = response.json()
        return DataFeed._from_generated(
            deserialized, json_response["dataSourceParameter"], json_response["dataSourceType"]
        )

    @distributed_trace
    def get_alert_configuration(self, alert_configuration_id, **kwargs):
        # type: (str, Any) -> AnomalyAlertConfiguration
        error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop("error_map", {}))

        request = build_get_alert_configuration_request(
            configuration_id=alert_configuration_id,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)

        pipeline_response = self._client._pipeline.run(  # pylint: disable=protected-access
            request, stream=False, **kwargs
        )
        response = pipeline_response.http_response

        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            error = self._deserialize.failsafe_deserialize(ErrorCode, pipeline_response)
            raise HttpResponseError(response=response, model=error)

        return self._deserialize_anomaly_detection_configuration(pipeline_response, **kwargs)

    @distributed_trace
    def refresh_data_feed_ingestion(
        self,
        data_feed_id,  # type: str
        start_time,  # type: Union[str, datetime.datetime]
        end_time,  # type: Union[str, datetime.datetime]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        converted_start_time = self._convert_datetime(start_time)
        converted_end_time = self._convert_datetime(end_time)
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
    def update_data_feed(self, data_feed: Union[str, DataFeed], **kwargs: Any) -> DataFeed:
        data_feed_id, data_feed_patch, kwargs = self._update_data_feed_helper(data_feed, **kwargs)
        return super().update_data_feed(data_feed_id, data_feed_patch, **kwargs)

    @distributed_trace
    def update_alert_configuration(
        self, alert_configuration: Union[str, AnomalyAlertConfiguration], **kwargs: Any
    ) -> AnomalyAlertConfiguration:
        request, kwargs = self._update_alert_configuration_helper(alert_configuration, **kwargs)
        pipeline_response = self._client._pipeline.run(  # pylint: disable=protected-access
            request, stream=False, **kwargs
        )
        return self._deserialize_anomaly_detection_configuration(pipeline_response, **kwargs)

    @distributed_trace
    def update_detection_configuration(
        self, detection_configuration: Union[str, AnomalyDetectionConfiguration], **kwargs: Any
    ) -> AnomalyDetectionConfiguration:
        detection_configuration_id, detection_config_patch, kwargs = self._update_detection_configuration_helper(
            detection_configuration, **kwargs
        )

        return super().update_detection_configuration(
            configuration_id=detection_configuration_id, body=detection_config_patch, **kwargs
        )

    @distributed_trace
    def update_hook(
        self, hook: Union[str, EmailNotificationHook, WebNotificationHook], **kwargs: Any
    ) -> Union[NotificationHook, EmailNotificationHook, WebNotificationHook]:
        hook_id, hook_patch, kwargs = self._update_hook_helper(hook, **kwargs)

        return super().update_hook(hook_id, hook_patch, **kwargs)

    @distributed_trace
    def list_data_feeds(
        self,
        *,
        data_feed_name: Optional[str] = None,
        data_source_type: Optional[Union[str, "DataSourceType"]] = None,
        granularity_type: Optional[Union[str, "DataFeedGranularityType"]] = None,
        status: Optional[Union[str, "DataFeedStatus"]] = None,
        creator: Optional[str] = None,
        skip: Optional[int] = None,
        maxpagesize: Optional[int] = None,
        **kwargs: Any
    ) -> ItemPaged[DataFeed]:
        deserializer = functools.partial(self._deserialize, generated_models.DataFeed)

        def extract_data(deserializer, pipeline_response):
            response_json = pipeline_response.http_response.json()
            list_of_elem = []
            for l in response_json["value"]:
                data_source_type = l["dataSourceType"]  # this gets popped during deserialization
                data_source_parameter = l["dataSourceParameter"]
                list_of_elem.append(
                    DataFeed._from_generated(
                        deserializer(l),
                        data_source_parameter,
                        data_source_type,
                    )
                )
            return response_json.get("@nextLink", None) or None, iter(list_of_elem)

        return self._paging_helper(
            extract_data=functools.partial(extract_data, deserializer),
            initial_request=build_list_data_feeds_request(
                data_feed_name=data_feed_name,
                data_source_type=data_source_type,
                granularity_name=granularity_type,
                status=status,
                creator=creator,
                skip=skip,
                maxpagesize=maxpagesize,
            ),
            next_request=build_list_data_feeds_request(),
            **kwargs
        )

    @distributed_trace
    def list_alert_configurations(
        self, detection_configuration_id: str, **kwargs: Any
    ) -> ItemPaged[AnomalyAlertConfiguration]:
        deserializer = self._deserialize

        def extract_data(deserializer, pipeline_response):
            response_json = pipeline_response.http_response.json()
            list_of_elem = []
            for l in response_json["value"]:
                config_to_generated = functools.partial(deserializer, generated_models.MetricAlertConfiguration)
                l["metricAlertingConfigurations"] = [
                    config_to_generated(config) for config in l.get("metricAlertingConfigurations", [])
                ]
                list_of_elem.append(
                    AnomalyAlertConfiguration._from_generated(
                        deserializer(generated_models.AnomalyAlertConfiguration, l)
                    )
                )
            return response_json.get("@nextLink", None) or None, iter(list_of_elem)

        return self._paging_helper(
            extract_data=functools.partial(extract_data, deserializer),
            initial_request=build_list_alert_configurations_request(
                configuration_id=detection_configuration_id,
                skip=kwargs.pop("skip", None),
                maxpagesize=kwargs.pop("maxpagesize", None),
            ),
            next_request=build_list_alert_configurations_request(configuration_id=detection_configuration_id),
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
        initial_request, next_request, kwargs = self._list_data_feed_ingestion_status_requests(
            data_feed_id, start_time, end_time, **kwargs
        )
        return self._paging_helper(
            initial_request=initial_request,
            next_request=next_request,
            deserializer=DataFeedIngestionStatus.deserialize,
            **kwargs
        )

    @distributed_trace
    def create_datasource_credential(
        self, datasource_credential: DatasourceCredentialUnion, **kwargs: Any
    ) -> DatasourceCredentialUnion:
        response_headers = super().create_datasource_credential(  # type: ignore
            datasource_credential,  # type: ignore
            cls=lambda pipeline_response, _, response_headers: response_headers,
            **kwargs
        )
        credential_id = response_headers["Location"].split("credentials/")[1]
        return self.get_datasource_credential(credential_id)

    @distributed_trace
    def update_datasource_credential(
        self,
        datasource_credential,  # type: DatasourceCredential
        **kwargs  # type: Any
    ):
        return super().update_datasource_credential(datasource_credential.id, datasource_credential, **kwargs)

    @distributed_trace
    def delete_datasource_credential(self, *credential_id, **kwargs):
        # type: (*str, Any) -> None
        if len(credential_id) != 1:
            raise TypeError("Credential requires exactly one id.")

        super().delete_datasource_credential(credential_id=credential_id[0], **kwargs)

    @distributed_trace
    def get_feedback(self, feedback_id, **kwargs):
        # type: (str, Any) -> Union[MetricFeedback, FeedbackUnion]
        cls = kwargs.pop("cls", None)
        error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop("error_map", {}))

        request = self._get_feedback_request(feedback_id=feedback_id)
        pipeline_response = self._client._pipeline.run(  # pylint: disable=protected-access
            request, stream=False, **kwargs
        )
        return self._get_feedback_deserialize(pipeline_response, cls=cls, error_map=error_map, **kwargs)

    @distributed_trace
    def list_feedback(self, metric_id: str, **kwargs: Any) -> ItemPaged[Union[MetricFeedback, FeedbackUnion]]:
        deserializer = functools.partial(self._deserialize, generated_models.MetricFeedback)
        initial_request, next_request, kwargs = self._list_feedback_requests(metric_id, **kwargs)
        return self._paging_helper(
            initial_request=initial_request, next_request=next_request, deserializer=deserializer, **kwargs
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
        initial_request, next_request, kwargs = self._list_metric_enriched_series_data_requests(
            detection_configuration_id=detection_configuration_id,
            series=series,
            start_time=start_time,
            end_time=end_time,
            **kwargs
        )

        return self._paging_helper(
            initial_request=initial_request,
            next_request=next_request,
            deserializer=MetricEnrichedSeriesData.deserialize,
            **kwargs
        )

    @distributed_trace
    def list_alerts(
        self,
        alert_configuration_id: str,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        time_mode: Union[str, AlertQueryTimeMode],
        **kwargs: Any
    ) -> ItemPaged[AnomalyAlert]:
        initial_request, next_request, kwargs = self._list_alerts_requests(
            alert_configuration_id=alert_configuration_id,
            start_time=start_time,
            end_time=end_time,
            time_mode=time_mode,
            **kwargs
        )
        return self._paging_helper(
            initial_request=initial_request, next_request=next_request, deserializer=AnomalyAlert.deserialize, **kwargs
        )

    def _list_anomalies_for_detection_configuration(self, detection_configuration_id, start_time, end_time, **kwargs):
        # type: (...) -> ItemPaged[DataPointAnomaly]

        initial_request, next_request, kwargs = self._list_anomalies_for_detection_configuration_requests(
            detection_configuration_id=detection_configuration_id, start_time=start_time, end_time=end_time, **kwargs
        )
        return self._paging_helper(
            initial_request=initial_request,
            next_request=next_request,
            deserializer=DataPointAnomaly.deserialize,
            **kwargs
        )

    @distributed_trace
    def _list_anomalies_for_alert(
        self, alert_configuration_id: str, alert_id: str, **kwargs: Any
    ) -> Iterable[DataPointAnomaly]:
        initial_request, next_request, kwargs = self._list_anomalies_for_alert_requests(
            alert_configuration_id=alert_configuration_id, alert_id=alert_id, **kwargs
        )
        return self._paging_helper(
            initial_request=initial_request,
            next_request=next_request,
            deserializer=DataPointAnomaly.deserialize,
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
        return self._list_anomalies_for_alert(**kwargs)  # type: ignore

    @distributed_trace
    def list_anomaly_dimension_values(self, detection_configuration_id, dimension_name, start_time, end_time, **kwargs):
        # type: (str, str, Union[str, datetime.datetime], Union[str, datetime.datetime], Any) -> ItemPaged[str]
        initial_request, next_request, kwargs = self._list_anomaly_dimension_values_requests(
            detection_configuration_id=detection_configuration_id,
            dimension_name=dimension_name,
            start_time=start_time,
            end_time=end_time,
            **kwargs
        )

        return self._paging_helper(
            initial_request=initial_request, next_request=next_request, deserializer=lambda x: x, **kwargs
        )

    def _list_incidents_for_detection_configuration(self, detection_configuration_id, start_time, end_time, **kwargs):
        # type: (str, Union[str, datetime.datetime], Union[str, datetime.datetime], Any) -> ItemPaged[AnomalyIncident]
        initial_request, next_request, kwargs = self._list_incidents_for_detection_configuration_requests(
            detection_configuration_id=detection_configuration_id, start_time=start_time, end_time=end_time, **kwargs
        )
        return self._paging_helper(
            initial_request=initial_request,
            next_request=next_request,
            deserializer=AnomalyIncident.deserialize,
            **kwargs
        )

    @distributed_trace
    def _list_incidents_for_alert(
        self,
        alert_configuration_id: str,
        alert_id: str,
        *,
        skip: Optional[int] = None,
        maxpagesize: Optional[int] = None,
        **kwargs: Any
    ) -> Iterable[AnomalyIncident]:
        initial_request, next_request, kwargs = self._list_incidents_for_alert_requests(
            alert_configuration_id=alert_configuration_id,
            alert_id=alert_id,
            skip=skip,
            maxpagesize=maxpagesize,
            **kwargs
        )
        return self._paging_helper(
            initial_request=initial_request,
            next_request=next_request,
            deserializer=AnomalyIncident.deserialize,
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
        return self._list_incidents_for_alert(**kwargs)  # type: ignore

    @distributed_trace
    def list_metric_dimension_values(self, metric_id, dimension_name, **kwargs):
        # type: (str, str, Any) -> ItemPaged[str]
        initial_request, next_request, kwargs = self._list_metric_dimension_values_requests(
            metric_id=metric_id, dimension_name=dimension_name, **kwargs
        )
        return self._paging_helper(
            initial_request=initial_request, next_request=next_request, deserializer=lambda x: x, **kwargs
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
        initial_request, next_request, kwargs = self._list_metric_series_data_requests(
            metric_id=metric_id, series_keys=series_keys, start_time=start_time, end_time=end_time, **kwargs
        )

        return self._paging_helper(
            initial_request=initial_request,
            next_request=next_request,
            deserializer=MetricSeriesData.deserialize,
            **kwargs
        )

    @distributed_trace
    def list_metric_series_definitions(self, metric_id, active_since, **kwargs):
        # type: (str, datetime.datetime, Any) -> ItemPaged[MetricSeriesDefinition]
        cls = kwargs.pop("cls", None)

        initial_request, next_request, kwargs = self._list_metric_series_definitions_requests(
            metric_id, active_since, **kwargs
        )

        next_request.method = "POST"
        return self._paging_helper(
            initial_request=initial_request,
            next_request=next_request,
            deserializer=MetricSeriesDefinition.deserialize,
            **kwargs
        )

    @distributed_trace
    def list_metric_enrichment_status(self, metric_id, start_time, end_time, **kwargs):
        # type: (str, Union[str, datetime.datetime], Union[str, datetime.datetime], Any) -> ItemPaged[EnrichmentStatus]
        initial_request, next_request, kwargs = self._list_metric_enrichment_status_requests(
            metric_id=metric_id, start_time=start_time, end_time=end_time, **kwargs
        )
        return self._paging_helper(
            initial_request=initial_request,
            next_request=next_request,
            deserializer=EnrichmentStatus.deserialize,
            **kwargs
        )

    @distributed_trace
    def list_incident_root_causes(
        self, detection_configuration_id: str, incident_id: str, **kwargs: Any
    ) -> ItemPaged[IncidentRootCause]:
        initial_request, next_request, kwargs = self._list_incident_root_causes_requests(
            detection_configuration_id=detection_configuration_id, incident_id=incident_id, **kwargs
        )
        return self._paging_helper(
            initial_request=initial_request,
            next_request=next_request,
            deserializer=IncidentRootCause.deserialize,
            **kwargs
        )

    @distributed_trace
    def list_hooks(self, **kwargs: Any) -> ItemPaged[NotificationHook]:
        initial_request, next_request, kwargs = self._list_hooks_requests(**kwargs)
        return self._paging_helper(
            initial_request=initial_request,
            next_request=next_request,
            deserializer=NotificationHook.deserialize,
            **kwargs
        )


__all__ = ["MetricsAdvisorClientOperationsMixin"]


def patch_sdk():
    pass
