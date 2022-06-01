# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.pipeline.policies import SansIOHTTPPolicy
from ._models import TextDocumentBatchStatistics
from ._lro import _FINISHED


class TextAnalyticsResponseHookPolicy(SansIOHTTPPolicy):
    def __init__(self, **kwargs):
        self._response_callback = kwargs.get("raw_response_hook")
        self._is_lro = None
        super().__init__()

    def on_request(self, request):
        self._response_callback = request.context.options.pop(
            "raw_response_hook", self._response_callback
        )

    def on_response(self, request, response):
        if self._is_lro is None:
            # determine LRO based off of initial response. If 202, we say it's an LRO
            self._is_lro = response.http_response.status_code == 202
        if self._response_callback:
            data = ContentDecodePolicy.deserialize_from_http_generics(
                response.http_response
            )
            if self._is_lro and (not data or data.get("status", "").lower() not in _FINISHED):
                return
            if response.http_response.status_code == 429:
                return
            if data:
                inner = data.get("results", data)  # language API compat
                statistics = inner.get("statistics", None)
                model_version = inner.get("modelVersion", None)
                batch_statistics = TextDocumentBatchStatistics._from_generated(  # pylint: disable=protected-access
                    statistics
                )
                response.statistics = batch_statistics
                response.model_version = model_version
            response.raw_response = data
            self._response_callback(response)
