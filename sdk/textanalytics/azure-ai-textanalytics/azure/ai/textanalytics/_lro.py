from urllib.parse import urlencode
from azure.core.polling.base_polling import LROBasePolling, OperationResourcePolling
from azure.core.polling.async_base_polling import AsyncLROBasePolling

_FINISHED = frozenset(["succeeded", "cancelled", "failed", "partiallysucceeded"])
_FAILED = frozenset(["cancelled", "failed"])
_SUCCEEDED = frozenset(["succeeded", "partiallysucceeded"])

class TextAnalyticsOperationResourcePolling(OperationResourcePolling):
    def __init__(self, operation_location_header="operation-location", show_stats=False):
        super(TextAnalyticsOperationResourcePolling, self).__init__(operation_location_header=operation_location_header)
        self._show_stats = show_stats
        self._query_params = {
            "showStats": show_stats
        }

    def get_polling_url(self):
        if not self._show_stats:
            return super().get_polling_url()

        return super().get_polling_url() + "?" + urlencode(self._query_params)


class TextAnalyticsLROPoller(LROBasePolling):
    def __init__(self,
        timeout=30,
        lro_algorithms=None,
        lro_options=None,
        path_format_arguments=None,
        **operation_config
    ):

        super(TextAnalyticsLROPoller, self).__init__(
            timeout=timeout,
            lro_algorithms=lro_algorithms,
            lro_options=lro_options,
            path_format_arguments=path_format_arguments,
            **operation_config
        )

    def finished(self):
        """Is this polling finished?
        :rtype: bool
        """
        return self._finished(self.status())

    def _finished(self, status):
        if hasattr(status, "value"):
            status = status.value
        return str(status).lower() in _FINISHED


class TextAnalyticsAsyncLROPoller(AsyncLROBasePolling):
    def __init__(self,
        timeout=30,
        lro_algorithms=None,
        lro_options=None,
        path_format_arguments=None,
        **operation_config
    ):

        super(TextAnalyticsAsyncLROPoller, self).__init__(
            timeout=timeout,
            lro_algorithms=lro_algorithms,
            lro_options=lro_options,
            path_format_arguments=path_format_arguments,
            **operation_config
        )

    def finished(self):
        """Is this polling finished?
        :rtype: bool
        """
        return self._finished(self.status())

    def _finished(self, status):
        if hasattr(status, "value"):
            status = status.value
        return str(status).lower() in _FINISHED