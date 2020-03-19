# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import asyncio
from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.pipeline.policies import AsyncHTTPPolicy
from .._models import TextDocumentBatchStatistics


class AsyncTextAnalyticsResponseHook(AsyncHTTPPolicy):

    def __init__(self, **kwargs):
        self._response_callback = kwargs.get('response_hook')
        super(AsyncTextAnalyticsResponseHook, self).__init__()

    async def send(self, request):
        response_callback = request.context.options.pop("response_hook", self._response_callback)
        if response_callback:
            response = await self.next.send(request)
            data = ContentDecodePolicy.deserialize_from_http_generics(response.http_response)
            statistics = data.get("statistics", None)
            model_version = data.get("modelVersion", None)

            batch_statistics = TextDocumentBatchStatistics._from_generated(statistics)  # pylint: disable=protected-access
            response.statistics = batch_statistics
            response.model_version = model_version
            response.raw_response = data
            if asyncio.iscoroutine(response_callback):
                await response_callback(response)
            else:
                response_callback(response)
            return response
        return await self.next.send(request)
