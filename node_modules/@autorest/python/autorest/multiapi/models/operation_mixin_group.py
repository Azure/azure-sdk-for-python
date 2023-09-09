# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
from typing import Any, Dict, List
from pathlib import Path
from .imports import FileImport
from .mixin_operation import MixinOperation


class OperationMixinGroup:
    def __init__(
        self,
        version_path_to_metadata: Dict[Path, Dict[str, Any]],
        default_api_version: str,
    ):
        self.default_api_version = default_api_version
        self.version_path_to_metadata = version_path_to_metadata

    def imports(self, async_mode: bool) -> FileImport:
        imports = FileImport()
        imports_to_load = "async_imports" if async_mode else "sync_imports"
        for metadata_json in self.version_path_to_metadata.values():
            if not metadata_json.get("operation_mixins"):
                continue
            mixin_imports = metadata_json["operation_mixins"][imports_to_load]
            if mixin_imports != "None":
                current_version_imports = FileImport(json.loads(mixin_imports))
                imports.merge(current_version_imports)
        return imports

    def typing_definitions(self, async_mode: bool) -> str:
        key = (
            "sync_mixin_typing_definitions"
            if async_mode
            else "async_mixin_typing_definitions"
        )
        origin = "".join(
            [
                metadata_json.get("operation_mixins", {}).get(key, "")
                for metadata_json in self.version_path_to_metadata.values()
            ]
        )
        return "\n".join(set(origin.split("\n")))

    def _use_metadata_of_default_api_version(
        self, mixin_operations: List[MixinOperation]
    ) -> List[MixinOperation]:
        default_api_version_path = [
            version_path
            for version_path in self.version_path_to_metadata.keys()
            if version_path.name == self.default_api_version
        ][0]
        default_version_metadata = self.version_path_to_metadata[
            default_api_version_path
        ]
        if not default_version_metadata.get("operation_mixins"):
            return mixin_operations
        for name, metadata in default_version_metadata["operation_mixins"][
            "operations"
        ].items():
            if name.startswith("_"):
                continue
            mixin_operation = [mo for mo in mixin_operations if mo.name == name][0]
            mixin_operation.mixin_operation_metadata = metadata
        return mixin_operations

    @property
    def mixin_operations(self) -> List[MixinOperation]:
        mixin_operations: List[MixinOperation] = []
        for version_path, metadata_json in self.version_path_to_metadata.items():
            if not metadata_json.get("operation_mixins"):
                continue
            mixin_operations_metadata = metadata_json["operation_mixins"]["operations"]
            for (
                mixin_operation_name,
                mixin_operation_metadata,
            ) in mixin_operations_metadata.items():
                if mixin_operation_name.startswith("_"):
                    continue
                try:
                    mixin_operation = [
                        mo for mo in mixin_operations if mo.name == mixin_operation_name
                    ][0]
                except IndexError:
                    mixin_operation = MixinOperation(
                        name=mixin_operation_name,
                        mixin_operation_metadata=mixin_operation_metadata,
                    )
                    mixin_operations.append(mixin_operation)
                mixin_operation.append_available_api(version_path.name)

        # make sure that the signature, doc, call, and coroutine is based off of the default api version,
        # if the default api version has a definition for it.
        # will hopefully get this removed once we deal with mixin operations with different signatures
        # for different api versions
        mixin_operations = self._use_metadata_of_default_api_version(mixin_operations)
        mixin_operations.sort(key=lambda x: x.name)
        return mixin_operations
