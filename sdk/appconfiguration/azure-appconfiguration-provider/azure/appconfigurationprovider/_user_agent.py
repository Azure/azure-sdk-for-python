# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import platform
from ._version import VERSION
from azure.appconfiguration._version import VERSION as SDK_VERSION

USER_AGENT = "python-appconfigurationprovider/{} azsdk-python-appconfiguration/{} Python/{} ({})".format(
    VERSION, SDK_VERSION, platform.python_version(), platform.platform()
)
