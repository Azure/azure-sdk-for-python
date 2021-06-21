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
import sys

def start_testserver():
    os.environ["FLASK_APP"] = "coretestserver"
    cmd = "flask run"
    if os.name == 'nt': #On windows, subprocess creation works without being in the shell
        child_process = subprocess.Popen(cmd, env=dict(os.environ))
    else:
        child_process = subprocess.Popen("FLASK_APP=coretestserver flask run", shell=True, preexec_fn=os.setsid)
    time.sleep(1)
    if child_process.returncode is not None:
        raise ValueError("Didn't start!")
    return child_process #On linux, have to set shell=True

def terminate_testserver(process):
    if os.name == 'nt':
        process.kill()
    else:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)  # Send the signal to all the process groups

@pytest.fixture(autouse=True, scope="module")
def testserver():
    """Start the Autorest testserver."""
    server = start_testserver()
    yield
    terminate_testserver(server)


# Ignore collection of async tests for Python 2
collect_ignore = []
if sys.version_info < (3, 5):
    collect_ignore.append("*_async.py")
