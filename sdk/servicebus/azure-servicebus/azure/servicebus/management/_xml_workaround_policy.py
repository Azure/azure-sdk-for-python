# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.policies import SansIOHTTPPolicy


class ServiceBusXMLWorkaroundPolicy(SansIOHTTPPolicy):
    """A policy that mutates serialized XML to workaround ServiceBus requirement

    """
    def __init__(self):
        # type: () -> None
        super(ServiceBusXMLWorkaroundPolicy, self).__init__()

    def on_request(self, request):
        # type: (PipelineRequest) -> None
        """Mutate serialized (QueueDescription, TopicDescription, SubscriptionDescription, RuleDescription)
        XML to use default namespace.

        :param request: The pipeline request object
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        request_body = request.http_request.body
        if request_body:
            if b'<ns1:' in request_body:
                request_body = request_body.replace(b'ns1:', b'')
                request_body = request_body.replace(b':ns1', b'')
            if b'<Value>' in request_body:
                request_body = request_body.replace(
                    b'<Value>',
                    b'<Value xsi:type="d6p1:string" xmlns:d6p1="http://www.w3.org/2001/XMLSchema">')
            request.http_request.body = request_body
            request.http_request.data = request_body
            request.http_request.headers["Content-Length"] = str(len(request_body))
