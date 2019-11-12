# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
from ._poller import NoPolling as _NoPolling

class AsyncPollingMethod(object):
    """ABC class for polling method.
    """
    def initialize(self, client, initial_response, deserialization_callback):
        raise NotImplementedError("This method needs to be implemented")

    async def run(self):
        raise NotImplementedError("This method needs to be implemented")

    def status(self):
        raise NotImplementedError("This method needs to be implemented")

    def finished(self):
        raise NotImplementedError("This method needs to be implemented")

    def resource(self):
        raise NotImplementedError("This method needs to be implemented")


class AsyncNoPolling(_NoPolling):
    """An empty async poller that returns the deserialized initial response.
    """
    async def run(self):
        """Empty run, no polling.
        Just override initial run to add "async"
        """


async def async_poller(client, initial_response, deserialization_callback, polling_method):
    """Async Poller for long running operations.

    :param client: A pipeline service client.
    :type client: ~azure.core.PipelineClient
    :param initial_response: The initial call response
    :type initial_response: ~azure.core.pipeline.transport.AsyncHttpResponse
    :param deserialization_callback: A callback that takes a Response and return a deserialized object.
                                     If a subclass of Model is given, this passes "deserialize" as callback.
    :type deserialization_callback: callable or msrest.serialization.Model
    :param polling_method: The polling strategy to adopt
    :type polling_method: ~azure.core.polling.PollingMethod
    """

    # This implicit test avoids bringing in an explicit dependency on Model directly
    try:
        deserialization_callback = deserialization_callback.deserialize
    except AttributeError:
        pass

    # Might raise a CloudError
    polling_method.initialize(client, initial_response, deserialization_callback)

    await polling_method.run()
    return polling_method.resource()
