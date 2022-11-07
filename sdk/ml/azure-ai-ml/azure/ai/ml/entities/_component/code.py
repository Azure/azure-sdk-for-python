# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import tempfile
from os import PathLike
from pathlib import Path
from typing import Dict, Optional, Union

from azure.ai.ml._utils._asset_utils import get_content_hash, get_ignore_file, IgnoreFile
from azure.ai.ml._utils._pathspec import normalize_file
from azure.ai.ml.constants._common import ArmConstants
from .._assets import Code


class ComponentIgnoreFile(IgnoreFile):
    """Inherit to add custom ignore items. Different from original ignore file,
    this ignores file will locate under temp folder so there is some different logic.
    """
    _COMPONENT_CODE_IGNORE_ITEMS = ["__pycache__", "*.additional_includes"]
    _COMPONENT_IGNORE_FILENAME = ".componentignore"

    @staticmethod
    def from_directory_path(path: Union[Path, str]) -> Optional["ComponentIgnoreFile"]:
        ignore_items = []
        # get original ignore file
        original_ignore_file = get_ignore_file(path)
        if original_ignore_file.exists():
            with open(original_ignore_file.path) as f:
                ignore_items = f.readlines()
        # add custom ignore items and create ignore file under temp folder
        ignore_items.extend(ComponentIgnoreFile._COMPONENT_CODE_IGNORE_ITEMS)
        # note: create temp folder rather than temp file directly here,
        # because NamedTemporaryFile will lead to PermissionError under Windows.
        # refer to https://docs.python.org/3.9/library/tempfile.html#tempfile.NamedTemporaryFile
        # for more details.
        temp_file = Path(tempfile.mkdtemp()) / ComponentIgnoreFile._COMPONENT_IGNORE_FILENAME
        with open(temp_file, "w") as f:
            f.writelines(ignore_items)
        return ComponentIgnoreFile(temp_file)

    def is_file_excluded(self, file_path: Union[str, Path]) -> bool:
        """Override this function to bypass the absolute logic as this ignore file is under temp folder."""
        if not self.exists():
            return False
        if not self._path_spec:
            self._path_spec = self._create_pathspec()
        norm_file = normalize_file(file_path)
        for pattern in self._path_spec:
            if pattern.include is not None:
                if norm_file in pattern.match((norm_file,)):
                    return bool(pattern.include)
        return False


class ComponentCode(Code):
    """Inherit to add custom ignore file to Code object, which will be applied during upload operation."""
    def __init__(
        self,
        *,
        name: str = None,
        version: str = None,
        description: str = None,
        tags: Dict = None,
        properties: Dict = None,
        path: Union[str, PathLike] = None,
        **kwargs,
    ):
        # call grandparent Artifact __init__ function
        super(Code, self).__init__(
            name=name,
            version=version,
            description=description,
            tags=tags,
            properties=properties,
            path=path,
            **kwargs,
        )
        self._arm_type = ArmConstants.CODE_VERSION_TYPE
        if self.path and os.path.isabs(self.path):
            # only calculate hash for local files
            self._ignore_file = ComponentIgnoreFile.from_directory_path(self.path)
            self._hash_sha256 = get_content_hash(self.path, self._ignore_file)

    @property
    def ignore_file(self) -> IgnoreFile:
        """Take effect in _artifact_utilities._check_and_upload_path."""
        return self._ignore_file
