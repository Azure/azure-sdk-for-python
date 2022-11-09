# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from pathlib import Path
from typing import List, Optional, Union

from azure.ai.ml._utils._asset_utils import get_ignore_file, IgnoreFile
from azure.ai.ml._utils._pathspec import GitWildMatchPattern, normalize_file


class ComponentIgnoreFile(IgnoreFile):
    _COMPONENT_CODE_IGNORES = ["__pycache__"]

    def __init__(self, directory_path: Optional[Union[str, Path]] = None):
        # note: the parameter changes to directory path in this class, rather than file path
        file_path = get_ignore_file(directory_path).path if directory_path is not None else None
        super(ComponentIgnoreFile, self).__init__(file_path=file_path)
        self._path_spec = self._create_pathspec()  # add custom ignores here

    def _create_pathspec(self) -> List[GitWildMatchPattern]:
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
