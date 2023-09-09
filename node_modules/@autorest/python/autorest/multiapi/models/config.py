# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
from typing import Any, Dict
from .imports import FileImport


class Config:
    def __init__(self, default_version_metadata: Dict[str, Any]):
        self.credential = default_version_metadata["config"]["credential"]
        self.credential_scopes = default_version_metadata["config"]["credential_scopes"]
        self.default_version_metadata = default_version_metadata

    def imports(self, async_mode: bool) -> FileImport:
        imports_to_load = "async_imports" if async_mode else "sync_imports"
        return FileImport(
            json.loads(self.default_version_metadata["config"][imports_to_load])
        )

    def credential_call(self, async_mode: bool) -> str:
        if async_mode:
            return self.default_version_metadata["config"]["credential_call_async"]
        return self.default_version_metadata["config"]["credential_call_sync"]
