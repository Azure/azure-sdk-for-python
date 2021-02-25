from azure_devtools.perfstress_tests import PerfStressTest

from azure.eventgrid import EventGridPublisherClient as SyncPublisherClient, EventGridEvent
from azure.eventgrid.aio import EventGridPublisherClient as AsyncPublisherClient

from azure.core.credentials import AzureKeyCredential

class EventGridPerfTest(PerfStressTest):
    def __init__(self, arguments):
        super().__init__(arguments)

        # auth configuration
        topic_key = self.get_from_env("EG_ACCESS_KEY")
        endpoint = self.get_from_env("EG_TOPIC_HOSTNAME")

        # Create clients
        self.publisher_client = SyncPublisherClient(
            endpoint=endpoint
            credential=AzureKeyCredential(topic_key)
        )
        self._async_publisher_client = AsyncPublisherClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(topic_key)
        )
        