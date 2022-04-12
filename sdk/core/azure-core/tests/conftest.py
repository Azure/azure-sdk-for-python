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
import time
import pytest
import signal
import os
import subprocess
import random
import platform
from six.moves import urllib
from rest_client import TestRestClient
import sys

# If opencensus is loadable while doing these tests, register an empty tracer to avoid this:
# https://github.com/census-instrumentation/opencensus-python/issues/442
try:
    from azure.core.tracing.ext.opencensus_span import OpenCensusSpan
    from opencensus.trace.tracer import Tracer
    Tracer()
except ImportError:
    pass

def is_port_available(port_num):
    req = urllib.request.Request("http://localhost:{}/health".format(port_num))
    try:
        return urllib.request.urlopen(req).code != 200
    except Exception as e:
        return True

def get_port():
    count = 3
    for _ in range(count):
        port_num = random.randrange(3000, 5000)
        if is_port_available(port_num):
            return port_num
    raise TypeError("Tried {} times, can't find an open port".format(count))

@pytest.fixture
def port():
    return os.environ["FLASK_PORT"]

def start_testserver():
    port = get_port()
    os.environ["FLASK_APP"] = "coretestserver"
    os.environ["FLASK_PORT"] = str(port)
    if platform.python_implementation() == 'PyPy':
        # pypy is now getting mad at us for some of our encoding / text, so need
        # to set these additional env vars for pypy
        os.environ["LC_ALL"] = "C.UTF-8"
        os.environ["LANG"] = "C.UTF-8"
    cmd = "flask run -p {}".format(port)
    if os.name == 'nt': #On windows, subprocess creation works without being in the shell
        child_process = subprocess.Popen(cmd, env=dict(os.environ))
    else:
        #On linux, have to set shell=True
        child_process = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid, env=dict(os.environ))
    count = 5
    for _ in range(count):
        if not is_port_available(port):
            return child_process
        time.sleep(1)
    raise ValueError("Didn't start!")

def terminate_testserver(process):
    if os.name == 'nt':
        process.kill()
    else:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)  # Send the signal to all the process groups

@pytest.fixture(autouse=True, scope="package")
def testserver():
    """Start the Autorest testserver."""
    server = start_testserver()
    yield
    terminate_testserver(server)

@pytest.fixture
def client(port):
    return TestRestClient(port)
