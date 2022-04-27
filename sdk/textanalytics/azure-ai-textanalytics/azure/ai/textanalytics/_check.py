# pylint: disable=too-many-lines
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import re


def is_language_api(api_version):
    """Language API is date-based
    """
    return re.search(r'\d{4}-\d{2}-\d{2}', api_version)
