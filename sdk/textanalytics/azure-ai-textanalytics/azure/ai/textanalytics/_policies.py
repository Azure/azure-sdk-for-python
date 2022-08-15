# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.exceptions import HttpResponseError
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


class QuotaExceededPolicy(SansIOHTTPPolicy):
    """Raises an exception immediately when the call quota volume has been exceeded in a F0
    tier language resource. This is to avoid waiting the Retry-After time returned in
    the response.
    """

    def on_response(self, request, response):
        """Is executed after the request comes back from the policy.

        :param request: Request to be modified after returning from the policy.
        :type request: ~azure.core.pipeline.PipelineRequest
        :param response: Pipeline response object
        :type response: ~azure.core.pipeline.PipelineResponse
        """
        http_response = response.http_response
        if http_response.status_code == 403 and \
                "Out of call volume quota for TextAnalytics F0 pricing tier" in http_response.text():
            raise HttpResponseError(http_response.text(), response=http_response)
