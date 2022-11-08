# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from azure.ai.ml._utils._asset_utils import get_content_hash, get_ignore_file, IgnoreFile
from azure.ai.ml._utils._pathspec import GitWildMatchPattern, normalize_file
from azure.ai.ml.constants._common import ArmConstants
from .._assets import Code


class ComponentIgnoreFile(IgnoreFile):
    _COMPONENT_CODE_IGNORES = ["__pycache__"]

    def __init__(self, file_path: Optional[Union[str, Path]] = None):
        super(ComponentIgnoreFile, self).__init__(file_path=file_path)
        self._path_spec = self._create_pathspec()

    @staticmethod
    def from_ignore_file(ignore_file: IgnoreFile) -> "ComponentIgnoreFile":
        return ComponentIgnoreFile(ignore_file.path)

    def _create_pathspec(self) -> List[GitWildMatchPattern]:
        """Override to add custom ignores."""
        if not super(ComponentIgnoreFile, self).exists():
            path_spec = []
        else:
            path_spec = super(ComponentIgnoreFile, self)._create_pathspec()
        path_spec.extend([GitWildMatchPattern(ignore) for ignore in self._COMPONENT_CODE_IGNORES])
        return path_spec

    def is_file_excluded(self, file_path: Union[str, Path]) -> bool:
        if self.exists():
            return super(ComponentIgnoreFile, self).is_file_excluded(file_path)
        file_path = str(file_path)
        norm_file = normalize_file(file_path)
        for pattern in self._path_spec:
            if pattern.include is not None:
                if norm_file in pattern.match((norm_file,)):
                    return bool(pattern.include)
        return False


class ComponentCode(Code):
    def __init__(
        self,
        *,
        name: str = None,
        version: str = None,
        description: str = None,
        tags: Dict = None,
        properties: Dict = None,
        path: Union[str, os.PathLike] = None,
        **kwargs,
    ):
        # call grandparent Artifact __init__ function
        super(Code, self).__init__(  # pylint: disable=bad-super-call
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
            self._ignore_file = ComponentIgnoreFile.from_ignore_file(get_ignore_file(self.path))
        else:
            self._ignore_file = ComponentIgnoreFile()
        # only calculate hash for local files
        self._hash_sha256 = get_content_hash(self.path, self._ignore_file)
