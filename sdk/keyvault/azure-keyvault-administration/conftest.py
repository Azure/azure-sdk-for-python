# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import sys

import pytest

if sys.version_info < (3, 5, 3):
    collect_ignore_glob = ["*_async.py"]


@pytest.fixture(scope="class")
def managed_hsm(request):
    """Fixture for tests requiring a Managed HSM instance"""

    playback_url = "https://managedhsm"
    request.cls.managed_hsm = {
        "url": os.environ.get("MANAGED_HSM_URL", playback_url),
        "playback_url": playback_url,
    }
