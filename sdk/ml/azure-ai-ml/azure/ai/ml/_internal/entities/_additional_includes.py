# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import yaml
from pathlib import Path
from typing import Union

from .code import InternalComponentIgnoreFile
from ...entities._component._additional_includes import (
    AdditionalIncludes,
    ADDITIONAL_INCLUDES_KEY,
    ADDITIONAL_INCLUDES_SUFFIX,
)


class _InternalAdditionalIncludes(AdditionalIncludes):
    def __init__(
        self,
        code_path: Union[None, str],
        yaml_path: str,
    ):
        super(_InternalAdditionalIncludes, self).__init__(code_path, yaml_path)
        self._yaml_path = yaml_path
        self._code_path = code_path

    @property
    def includes(self):
        if not self.additional_includes_file_path.is_file():
            return []
        if self._includes is None:
            if self.is_artifact_includes:
                self._includes = self._load_artifact_additional_includes()
            else:
                with open(self.additional_includes_file_path, "r") as f:
                    lines = f.readlines()
                    self._includes = [line.strip() for line in lines if len(line.strip()) > 0]
        return self._includes

    @property
    def code_path(self) -> Path:
        if self._code_path is not None:
            return (self.yaml_path.parent / self._code_path).resolve()
        return self.yaml_path.parent

    @property
    def additional_includes_file_path(self) -> Path:
        return self.yaml_path.with_suffix(ADDITIONAL_INCLUDES_SUFFIX)

    @property
    def is_artifact_includes(self):
        try:
            with open(self.additional_includes_file_path) as f:
                additional_includes_configs = yaml.safe_load(f)
                return (
                    isinstance(additional_includes_configs, dict)
                    and ADDITIONAL_INCLUDES_KEY in additional_includes_configs
                )
        except Exception:  # pylint: disable=broad-except
            return False

    def _resolve_code(self, tmp_folder_path):
        """Resolve code when additional includes is specified.

        create a tmp folder and copy all files under real code path to it.
        """

        # code can be either file or folder, as additional includes exists, need to copy to temporary folder
        if Path(self.code_path).is_file():
            # use a dummy ignore file to save base path
            root_ignore_file = InternalComponentIgnoreFile(
                Path(self.code_path).parent,
                additional_includes_file_name=self.additional_includes_file_path.name,
                skip_ignore_file=True,
            )
            self._copy(Path(self.code_path), tmp_folder_path / Path(self.code_path).name, ignore_file=root_ignore_file)
        else:
            # current implementation of ignore file is based on absolute path, so it cannot be shared
            root_ignore_file = InternalComponentIgnoreFile(
                self.code_path,
                additional_includes_file_name=self.additional_includes_file_path.name,
            )
            self._copy(self.code_path, tmp_folder_path, ignore_file=root_ignore_file)
        return root_ignore_file
