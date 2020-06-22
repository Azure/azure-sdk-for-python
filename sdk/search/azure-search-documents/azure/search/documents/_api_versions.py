# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

_SUPPORTED_API_VERSIONS = [
    "2019-05-06-Preview",
]

def get_api_version(kwargs, default):
    # type: (Dict[str, Any]) -> str
    api_version = kwargs.pop('api_version', None)
    if api_version and api_version not in _SUPPORTED_API_VERSIONS:
        versions = '\n'.join(_SUPPORTED_API_VERSIONS)
        raise ValueError("Unsupported API version '{}'. Please select from:\n{}".format(api_version, versions))
    return api_version or default
