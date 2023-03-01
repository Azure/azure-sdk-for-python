# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from pathlib import Path
from typing import List, Optional, Union

from ..._utils._asset_utils import IgnoreFile
from ...entities._assets import Code
from ...entities._component.code import ComponentIgnoreFile


class InternalComponentIgnoreFile(ComponentIgnoreFile):
    def __init__(
        self,
        directory_path: Union[str, Path],
        *,
        additional_includes_file_name: Optional[str] = None,
        skip_ignore_file: bool = False,
        extra_ignore_list: Optional[List[IgnoreFile]] = None,
    ):
        super(InternalComponentIgnoreFile, self).__init__(
            directory_path=directory_path,
            skip_ignore_file=skip_ignore_file,
        )
        self._extra_ignore_list: List[IgnoreFile] = extra_ignore_list or []
        # only the additional include file in root directory is ignored
        # additional include files in subdirectories are not processed so keep them
        self._additional_includes_file_name = additional_includes_file_name

    def is_file_excluded(self, file_path: Union[str, Path]) -> bool:
        """Override to add custom ignores for internal component."""
        if self._additional_includes_file_name and self._get_rel_path(file_path) == self._additional_includes_file_name:
            return True
        for ignore_file in self._extra_ignore_list:
            if ignore_file.is_file_excluded(file_path):
                return True
        return super(InternalComponentIgnoreFile, self).is_file_excluded(file_path)

    def merge(self, other_path: Path) -> "InternalComponentIgnoreFile":
        """Merge ignore list from another InternalComponentIgnoreFile object."""
        if other_path.is_file():
            return self
        return InternalComponentIgnoreFile(other_path, extra_ignore_list=self._extra_ignore_list + [self])

    def rebase(self, directory_path: Union[str, Path]) -> "InternalComponentIgnoreFile":
        """Rebase the ignore file to a new directory."""
        self._base_path = directory_path
        return self


class InternalCode(Code):
    @property
    def _upload_hash(self) -> Optional[str]:
        # This property will be used to identify the uploaded content when trying to
        # upload to datastore. The tracebacks will be as below:
        #   Traceback (most recent call last):
        #     _artifact_utilities._check_and_upload_path
        #     _artifact_utilities._upload_to_datastore
        #     _artifact_utilities.upload_artifact
        #     _blob_storage_helper.upload
        # where asset id will be calculated based on the upload hash.

        if self._is_anonymous is True:
            # Name of an anonymous internal code is the same as its snapshot id
            # in ml-component, use it as the upload hash to avoid duplicate hash
            # calculation with _asset_utils.get_object_hash.
            return self.name

        return getattr(super(InternalCode, self), "_upload_hash")

    def __setattr__(self, key, value):
        if key == "name" and hasattr(self, key) and self._is_anonymous is True and value != self.name:
            raise AttributeError(
                "InternalCode name are calculated based on its content and cannot "
                "be changed: current name is {} and new value is {}".format(self.name, value)
            )
        super().__setattr__(key, value)
