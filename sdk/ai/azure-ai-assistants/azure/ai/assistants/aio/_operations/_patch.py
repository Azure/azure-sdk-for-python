# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, List, Optional, TYPE_CHECKING

import asyncio
import concurrent.futures
from azure.core.credentials import TokenCredential

if TYPE_CHECKING:
    from azure.core.credentials import AccessToken
    from azure.core.credentials_async import AsyncTokenCredential


class _SyncCredentialWrapper(TokenCredential):
    """
    The class, synchronizing AsyncTokenCredential.

    :param async_credential: The async credential to be synchronized.
    :type async_credential: ~azure.core.credentials_async.AsyncTokenCredential
    """

    def __init__(self, async_credential: "AsyncTokenCredential"):
        self._async_credential = async_credential

    def get_token(
        self,
        *scopes: str,
        claims: Optional[str] = None,
        tenant_id: Optional[str] = None,
        enable_cae: bool = False,
        **kwargs: Any,
    ) -> "AccessToken":
        return concurrent.futures.ThreadPoolExecutor().submit(
            asyncio.run,
            self._async_credential.get_token(
                *scopes,
                claims=claims,
                tenant_id=tenant_id,
                enable_cae=enable_cae,
                **kwargs,
            ),
        ).result()


__all__: List[str] = []


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
