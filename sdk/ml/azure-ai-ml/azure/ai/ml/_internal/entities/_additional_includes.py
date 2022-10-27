# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import shutil
import tempfile
from pathlib import Path
from typing import Union

from azure.ai.ml.entities._util import _copy_folder_ignore_pycache, _general_copy
from azure.ai.ml.entities._validation import MutableValidationResult, _ValidationResultBuilder

ADDITIONAL_INCLUDES_SUFFIX = "additional_includes"
PLACEHOLDER_FILE_NAME = "_placeholder_spec.yaml"


class _AdditionalIncludes:
    def __init__(self, code_path: Union[None, str], yaml_path: str):
        self.__yaml_path = yaml_path
        self.__code_path = code_path

        self._tmp_code_path = None
        self.__includes = None

    @property
    def _includes(self):
        if not self._additional_includes_file_path.is_file():
            return []
        if self.__includes is None:
            with open(self._additional_includes_file_path, "r") as f:
                lines = f.readlines()
                self.__includes = [line.strip() for line in lines if len(line.strip()) > 0]
        return self.__includes

    @property
    def with_includes(self):
        return len(self._includes) != 0

    @property
    def _yaml_path(self) -> Path:
        if self.__yaml_path is None:
            # if yaml path is not specified, use a not created
            # temp file name
            return Path.cwd() / PLACEHOLDER_FILE_NAME
        return Path(self.__yaml_path)

    @property
    def _code_path(self) -> Path:
        if self.__code_path is not None:
            return (self._yaml_path.parent / self.__code_path).resolve()
        return self._yaml_path.parent

    @property
    def _yaml_name(self) -> str:
        return self._yaml_path.name

    @property
    def _additional_includes_file_path(self) -> Path:
        return self._yaml_path.with_suffix(f".{ADDITIONAL_INCLUDES_SUFFIX}")

    @property
    def code(self) -> Path:
        return self._tmp_code_path if self._tmp_code_path else self._code_path

    @staticmethod
    def _copy(src: Path, dst: Path) -> None:
        if src.is_file():
            _general_copy(src, dst)
        else:
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__"))

    @staticmethod
    def _is_folder_to_compress(path: Path) -> bool:
        """Check if the additional include needs to compress corresponding folder as a zip.

        For example, given additional include /mnt/c/hello.zip
          1) if a file named /mnt/c/hello.zip already exists, return False (simply copy)
          2) if a folder named /mnt/c/hello exists, return True (compress as a zip and copy)

        :param path: Given path in additional include.
        :type path: Path
        :return: If the path need to be compressed as a zip file.
        :rtype: bool
        """
        if path.suffix != ".zip":
            return False
        # if zip file exists, simply copy as other additional includes
        if path.exists():
            return False
        # remove .zip suffix and check whether the folder exists
        stem_path = path.parent / path.stem
        return stem_path.is_dir()

    def _validate(self) -> MutableValidationResult:
        validation_result = _ValidationResultBuilder.success()
        if not self.with_includes:
            return validation_result
        for additional_include in self._includes:
            include_path = self._additional_includes_file_path.parent / additional_include
            # if additional include has not supported characters, resolve will fail and raise OSError
            try:
                src_path = include_path.resolve()
            except OSError:
                error_msg = f"Failed to resolve additional include {additional_include} for {self._yaml_name}."
                validation_result.append_error(message=error_msg)
                continue

            if not src_path.exists() and not self._is_folder_to_compress(src_path):
                error_msg = f"Unable to find additional include {additional_include} for {self._yaml_name}."
                validation_result.append_error(message=error_msg)
                continue

            if len(src_path.parents) == 0:
                error_msg = f"Root directory is not supported for additional includes for {self._yaml_name}."
                validation_result.append_error(message=error_msg)
                continue

            dst_path = Path(self._code_path) / src_path.name
            if dst_path.is_symlink():
                # if destination path is symbolic link, check if it points to the same file/folder as source path
                if dst_path.resolve() != src_path.resolve():
                    error_msg = (
                        f"A symbolic link already exists for additional include {additional_include} "
                        f"for {self._yaml_name}."
                    )
                    validation_result.append_error(message=error_msg)
                    continue
            elif dst_path.exists():
                error_msg = f"A file already exists for additional include {additional_include} for {self._yaml_name}."
                validation_result.append_error(message=error_msg)
        return validation_result

    def resolve(self) -> None:
        """Resolve code and potential additional includes.

        If no additional includes is specified, just return and use
        original real code path; otherwise, create a tmp folder and copy
        all files under real code path and additional includes to it.
        """
        if not self.with_includes:
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
            if self._is_folder_to_compress(src_path):
                # note: additional include is a zip file, we need to compress corresponding folder,
                # create a temp folder and copy files to this, filter __pycache__ in the folder
                # during the copy.
                # this operation can be replaced by using zipfile.ZipFile, which
                # allows us pick files to compress rather than copy -- may improve performance.
                zip_additional_include = (base_path / additional_include).resolve()
                folder_to_zip = zip_additional_include.parent / zip_additional_include.stem
                with tempfile.TemporaryDirectory() as tmp_dir:
                    tmp_folder_to_zip = (Path(tmp_dir) / "zip").resolve()
                    _copy_folder_ignore_pycache(folder_to_zip, tmp_folder_to_zip)
                    src_path = (Path(tempfile.mkdtemp()) / zip_additional_include.name).resolve()
                    shutil.make_archive(str(src_path.parent / src_path.stem), "zip", tmp_folder_to_zip)
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
