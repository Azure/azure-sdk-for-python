# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import functools
import sys
from enum import Enum
from azure.iot.modelsrepository import (
    DEFAULT_LOCATION,
)

class ClientType(Enum):
    """
    Model repository properties
    """
    local = "local"
    remote = "remote"


def determine_repo(
    client_type=ClientType.remote.value,
    has_metadata=False,
):
    if client_type == ClientType.remote.value and has_metadata:
        repo = DEFAULT_LOCATION
    elif client_type == ClientType.remote.value and not has_metadata:
        repo = "https://raw.githubusercontent.com/Azure/iot-plugandplay-models/main/"
    elif client_type == ClientType.local.value and has_metadata:
        test_dir = os.path.dirname(os.path.abspath(__file__))
        repo = os.path.join(test_dir, "local_repository", "metadata_repository")
    elif client_type == ClientType.local.value and not has_metadata:
        test_dir = os.path.dirname(os.path.abspath(__file__))
        repo = os.path.join(test_dir, "local_repository")

    return repo


def await_prepared_test(test_fn):
    """Synchronous wrapper for async test methods. Used to avoid making changes
    upstream to AbstractPreparer, which only awaits async tests that use preparers.
    (Add @AzureTestCase.await_prepared_test decorator to async tests without preparers)

    # Note: this will only be needed so long as we maintain unittest.TestCase in our
    test-class inheritance chain.
    """

    if sys.version_info < (3, 5):
        raise ImportError("Async wrapper is not needed for Python 2.7 code.")

    import asyncio

    @functools.wraps(test_fn)
    def run(test_class_instance, *args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(test_fn(test_class_instance, *args))

    return run
