# pylint: disable=too-many-lines
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
import datetime
from typing import Any, Callable, List, Tuple, Union, cast, Dict, Optional, Iterable
from msrest import Serializer
from azure.core.tracing.decorator import distributed_trace
from azure.core.rest import HttpRequest
from azure.core.paging import ItemPaged
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    map_error,
)

from . import _operations as operations
from ._operations import MetricsAdvisorClientOperationsMixin as _MetricsAdvisorClientOperationsMixin
from .. import models
from ..models import _models as generated_models
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
    FeedbackDimensionFilter,
)

DatasourceCredentialUnion = Union[
    models.DatasourceSqlConnectionString,
    models.DatasourceDataLakeGen2SharedKey,
    models.DatasourceServicePrincipal,
    models.DatasourceServicePrincipalInKeyVault,
]

DataFeedSourceUnion = Union[
    models.AzureApplicationInsightsDataFeedSource,
    models.AzureBlobDataFeedSource,
    models.AzureCosmosDbDataFeedSource,
    models.AzureDataExplorerDataFeedSource,
    models.AzureTableDataFeedSource,
    models.AzureLogAnalyticsDataFeedSource,
    models.InfluxDbDataFeedSource,
    models.MySqlDataFeedSource,
    models.PostgreSqlDataFeedSource,
    models.SqlServerDataFeedSource,
    models.MongoDbDataFeedSource,
    models.AzureDataLakeStorageGen2DataFeedSource,
    models.AzureEventHubsDataFeedSource,
]

FeedbackUnion = Union[
    models.AnomalyFeedback,
    models.ChangePointFeedback,
    models.CommentFeedback,
    models.PeriodFeedback,
]

UpdateHelperRetval = Tuple[str, Union[Any, models.DataFeed], Any]

########################### HELPERS ###########################


