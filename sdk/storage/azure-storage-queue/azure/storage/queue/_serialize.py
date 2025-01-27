# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import (Any, Dict)

_SUPPORTED_API_VERSIONS = [
    '2019-02-02',
    '2019-07-07',
    '2019-10-10',
    '2019-12-12',
    '2020-02-10',
    '2020-04-08',
    '2020-06-12',
    '2020-08-04',
    '2020-10-02',
    '2020-12-06',
    '2021-02-12',
    '2021-04-10',
    '2021-06-08',
    '2021-08-06',
    '2021-12-02',
    '2022-11-02',
    '2023-01-03',
    '2023-05-03',
    '2023-08-03',
    '2023-11-03',
    '2024-05-04',
    '2024-08-04',
]


def get_api_version(kwargs):
    # type: (Dict[str, Any]) -> str
    api_version = kwargs.get('api_version', None)
    if api_version and api_version not in _SUPPORTED_API_VERSIONS:
        versions = '\n'.join(_SUPPORTED_API_VERSIONS)
        raise ValueError(f"Unsupported API version '{api_version}'. Please select from:\n{versions}")
    return api_version or _SUPPORTED_API_VERSIONS[-1]
