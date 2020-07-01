
class EventGridConsumer(
    ConsumerProducerMixin
):  # pylint:disable=too-many-instance-attributes
    """
    A consumer responsible for deserializing EventGridEventBatch/CloudEventBatch into a list of event type objects
    specified in the EventGridEvents/CloudEvents.
    """

    def __init__(self, **kwargs):
        pass

    def consume_message_from_event_handler(self, message, **kwargs):
        """A message of a list of events from an event handler will be deserialized and returned as a list of
        BaseEventType objects.
        :param message: The `EventDataBatch` object to be sent or a list of `EventData` to be sent
         in a batch. All `EventData` in the list or `EventDataBatch` will land on the same partition.
        :type message: Union[azure.eventhub.EventData, azure.functions.EventGridEvent, azure.servicebus.Message, azure.functions.HttpRequest, azure.storage.queue.QueueMessage]
        :rtype: List[BaseEventType]
        """
        pass

