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
import sys
import os
import subprocess
import platform
import urllib
from rest_client import MockRestClient


def is_port_available(port_num):
    req = urllib.request.Request("http://127.0.0.1:{}/health".format(port_num))
    try:
        return urllib.request.urlopen(req).code != 200
    except Exception as e:
        return True


def get_port():
    """Ask the OS for a free ephemeral port to avoid collisions in parallel CI."""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def start_testserver():
    port = get_port()
    os.environ["FLASK_APP"] = "coretestserver"
    os.environ["FLASK_PORT"] = str(port)
    if platform.python_implementation() == "PyPy":
        # pypy is now getting mad at us for some of our encoding / text, so need
        # to set these additional env vars for pypy
        os.environ["LC_ALL"] = "C.UTF-8"
        os.environ["LANG"] = "C.UTF-8"
    cmd = f"{sys.executable} -m flask run -p {port}"
    if os.name == "nt":  # On windows, subprocess creation works without being in the shell
        child_process = subprocess.Popen(cmd, env=dict(os.environ))
    else:
        # On linux, have to set shell=True
        child_process = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid, env=dict(os.environ))
    # Wait up to ~20s with backoff for Flask to start serving
    for delay in [0.5, 1, 1, 2, 2, 2, 4, 4, 4]:
        if child_process.poll() is not None:
            raise ValueError("Flask process exited with code {}".format(child_process.returncode))
        if not is_port_available(port):
            return child_process
        time.sleep(delay)
    raise ValueError("Didn't start!")


def terminate_testserver(process):
    if os.name == "nt":
        process.kill()
    else:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)  # cspell:disable-line


@pytest.fixture(scope="session")
def port():
    server = start_testserver()
    yield os.environ["FLASK_PORT"]
    terminate_testserver(server)
