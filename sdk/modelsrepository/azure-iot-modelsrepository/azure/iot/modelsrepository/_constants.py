# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import platform

VERSION = "1.0.0b1"
USER_AGENT = "azsdk-python-modelsrepository/{pkg_version} Python/{py_version} ({platform})".format(
    pkg_version=VERSION, py_version=(platform.python_version()), platform=platform.platform()
)
DEFAULT_API_VERSION = "2021-02-11"
