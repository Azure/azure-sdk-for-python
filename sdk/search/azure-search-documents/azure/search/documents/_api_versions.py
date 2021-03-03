# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from enum import Enum

class ApiVersion(str, Enum):
    """Key Vault API versions supported by this package"""

    #: this is the default version
    V2020_06_30 = "2020-06-30"
    V2020_06_30_preview = "2020-06-30-preview"

DEFAULT_VERSION = ApiVersion.V2020_06_30

def _validate_api_version(api_version):
    # type: (str) -> None
    """Raise error if api_version is invalid """
    if not api_version:
        return
    if api_version not in ApiVersion:
        versions = '\n'.join(v.value for v in ApiVersion)
        raise ValueError("Unsupported API version '{}'. Please select from:\n{}".format(api_version, versions))


def get_api_version(kwargs):
    # type: (Dict[str, Any], str) -> str
    api_version = kwargs.pop('api_version', None)
    _validate_api_version(api_version)
    return api_version or DEFAULT_VERSION
