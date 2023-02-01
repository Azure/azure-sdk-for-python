# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from pathlib import Path
from typing import List, Optional, Union

from ..._utils._asset_utils import IgnoreFile
from ...entities._assets import Code
from ...entities._component.code import ComponentIgnoreFile


class InternalComponentIgnoreFile(ComponentIgnoreFile):
    def __init__(self, directory_path: Union[str, Path], additional_include_file_name: Optional[str]):
        super(InternalComponentIgnoreFile, self).__init__(directory_path=directory_path)
        # only the additional include file in root directory is ignored
        # additional include files in subdirectories are not processed so keep them
        self._additional_include_file_name = additional_include_file_name
        self._other_ignores = []

    def _get_ignore_list(self) -> List[str]:
        """Override to add custom ignores for internal component."""
        if self._additional_include_file_name is None:
            return super(InternalComponentIgnoreFile, self)._get_ignore_list()
        return super(InternalComponentIgnoreFile, self)._get_ignore_list() + [self._additional_include_file_name]

    def merge(self, other: IgnoreFile):
        """Merge other ignore file with this one and create a new IgnoreFile for it.
        """
        ignore_file = InternalComponentIgnoreFile(self._base_path, self._additional_include_file_name)
        ignore_file._other_ignores.append(other)  # pylint: disable=protected-access
        return ignore_file

    def is_file_excluded(self, file_path: Union[str, Path]) -> bool:
        """Override to check if file is excluded in other ignore files."""
        # TODO: current design of ignore file can't distinguish between files and directories of the same name
        if super(InternalComponentIgnoreFile, self).is_file_excluded(file_path):
            return True
        for other in self._other_ignores:
            if other.is_file_excluded(file_path):
                return True
        return False


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
