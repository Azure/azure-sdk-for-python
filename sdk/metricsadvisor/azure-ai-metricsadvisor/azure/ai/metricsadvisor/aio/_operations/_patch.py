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
import functools
from typing import List, Dict, Any, Optional, Union, cast
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.async_paging import AsyncItemPaged, AsyncList
from azure.core.rest import HttpRequest
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    map_error,
)
from ...models import _models_py3 as generated_models
from ...models._patch import (
    IngestionProgressResetOptions,
    ErrorCode,
)

from ._operations import MetricsAdvisorClientOperationsMixin as MetricsAdvisorClientOperationsMixinGenerated
from ..._operations._patch import (
    DataFeedSourceUnion,
    DatasourceCredentialUnion,
    FeedbackUnion,
    build_get_data_feed_request,
    build_list_data_feeds_request,
    build_get_alert_configuration_request,
    build_list_alert_configurations_request,
    build_list_metric_series_definitions_request,
    OperationMixinHelpers,
)
from ...models import *


async def _extract_data_default(deserializer, pipeline_response):
    response_json = pipeline_response.http_response.json()
    list_of_elem = [deserializer(l) for l in response_json["value"]]
    return response_json.get("@nextLink", None) or None, AsyncList(list_of_elem)


class MetricsAdvisorClientOperationsMixin(MetricsAdvisorClientOperationsMixinGenerated, OperationMixinHelpers):
    def _paging_helper(
        self, *, extract_data=None, initial_request: HttpRequest, next_request: HttpRequest, deserializer=None, **kwargs
    ) -> AsyncItemPaged:
        extract_data = extract_data or functools.partial(_extract_data_default, deserializer)
        error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop("error_map", {}))

        prepare_request = self._get_paging_prepare_request(
            initial_request=initial_request, next_request=next_request, **kwargs
        )

        async def get_next(next_link=None):
            request = prepare_request(next_link)

            pipeline_response = await self._client._pipeline.run(  # pylint: disable=protected-access
                request, stream=False, **kwargs
            )
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                error = self._deserialize.failsafe_deserialize(ErrorCode, pipeline_response)
                raise HttpResponseError(response=response, model=error)

            return pipeline_response

        return AsyncItemPaged(get_next, extract_data)

    @distributed_trace_async
    async def create_alert_configuration(
        self, name: str, metric_alert_configurations: List[MetricAlertConfiguration], hook_ids: List[str], **kwargs: Any
    ) -> AnomalyAlertConfiguration:
        cross_metrics_operator = kwargs.pop("cross_metrics_operator", None)
        response_headers = await super().create_alert_configuration(
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
        response_headers = await super().create_data_feed(  # type: ignore
            data_feed._to_generated(), cls=lambda pipeline_response, _, response_headers: response_headers, **kwargs
        )
        data_feed_id = response_headers["Location"].split("dataFeeds/")[1]
        return await self.get_data_feed(data_feed_id)

    @distributed_trace_async
    async def create_hook(
        self, hook: Union[EmailNotificationHook, WebNotificationHook], **kwargs: Any
    ) -> Union[NotificationHook, EmailNotificationHook, WebNotificationHook]:
        response_headers = await super().create_hook(  # type: ignore
            hook, cls=lambda pipeline_response, _, response_headers: response_headers, **kwargs  # type: ignore
        )
        hook_id = response_headers["Location"].split("hooks/")[1]
        return await self.get_hook(hook_id)

    @distributed_trace_async
    async def create_detection_configuration(
        self, name: str, metric_id: str, whole_series_detection_condition: MetricDetectionCondition, **kwargs: Any
    ) -> AnomalyDetectionConfiguration:
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

        response_headers = await super().create_detection_configuration(
            config, cls=lambda pipeline_response, _, response_headers: response_headers, **kwargs
        )
        response_headers = cast(dict, response_headers)
        config_id = response_headers["Location"].split("configurations/")[1]
        return await self.get_detection_configuration(config_id)

    @distributed_trace_async
    async def get_data_feed(self, data_feed_id: str, **kwargs: Any) -> DataFeed:
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

        pipeline_response = await self._client._pipeline.run(  # pylint: disable=protected-access
            request, stream=False, **kwargs
        )
        response = pipeline_response.http_response

        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            error = self._deserialize.failsafe_deserialize(ErrorCode, pipeline_response)
            raise HttpResponseError(response=response, model=error)

        if cls:
            return cls(pipeline_response, self._deserialize(generated_models.DataFeed, pipeline_response), {})
        json_response = response.json()
        return self._deserialize_data_feed(json_response)

    @distributed_trace_async
    async def get_alert_configuration(self, alert_configuration_id: str, **kwargs: Any) -> AnomalyAlertConfiguration:
        error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop("error_map", {}))

        request = build_get_alert_configuration_request(
            configuration_id=alert_configuration_id,
        )
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)

        pipeline_response = await self._client._pipeline.run(  # pylint: disable=protected-access
            request, stream=False, **kwargs
        )
        response = pipeline_response.http_response

        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            error = self._deserialize.failsafe_deserialize(ErrorCode, pipeline_response)
            raise HttpResponseError(response=response, model=error)

        return self._deserialize_anomaly_detection_configuration(pipeline_response, **kwargs)

    @distributed_trace_async
    async def refresh_data_feed_ingestion(
        self,
        data_feed_id: str,
        start_time: Union[str, datetime.datetime],
        end_time: Union[str, datetime.datetime],
        **kwargs: Any
    ) -> None:
        converted_start_time = self._convert_datetime(start_time)
        converted_end_time = self._convert_datetime(end_time)
        await super().refresh_data_feed_ingestion(
            data_feed_id,
            body=IngestionProgressResetOptions(start_time=converted_start_time, end_time=converted_end_time),
            **kwargs
        )

    @distributed_trace_async
    async def delete_alert_configuration(self, *alert_configuration_id: str, **kwargs: Any) -> None:
        if len(alert_configuration_id) != 1:
            raise TypeError("Alert configuration requires exactly one id.")

        await super().delete_alert_configuration(alert_configuration_id[0], **kwargs)

    @distributed_trace_async
    async def delete_detection_configuration(self, *detection_configuration_id: str, **kwargs: Any) -> None:
        if len(detection_configuration_id) != 1:
            raise TypeError("Detection configuration requires exactly one id.")

        await super().delete_detection_configuration(detection_configuration_id[0], **kwargs)

    @distributed_trace_async
    async def delete_data_feed(self, *data_feed_id: str, **kwargs: Any) -> None:
        if len(data_feed_id) != 1:
            raise TypeError("Data feed requires exactly one id.")

        await super().delete_data_feed(data_feed_id[0], **kwargs)

    @distributed_trace_async
    async def delete_hook(self, *hook_id: str, **kwargs: Any) -> None:
        if len(hook_id) != 1:
            raise TypeError("Hook requires exactly one id.")

        await super().delete_hook(hook_id[0], **kwargs)

    @distributed_trace_async
    async def update_data_feed(self, data_feed: Union[str, DataFeed], **kwargs: Any) -> DataFeed:
        data_feed_id, data_feed_patch, kwargs = self._update_data_feed_helper(data_feed, **kwargs)
        return await super().update_data_feed(data_feed_id, data_feed_patch, **kwargs)

    @distributed_trace_async
    async def update_alert_configuration(
        self, alert_configuration: Union[str, AnomalyAlertConfiguration], **kwargs: Any
    ) -> AnomalyAlertConfiguration:
        request, kwargs = self._update_alert_configuration_helper(alert_configuration, **kwargs)
        pipeline_response = await self._client._pipeline.run(  # pylint: disable=protected-access
            request, stream=False, **kwargs
        )
        return self._deserialize_anomaly_detection_configuration(pipeline_response, **kwargs)

    @distributed_trace_async
    async def update_detection_configuration(
        self, detection_configuration: Union[str, AnomalyDetectionConfiguration], **kwargs: Any
    ) -> AnomalyDetectionConfiguration:
        detection_configuration_id, detection_config_patch, kwargs = self._update_detection_configuration_helper(
            detection_configuration, **kwargs
        )

        return await super().update_detection_configuration(
            configuration_id=detection_configuration_id, body=detection_config_patch, **kwargs
        )

    @distributed_trace_async
    async def update_hook(
        self, hook: Union[str, EmailNotificationHook, WebNotificationHook], **kwargs: Any
    ) -> Union[NotificationHook, EmailNotificationHook, WebNotificationHook]:
        hook_id, hook_patch, kwargs = self._update_hook_helper(hook, **kwargs)

        return await super().update_hook(hook_id, hook_patch, **kwargs)

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
    ) -> AsyncItemPaged[DataFeed]:
        return self._paging_helper(
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
            deserializer=self._deserialize_data_feed,
            **kwargs
        )

    @distributed_trace
    def list_alert_configurations(
        self, detection_configuration_id: str, **kwargs: Any
    ) -> AsyncItemPaged[AnomalyAlertConfiguration]:
        def _deserialize(deserializer, line):
            config_to_generated = functools.partial(deserializer, generated_models.MetricAlertConfiguration)
            line["metricAlertingConfigurations"] = [
                config_to_generated(config) for config in line.get("metricAlertingConfigurations", [])
            ]
            return AnomalyAlertConfiguration._from_generated(
                deserializer(generated_models.AnomalyAlertConfiguration, line)
            )

        return self._paging_helper(
            initial_request=build_list_alert_configurations_request(
                configuration_id=detection_configuration_id,
                skip=kwargs.pop("skip", None),
                maxpagesize=kwargs.pop("maxpagesize", None),
            ),
            next_request=build_list_alert_configurations_request(configuration_id=detection_configuration_id),
            deserializer=functools.partial(_deserialize, self._deserialize),
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
        initial_request, next_request, kwargs = self._list_data_feed_ingestion_status_requests(
            data_feed_id, start_time, end_time, **kwargs
        )
        return self._paging_helper(
            initial_request=initial_request,
            next_request=next_request,
            deserializer=DataFeedIngestionStatus.deserialize,
            **kwargs
        )

    @distributed_trace_async
    async def create_datasource_credential(
        self,
        datasource_credential,  # type: DatasourceCredentialUnion
        **kwargs  # type: Any
    ):
        # type: (...) -> DatasourceCredentialUnion
        response_headers = await super().create_datasource_credential(  # type: ignore
            datasource_credential,  # type: ignore
            cls=lambda pipeline_response, _, response_headers: response_headers,
            **kwargs
        )
        credential_id = response_headers["Location"].split("credentials/")[1]  # type: ignore
        return await self.get_datasource_credential(credential_id)

    @distributed_trace_async
    async def update_datasource_credential(
        self, datasource_credential: DatasourceCredentialUnion, **kwargs: Any
    ) -> DatasourceCredentialUnion:
        response = await super().update_datasource_credential(datasource_credential.id, datasource_credential, **kwargs)
        return self._deserialize_datasource_credential(response)

    @distributed_trace
    async def get_datasource_credential(self, credential_id: str, **kwargs: Any) -> DatasourceCredentialUnion:
        response = await super().get_datasource_credential(credential_id=credential_id, **kwargs)
        return self._deserialize_datasource_credential(response)

    @distributed_trace_async
    async def delete_datasource_credential(self, *credential_id: str, **kwargs: Any) -> None:
        if len(credential_id) != 1:
            raise TypeError("Credential requires exactly one id.")

        await super().delete_datasource_credential(credential_id=credential_id[0], **kwargs)

    @distributed_trace_async
    async def get_feedback(self, feedback_id, **kwargs):
        # type: (str, Any) -> Union[MetricFeedback, FeedbackUnion]
        cls = kwargs.pop("cls", None)
        error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop("error_map", {}))

        request = self._get_feedback_request(feedback_id=feedback_id)
        pipeline_response = await self._client._pipeline.run(  # pylint: disable=protected-access
            request, stream=False, **kwargs
        )
        return self._get_feedback_deserialize(pipeline_response, cls=cls, error_map=error_map, **kwargs)

    @distributed_trace
    def list_feedback(self, metric_id: str, **kwargs: Any) -> AsyncItemPaged[Union[MetricFeedback, FeedbackUnion]]:
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
        # type: (...) -> AsyncItemPaged[MetricEnrichedSeriesData]
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
        start_time: Union[str, datetime.datetime],
        end_time: Union[str, datetime.datetime],
        time_mode: Union[str, AlertQueryTimeMode],
        **kwargs: Any
    ) -> AsyncItemPaged[AnomalyAlert]:
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

    def _list_anomalies_for_detection_configuration(
        self,
        detection_configuration_id,  # type: str
        start_time,  # type: Union[str, datetime.datetime]
        end_time,  # type: Union[str, datetime.datetime]
        **kwargs  # type: Any
    ):
        # type: (...) -> AsyncItemPaged[DataPointAnomaly]
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
    ) -> AsyncItemPaged[DataPointAnomaly]:
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
    def list_anomalies(self, **kwargs: Any) -> AsyncItemPaged[DataPointAnomaly]:
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
        # type: (str, str, Union[str, datetime.datetime], Union[str, datetime.datetime], Any) -> AsyncItemPaged[str]
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
    ) -> AsyncItemPaged[AnomalyIncident]:
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
    ) -> AsyncItemPaged[AnomalyIncident]:
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
        # type: (Any) -> AsyncItemPaged[AnomalyIncident]
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
        # type: (str, str, Any) -> AsyncItemPaged[str]
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
        # type: (...) -> AsyncItemPaged[MetricSeriesData]
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
        # type: (str, datetime.datetime, Any) -> AsyncItemPaged[MetricSeriesDefinition]
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
    def list_metric_enrichment_status(
        self,
        metric_id,  # type: str
        start_time,  # type: Union[str, datetime.datetime]
        end_time,  # type: Union[str, datetime.datetime]
        **kwargs  # type: Any
    ):
        # type: (...) -> AsyncItemPaged[EnrichmentStatus]
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
    ) -> AsyncItemPaged[IncidentRootCause]:
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
    def list_hooks(self, **kwargs: Any) -> AsyncItemPaged[NotificationHook]:
        initial_request, next_request, kwargs = self._list_hooks_requests(**kwargs)
        return self._paging_helper(
            initial_request=initial_request,
            next_request=next_request,
            deserializer=NotificationHook.deserialize,
            **kwargs
        )

    @distributed_trace
    def list_detection_configurations(
        self, metric_id: str, **kwargs: Any
    ) -> AsyncItemPaged[AnomalyDetectionConfiguration]:
        initial_request, next_request, kwargs = self._list_detection_configurations_requests(metric_id, **kwargs)
        return self._paging_helper(
            initial_request=initial_request,
            next_request=next_request,
            deserializer=AnomalyDetectionConfiguration.deserialize,
            **kwargs
        )

    @distributed_trace
    def list_datasource_credentials(self, **kwargs: Any) -> AsyncItemPaged[DatasourceCredential]:
        initial_request, next_request, kwargs = self._list_datasource_credentials_requests(**kwargs)
        return self._paging_helper(
            initial_request=initial_request,
            next_request=next_request,
            deserializer=self._deserialize_datasource_credential,
            **kwargs
        )


__all__ = ["MetricsAdvisorClientOperationsMixin"]


def patch_sdk():
    pass
