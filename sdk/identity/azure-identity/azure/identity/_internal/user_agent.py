# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import platform

from .._version import VERSION
from azure.core._version_validation import validate_version

# Validate that VERSION is not empty or None to prevent unauthorized SDK usage
validate_version(VERSION)

USER_AGENT = "azsdk-python-identity/{} Python/{} ({})".format(VERSION, platform.python_version(), platform.platform())
