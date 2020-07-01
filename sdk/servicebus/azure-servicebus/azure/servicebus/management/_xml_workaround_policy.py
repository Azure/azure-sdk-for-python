# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.policies import SansIOHTTPPolicy


class ServiceBusXMLWorkaroundPolicy(SansIOHTTPPolicy):
    """A policy that mutates serialized XML to workaround ServiceBus requirement.

    For some request with xml body, ServiceBus doesn't accept namespace prefix. An example is prefix "ns1"
    in the following xml. This workaround is to remove it.

    <ns0:content type="application/xml">
		<ns1:RuleDescription>
			<ns1:Filter xsi:type="CorrelationFilter">
				<ns1:CorrelationId>1</ns1:CorrelationId>
				<ns1:MessageId>1</ns1:MessageId>
	    ...
	</ns0:content>

    Another problem is Swagger specification doesn't allow an XML tag to have both a value and attributes.
    For instance <ns1:Value xsi:type="d6p1:string">value1</ns1:Value> can't be defined in swagger.
    So here we add it.

    <ns1:Filter xsi:type="CorrelationFilter">
        <ns1:CorrelationId>1</ns1:CorrelationId>
        ...
        <ns1:Properties>
            <ns1:KeyValueOfstringanyType>
                <ns1:Key>key1</ns1:Key>
                <ns1:Value xsi:type="d6p1:string">value1</ns1:Value>
            </ns1:KeyValueOfstringanyType>
        </ns1:Properties>
    </ns1:Filter>

    """
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
