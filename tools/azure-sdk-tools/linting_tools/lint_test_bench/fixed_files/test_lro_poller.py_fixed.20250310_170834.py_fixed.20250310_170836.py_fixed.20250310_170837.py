from azure.core.tracing.decorator import distributed_trace

class SomeClient:

    def __init__(self):
        pass

    @distributed_trace
    def poller(self):
        pass
