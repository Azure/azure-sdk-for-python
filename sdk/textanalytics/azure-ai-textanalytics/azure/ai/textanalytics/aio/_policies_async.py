# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import asyncio
from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.pipeline.policies import SansIOHTTPPolicy
from .._models import TextDocumentBatchStatistics


class AsyncTextAnalyticsResponseHookPolicy(SansIOHTTPPolicy):

    def __init__(self, **kwargs):
        self._response_callback = kwargs.get('raw_response_hook')
        super(AsyncTextAnalyticsResponseHookPolicy, self).__init__()

    async def on_request(self, request):
        self._response_callback = request.context.options.pop("raw_response_hook", self._response_callback)

    async def on_response(self, request, response):
        if self._response_callback:
            data = ContentDecodePolicy.deserialize_from_http_generics(response.http_response)
            statistics = data.get("statistics", None)
            model_version = data.get("modelVersion", None)

            if statistics or model_version:
                batch_statistics = TextDocumentBatchStatistics._from_generated(statistics)  # pylint: disable=protected-access
                response.statistics = batch_statistics
                response.model_version = model_version
                response.raw_response = data
                if asyncio.iscoroutine(self._response_callback):
                    await self._response_callback(response)
                else:
                    self._response_callback(response)
