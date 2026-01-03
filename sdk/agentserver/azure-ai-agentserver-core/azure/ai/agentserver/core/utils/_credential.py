# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from __future__ import annotations

import asyncio
import inspect
from types import TracebackType
from typing import Any, Optional, Sequence, Type, Union

from azure.core.credentials import AccessToken, TokenCredential
from azure.core.credentials_async import AsyncTokenCredential


async def _to_thread(func, *args, **kwargs):
    """Compatibility wrapper for asyncio.to_thread (Python 3.8+)."""
    if hasattr(asyncio, "to_thread"):
        return await asyncio.to_thread(func, *args, **kwargs)  # py>=3.9
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))


class AsyncTokenCredentialAdapter(AsyncTokenCredential):
    """
    AsyncTokenCredential adapter for either:
      - azure.core.credentials.TokenCredential (sync)
      - azure.core.credentials_async.AsyncTokenCredential (async)
    """

    def __init__(self, credential: TokenCredential |AsyncTokenCredential) -> None:
        if not hasattr(credential, "get_token"):
            raise TypeError("credential must have a get_token method")
        self._credential = credential
        self._is_async = isinstance(credential, AsyncTokenCredential) or inspect.iscoroutinefunction(
            getattr(credential, "get_token", None)
        )

    async def get_token(
            self,
            *scopes: str,
            claims: str | None = None,
            tenant_id: str | None = None,
            enable_cae: bool = False,
            **kwargs: Any,
    ) -> AccessToken:
        if self._is_async:
            return await self._credential.get_token(*scopes,
                                                    claims=claims,
                                                    tenant_id=tenant_id,
                                                    enable_cae=enable_cae,
                                                    **kwargs)
        return await _to_thread(self._credential.get_token,
                                *scopes,
                                claims=claims,
                                tenant_id=tenant_id,
                                enable_cae=enable_cae,
                                **kwargs)

    async def close(self) -> None:
        """
        Best-effort resource cleanup:
        - if underlying has async close(): await it
        - else if underlying has sync close(): run it in a thread
        """
        close_fn = getattr(self._credential, "close", None)
        if close_fn is None:
            return

        if inspect.iscoroutinefunction(close_fn):
            await close_fn()
        else:
            await _to_thread(close_fn)

    async def __aenter__(self) -> "AsyncTokenCredentialAdapter":
        enter = getattr(self._credential, "__aenter__", None)
        if enter is not None and inspect.iscoroutinefunction(enter):
            await enter()
        return self

    async def __aexit__(
            self,
            exc_type: Type[BaseException] | None = None,
            exc_value: BaseException | None = None,
            traceback: TracebackType | None = None,
    ) -> None:
        aexit = getattr(self._credential, "__aexit__", None)
        if aexit is not None and inspect.iscoroutinefunction(aexit):
            return await aexit(exc_type, exc_value, traceback)
        await self.close()