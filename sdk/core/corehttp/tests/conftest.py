# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import time
import pytest
import signal
import os
import subprocess
import random
import platform
import urllib
from typing import Generator

from corehttp.settings import settings
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

from rest_client import MockRestClient


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
    if platform.python_implementation() == "PyPy":
        # pypy is now getting mad at us for some of our encoding / text, so need
        # to set these additional env vars for pypy
        os.environ["LC_ALL"] = "C.UTF-8"
        os.environ["LANG"] = "C.UTF-8"
    cmd = "flask run -p {}".format(port)
    if os.name == "nt":  # On windows, subprocess creation works without being in the shell
        child_process = subprocess.Popen(cmd, env=dict(os.environ))
    else:
        # On linux, have to set shell=True
        child_process = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid, env=dict(os.environ))
    count = 5
    for _ in range(count):
        if not is_port_available(port):
            return child_process
        time.sleep(1)
    raise ValueError("Didn't start!")


def terminate_testserver(process):
    if os.name == "nt":
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
    return MockRestClient(port)


class TracingTestHelper:
    def __init__(self, tracer, exporter):
        self.tracer = tracer
        self.exporter = exporter


@pytest.fixture(scope="session", autouse=True)
def enable_tracing():
    provider = TracerProvider()
    trace.set_tracer_provider(provider)


@pytest.fixture(scope="function")
def tracing_helper() -> Generator[TracingTestHelper, None, None]:
    settings.tracing_enabled = True
    span_exporter = InMemorySpanExporter()
    processor = SimpleSpanProcessor(span_exporter)
    trace.get_tracer_provider().add_span_processor(processor)
    yield TracingTestHelper(trace.get_tracer(__name__), span_exporter)
    settings.tracing_enabled = False