class OperationMixinHelpers:
    def _convert_to_sub_feedback(self, feedback) -> FeedbackUnion:
        feedback_type = feedback["feedbackType"]
        if feedback_type == "Anomaly":
            generated = self._deserialize(generated_models.AnomalyFeedback, feedback)
            return models.AnomalyFeedback._from_generated(generated)
        if feedback_type == "ChangePoint":
            return models.ChangePointFeedback._from_generated(feedback)  # type: ignore
        if feedback_type == "Comment":
            return models.CommentFeedback._from_generated(feedback)  # type: ignore
        if feedback_type == "Period":
            return models.PeriodFeedback._from_generated(feedback)  # type: ignore
        raise HttpResponseError("Invalid feedback type returned in the response.")

    @staticmethod
    def _construct_data_feed(**kwargs):
        granularity = kwargs.pop("granularity", None)
        schema = kwargs.pop("schema", None)
        ingestion_settings = kwargs.pop("ingestion_settings", None)
        if isinstance(granularity, (models.DataFeedGranularityType, str)):
            granularity = models.DataFeedGranularity(
                granularity_type=granularity,
            )
        if isinstance(schema, list):
            schema = models.DataFeedSchema(metrics=[models.DataFeedMetric(name=metric_name) for metric_name in schema])
        if isinstance(ingestion_settings, (datetime.datetime, str)):
            ingestion_settings = models.DataFeedIngestionSettings(ingestion_begin_time=ingestion_settings)
        return models.DataFeed(granularity=granularity, schema=schema, ingestion_settings=ingestion_settings, **kwargs)

    def _deserialize_anomaly_detection_configuration(
        self, pipeline_response, **kwargs
    ) -> models.AnomalyAlertConfiguration:
        cls = kwargs.pop("cls", None)
        response_json = pipeline_response.http_response.json()
        try:
            response_json["metricAlertingConfigurations"] = [
                self._deserialize(generated_models.MetricAlertConfiguration, m)  # type: ignore  # pylint: disable=no-member
                for m in response_json["metricAlertingConfigurations"]
            ]
        except KeyError:
            raise ValueError(response_json)
        deserialized = self._deserialize(  # type: ignore  # pylint: disable=no-member
            generated_models.AnomalyAlertConfiguration, response_json
        )
        if cls:
            return cls(pipeline_response, deserialized, {})

        return models.AnomalyAlertConfiguration._from_generated(deserialized)  # pylint: disable=protected-access

    @staticmethod
    def _deserialize_datasource_credential(response) -> DatasourceCredentialUnion:
        type_to_datasource_credential = {
            "AzureSQLConnectionString": models.DatasourceSqlConnectionString,
            "DataLakeGen2SharedKey": models.DatasourceDataLakeGen2SharedKey,
            "ServicePrincipal": models.DatasourceServicePrincipal,
            "ServicePrincipalInKV": models.DatasourceServicePrincipalInKeyVault,
        }
        datasource_class = type_to_datasource_credential[response["dataSourceCredentialType"]]
        return datasource_class.from_dict(response)

    @staticmethod
    def _update_detection_configuration_helper(
        detection_configuration, **kwargs
    ) -> Tuple[str, Union[Any, models.AnomalyDetectionConfiguration], Any]:

        unset = object()
        update_kwargs = {}
        update_kwargs["name"] = kwargs.pop("name", unset)
        update_kwargs["whole_series_detection_condition"] = kwargs.pop("whole_series_detection_condition", unset)
        update_kwargs["series_group_detection_conditions"] = kwargs.pop("series_group_detection_conditions", unset)
        update_kwargs["series_detection_conditions"] = kwargs.pop("series_detection_conditions", unset)
        update_kwargs["description"] = kwargs.pop("description", unset)

        update = {key: value for key, value in update_kwargs.items() if value != unset}
        if isinstance(detection_configuration, str):
            detection_configuration_id = detection_configuration
            detection_config_patch = models.AnomalyDetectionConfiguration.from_dict(update).serialize()
        else:
            detection_configuration_id = detection_configuration.id
            detection_config_patch = models.AnomalyDetectionConfiguration(
                name=update.pop("name", detection_configuration.name),
                metric_id=detection_configuration.metric_id,
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
            ).serialize()
            detection_config_patch.pop("metricId")
        return detection_configuration_id, detection_config_patch, kwargs

    @staticmethod
    def _update_data_feed_helper(data_feed: Union[str, models.DataFeed], **kwargs) -> UpdateHelperRetval:
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
            if "dataSourceParameter" in update:
                update["authenticationType"] = update["dataSourceParameter"].authentication_type
                update["credentialId"] = update["dataSourceParameter"].credential_id
                update["dataSourceParameter"] = update["dataSourceParameter"]
            data_feed_patch = update

        else:
            data_feed_id = data_feed.id
            data_feed_patch = data_feed._to_generated(**update).serialize()  # pylint: disable=protected-access
        return data_feed_id, data_feed_patch, kwargs

    def _list_metric_enriched_series_data_requests(
        self,
        detection_configuration_id: str,
        series: Union[List[models.SeriesIdentity], List[Dict[str, str]]],
        start_time: Union[str, datetime.datetime],
        end_time: Union[str, datetime.datetime],
        **kwargs: Any
    ) -> Tuple[HttpRequest, HttpRequest, Any]:
        series_list = [
            models.SeriesIdentity(dimension=dimension) for dimension in series if isinstance(dimension, dict)
        ] or series

        series_list = cast(List[models.SeriesIdentity], series_list)
        converted_start_time = self._convert_datetime(start_time)
        converted_end_time = self._convert_datetime(end_time)
        detection_series_query = DetectionSeriesQuery(
            start_time=converted_start_time,
            end_time=converted_end_time,
            series=series_list,
        )
        content_type = kwargs.pop("content_type", "application/json")
        initial_request = operations.build_list_metric_enriched_series_data_request(
            configuration_id=detection_configuration_id,
            json=detection_series_query.serialize(),
            content_type=content_type,
        )
        next_request = operations.build_list_metric_enriched_series_data_request(
            configuration_id=detection_configuration_id,
            json=detection_series_query.serialize(),
            content_type=content_type,
        )
        return initial_request, next_request, kwargs

    def _list_feedback_requests(self, metric_id: str, **kwargs) -> Tuple[HttpRequest, HttpRequest, Any]:
        dimension_filter = None
        dimension_key = kwargs.pop("dimension_key", None)
        if dimension_key:
            dimension_filter = FeedbackDimensionFilter(dimension=dimension_key)
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
            operations.build_list_feedback_request(json=feedback_filter.serialize(), skip=kwargs.pop("skip", None)),
            operations.build_list_feedback_request(),
            kwargs,
        )

    def _list_data_feed_ingestion_status_requests(
        self, data_feed_id, start_time, end_time, **kwargs
    ) -> Tuple[HttpRequest, HttpRequest, Any]:
        skip = kwargs.pop("skip", None)
        converted_start_time = self._convert_datetime(start_time)
        converted_end_time = self._convert_datetime(end_time)
        body = IngestionStatusQueryOptions(start_time=converted_start_time, end_time=converted_end_time)
        content_type = kwargs.pop("content_type", "application/json")
        initial_request = operations.build_list_data_feed_ingestion_status_request(
            data_feed_id=data_feed_id, json=body.serialize(), content_type=content_type, skip=skip
        )
        next_request = operations.build_list_data_feed_ingestion_status_request(
            data_feed_id=data_feed_id, json=body.serialize(), content_type=content_type
        )
        return initial_request, next_request, kwargs

    @staticmethod
    def _list_metric_series_definitions_requests(metric_id, active_since, **kwargs):
        dimension_filter = kwargs.pop("dimension_filter", None)
        metric_series_query_options = MetricSeriesQueryOptions(
            active_since=active_since,
            dimension_filter=dimension_filter,
        )
        content_type = kwargs.pop("content_type", "application/json")
        initial_request = operations.build_list_metric_series_definitions_request(
            metric_id=metric_id,
            content_type=content_type,
            json=metric_series_query_options.serialize(),
            skip=kwargs.pop("skip", None),
            maxpagesize=kwargs.pop("maxpagesize", None),
        )
        next_request = operations.build_list_metric_series_definitions_request(
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
        time_mode: Union[str, models.AlertQueryTimeMode],
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
        initial_request = operations.build_list_alerts_request(
            configuration_id=alert_configuration_id,
            skip=skip,
            json=alerting_result_query.serialize(),
            content_type=content_type,
        )
        next_request = operations.build_list_alerts_request(
            configuration_id=alert_configuration_id,
            json=alerting_result_query.serialize(),
            content_type=content_type,
        )
        return initial_request, next_request, kwargs

    def _list_anomalies_for_detection_configuration_requests(
        self,
        detection_configuration_id: str,
        start_time: Union[str, datetime.datetime],
        end_time: Union[str, datetime.datetime],
        **kwargs: Any
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
        initial_request = operations.build_get_anomalies_by_anomaly_detection_configuration_request(
            configuration_id=detection_configuration_id,
            skip=skip,
            json=detection_anomaly_result_query.serialize(),
            content_type=content_type,
        )
        next_request = operations.build_get_anomalies_by_anomaly_detection_configuration_request(
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
        dimension_filter = models.DimensionGroupIdentity(dimension=dimension) if dimension else None
        converted_start_time = self._convert_datetime(start_time)
        converted_end_time = self._convert_datetime(end_time)
        anomaly_dimension_query = AnomalyDimensionQuery(
            start_time=converted_start_time,
            end_time=converted_end_time,
            dimension_name=dimension_name,
            dimension_filter=dimension_filter,
        )
        content_type = kwargs.pop("content_type", "application/json")
        initial_request = operations.build_list_anomaly_dimension_values_request(
            configuration_id=detection_configuration_id,
            skip=skip,
            json=anomaly_dimension_query.serialize(),
            content_type=content_type,
        )
        next_request = operations.build_list_anomaly_dimension_values_request(
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
        filter_condition = condition._to_generated() if condition else None  # pylint: disable=protected-access
        converted_start_time = self._convert_datetime(start_time)
        converted_end_time = self._convert_datetime(end_time)
        content_type = kwargs.pop("content_type", "application/json")
        detection_incident_result_query = DetectionIncidentResultQuery(
            start_time=converted_start_time,
            end_time=converted_end_time,
            filter=filter_condition,
        )
        initial_request = operations.build_get_incidents_by_anomaly_detection_configuration_request(
            configuration_id=detection_configuration_id,
            json=detection_incident_result_query.serialize(),
            content_type=content_type,
        )
        next_request = operations.build_get_incidents_by_anomaly_detection_configuration_request(
            configuration_id=detection_configuration_id,
            json=detection_incident_result_query.serialize(),
            content_type=content_type,
        )
        return initial_request, next_request, kwargs

    @staticmethod
    def _list_metric_dimension_values_requests(
        metric_id, dimension_name, **kwargs
    ) -> Tuple[HttpRequest, HttpRequest, Any]:
        skip = kwargs.pop("skip", None)
        dimension_value_filter = kwargs.pop("dimension_value_filter", None)
        content_type = kwargs.pop("content_type", "application/json")
        metric_dimension_query_options = MetricDimensionQueryOptions(
            dimension_name=dimension_name,
            dimension_value_filter=dimension_value_filter,
        )
        initial_request = operations.build_list_metric_dimension_values_request(
            metric_id=metric_id,
            json=metric_dimension_query_options.serialize(),
            skip=skip,
            content_type=content_type,
        )
        next_request = operations.build_list_metric_dimension_values_request(
            metric_id=metric_id,
            json=metric_dimension_query_options.serialize(),
            content_type=content_type,
        )
        return initial_request, next_request, kwargs

    def _list_metric_series_data_requests(
        self,
        metric_id: str,
        series_keys: List[Dict[str, str]],
        start_time: Union[str, datetime.datetime],
        end_time: Union[str, datetime.datetime],
        **kwargs: Any
    ) -> Tuple[HttpRequest, HttpRequest, Any]:
        converted_start_time = self._convert_datetime(start_time)
        converted_end_time = self._convert_datetime(end_time)

        metric_data_query_options = MetricDataQueryOptions(
            start_time=converted_start_time,
            end_time=converted_end_time,
            series=series_keys,
        )
        initial_request = operations.build_list_metric_series_data_request(
            metric_id=metric_id,
            json=metric_data_query_options.serialize(),
            content_type=kwargs.pop("content_type", "application/json"),
        )
        next_request = operations.build_list_metric_series_data_request(metric_id=metric_id)
        return initial_request, next_request, kwargs

    def _list_metric_enrichment_status_requests(
        self,
        metric_id: str,
        start_time: Union[str, datetime.datetime],
        end_time: Union[str, datetime.datetime],
        **kwargs: Any
    ) -> Tuple[HttpRequest, HttpRequest, Any]:
        skip = kwargs.pop("skip", None)
        converted_start_time = self._convert_datetime(start_time)
        converted_end_time = self._convert_datetime(end_time)
        enrichment_status_query_option = EnrichmentStatusQueryOption(
            start_time=converted_start_time,
            end_time=converted_end_time,
        )
        initial_request = operations.build_list_metric_enrichment_status_request(
            metric_id=metric_id,
            json=enrichment_status_query_option.serialize(),
            skip=skip,
            content_type=kwargs.pop("content_type", "application/json"),
        )
        next_request = operations.build_list_metric_enrichment_status_request(metric_id=metric_id)
        return initial_request, next_request, kwargs

    @staticmethod
    def _list_incidents_for_alert_requests(
        alert_configuration_id: str,
        alert_id: str,
        *,
        skip: Optional[int] = None,
        maxpagesize: Optional[int] = None,
        **kwargs: Any
    ) -> Tuple[HttpRequest, HttpRequest, Any]:
        initial_request = operations.build_list_incidents_for_alert_request(
            alert_configuration_id=alert_configuration_id,
            alert_id=alert_id,
            skip=skip,
            maxpagesize=maxpagesize,
        )
        next_request = operations.build_list_incidents_for_alert_request(
            alert_configuration_id=alert_configuration_id,
            alert_id=alert_id,
        )
        return initial_request, next_request, kwargs

    @staticmethod
    def _list_anomalies_for_alert_requests(
        alert_configuration_id: str, alert_id: str, **kwargs: Any
    ) -> Tuple[HttpRequest, HttpRequest, Any]:
        initial_request = operations.build_list_anomalies_for_alert_request(
            alert_configuration_id=alert_configuration_id,
            alert_id=alert_id,
            skip=kwargs.pop("skip", None),
        )
        next_request = operations.build_list_anomalies_for_alert_request(
            alert_configuration_id=alert_configuration_id, alert_id=alert_id
        )
        return initial_request, next_request, kwargs

    @staticmethod
    def _list_incident_root_causes_requests(detection_configuration_id: str, incident_id: str, **kwargs):
        initial_request = operations.build_list_incident_root_causes_request(
            detection_configuration_id=detection_configuration_id,
            incident_id=incident_id,
        )
        return initial_request, initial_request, kwargs

    @staticmethod
    def _list_hooks_requests(**kwargs):
        hook_name = kwargs.pop("hook_name", None)
        skip = kwargs.pop("skip", None)
        initial_request = operations.build_list_hooks_request(hook_name=hook_name, skip=skip)
        return initial_request, operations.build_list_hooks_request(), kwargs

    @staticmethod
    def _list_detection_configurations_requests(metric_id: str, **kwargs: Any):
        skip = kwargs.pop("skip", None)
        initial_request = operations.build_list_detection_configurations_request(metric_id=metric_id, skip=skip)
        next_request = operations.build_list_detection_configurations_request(metric_id=metric_id)
        return initial_request, next_request, kwargs

    @staticmethod
    def _list_datasource_credentials_requests(**kwargs):
        skip = kwargs.pop("skip", None)
        initial_request = operations.build_list_datasource_credentials_request(skip=skip)
        next_request = operations.build_list_datasource_credentials_request()
        return initial_request, next_request, kwargs

    def _update_alert_configuration_helper(
        self, alert_configuration: Union[str, models.AnomalyAlertConfiguration], **kwargs
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
                    [
                        config._to_generated()  # pylint: disable=protected-access
                        for config in update["metricAlertingConfigurations"]
                    ]
                    if update["metricAlertingConfigurations"]
                    else None
                )
            alert_configuration_patch = update

        else:
            alert_configuration_id = alert_configuration.id
            alert_configuration_patch = alert_configuration._to_generated(  # pylint: disable=protected-access
                **update
            ).serialize()
        content_type = kwargs.pop("content_type", "application/merge-patch+json")  # type: Optional[str]

        _json = self._serialize.body(alert_configuration_patch, "object")  # type: ignore  # pylint: disable=no-member

        request = operations.build_update_alert_configuration_request(
            configuration_id=alert_configuration_id,
            content_type=content_type,
            json=_json,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url(  # type: ignore  # pylint: disable=no-member
                "self._config.endpoint", self._config.endpoint, "str", skip_quote=True  # type: ignore  # pylint: disable=no-member
            ),
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)  # type: ignore  # pylint: disable=no-member
        return request, kwargs

    def _update_alert_configuration_deserialize(self, pipeline_response, **kwargs: Any):
        cls = kwargs.pop("cls", None)
        error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop("error_map", {}))
        response = pipeline_response.http_response

        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            error = self._deserialize.failsafe_deserialize(ErrorCode, pipeline_response)  # type: ignore  # pylint: disable=no-member
            raise HttpResponseError(response=response, model=error)

        deserialized = self._deserialize(  # type: ignore  # pylint: disable=no-member
            generated_models.AnomalyAlertConfiguration, pipeline_response
        )

        if cls:
            return cls(pipeline_response, deserialized, {})

        return deserialized

    def _get_feedback_request(self, feedback_id: str) -> HttpRequest:
        request = operations.build_get_feedback_request(
            feedback_id=feedback_id,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url(  # type: ignore  # pylint: disable=no-member
                "self._config.endpoint", self._config.endpoint, "str", skip_quote=True  # type: ignore  # pylint: disable=no-member
            ),
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)  # type: ignore  # pylint: disable=no-member
        return request

    def _get_feedback_deserialize(self, pipeline_response, **kwargs) -> models.MetricFeedback:
        cls = kwargs.pop("cls", None)
        error_map = kwargs.pop("error_map", None)
        response = pipeline_response.http_response
        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            error = self._deserialize.failsafe_deserialize(ErrorCode, pipeline_response)  # type: ignore  # pylint: disable=no-member
            raise HttpResponseError(response=response, model=error)
        deserialized = self._convert_to_sub_feedback(pipeline_response.http_response.json())

        if cls:
            return cls(pipeline_response, deserialized, {})

        return deserialized

    @staticmethod
    def _update_hook_helper(
        hook: Union[str, models.EmailNotificationHook, models.WebNotificationHook], **kwargs: Any
    ) -> Tuple[str, Union[Any, models.NotificationHook], Any]:
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
            hook_class = models.EmailNotificationHook if hook_type.lower() == "email" else models.WebNotificationHook
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
        shared_kwargs = {"externalLink": "external_link", "description": "description", "hookName": "name"}
        for rest_name, attr_name in shared_kwargs.items():
            hook_patch[rest_name] = passed_kwargs.pop(attr_name, hook_patch.get(rest_name))
        hook_patch["hookParameter"] = hook_patch.get("hookParameter", {})
        for rest_name, attr_name in specific_kwargs.items():
            hook_patch["hookParameter"][rest_name] = passed_kwargs.pop(
                attr_name, hook_patch["hookParameter"].get(rest_name)
            )
        for k in hook_kwarg_names:
            if k in kwargs:
                kwargs.pop(k)
        return hook_id, hook_patch, kwargs

    @staticmethod
    def _convert_datetime(date_time: Union[str, datetime.datetime]) -> datetime.datetime:
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

    def _get_paging_prepare_request(self, initial_request: HttpRequest, next_request: HttpRequest) -> Callable:
        def prepare_request(next_link=None):
            path_format_arguments = {
                "endpoint": self._serialize.url(  # type: ignore  # pylint: disable=no-member
                    "self._config.endpoint", self._config.endpoint, "str", skip_quote=True  # type: ignore  # pylint: disable=no-member
                ),
            }
            if not next_link:
                request = initial_request
                request.url = self._client.format_url(request.url, **path_format_arguments)  # type: ignore  # pylint: disable=no-member
            else:
                request = next_request
                request.url = self._client.format_url(next_link, **path_format_arguments)  # type: ignore  # pylint: disable=no-member
            return request

        return prepare_request

    def _deserialize_data_feed(self, json_response) -> models.DataFeed:
        data_source_parameter = json_response["dataSourceParameter"]
        data_source_type = json_response["dataSourceType"]
        return models.DataFeed._from_generated(  # pylint: disable=protected-access
            self._deserialize(generated_models.DataFeed, json_response),  # type: ignore  # pylint: disable=no-member
            data_source_parameter,
            data_source_type,
        )


def _extract_data_default(deserializer, pipeline_response):
    response_json = pipeline_response.http_response.json()
    list_of_elem = [deserializer(l) for l in response_json["value"]]
    return response_json.get("@nextLink", None) or None, iter(list_of_elem)


class MetricsAdvisorClientOperationsMixin(  # pylint: disable=too-many-public-methods,function-redefined
    _MetricsAdvisorClientOperationsMixin, OperationMixinHelpers
):
    def _paging_helper(
        self, *, extract_data=None, initial_request: HttpRequest, next_request: HttpRequest, deserializer=None, **kwargs
    ) -> ItemPaged:
        extract_data = extract_data or functools.partial(_extract_data_default, deserializer)
        error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop("error_map", {}))

        prepare_request = self._get_paging_prepare_request(initial_request=initial_request, next_request=next_request)

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
    def create_alert_configuration(  # type: ignore # pylint: disable=arguments-differ
        self,
        name: str,
        metric_alert_configurations: List[models.MetricAlertConfiguration],
        hook_ids: List[str],
        **kwargs: Any
    ) -> models.AnomalyAlertConfiguration:
        cross_metrics_operator = kwargs.pop("cross_metrics_operator", None)
        response_headers = super().create_alert_configuration(  # type: ignore
            models.AnomalyAlertConfiguration(
                name=name,
                metric_alert_configurations=[
                    m._to_generated() for m in metric_alert_configurations  # pylint: disable=protected-access
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
    def create_data_feed(  # type: ignore # pylint: disable=arguments-differ
        self,
        name: str,
        source: DataFeedSourceUnion,
        granularity: Union[str, models.DataFeedGranularityType, models.DataFeedGranularity],
        schema: Union[List[str], models.DataFeedSchema],
        ingestion_settings: Union[datetime.datetime, models.DataFeedIngestionSettings],
        **kwargs: Any
    ) -> models.DataFeed:
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
            data_feed._to_generated(),  # pylint: disable=protected-access
            cls=lambda pipeline_response, _, response_headers: response_headers,
            **kwargs
        )
        data_feed_id = response_headers["Location"].split("dataFeeds/")[1]
        return self.get_data_feed(data_feed_id)

    @distributed_trace
    def create_hook(  # type: ignore # pylint: disable=arguments-differ
        self, hook: Union[models.EmailNotificationHook, models.WebNotificationHook], **kwargs: Any
    ) -> Union[models.NotificationHook, models.EmailNotificationHook, models.WebNotificationHook]:
        response_headers = super().create_hook(  # type: ignore
            hook, cls=lambda pipeline_response, _, response_headers: response_headers, **kwargs  # type: ignore
        )
        hook_id = response_headers["Location"].split("hooks/")[1]
        return self.get_hook(hook_id)

    @distributed_trace
    def create_detection_configuration(  # type: ignore # pylint: disable=arguments-differ
        self,
        name: str,
        metric_id: str,
        whole_series_detection_condition: models.MetricDetectionCondition,
        **kwargs: Any
    ) -> models.AnomalyDetectionConfiguration:
        config = models.AnomalyDetectionConfiguration(
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
    def get_data_feed(self, data_feed_id: str, **kwargs: Any) -> models.DataFeed:
        cls = kwargs.pop("cls", None)
        error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop("error_map", {}))

        request = operations.build_get_data_feed_request(
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

        if cls:
            return cls(pipeline_response, self._deserialize(generated_models.DataFeed, pipeline_response), {})
        return self._deserialize_data_feed(response.json())

    @distributed_trace
    def get_alert_configuration(  # type: ignore # pylint: disable=arguments-differ
        self, alert_configuration_id: str, **kwargs: Any
    ) -> models.AnomalyAlertConfiguration:
        error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop("error_map", {}))

        request = operations.build_get_alert_configuration_request(
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
    def refresh_data_feed_ingestion(  # type: ignore # pylint: disable=arguments-differ
        self,
        data_feed_id: str,
        start_time: Union[str, datetime.datetime],
        end_time: Union[str, datetime.datetime],
        **kwargs: Any
    ) -> None:
        converted_start_time = self._convert_datetime(start_time)
        converted_end_time = self._convert_datetime(end_time)
        super().refresh_data_feed_ingestion(
            data_feed_id,
            body=IngestionProgressResetOptions(start_time=converted_start_time, end_time=converted_end_time),
            **kwargs
        )

    @distributed_trace
    def delete_alert_configuration(self, *alert_configuration_id: str, **kwargs: Any) -> None:
        if len(alert_configuration_id) != 1:
            raise TypeError("Alert configuration requires exactly one id.")

        super().delete_alert_configuration(alert_configuration_id[0], **kwargs)

    @distributed_trace
    def delete_detection_configuration(self, *detection_configuration_id: str, **kwargs: Any) -> None:
        if len(detection_configuration_id) != 1:
            raise TypeError("Detection configuration requires exactly one id.")

        super().delete_detection_configuration(detection_configuration_id[0], **kwargs)

    @distributed_trace
    def delete_data_feed(self, *data_feed_id: str, **kwargs: Any) -> None:
        if len(data_feed_id) != 1:
            raise TypeError("Data feed requires exactly one id.")

        super().delete_data_feed(data_feed_id[0], **kwargs)

    @distributed_trace
    def delete_hook(self, *hook_id: str, **kwargs: Any) -> None:
        if len(hook_id) != 1:
            raise TypeError("Hook requires exactly one id.")

        super().delete_hook(hook_id[0], **kwargs)

    @distributed_trace
    def update_data_feed(  # type: ignore # pylint: disable=arguments-differ
        self, data_feed: Union[str, models.DataFeed], **kwargs: Any
    ) -> models.DataFeed:
        data_feed_id, data_feed_patch, kwargs = self._update_data_feed_helper(data_feed, **kwargs)
        response = super().update_data_feed(data_feed_id, data_feed_patch, **kwargs)
        return self._deserialize_data_feed(response)

    @distributed_trace
    def update_alert_configuration(  # type: ignore # pylint: disable=arguments-differ
        self, alert_configuration: Union[str, models.AnomalyAlertConfiguration], **kwargs: Any
    ) -> models.AnomalyAlertConfiguration:
        request, kwargs = self._update_alert_configuration_helper(alert_configuration, **kwargs)
        pipeline_response = self._client._pipeline.run(  # pylint: disable=protected-access
            request, stream=False, **kwargs
        )
        return self._deserialize_anomaly_detection_configuration(pipeline_response, **kwargs)

    @distributed_trace
    def update_detection_configuration(  # type: ignore # pylint: disable=arguments-differ
        self, detection_configuration: Union[str, models.AnomalyDetectionConfiguration], **kwargs: Any
    ) -> models.AnomalyDetectionConfiguration:
        detection_configuration_id, detection_config_patch, kwargs = self._update_detection_configuration_helper(
            detection_configuration, **kwargs
        )

        return super().update_detection_configuration(
            configuration_id=detection_configuration_id, body=detection_config_patch, **kwargs
        )

    @distributed_trace
    def update_hook(  # type: ignore # pylint: disable=arguments-differ
        self, hook: Union[str, models.EmailNotificationHook, models.WebNotificationHook], **kwargs: Any
    ) -> Union[models.NotificationHook, models.EmailNotificationHook, models.WebNotificationHook]:
        hook_id, hook_patch, kwargs = self._update_hook_helper(hook, **kwargs)

        return super().update_hook(hook_id, hook_patch, **kwargs)

    @distributed_trace
    def list_data_feeds(  # type: ignore # pylint: disable=arguments-differ
        self,
        *,
        data_feed_name: Optional[str] = None,
        data_source_type: Optional[Union[str, "models.DatasourceType"]] = None,
        granularity_type: Optional[Union[str, "models.DataFeedGranularityType"]] = None,
        status: Optional[Union[str, "models.DataFeedStatus"]] = None,
        creator: Optional[str] = None,
        skip: Optional[int] = None,
        maxpagesize: Optional[int] = None,
        **kwargs: Any
    ) -> ItemPaged[models.DataFeed]:
        return self._paging_helper(
            initial_request=operations.build_list_data_feeds_request(
                data_feed_name=data_feed_name,
                data_source_type=data_source_type,
                granularity_name=granularity_type,
                status=status,
                creator=creator,
                skip=skip,
                maxpagesize=maxpagesize,
            ),
            next_request=operations.build_list_data_feeds_request(),
            deserializer=self._deserialize_data_feed,
            **kwargs
        )

    @distributed_trace
    def list_alert_configurations(  # type: ignore # pylint: disable=arguments-differ
        self, detection_configuration_id: str, **kwargs: Any
    ) -> ItemPaged[models.AnomalyAlertConfiguration]:
        def _deserialize(deserializer, line):
            config_to_generated = functools.partial(deserializer, generated_models.MetricAlertConfiguration)
            line["metricAlertingConfigurations"] = [
                config_to_generated(config) for config in line.get("metricAlertingConfigurations", [])
            ]
            return models.AnomalyAlertConfiguration._from_generated(  # pylint: disable=protected-access
                deserializer(generated_models.AnomalyAlertConfiguration, line)
            )

        return self._paging_helper(
            initial_request=operations.build_list_alert_configurations_request(
                configuration_id=detection_configuration_id,
                skip=kwargs.pop("skip", None),
                maxpagesize=kwargs.pop("maxpagesize", None),
            ),
            next_request=operations.build_list_alert_configurations_request(
                configuration_id=detection_configuration_id
            ),
            deserializer=functools.partial(_deserialize, self._deserialize),
            **kwargs
        )

    @distributed_trace
    def list_data_feed_ingestion_status(  # type: ignore # pylint: disable=arguments-differ
        self,
        data_feed_id: str,
        start_time: Union[str, datetime.datetime],
        end_time: Union[str, datetime.datetime],
        **kwargs: Any
    ) -> ItemPaged[models.DataFeedIngestionStatus]:
        initial_request, next_request, kwargs = self._list_data_feed_ingestion_status_requests(
            data_feed_id, start_time, end_time, **kwargs
        )
        return self._paging_helper(
            initial_request=initial_request,
            next_request=next_request,
            deserializer=models.DataFeedIngestionStatus.deserialize,
            **kwargs
        )

    @distributed_trace
    def create_datasource_credential(  # type: ignore # pylint: disable=arguments-differ
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
    def get_datasource_credential(self, credential_id: str, **kwargs: Any) -> DatasourceCredentialUnion:
        response = super().get_datasource_credential(credential_id=credential_id, **kwargs)
        return self._deserialize_datasource_credential(response)

    @distributed_trace
    def update_datasource_credential(  # type: ignore # pylint: disable=arguments-differ
        self, datasource_credential: DatasourceCredentialUnion, **kwargs: Any
    ) -> DatasourceCredentialUnion:
        response = super().update_datasource_credential(datasource_credential.id, datasource_credential, **kwargs)
        return self._deserialize_datasource_credential(response)

    @distributed_trace
    def delete_datasource_credential(self, *credential_id: str, **kwargs: Any) -> None:
        if len(credential_id) != 1:
            raise TypeError("Credential requires exactly one id.")

        super().delete_datasource_credential(credential_id=credential_id[0], **kwargs)

    @distributed_trace
    def get_feedback(self, feedback_id: str, **kwargs: Any) -> Union[models.MetricFeedback, FeedbackUnion]:
        cls = kwargs.pop("cls", None)
        error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop("error_map", {}))

        request = self._get_feedback_request(feedback_id=feedback_id)
        pipeline_response = self._client._pipeline.run(  # pylint: disable=protected-access
            request, stream=False, **kwargs
        )
        return self._get_feedback_deserialize(pipeline_response, cls=cls, error_map=error_map, **kwargs)

    @distributed_trace
    def list_feedback(  # type: ignore # pylint: disable=arguments-differ
        self, metric_id: str, **kwargs: Any
    ) -> ItemPaged[Union[models.MetricFeedback, FeedbackUnion]]:
        deserializer = functools.partial(self._deserialize, generated_models.MetricFeedback)
        initial_request, next_request, kwargs = self._list_feedback_requests(metric_id, **kwargs)
        return self._paging_helper(
            initial_request=initial_request, next_request=next_request, deserializer=deserializer, **kwargs
        )

    @distributed_trace
    def list_metric_enriched_series_data(  # type: ignore # pylint: disable=arguments-differ
        self,
        detection_configuration_id: str,
        series: Union[List[models.SeriesIdentity], List[Dict[str, str]]],
        start_time: Union[str, datetime.datetime],
        end_time: Union[str, datetime.datetime],
        **kwargs: Any
    ) -> ItemPaged[models.MetricEnrichedSeriesData]:
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
            deserializer=models.MetricEnrichedSeriesData.deserialize,
            **kwargs
        )

    @distributed_trace
    def list_alerts(  # type: ignore # pylint: disable=arguments-differ
        self,
        alert_configuration_id: str,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        time_mode: Union[str, models.AlertQueryTimeMode],
        **kwargs: Any
    ) -> ItemPaged[models.AnomalyAlert]:
        initial_request, next_request, kwargs = self._list_alerts_requests(
            alert_configuration_id=alert_configuration_id,
            start_time=start_time,
            end_time=end_time,
            time_mode=time_mode,
            **kwargs
        )
        return self._paging_helper(
            initial_request=initial_request,
            next_request=next_request,
            deserializer=models.AnomalyAlert.deserialize,
            **kwargs
        )

    def _list_anomalies_for_detection_configuration(
        self,
        detection_configuration_id: str,
        start_time: Union[str, datetime.datetime],
        end_time: Union[str, datetime.datetime],
        **kwargs: Any
    ) -> ItemPaged[models.DataPointAnomaly]:
        initial_request, next_request, kwargs = self._list_anomalies_for_detection_configuration_requests(
            detection_configuration_id=detection_configuration_id, start_time=start_time, end_time=end_time, **kwargs
        )
        return self._paging_helper(
            initial_request=initial_request,
            next_request=next_request,
            deserializer=models.DataPointAnomaly.deserialize,
            **kwargs
        )

    @distributed_trace
    def _list_anomalies_for_alert(
        self, alert_configuration_id: str, alert_id: str, **kwargs: Any
    ) -> Iterable[models.DataPointAnomaly]:
        initial_request, next_request, kwargs = self._list_anomalies_for_alert_requests(
            alert_configuration_id=alert_configuration_id, alert_id=alert_id, **kwargs
        )
        return self._paging_helper(
            initial_request=initial_request,
            next_request=next_request,
            deserializer=models.DataPointAnomaly.deserialize,
            **kwargs
        )

    @distributed_trace
    def list_anomalies(self, **kwargs: Any) -> ItemPaged[models.DataPointAnomaly]:
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
    def list_anomaly_dimension_values(  # type: ignore # pylint: disable=arguments-differ
        self,
        detection_configuration_id: str,
        dimension_name: str,
        start_time: Union[str, datetime.datetime],
        end_time: Union[str, datetime.datetime],
        **kwargs: Any
    ) -> ItemPaged[str]:
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

    def _list_incidents_for_detection_configuration(
        self,
        detection_configuration_id: str,
        start_time: Union[str, datetime.datetime],
        end_time: Union[str, datetime.datetime],
        **kwargs: Any
    ) -> ItemPaged[models.AnomalyIncident]:
        initial_request, next_request, kwargs = self._list_incidents_for_detection_configuration_requests(
            detection_configuration_id=detection_configuration_id, start_time=start_time, end_time=end_time, **kwargs
        )
        return self._paging_helper(
            initial_request=initial_request,
            next_request=next_request,
            deserializer=models.AnomalyIncident.deserialize,
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
    ) -> Iterable[models.AnomalyIncident]:
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
            deserializer=models.AnomalyIncident.deserialize,
            **kwargs
        )

    @distributed_trace
    def list_incidents(self, **kwargs: Any) -> ItemPaged[models.AnomalyIncident]:
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
    def list_metric_dimension_values(  # type: ignore # pylint: disable=arguments-differ
        self, metric_id: str, dimension_name: str, **kwargs: Any
    ) -> ItemPaged[str]:
        initial_request, next_request, kwargs = self._list_metric_dimension_values_requests(
            metric_id=metric_id, dimension_name=dimension_name, **kwargs
        )
        return self._paging_helper(
            initial_request=initial_request, next_request=next_request, deserializer=lambda x: x, **kwargs
        )

    @distributed_trace
    def list_metric_series_data(  # type: ignore # pylint: disable=arguments-differ
        self,
        metric_id: str,
        series_keys: List[Dict[str, str]],
        start_time: Union[str, datetime.datetime],
        end_time: Union[str, datetime.datetime],
        **kwargs: Any
    ) -> ItemPaged[models.MetricSeriesData]:
        initial_request, next_request, kwargs = self._list_metric_series_data_requests(
            metric_id=metric_id, series_keys=series_keys, start_time=start_time, end_time=end_time, **kwargs
        )

        return self._paging_helper(
            initial_request=initial_request,
            next_request=next_request,
            deserializer=models.MetricSeriesData.deserialize,
            **kwargs
        )

    @distributed_trace
    def list_metric_series_definitions(  # type: ignore # pylint: disable=arguments-differ
        self, metric_id: str, active_since: datetime.datetime, **kwargs: Any
    ) -> ItemPaged[models.MetricSeriesDefinition]:
        initial_request, next_request, kwargs = self._list_metric_series_definitions_requests(
            metric_id, active_since, **kwargs
        )

        next_request.method = "POST"
        return self._paging_helper(
            initial_request=initial_request,
            next_request=next_request,
            deserializer=models.MetricSeriesDefinition.deserialize,
            **kwargs
        )

    @distributed_trace
    def list_metric_enrichment_status(  # type: ignore # pylint: disable=arguments-differ
        self,
        metric_id: str,
        start_time: Union[str, datetime.datetime],
        end_time: Union[str, datetime.datetime],
        **kwargs: Any
    ) -> ItemPaged[models.EnrichmentStatus]:
        initial_request, next_request, kwargs = self._list_metric_enrichment_status_requests(
            metric_id=metric_id, start_time=start_time, end_time=end_time, **kwargs
        )
        return self._paging_helper(
            initial_request=initial_request,
            next_request=next_request,
            deserializer=models.EnrichmentStatus.deserialize,
            **kwargs
        )

    @distributed_trace
    def list_incident_root_causes(
        self, detection_configuration_id: str, incident_id: str, **kwargs: Any
    ) -> ItemPaged[models.IncidentRootCause]:
        initial_request, next_request, kwargs = self._list_incident_root_causes_requests(
            detection_configuration_id=detection_configuration_id, incident_id=incident_id, **kwargs
        )
        return self._paging_helper(
            initial_request=initial_request,
            next_request=next_request,
            deserializer=models.IncidentRootCause.deserialize,
            **kwargs
        )

    @distributed_trace
    def list_hooks(self, **kwargs: Any) -> ItemPaged[models.NotificationHook]:  # type: ignore
        initial_request, next_request, kwargs = self._list_hooks_requests(**kwargs)
        return self._paging_helper(
            initial_request=initial_request,
            next_request=next_request,
            deserializer=models.NotificationHook.deserialize,
            **kwargs
        )

    @distributed_trace
    def list_detection_configurations(  # type: ignore
        self, metric_id: str, **kwargs: Any
    ) -> ItemPaged[models.AnomalyDetectionConfiguration]:
        initial_request, next_request, kwargs = self._list_detection_configurations_requests(metric_id, **kwargs)
        return self._paging_helper(
            initial_request=initial_request,
            next_request=next_request,
            deserializer=models.AnomalyDetectionConfiguration.deserialize,
            **kwargs
        )

    @distributed_trace
    def list_datasource_credentials(self, **kwargs: Any) -> ItemPaged[models.DatasourceCredential]:  # type: ignore
        initial_request, next_request, kwargs = self._list_datasource_credentials_requests(**kwargs)
        return self._paging_helper(
            initial_request=initial_request,
            next_request=next_request,
            deserializer=self._deserialize_datasource_credential,
            **kwargs
        )


__all__ = ["MetricsAdvisorClientOperationsMixin"]


def patch_sdk():  # pylint: disable=function-redefined
    pass
