# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


_SUPPORTED_API_VERSIONS = [
    "2.0",
]

def validate_api_version(api_version):
    # type: (str) -> None
    """Raise error if api_version is invalid """
    if not api_version:
        return
    if api_version not in _SUPPORTED_API_VERSIONS:
        versions = '\n'.join(_SUPPORTED_API_VERSIONS)
        raise ValueError("Unsupported API version '{}'. Please select from:\n{}".format(api_version, versions))
