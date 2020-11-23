# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from six.moves.urllib.parse import urlencode
from azure.core.polling.base_polling import OperationResourcePolling, OperationState


class TextAnalyticsOperationResourcePolling(OperationResourcePolling):
    def __init__(self, operation_location_header="operation-location", show_stats=False):
        super(TextAnalyticsOperationResourcePolling, self).__init__(operation_location_header=operation_location_header)
        self._show_stats = show_stats
        self._query_params = {
            "showStats": show_stats
        }

    def get_polling_url(self):
        if not self._show_stats:
            return super(TextAnalyticsOperationResourcePolling, self).get_polling_url()

        return super(TextAnalyticsOperationResourcePolling, self).get_polling_url() + \
            "?" + urlencode(self._query_params)


class TextAnalyticsOperationState(OperationState):
    def __init__(self):
        self._finished = frozenset(["succeeded", "cancelled", "failed", "partiallysucceeded"])
        self._failed = frozenset(["failed"])
        self._succeeded = frozenset(["succeeded", "partiallysucceeded"])

    @property
    def finished(self):
        return self._finished
    
    @property
    def failed(self):
        return self._failed
    
    @property
    def succeeded(self):
        return self._succeeded
