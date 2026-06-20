# coding=utf-8
# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------


# This file is used for handwritten extensions to the generated code. Example:
# https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/customize_code/how-to-patch-sdk-code.md
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

from ._client import RunHistoryClient as _RunHistoryClient

__all__ = ["RunHistoryClient"]


class RunHistoryClient(_RunHistoryClient):
    """Patched client that accepts the legacy (credential, base_url) signature."""

    def __init__(
        self,
        credential: Optional["TokenCredential"] = None,
        *,
        subscription_id: Optional[str] = None,
        base_url: Optional[str] = None,
        endpoint: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        resolved_endpoint = endpoint or base_url or ""
        self._subscription_id = subscription_id
        self._base_url = resolved_endpoint
        super().__init__(endpoint=resolved_endpoint, credential=credential, **kwargs)
        self._client._base_url = resolved_endpoint


def patch_sdk():
    pass
