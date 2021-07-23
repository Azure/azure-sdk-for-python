# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any
    from typing_extensions import Protocol
    from .credentials import AccessToken

    class AsyncTokenCredential(Protocol):
        async def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:
            pass

        def supports_caching(self):
            # type: () -> bool
            """Whether this TokenCredential maintains its own token cache.

            An authentication policy may call this before deciding whether to establish its own cache.
            """

        async def close(self) -> None:
            pass

        async def __aenter__(self):
            pass

        async def __aexit__(self, exc_type, exc_value, traceback) -> None:
            pass
