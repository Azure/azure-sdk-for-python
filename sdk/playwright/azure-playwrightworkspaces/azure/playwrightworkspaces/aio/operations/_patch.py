# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Optional, Union

from ._operations import BrowserSessionsOperations as _GeneratedBrowserSessionsOperations
from ._operations import TestRunsOperations as _GeneratedTestRunsOperations
from ._operations import WorkspacesOperations as _GeneratedWorkspacesOperations
from ... import models as _models
from ...operations._patch import _ReportingEndpointConfig


class WorkspacesOperations(_GeneratedWorkspacesOperations):
    """Customized WorkspacesOperations with redirect handling fix for get_browsers.

    The get_browsers endpoint returns a 302 redirect to a WebSocket URL.
    We disable automatic redirect following so the caller receives the
    302 response with the location header instead of the pipeline
    attempting to follow the redirect (which fails due to auth policy
    rejecting non-HTTPS targets).
    """

    async def get_browsers(
        self,
        workspace_id: str,
        *,
        os: Union[str, _models.OS],
        run_id: Optional[str] = None,
        x_ms_useragent: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault("permit_redirects", False)
        return await super().get_browsers(workspace_id, os=os, run_id=run_id, x_ms_useragent=x_ms_useragent, **kwargs)


class TestRunsOperations(_GeneratedTestRunsOperations):
    """Customized TestRunsOperations that routes requests to the reporting subdomain.

    The test-runs API is served from a different subdomain
    (*.reporting.api.playwright.microsoft.com) than the main API
    (*.api.playwright.microsoft.com). This override wraps the shared
    config with a proxy that returns the reporting endpoint, without
    copying or mutating the original config object.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._config = _ReportingEndpointConfig(self._config)  # type: ignore[assignment]


class BrowserSessionsOperations(_GeneratedBrowserSessionsOperations):
    """Customized BrowserSessionsOperations that routes requests to the reporting subdomain.

    The browser-sessions API is served from a different subdomain
    (*.reporting.api.playwright.microsoft.com) than the main API
    (*.api.playwright.microsoft.com). This override wraps the shared
    config with a proxy that returns the reporting endpoint, without
    copying or mutating the original config object.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._config = _ReportingEndpointConfig(self._config)  # type: ignore[assignment]


__all__: list[str] = [
    "WorkspacesOperations",
    "TestRunsOperations",
    "BrowserSessionsOperations",
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
