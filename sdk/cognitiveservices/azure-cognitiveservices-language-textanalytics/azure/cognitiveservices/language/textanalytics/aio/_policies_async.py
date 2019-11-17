# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import asyncio
from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.pipeline.policies import AsyncHTTPPolicy
from .._models import RequestStatistics


class AsyncTextAnalyticsResponseHook(AsyncHTTPPolicy):

    def __init__(self, **kwargs):
        self._response_callback = kwargs.get('raw_response_hook')
        super(AsyncTextAnalyticsResponseHook, self).__init__()

    async def send(self, request):
        if request.context.options.get('response_hook', self._response_callback):
            statistics = request.context.get("statistics") or \
                request.context.options.pop("statistics", None)
            model_version = request.context.get("model_version") or \
                request.context.options.pop("model_version", None)
            response_callback = request.context.get('response_callback') or \
                request.context.options.pop('response_hook', self._response_callback)

            response = await self.next.send(request)
            if statistics is None and model_version is None:
                data = ContentDecodePolicy.deserialize_from_http_generics(response.http_response)
                statistics = data.get('statistics', None)
                model_version = data.get('modelVersion', None)
            for pipeline_obj in [request, response]:
                if statistics is not None and not isinstance(statistics, RequestStatistics):
                    statistics = RequestStatistics._from_generated(statistics)  # pylint: disable=protected-access
                pipeline_obj.statistics = statistics
                pipeline_obj.model_version = model_version
            if response_callback:
                if asyncio.iscoroutine(response_callback):
                    await response_callback(response)
                else:
                    response_callback(response)
                request.context.response_callback = response_callback
            return response
        return await self.next.send(request)
