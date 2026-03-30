# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, TYPE_CHECKING

from ._client import PlaywrightClient as _GeneratedPlaywrightClient

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class PlaywrightClient(_GeneratedPlaywrightClient):
    """Customized PlaywrightClient with correct credential scope.

    The generated scope (playwright.microsoft.com) is incorrect due to a
    spec bug. This override sets the working scope until the spec is fixed.
    """

    def __init__(self, endpoint: str, credential: "AsyncTokenCredential", **kwargs: Any) -> None:
        kwargs.setdefault("credential_scopes", ["https://management.core.windows.net/.default"])
        super().__init__(endpoint, credential, **kwargs)


__all__: list[str] = ["PlaywrightClient"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
