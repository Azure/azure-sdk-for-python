# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from pathlib import Path
from typing import List, Union, Optional

from azure.ai.ml._utils._asset_utils import IgnoreFile, get_ignore_file


class ComponentIgnoreFile(IgnoreFile):
    _COMPONENT_CODE_IGNORES = ["__pycache__"]

    def __init__(
        self,
        directory_path: Union[str, Path],
        *,
        additional_includes_file_name: Optional[str] = None,
        skip_ignore_file: bool = False,
        extra_ignore_list: Optional[List[IgnoreFile]] = None,
    ):
        self._base_path = Path(directory_path)
        self._extra_ignore_list: List[IgnoreFile] = extra_ignore_list or []
        # only the additional include file in root directory is ignored
        # additional include files in subdirectories are not processed so keep them
        self._additional_includes_file_name = additional_includes_file_name
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

    def rebase(self, directory_path: Union[str, Path]) -> "ComponentIgnoreFile":
        """Rebase the ignore file to a new directory."""
        self._base_path = directory_path
        return self

    def is_file_excluded(self, file_path: Union[str, Path]) -> bool:
        """Override to add custom ignores for internal component."""
        if self._additional_includes_file_name and self._get_rel_path(file_path) == self._additional_includes_file_name:
            return True
        for ignore_file in self._extra_ignore_list:
            if ignore_file.is_file_excluded(file_path):
                return True
        return super(ComponentIgnoreFile, self).is_file_excluded(file_path)

    def merge(self, other_path: Path) -> "ComponentIgnoreFile":
        """Merge ignore list from another ComponentIgnoreFile object."""
        if other_path.is_file():
            return self
        return ComponentIgnoreFile(other_path, extra_ignore_list=self._extra_ignore_list + [self])

    def _get_ignore_list(self) -> List[str]:
        """Override to add custom ignores."""
        if not super(ComponentIgnoreFile, self).exists():
            return self._COMPONENT_CODE_IGNORES
        return super(ComponentIgnoreFile, self)._get_ignore_list() + self._COMPONENT_CODE_IGNORES
