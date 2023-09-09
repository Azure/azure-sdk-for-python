# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, Dict, List, TypeVar
from ..utils import _sync_or_async

T = TypeVar("T")
OrderedSet = Dict[T, None]


class MixinOperation:
    def __init__(self, name: str, mixin_operation_metadata: Dict[str, Any]):
        self.name = name
        self.mixin_operation_metadata = mixin_operation_metadata
        self._available_apis: OrderedSet[str] = {}

    def call(self, async_mode: bool) -> str:
        return self.mixin_operation_metadata[_sync_or_async(async_mode)]["call"]

    def signature(self, async_mode: bool) -> str:
        return self.mixin_operation_metadata[_sync_or_async(async_mode)]["signature"]

    def description(self, async_mode: bool) -> str:
        return self.mixin_operation_metadata[_sync_or_async(async_mode)]["doc"]

    def coroutine(self, async_mode: bool) -> bool:
        if not async_mode:
            return False
        return self.mixin_operation_metadata["async"]["coroutine"]

    @property
    def available_apis(self) -> List[str]:
        return list(self._available_apis.keys())

    def append_available_api(self, val: str) -> None:
        self._available_apis[val] = None
