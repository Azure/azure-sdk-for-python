# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, TYPE_CHECKING

from azure.core.exceptions import ServiceRequestError
from ._shared.request_handlers import throw_exception_if_contains_header
from ._generated.version import VERSION

if TYPE_CHECKING:
    from azure.core.pipeline import PipelineRequest

START_COPY_OPERATION = 'start_copy_from_url'


def version_check(request):
    # type: (PipelineRequest, Any) -> None
    headers = request.http_request.headers
    request_service_version = headers['x-ms-version']

    if request_service_version == VERSION:
        return

    # 2019 - 07 - 07 check
    if request_service_version < '2019-07-07':
        # File Lease
        throw_exception_if_contains_header(headers, "x-ms-lease-id",
                                           "any file API",
                                           request_service_version)
        throw_exception_if_contains_header(headers, "x-ms-lease-duration",
                                           "any file API",
                                           request_service_version)
        throw_exception_if_contains_header(headers, "x-ms-proposed-lease-id",
                                           "any file API",
                                           request_service_version)

        if "comp=lease" in request.http_request.url:
            raise ServiceRequestError("File lease operations are not supported in service version {}"
                                      .format(request_service_version))

        # File Copy SMB Headers.The file copy operation does not recognize contain any of the following
        # headers in service versions < 2019-07-07.
        if "x-ms-copy-source" in headers:
            throw_exception_if_contains_header(headers, "x-ms-file-permission",
                                               START_COPY_OPERATION,
                                               request_service_version)
            throw_exception_if_contains_header(headers, "x-ms-file-permission-key",
                                               START_COPY_OPERATION,
                                               request_service_version)
            throw_exception_if_contains_header(headers, "x-ms-file-permission-copy-mode",
                                               START_COPY_OPERATION,
                                               request_service_version)
            throw_exception_if_contains_header(headers, "x-ms-file-copy-ignore-read-only",
                                               START_COPY_OPERATION,
                                               request_service_version)
            throw_exception_if_contains_header(headers, "x-ms-file-copy-set-archive",
                                               START_COPY_OPERATION,
                                               request_service_version)
            throw_exception_if_contains_header(headers, "x-ms-file-attributes",
                                               START_COPY_OPERATION,
                                               request_service_version)
            throw_exception_if_contains_header(headers, "x-ms-file-creation-time",
                                               START_COPY_OPERATION,
                                               request_service_version)
            throw_exception_if_contains_header(headers, "x-ms-file-last-write-time",
                                               START_COPY_OPERATION,
                                               request_service_version)
