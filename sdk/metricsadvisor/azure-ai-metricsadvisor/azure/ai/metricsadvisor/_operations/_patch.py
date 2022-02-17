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
from azure.core import PipelineClient
from ._operations import (
    MetricsAdvisorClientOperationsMixin as _MetricsAdvisorClientOperationsMixin,
    build_get_data_feed_request,
    build_list_data_feeds_request,
    build_get_alert_configuration_request,
    build_list_alert_configurations_request,
    build_update_alert_configuration_request,
    build_get_feedback_request,
    JSONType,
)
from ..models import *
from ..models import _models_py3 as generated_models
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

    def _convert_to_datasource_credential(self, datasource_credential):
        if datasource_credential.data_source_credential_type == "AzureSQLConnectionString":
            return DatasourceSqlConnectionString._from_generated(datasource_credential)
        if datasource_credential.data_source_credential_type == "DataLakeGen2SharedKey":
            return DatasourceDataLakeGen2SharedKey._from_generated(datasource_credential)
        if datasource_credential.data_source_credential_type == "ServicePrincipal":
            return DatasourceServicePrincipal._from_generated(datasource_credential)
        return DatasourceServicePrincipalInKeyVault._from_generated(datasource_credential)

    def _construct_alert_config_dict(self, **update_kwargs):

        if "metricAlertingConfigurations" in update_kwargs:
            update_kwargs["metricAlertingConfigurations"] = (
                [config._to_generated() for config in update_kwargs["metricAlertingConfigurations"]]
                if update_kwargs["metricAlertingConfigurations"]
                else None
            )

        return update_kwargs

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

    def _deserialize_anomaly_detection_configuration(self, http_response, **kwargs) -> AnomalyAlertConfiguration:
        cls = kwargs.pop("cls", None)
        response_json = http_response.json()
        response_json["metricAlertingConfigurations"] = [
            self._deserialize(generated_models.MetricAlertConfiguration, m)
            for m in response_json["metricAlertingConfigurations"]
        ]
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

        _json = self._serialize.body(alert_configuration_patch, "AnomalyAlertingConfigurationPatch")

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

        deserialized =  self._convert_to_sub_feedback(self._deserialize(generated_models.MetricFeedback, pipeline_response))

        if cls:
            return cls(pipeline_response, deserialized, {})

        return deserialized

    def _update_hook_helper(
        self, hook: Union[str, EmailNotificationHook, WebNotificationHook], **kwargs: Any
    ) -> Tuple[str, Union[JSONType, NotificationHook], Any]:
        hook_patch = None
        hook_type = kwargs.get("hook_type")
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
        if isinstance(hook, str):
            hook_id = hook
            if hook_type is None:
                raise ValueError("hook_type must be passed with a hook ID.")
            hook_patch = {k: v for k, v in kwargs.items() if k in hook_kwarg_names}

        else:
            hook_patch = hook
            hook_id = hook.id
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


