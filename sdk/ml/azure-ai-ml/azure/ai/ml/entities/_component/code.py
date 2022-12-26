# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from pathlib import Path
from typing import List, Union

from azure.ai.ml._utils._asset_utils import IgnoreFile, get_ignore_file


class ComponentIgnoreFile(IgnoreFile):
    _COMPONENT_CODE_IGNORES = ["__pycache__"]

    def __init__(self, directory_path: Union[str, Path]):
        # note: the parameter changes to directory path in this class, rather than file path
        file_path = get_ignore_file(directory_path).path
        super(ComponentIgnoreFile, self).__init__(file_path=file_path)
        self._base_path = Path(directory_path)

    def exists(self) -> bool:
        """Override to always return True as we do have default ignores."""
        return True

    def _get_ignore_list(self) -> List[str]:
        """Override to add custom ignores."""
        if not super(ComponentIgnoreFile, self).exists():
            return self._COMPONENT_CODE_IGNORES
        return super(ComponentIgnoreFile, self)._get_ignore_list() + self._COMPONENT_CODE_IGNORES

    def is_file_excluded(self, file_path: Union[str, Path]) -> bool:
        """Convert file path to relative path to parent method."""
        # ValueError is raised when file_path is on different drive with self._base_path
        # this will be excluded in IgnoreFile, so also exclude it here.
        try:
            relative_path = os.path.relpath(file_path, self._base_path)
        except ValueError:
            return True
        return super(ComponentIgnoreFile, self).is_file_excluded(relative_path)
