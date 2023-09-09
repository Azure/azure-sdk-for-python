# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, Dict


class GlobalParameter:
    def __init__(
        self,
        name: str,
        global_parameter_metadata_sync: Dict[str, Any],
        global_parameter_metadata_async: Dict[str, Any],
    ):
        self.name = name
        self.global_parameter_metadata_sync = global_parameter_metadata_sync
        self.global_parameter_metadata_async = global_parameter_metadata_async
        self.required = global_parameter_metadata_sync["required"]
        self.method_location = global_parameter_metadata_sync["method_location"]

    def _global_parameter_metadata(self, async_mode: bool) -> Dict[str, Any]:
        if async_mode:
            return self.global_parameter_metadata_async
        return self.global_parameter_metadata_sync

    def signature(self, async_mode: bool) -> str:
        return self._global_parameter_metadata(async_mode)["signature"]

    def description(self, async_mode: bool) -> str:
        return self._global_parameter_metadata(async_mode)["description"]

    def docstring_type(self, async_mode: bool) -> str:
        return self._global_parameter_metadata(async_mode)["docstring_type"]
