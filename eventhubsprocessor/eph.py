# Represents a host for processing Event Hubs event data at scale (To be discussed)
class EventProcessorHost:
    def __init__(self, AbstractEventProcessor):
        self.EventProcessor = AbstractEventProcessor