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
import six
from typing import TYPE_CHECKING, List, Any, Union
import datetime
from azure.core.tracing.decorator_async import distributed_trace_async
from ._metrics_advisor_client_operations import MetricsAdvisorClientOperationsMixinGenerated
from ...models import *
from ...operations._patch import (
    DATA_FEED,
    construct_data_feed_dict,
    construct_hook_dict,
    convert_to_generated_data_feed_type,
    convert_datetime,
)
if TYPE_CHECKING:
    from ...models._patch import DataFeedSourceUnion

class MetricsAdvisorClientOperationsMixin(MetricsAdvisorClientOperationsMixinGenerated):
    @distributed_trace_async
    async def create_alert_configuration(
        self,
        name: str,  # type: str
        metric_alert_configurations: List[MetricAlertConfiguration],
        hook_ids: List[str],
        **kwargs: Any
    )-> AnomalyAlertConfiguration:
        cross_metrics_operator = kwargs.pop("cross_metrics_operator", None)
        response_headers = await super().create_alert_configuration(
            AnomalyAlertConfiguration(
                name=name,
                metric_alert_configurations=metric_alert_configurations,
                hook_ids=hook_ids,
                cross_metrics_operator=cross_metrics_operator,
                description=kwargs.pop("description", None),
            ),
            cls=lambda pipeline_response, _, response_headers: response_headers,
            **kwargs
        )

        config_id = response_headers["Location"].split("configurations/")[1]
        return await self.get_alert_configuration(config_id)

    @distributed_trace_async
    async def create_data_feed(
        self,
        name: str,
        source: "DataFeedSourceUnion",
        granularity: Union[str, DataFeedGranularityType, DataFeedGranularity],
        schema: Union[List[str], DataFeedSchema],
        ingestion_settings: Union[datetime.datetime, DataFeedIngestionSettings],
        **kwargs: Any
    ) -> DataFeed:
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

        response_headers = await super().create_data_feed(  # type: ignore
            data_feed_detail,
            cls=lambda pipeline_response, _, response_headers: response_headers,
            **kwargs
        )
        data_feed_id = response_headers["Location"].split("dataFeeds/")[1]
        return await self.get_data_feed(data_feed_id)

    @distributed_trace_async
    async def create_detection_configuration(
        self,
        name: str,
        metric_id: str,
        whole_series_detection_condition: MetricDetectionCondition,
        **kwargs: Any
    ) -> AnomalyDetectionConfiguration:

        description = kwargs.pop("description", None)
        series_group_detection_conditions = kwargs.pop(
            "series_group_detection_conditions", None
        )
        series_detection_conditions = kwargs.pop("series_detection_conditions", None)
        config = AnomalyDetectionConfiguration(
            name=name,
            metric_id=metric_id,
            description=description,
            whole_metric_configuration=whole_series_detection_condition,
            dimension_group_override_configurations=series_group_detection_conditions,
            series_override_configurations=series_detection_conditions,
        )

        response_headers = await super().create_anomaly_detection_configuration(  # type: ignore
            config,
            cls=lambda pipeline_response, _, response_headers: response_headers,
            **kwargs
        )
        config_id = response_headers["Location"].split("configurations/")[1]
        return await self.get_detection_configuration(config_id)

    @distributed_trace_async
    async def refresh_data_feed_ingestion(
        self,
        data_feed_id: str,
        start_time: Union[str, datetime.datetime],
        end_time: Union[str, datetime.datetime],
        **kwargs: Any
    ) -> None:
        converted_start_time = convert_datetime(start_time)
        converted_end_time = convert_datetime(end_time)
        await super().refresh_data_feed_ingestion(
            data_feed_id,
            body=IngestionProgressResetOptions(
                start_time=converted_start_time, end_time=converted_end_time
            ),
            **kwargs
        )

    @distributed_trace_async
    async def update_data_feed(
        self,
        data_feed: Union[str, DataFeed],
        **kwargs: Any
    )-> DataFeed:
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
            data_feed_patch = update

        return await super().update_data_feed(data_feed_id, data_feed_patch, **kwargs)

    @distributed_trace_async
    async def update_alert_configuration(
        self,
        alert_configuration: Union[str, AnomalyAlertConfiguration],
        **kwargs: Any
    ) -> AnomalyAlertConfiguration:
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
            alert_configuration_patch = update

        else:
            alert_configuration_id = alert_configuration.id
            alert_configuration_patch = update

        return await super().update_alert_configuration(
            alert_configuration_id, alert_configuration_patch, **kwargs
        )

    @distributed_trace_async
    async def update_detection_configuration(
        self,
        detection_configuration,  # type: Union[str, AnomalyDetectionConfiguration]
        **kwargs  # type: Any
    ) -> AnomalyDetectionConfiguration:
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
            detection_config_patch = update

        else:
            detection_configuration_id = detection_configuration.id
            detection_config_patch = detection_configuration

        return await super().update_anomaly_detection_configuration(
            detection_configuration_id, detection_config_patch, **kwargs
        )


# This file is used for handwritten extensions to the generated code. Example:
# https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/customize_code/how-to-patch-sdk-code.md
def patch_sdk():
    pass

__all__ = ["MetricsAdvisorClientOperationsMixin"]
