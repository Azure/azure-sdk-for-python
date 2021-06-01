
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import sys
import pytest
import signal
import subprocess
from azure.core.rest import TestRestClient

def start_testserver():
    os.environ["FLASK_APP"] = "core.testserver.app.py"
    cmd = "flask run"
    if os.name == 'nt': #On windows, subprocess creation works without being in the shell
        return subprocess.Popen(cmd.format("set"))

    return subprocess.Popen(cmd.format("export"), shell=True, preexec_fn=os.setsid) #On linux, have to set shell=True

def terminate_testserver(process):
    os.environ["FLASK_APP"] = ""
    if os.name == 'nt':
        process.kill()
    else:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)  # Send the signal to all the process groups

@pytest.fixture(scope="session")
def testserver():
    """Start the Autorest testserver."""
    server = start_testserver()
    yield
    terminate_testserver(server)

# Ignore async tests for Python < 3.5
collect_ignore_glob = []
if sys.version_info < (3, 5):
    collect_ignore_glob.append("async_tests")

@pytest.fixture
def client():
    return TestRestClient()