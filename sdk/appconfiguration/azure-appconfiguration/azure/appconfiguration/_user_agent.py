# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import platform
from ._version import VERSION

USER_AGENT = f"azsdk-python-appconfiguration/{VERSION} Python/{platform.python_version()} ({platform.platform()})"
