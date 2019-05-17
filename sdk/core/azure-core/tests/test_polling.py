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

from azure.core.polling import *
from msrest.service_client import ServiceClient
from msrest.serialization import Model
from msrest.configuration import Configuration


def test_abc_polling():
    abc_polling = PollingMethod()

    with pytest.raises(NotImplementedError):
        abc_polling.initialize(None, None, None)

    with pytest.raises(NotImplementedError):
        abc_polling.run()

    with pytest.raises(NotImplementedError):
        abc_polling.status()

    with pytest.raises(NotImplementedError):
        abc_polling.finished()

    with pytest.raises(NotImplementedError):
        abc_polling.resource()

def test_no_polling():
    no_polling = NoPolling()

    initial_response = "initial response"
    def deserialization_cb(response):
        assert response == initial_response
        return "Treated: "+response

    no_polling.initialize(None, initial_response, deserialization_cb)
    no_polling.run() # Should no raise and do nothing
    assert no_polling.status() == "succeeded"
    assert no_polling.finished()
    assert no_polling.resource() == "Treated: "+initial_response


class PollingTwoSteps(PollingMethod):
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

    def run(self):
        """Empty run, no polling.
        """
        self._finished = True
        time.sleep(self._sleep) # Give me time to add callbacks!

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

@pytest.fixture
def client():
    # We need a ServiceClient instance, but the poller itself don't use it, so we don't need
    # Something functionnal
    return ServiceClient(None, Configuration("http://example.org"))

def test_poller(client):

    # Same the poller itself doesn't care about the initial_response, and there is no type constraint here
    initial_response = "Initial response"

    # Same for deserialization_callback, just pass to the polling_method
    def deserialization_callback(response):
        assert response == initial_response
        return "Treated: "+response

    method = NoPolling()

    poller = LROPoller(client, initial_response, deserialization_callback, method)

    done_cb = mock.MagicMock()
    poller.add_done_callback(done_cb)

    result = poller.result()
    assert poller.done()
    assert result == "Treated: "+initial_response
    assert poller.status() == "succeeded"
    done_cb.assert_called_once_with(method)

    # Test with a basic Model
    poller = LROPoller(client, initial_response, Model, method)
    assert poller._polling_method._deserialization_callback == Model.deserialize

    # Test poller that method do a run
    method = PollingTwoSteps(sleep=1)
    poller = LROPoller(client, initial_response, deserialization_callback, method)

    done_cb = mock.MagicMock()
    done_cb2 = mock.MagicMock()
    poller.add_done_callback(done_cb)
    poller.remove_done_callback(done_cb2)

    result = poller.result()
    assert result == "Treated: "+initial_response
    assert poller.status() == "succeeded"
    done_cb.assert_called_once_with(method)
    done_cb2.assert_not_called()

    with pytest.raises(ValueError) as excinfo:
        poller.remove_done_callback(done_cb)
    assert "Process is complete" in str(excinfo.value)

def test_broken_poller(client):

    class NoPollingError(PollingTwoSteps):
        def run(self):
            raise ValueError("Something bad happened")

    initial_response = "Initial response"
    def deserialization_callback(response):
        return "Treated: "+response

    method = NoPollingError()
    poller = LROPoller(client, initial_response, deserialization_callback, method)

    with pytest.raises(ValueError) as excinfo:
        poller.result()
    assert "Something bad happened" in str(excinfo.value)
