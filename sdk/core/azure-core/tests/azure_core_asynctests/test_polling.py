#--------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#--------------------------------------------------------------------------
import time
try:
    from unittest import mock
except ImportError:
    import mock

import pytest

from azure.core import AsyncPipelineClient
from azure.core.polling import *
from msrest.serialization import Model


@pytest.fixture
def client():
    # The poller itself don't use it, so we don't need something functionnal
    return AsyncPipelineClient("https://baseurl")


@pytest.mark.asyncio
async def test_no_polling(client):
    no_polling = AsyncNoPolling()

    initial_response = "initial response"
    def deserialization_cb(response):
        assert response == initial_response
        return "Treated: "+response

    no_polling.initialize(client, initial_response, deserialization_cb)
    await no_polling.run() # Should no raise and do nothing
    assert no_polling.status() == "succeeded"
    assert no_polling.finished()
    assert no_polling.resource() == "Treated: "+initial_response

    continuation_token = no_polling.get_continuation_token()
    assert isinstance(continuation_token, str)

    no_polling_revived_args = NoPolling.from_continuation_token(
        continuation_token,
        deserialization_callback=deserialization_cb,
        client=client
    )
    no_polling_revived = NoPolling()
    no_polling_revived.initialize(*no_polling_revived_args)
    assert no_polling_revived.status() == "succeeded"
    assert no_polling_revived.finished()
    assert no_polling_revived.resource() == "Treated: "+initial_response


class PollingTwoSteps(AsyncPollingMethod):
    """An empty poller that returns the deserialized initial response.
    """
    def __init__(self, sleep=0):
        self._initial_response = None
        self._deserialization_callback = None
        self._sleep = sleep

    def initialize(self, _, initial_response, deserialization_callback):
        self._initial_response = initial_response
        self._deserialization_callback = deserialization_callback
        self._finished = False

    async def run(self):
        """Empty run, no polling.
        """
        self._finished = True

    def status(self):
        """Return the current status as a string.
        :rtype: str
        """
        return "succeeded" if self._finished else "running"

    def finished(self):
        """Is this polling finished?
        :rtype: bool
        """
        return self._finished

    def resource(self):
        return self._deserialization_callback(self._initial_response)


@pytest.mark.asyncio
async def test_poller(client):

    # Same the poller itself doesn't care about the initial_response, and there is no type constraint here
    initial_response = "Initial response"

    # Same for deserialization_callback, just pass to the polling_method
    def deserialization_callback(response):
        assert response == initial_response
        return "Treated: "+response

    method = AsyncNoPolling()

    poller = AsyncLROPoller(client, initial_response, deserialization_callback, method)

    result = await poller.result()
    assert poller.done()
    assert result == "Treated: "+initial_response
    assert poller.status() == "succeeded"

    # Test with a basic Model
    poller = AsyncLROPoller(client, initial_response, Model, method)
    assert poller._polling_method._deserialization_callback == Model.deserialize

    # Test poller that method do a run
    method = PollingTwoSteps(sleep=1)
    poller = AsyncLROPoller(client, initial_response, deserialization_callback, method)

    result = await poller.result()
    assert result == "Treated: "+initial_response
    assert poller.status() == "succeeded"


@pytest.mark.asyncio
async def test_broken_poller(client):

    class NoPollingError(PollingTwoSteps):
        async def run(self):
            raise ValueError("Something bad happened")

    initial_response = "Initial response"
    def deserialization_callback(response):
        return "Treated: "+response

    method = NoPollingError()
    poller = AsyncLROPoller(client, initial_response, deserialization_callback, method)

    with pytest.raises(ValueError) as excinfo:
        await poller.result()
    assert "Something bad happened" in str(excinfo.value)
