# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from .basic import basic_api
from .encoding import encoding_api
from .errors import errors_api
from .multipart import multipart_api
from .polling import polling_api
from .streams import streams_api
from .urlencoded import urlencoded_api
from .xml_route import xml_api
from .headers import headers_api

__all__ = [
    "basic_api",
    "encoding_api",
    "errors_api",
    "multipart_api",
    "polling_api",
    "streams_api",
    "urlencoded_api",
    "xml_api",
    "headers_api",
]
