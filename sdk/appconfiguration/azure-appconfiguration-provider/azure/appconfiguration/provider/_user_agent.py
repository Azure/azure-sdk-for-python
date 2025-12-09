# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from ._version import VERSION
from azure.core._version_validation import validate_version

# Validate that VERSION is not empty or None to prevent unauthorized SDK usage
validate_version(VERSION)

USER_AGENT = "python-appconfiguration-provider/{}".format(VERSION)
