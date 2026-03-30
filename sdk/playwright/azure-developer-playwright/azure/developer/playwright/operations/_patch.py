# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Optional, Union

from ._operations import TestRunsOperations as _GeneratedTestRunsOperations
from ._operations import WorkspacesOperations as _GeneratedWorkspacesOperations
from .. import models as _models


def _to_reporting_endpoint(endpoint: str) -> str:
    """Derive the reporting API endpoint from the base service endpoint.

    The test-runs API is served from the reporting subdomain
    (e.g. https://{region}.reporting.api.playwright.microsoft.com) while
    all other operations use the base subdomain
    (e.g. https://{region}.api.playwright.microsoft.com).
    """
    return endpoint.replace(".api.playwright.", ".reporting.api.playwright.")


class _ReportingEndpointConfig:
    """Lightweight proxy that delegates all attribute access to the original
    config but returns the reporting subdomain for ``endpoint``.

    This avoids copying or mutating the shared config object.
    """

    def __init__(self, config):
        object.__setattr__(self, "_inner", config)
        object.__setattr__(
            self, "_reporting_endpoint", _to_reporting_endpoint(config.endpoint)
        )

    @property
    def endpoint(self) -> str:  # type: ignore[override]
        return object.__getattribute__(self, "_reporting_endpoint")

    def __getattr__(self, name):
        return getattr(object.__getattribute__(self, "_inner"), name)


class WorkspacesOperations(_GeneratedWorkspacesOperations):
    """Customized WorkspacesOperations with redirect handling fix for get_browsers.

    The get_browsers endpoint returns a 302 redirect to a WebSocket URL.
    We disable automatic redirect following so the caller receives the
    302 response with the location header instead of the pipeline
    attempting to follow the redirect (which fails due to auth policy
    rejecting non-HTTPS targets).
    """

    def get_browsers(
        self,
        workspace_id: str,
        *,
        os: Union[str, _models.OS],
        run_id: Optional[str] = None,
        x_ms_useragent: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault("permit_redirects", False)
        return super().get_browsers(
            workspace_id, os=os, run_id=run_id, x_ms_useragent=x_ms_useragent, **kwargs
        )


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
        self._config = _ReportingEndpointConfig(self._config)


__all__: list[str] = [
    "WorkspacesOperations",
    "TestRunsOperations",
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