class MetricsAdvisorClientOperationsMixin(_MetricsAdvisorClientOperationsMixin, OperationMixinHelpers):
    def _paging_helper(
        self, *, extract_data, initial_request: HttpRequest, next_request: HttpRequest, **kwargs
    ) -> ItemPaged:
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

        return self._deserialize_anomaly_detection_configuration(pipeline_response.http_response, **kwargs)

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
        return self._deserialize_anomaly_detection_configuration(pipeline_response.http_response, **kwargs)

    @distributed_trace
    def update_detection_configuration(
        self, detection_configuration: Union[str, AnomalyDetectionConfiguration], **kwargs: Any
    ) -> AnomalyDetectionConfiguration:
        detection_configuration_id, detection_config_patch, kwargs = self._update_detection_configuration_helper(
            detection_configuration, **kwargs
        )

        return super().update_anomaly_detection_configuration(
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
        skip = kwargs.pop("skip", None)
        converted_start_time = self._convert_datetime(start_time)
        converted_end_time = self._convert_datetime(end_time)

        return super().list_data_feed_ingestion_status(  # type: ignore
            data_feed_id=data_feed_id,
            body=IngestionStatusQueryOptions(start_time=converted_start_time, end_time=converted_end_time),
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
        datasource_credential = super().get_datasource_credential(credential_id, **kwargs)
        return convert_to_datasource_credential(datasource_credential)

    @distributed_trace
    def create_datasource_credential(
        self,
        datasource_credential,  # type: DatasourceCredentialUnion
        **kwargs  # type: Any
    ):
        # type: (...) -> DatasourceCredentialUnion
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
        return super().list_credentials(  # type: ignore
            cls=kwargs.pop(
                "cls",
                lambda credentials: [convert_to_datasource_credential(credential) for credential in credentials],
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
        datasource_credential_request = None
        if datasource_credential.credential_type in [
            "AzureSQLConnectionString",
            "DataLakeGen2SharedKey",
            "ServicePrincipal",
            "ServicePrincipalInKV",
        ]:
            datasource_credential_request = datasource_credential._to_generated_patch()

        updated_datasource_credential = super().update_credential(  # type: ignore
            datasource_credential.id, datasource_credential_request, **kwargs  # type: ignore
        )

        return convert_to_datasource_credential(updated_datasource_credential)

    @distributed_trace
    def delete_datasource_credential(self, *credential_id, **kwargs):
        # type: (*str, Any) -> None
        if len(credential_id) != 1:
            raise TypeError("Credential requires exactly one id.")

        super().delete_datasource_credential(credential_id=credential_id[0], **kwargs)

    @distributed_trace
    def add_feedback(self, feedback, **kwargs):
        # type: (FeedbackUnion, Any) -> None
        return super().add_feedback(body=feedback, **kwargs)

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
    def list_feedback(self, metric_id, **kwargs):
        # type: (str, Any) -> ItemPaged[Union[MetricFeedback, FeedbackUnion]]
        skip = kwargs.pop("skip", None)
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

        return super().list_feedback(  # type: ignore
            skip=skip,
            body=feedback_filter,
            cls=kwargs.pop("cls", lambda result: [self._convert_to_sub_feedback(x) for x in result]),
            **kwargs
        )

    @distributed_trace
    def list_incident_root_causes(self, detection_configuration_id, incident_id, **kwargs):
        # type: (str, str, Any) -> ItemPaged[IncidentRootCause]
        return super().list_incident_root_causes(  # type: ignore
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
        # type: (...) -> ItemPaged[MetricEnrichedSeriesData]
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

        return super().list_metric_enriched_series_data(  # type: ignore
            configuration_id=detection_configuration_id,
            body=detection_series_query,
            cls=kwargs.pop(
                "cls",
                lambda series: [MetricEnrichedSeriesData._from_generated(data) for data in series],
            ),
            **kwargs
        )

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
        skip = kwargs.pop("skip", None)
        converted_start_time = self._convert_datetime(start_time)
        converted_end_time = self._convert_datetime(end_time)

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
                lambda alerts: [AnomalyAlert._from_generated(alert) for alert in alerts],
            ),
            **kwargs
        )

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

    def _list_anomalies_for_detection_configuration(self, detection_configuration_id, start_time, end_time, **kwargs):
        # type: (...) -> ItemPaged[DataPointAnomaly]

        skip = kwargs.pop("skip", None)
        condition = kwargs.pop("filter", None)
        filter_condition = condition._to_generated() if condition else None
        converted_start_time = self._convert_datetime(start_time)
        converted_end_time = self._convert_datetime(end_time)
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
        return self._list_anomalies_for_alert(**kwargs)

    @distributed_trace
    def list_anomaly_dimension_values(self, detection_configuration_id, dimension_name, start_time, end_time, **kwargs):
        # type: (str, str, Union[str, datetime.datetime], Union[str, datetime.datetime], Any) -> ItemPaged[str]
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

        return super().list_anomaly_dimension_values(  # type: ignore
            configuration_id=detection_configuration_id, skip=skip, body=anomaly_dimension_query, **kwargs
        )

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

    def _list_incidents_for_detection_configuration(self, detection_configuration_id, start_time, end_time, **kwargs):
        # type: (str, Union[str, datetime.datetime], Union[str, datetime.datetime], Any) -> ItemPaged[AnomalyIncident]

        condition = kwargs.pop("filter", None)
        filter_condition = condition._to_generated() if condition else None
        converted_start_time = self._convert_datetime(start_time)
        converted_end_time = self._convert_datetime(end_time)

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
        return self._list_incidents_for_alert(**kwargs)

    @distributed_trace
    def list_metric_dimension_values(self, metric_id, dimension_name, **kwargs):
        # type: (str, str, Any) -> ItemPaged[str]
        skip = kwargs.pop("skip", None)
        dimension_value_filter = kwargs.pop("dimension_value_filter", None)

        metric_dimension_query_options = MetricDimensionQueryOptions(
            dimension_name=dimension_name,
            dimension_value_filter=dimension_value_filter,
        )

        return super().list_metric_dimension_values(  # type: ignore
            metric_id=metric_id, body=metric_dimension_query_options, skip=skip, **kwargs
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
        converted_start_time = self._convert_datetime(start_time)
        converted_end_time = self._convert_datetime(end_time)

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
                lambda result: [MetricSeriesData._from_generated(series) for series in result],
            ),
            **kwargs
        )

    @distributed_trace
    def list_metric_series_definitions(self, metric_id, active_since, **kwargs):
        # type: (str, datetime.datetime, Any) -> ItemPaged[MetricSeriesDefinition]
        skip = kwargs.pop("skip", None)
        dimension_filter = kwargs.pop("dimension_filter", None)

        metric_series_query_options = MetricSeriesQueryOptions(
            active_since=active_since,
            dimension_filter=dimension_filter,
        )

        return super().list_metric_series_definitions(  # type: ignore
            metric_id=metric_id, body=metric_series_query_options, skip=skip, **kwargs
        )

    @distributed_trace
    def list_metric_enrichment_status(self, metric_id, start_time, end_time, **kwargs):
        # type: (str, Union[str, datetime.datetime], Union[str, datetime.datetime], Any) -> ItemPaged[EnrichmentStatus]
        skip = kwargs.pop("skip", None)
        converted_start_time = self._convert_datetime(start_time)
        converted_end_time = self._convert_datetime(end_time)
        enrichment_status_query_option = EnrichmentStatusQueryOption(
            start_time=converted_start_time,
            end_time=converted_end_time,
        )

        return super().list_metric_enrichment_status(  # type: ignore
            metric_id=metric_id, skip=skip, body=enrichment_status_query_option, **kwargs
        )


__all__ = ["MetricsAdvisorClientOperationsMixin"]


def patch_sdk():
    pass
