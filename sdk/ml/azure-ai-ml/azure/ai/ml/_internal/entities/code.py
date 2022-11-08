# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from typing import Dict, Optional, Union
from pathlib import Path

from azure.ai.ml._utils._asset_utils import get_content_hash, get_ignore_file, IgnoreFile
from azure.ai.ml._utils._pathspec import GitWildMatchPattern
from azure.ai.ml.constants._common import ArmConstants
from ...entities._assets import Code
from ...entities._component.code import ComponentCode, ComponentIgnoreFile


class InternalComponentIgnoreFile(ComponentIgnoreFile):
    """Inherit to add custom ignores for internal component code."""
    _INTERNAL_COMPONENT_CODE_IGNORES = ["*.additional_includes"]

    def __init__(self, file_path: Optional[Union[str, Path]] = None):
        super(InternalComponentIgnoreFile, self).__init__(file_path=file_path)
        self._path_spec.extend([GitWildMatchPattern(ignore) for ignore in self._INTERNAL_COMPONENT_CODE_IGNORES])

    @staticmethod
    def from_ignore_file(ignore_file: IgnoreFile) -> "InternalComponentIgnoreFile":
        return InternalComponentIgnoreFile(ignore_file.path)


class InternalCode(ComponentCode):
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
            self._ignore_file = InternalComponentIgnoreFile.from_ignore_file(get_ignore_file(self.path))
        else:
            self._ignore_file = InternalComponentIgnoreFile()
        # only calculate hash for local files
        self._hash_sha256 = get_content_hash(self.path, self._ignore_file)

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
