# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from corehttp.runtime import PipelineClient
from copy import deepcopy


class MockRestClient(object):
    def __init__(self, port, *, transport=None, **kwargs):
        kwargs.setdefault("sdk_moniker", "corehttp/1.0.0b1")
        self._client = PipelineClient(endpoint="http://localhost:{}/".format(port), transport=transport, **kwargs)

    def send_request(self, request, **kwargs):
        """Runs the network request through the client's chained policies.
        >>> from corehttp.rest import HttpRequest
        >>> request = HttpRequest("GET", "http://localhost:3000/helloWorld")
        <HttpRequest [GET], url: 'http://localhost:3000/helloWorld'>
        >>> response = client.send_request(request)
        <HttpResponse: 200 OK>

        :param request: The network request you want to make. Required.
        :type request: ~corehttp.rest.HttpRequest
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call. Does not do error handling on your response.
        :rtype: ~corehttp.rest.HttpResponse
        """
        request_copy = deepcopy(request)
        request_copy.url = self._client.format_url(request_copy.url)
        return self._client.send_request(request_copy, **kwargs)
