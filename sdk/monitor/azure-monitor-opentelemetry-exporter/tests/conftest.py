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
import sys
from collections.abc import Generator

import pytest

from azure.monitor.opentelemetry.exporter._configuration import _ConfigurationManager
from azure.monitor.opentelemetry.exporter._configuration import _state as configuration_state
from azure.monitor.opentelemetry.exporter._utils import Singleton


# Ignore tests for Python < 3.6
collect_ignore_glob = []
if sys.version_info < (3, 6):
    collect_ignore_glob.append("*")


def _reset_configuration_manager() -> None:  # pylint: disable=protected-access
    manager = configuration_state._configuration_manager or Singleton._instances.get(_ConfigurationManager)
    if manager is not None:
        manager.shutdown()
    configuration_state._configuration_manager = None
    Singleton._instances.pop(_ConfigurationManager, None)


@pytest.fixture(autouse=True)
def isolate_configuration_manager() -> Generator[None, None, None]:
    """Give every test a fresh configuration cache, callback registry, and worker."""
    _reset_configuration_manager()
    yield
    _reset_configuration_manager()
