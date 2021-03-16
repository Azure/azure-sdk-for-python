try:
    from azure.ai.textanalytics._hlc import TextAnalyticsOperationMixin
except ImportError:
    class TextAnalyticsOperationMixin(object):
        pass

class TextAnalyticsClient(TextAnalyticsOperationMixin):

    def send_request(self, request):
        return 42