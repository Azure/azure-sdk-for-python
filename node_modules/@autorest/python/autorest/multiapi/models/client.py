# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import sys
import json
import re
from typing import Any, Dict, List
from pathlib import Path
from .imports import FileImport, TypingSection, ImportType


def _extract_version(metadata_json: Dict[str, Any], version_path: Path) -> str:
    version = metadata_json["chosen_version"]
    total_api_version_list = metadata_json["total_api_version_list"]
    if not version:
        if total_api_version_list:
            sys.exit(
                f"Unable to match {total_api_version_list} to label {version_path.stem}"
            )
        else:
            sys.exit(f"Unable to extract api version of {version_path.stem}")
    return version


class Client:
    def __init__(
        self,
        azure_arm: bool,
        default_version_metadata: Dict[str, Any],
        version_path_to_metadata: Dict[Path, Dict[str, Any]],
    ):
        self.name = default_version_metadata["client"]["name"]
        self.pipeline_client = "ARMPipelineClient" if azure_arm else "PipelineClient"
        self.filename = default_version_metadata["client"]["filename"]
        self.host_value = default_version_metadata["client"]["host_value"]
        self.description = default_version_metadata["client"]["description"]
        self.client_side_validation = default_version_metadata["client"][
            "client_side_validation"
        ]
        self.default_version_metadata = default_version_metadata
        self.version_path_to_metadata = version_path_to_metadata

    def imports(self, async_mode: bool) -> FileImport:
        imports_to_load = "async_imports" if async_mode else "sync_imports"
        file_import = FileImport(
            json.loads(self.default_version_metadata["client"][imports_to_load])
        )
        local_imports = file_import.imports.get(TypingSection.REGULAR, {}).get(
            ImportType.LOCAL, {}
        )
        for key in local_imports:
            if re.search("^\\.*_serialization$", key):
                relative_path = ".." if async_mode else "."
                local_imports[f"{relative_path}_serialization"] = local_imports.pop(key)
                break
        return file_import

    @property
    def parameterized_host_template_to_api_version(self) -> Dict[str, List[str]]:
        parameterized_host_template_to_api_version: Dict[str, List[str]] = {}
        for version_path, metadata_json in self.version_path_to_metadata.items():
            parameterized_host_template = metadata_json["client"][
                "parameterized_host_template"
            ]
            version = _extract_version(metadata_json, version_path)
            parameterized_host_template_to_api_version.setdefault(
                parameterized_host_template, []
            ).append(version)
        return parameterized_host_template_to_api_version

    @property
    def has_lro_operations(self) -> bool:
        has_lro_operations = False
        for _, metadata_json in self.version_path_to_metadata.items():
            current_client_has_lro_operations = metadata_json["client"][
                "has_lro_operations"
            ]
            if current_client_has_lro_operations:
                has_lro_operations = True
        return has_lro_operations
