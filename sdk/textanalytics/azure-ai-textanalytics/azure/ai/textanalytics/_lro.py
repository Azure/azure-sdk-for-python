from urllib.parse import urlencode
from azure.core.polling.base_polling import OperationResourcePolling

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