# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from azure.ai.ml._utils._asset_utils import get_content_hash, IgnoreFile
from azure.ai.ml._utils._pathspec import GitWildMatchPattern
from azure.ai.ml.constants._common import ArmConstants
from .._assets import Code


class ComponentIgnoreFile(IgnoreFile):
    """Inherit to add custom ignores."""
    _COMPONENT_CODE_IGNORES = ["__pycache__", "*.additional_includes"]

    def __init__(self, file_path: Optional[Union[str, Path]] = None):
        super(ComponentIgnoreFile, self).__init__(file_path=file_path)
        self._path_spec = self._create_pathspec()

    def _create_pathspec(self) -> List[GitWildMatchPattern]:
        """Override to add custom ignores."""
        if super(ComponentIgnoreFile, self).exists():
            path_spec = []
        else:
            path_spec = super(ComponentIgnoreFile, self)._create_pathspec()
        path_spec.extend([GitWildMatchPattern(ignore) for ignore in self._COMPONENT_CODE_IGNORES])
        return path_spec

    def exists(self) -> bool:
        """Always return True as custom ignores exist."""
        return True


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
        path: Union[str, os.PathLike] = None,
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
            self._ignore_file = ComponentIgnoreFile(self.path)
            self._hash_sha256 = get_content_hash(self.path, self._ignore_file)

    @property
    def ignore_file(self) -> IgnoreFile:
        """Take effect in _artifact_utilities._check_and_upload_path."""
        return self._ignore_file
