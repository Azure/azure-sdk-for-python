# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from ._version import VERSION
from azure.core._version_validation import validate_version

# Validate that VERSION is not empty or None to prevent unauthorized SDK usage
validate_version(VERSION)

USER_AGENT = f"ai-textanalytics/{VERSION}"
