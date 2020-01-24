# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint:disable=line-too-long
from typing import Any, TYPE_CHECKING

from azure.core.pipeline.policies import (
    SansIOHTTPPolicy
)
from ._shared.request_handlers import throw_exception_if_contains_header
from ._generated.version import VERSION

if TYPE_CHECKING:
    from azure.core.pipeline import PipelineRequest

Managed_DISK_DIFF_OPERATION = 'get_managed_disk_page_range_diff'
CREATE_CONTAINER_OPERATION = 'create container'


class StorageVersionCheckPolicy(SansIOHTTPPolicy):
    def on_request(self, request):
        # type: (PipelineRequest, Any) -> None
        headers = request.http_request.headers
        request_service_version = headers['x-ms-version']

        if request_service_version == VERSION:
            return

        # 2019 - 07 - 07 check
        if request_service_version < '2019-07-07':
            # encryption scope
            throw_exception_if_contains_header(headers, "x-ms-default-encryption-scope", CREATE_CONTAINER_OPERATION, request_service_version)
            throw_exception_if_contains_header(headers, "x-ms-deny-encryption-scope-override", CREATE_CONTAINER_OPERATION, request_service_version)
            throw_exception_if_contains_header(headers, "x-ms-encryption-scope", "any blob API", request_service_version)

            # managed disk diff
            throw_exception_if_contains_header(headers, "x-ms-previous-snapshot-url", Managed_DISK_DIFF_OPERATION, request_service_version)
