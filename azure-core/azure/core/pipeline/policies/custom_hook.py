from .base import SansIOHTTPPolicy

class CustomHookPolicy(SansIOHTTPPolicy):
    """A simple policy that enable the given callback
    with the response.
    """
    def __init__(self, **kwargs):
        self._cls = None
    
    def on_request(self, request):
        # type: (PipelineRequest, Any) -> None
        self._cls = request.context.options.pop('raw_response_hook', {})

    def on_response(self, request, response):
        # type: (PipelineRequest, Any) -> None
        if self._cls:
            self._cls(response)
            request.context.options.update('raw_response_hook', self._cls)
