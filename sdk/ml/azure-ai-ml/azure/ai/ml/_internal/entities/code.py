# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List, Optional, Union
from pathlib import Path

from azure.ai.ml._utils._pathspec import GitWildMatchPattern
from ...entities._assets import Code
from ...entities._component.code import ComponentIgnoreFile


class InternalComponentIgnoreFile(ComponentIgnoreFile):
    _INTERNAL_COMPONENT_CODE_IGNORES = ["*.additional_includes"]

    def __init__(
        self,
        directory_path: Optional[Union[str, Path]] = None,
        extra_ignores: Optional[List[str]] = None,
    ):
        super(InternalComponentIgnoreFile, self).__init__(directory_path=directory_path)
        _extra_ignores = extra_ignores.copy() if extra_ignores is not None else []  # .copy to avoid unexpected error
        _extra_ignores.extend(self._INTERNAL_COMPONENT_CODE_IGNORES)
        component_code_ignores = super(InternalComponentIgnoreFile, self)._COMPONENT_CODE_IGNORES
        # add custom ignores (avoid duplication to component code ignores)
        for ignore in set(_extra_ignores) - set(component_code_ignores):
            self._path_spec.append(GitWildMatchPattern(ignore))


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
