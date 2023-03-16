# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from pathlib import Path
from typing import List, Union

from azure.ai.ml._utils._asset_utils import IgnoreFile, get_ignore_file


class ComponentIgnoreFile(IgnoreFile):
    _COMPONENT_CODE_IGNORES = ["__pycache__"]

    def __init__(
        self,
        directory_path: Union[str, Path],
        *,
        skip_ignore_file: bool = False,
    ):
        self._base_path = Path(directory_path)
        # note: the parameter changes to directory path in this class, rather than file path
        file_path = None if skip_ignore_file else get_ignore_file(directory_path).path
        super(ComponentIgnoreFile, self).__init__(file_path=file_path)

    def exists(self) -> bool:
        """Override to always return True as we do have default ignores."""
        return True

    @property
    def base_path(self) -> Path:
        # for component ignore file, the base path can be different from file.parent
        return self._base_path

    def _get_ignore_list(self) -> List[str]:
        """Override to add custom ignores."""
        if not super(ComponentIgnoreFile, self).exists():
            return self._COMPONENT_CODE_IGNORES
        return super(ComponentIgnoreFile, self)._get_ignore_list() + self._COMPONENT_CODE_IGNORES
