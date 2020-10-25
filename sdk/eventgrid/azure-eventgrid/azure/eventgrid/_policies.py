# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
from typing import TYPE_CHECKING
import logging
from azure.core.pipeline.policies import SansIOHTTPPolicy

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from azure.core.pipeline import PipelineRequest

class CloudEventDistributedTracingPolicy(SansIOHTTPPolicy):
    """CloudEventDistributedTracingPolicy is a policy which adds distributed tracing informatiom
    to a batch of cloud events. It does so by copying the `traceparent` and `tracestate` properties
    from the HTTP request into the individual events as extension properties.
    This will only happen in the case where an event does not have a `traceparent` defined already. This
    allows events to explicitly set a traceparent and tracestate which would be respected during "multi-hop
    transmition".
    See https://github.com/cloudevents/spec/blob/master/extensions/distributed-tracing.md
    for more information on distributed tracing and cloud events.
    """
    _CONTENT_TYPE = "application/cloudevents-batch+json; charset=utf-8"

    def on_request(self, request):
        # type: (PipelineRequest) -> None
        try:
            traceparent = request.http_request.headers['traceparent']
            tracestate = request.http_request.headers['tracestate']
        except KeyError:
            return

        if (request.http_request.headers['content-type'] == CloudEventDistributedTracingPolicy._CONTENT_TYPE
            and traceparent is not None
            ):

            body = json.loads(request.http_request.body)
            for item in body:
                if 'traceparent' not in item and 'tracestate' not in item:
                    item['traceparent'] = traceparent
                    item['tracestate'] = tracestate

            request.http_request.body = json.dumps(body)
