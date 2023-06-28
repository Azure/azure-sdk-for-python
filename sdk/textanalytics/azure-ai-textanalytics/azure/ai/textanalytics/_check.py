# pylint: disable=too-many-lines
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import re


def is_language_api(api_version):
    """Language API is date-based

    :param str api_version: the given API version
    :returns: Whether the API version specified targets Text Analytics
        or Language service APIs.
    :rtype: bool
    """
    return re.search(r'\d{4}-\d{2}-\d{2}', api_version)


def string_index_type_compatibility(string_index_type):
    """Language API changed this string_index_type option to plural.
    Convert singular to plural for language API

    :param str string_index_type: the given string_index_type
    :returns: Performs backwards compat for string_index_type between
        TA and Language APIs.
    :rtype: str
    """
    if string_index_type == "TextElement_v8":
        return "TextElements_v8"
    return string_index_type
