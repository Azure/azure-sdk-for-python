# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import shutil
import tempfile
from pathlib import Path
from typing import Union

from azure.ai.ml.entities._util import _general_copy
from azure.ai.ml.entities._validation import ValidationResult, _ValidationResultBuilder

ADDITIONAL_INCLUDES_SUFFIX = "additional_includes"


class _AdditionalIncludes:
    def __init__(self, code_path: Union[None, str], yaml_path: str):
        self._yaml_path = Path(yaml_path)
        self._yaml_name = self._yaml_path.name
        self._code_path = self._yaml_path.parent
        if code_path is not None:
            self._code_path = (self._code_path / code_path).resolve()
        self._tmp_code_path = None
        self._additional_includes_file_path = self._yaml_path.with_suffix(f".{ADDITIONAL_INCLUDES_SUFFIX}")
        self._includes = None
        if self._additional_includes_file_path.is_file():
            with open(self._additional_includes_file_path, "r") as f:
                lines = f.readlines()
                self._includes = [line.strip() for line in lines if len(line.strip()) > 0]

    @property
    def code(self) -> Path:
        return self._tmp_code_path if self._tmp_code_path else self._code_path

    @staticmethod
    def _copy(src: Path, dst: Path) -> None:
        if src.is_file():
            _general_copy(src, dst)
        else:
            shutil.copytree(src, dst)

    def validate(self) -> ValidationResult:
        if self._includes is None:
            return _ValidationResultBuilder.success()
        for additional_include in self._includes:
            include_path = self._additional_includes_file_path.parent / additional_include
            # if additional include has not supported characters, resolve will fail and raise OSError
            try:
                src_path = include_path.resolve()
            except OSError:
                error_msg = f"Failed to resolve additional include {additional_include} for {self._yaml_name}."
                return _ValidationResultBuilder.from_single_message(error_msg)

            if not src_path.exists():
                error_msg = f"Unable to find additional include {additional_include} for {self._yaml_name}."
                return _ValidationResultBuilder.from_single_message(error_msg)

            if len(src_path.parents) == 0:
                error_msg = f"Root directory is not supported for additional includes for {self._yaml_name}."
                return _ValidationResultBuilder.from_single_message(error_msg)

            dst_path = Path(self._code_path) / src_path.name
            if dst_path.is_symlink():
                # if destination path is symbolic link, check if it points to the same file/folder as source path
                if dst_path.resolve() != src_path.resolve():
                    error_msg = (
                        f"A symbolic link already exists for additional include {additional_include} "
                        f"for {self._yaml_name}."
                    )
                    return _ValidationResultBuilder.from_single_message(error_msg)
            elif dst_path.exists():
                error_msg = f"A file already exists for additional include {additional_include} for {self._yaml_name}."
                return _ValidationResultBuilder.from_single_message(error_msg)
        return _ValidationResultBuilder.success()

    def resolve(self) -> None:
        """Resolve code and potential additional includes.

        If no additional includes is specified, just return and use
        original real code path; otherwise, create a tmp folder and copy
        all files under real code path and additional includes to it.
        """
        if self._includes is None:
            return
        tmp_folder_path = Path(tempfile.mkdtemp())
        # code can be either file or folder, as additional includes exists, need to copy to temporary folder
        if Path(self._code_path).is_file():
            self._copy(Path(self._code_path), tmp_folder_path / Path(self._code_path).name)
        else:
            for path in os.listdir(self._code_path):
                src_path = (Path(self._code_path) / str(path)).resolve()
                if src_path.suffix == ADDITIONAL_INCLUDES_SUFFIX:
                    continue
                dst_path = tmp_folder_path / str(path)
                self._copy(src_path, dst_path)
        # additional includes
        base_path = self._additional_includes_file_path.parent
        for additional_include in self._includes:
            src_path = (base_path / additional_include).resolve()
            dst_path = (tmp_folder_path / src_path.name).resolve()
            self._copy(src_path, dst_path)
        self._tmp_code_path = tmp_folder_path  # point code path to tmp folder
        return

    def cleanup(self) -> None:
        """Clean up potential tmp folder generated during resolve as it can be
        very disk consuming."""
        if not self._tmp_code_path:
            return
        if Path(self._tmp_code_path).is_dir():
            shutil.rmtree(self._tmp_code_path)
        self._tmp_code_path = None  # point code path back to real path
