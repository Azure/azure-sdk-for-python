
class EventGridPublisher(
    ConsumerPublisherMixin
):  # pylint:disable=too-many-instance-attributes
    """
    A publisher responsible for sending events in batches to an EventGrid topic.

    :param client: The parent EventGridPublisherClient.
    :type client: ~azure.eventhub.EventGridPublisherClient
    """

    def __init__(self, client, **kwargs):
        # type: (EventGridPublisherClient, Any) -> None

        self.running = False
        self.closed = False


    def close(self):
        # type:() -> None
        """
        Close down the handler. If the handler has already closed,
        this will be a no op.
        """
        with self._lock:
            super(EventGridPublisher, self).close()
