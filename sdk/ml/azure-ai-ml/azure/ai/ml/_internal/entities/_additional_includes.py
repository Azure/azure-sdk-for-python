# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Union

from azure.ai.ml.entities._util import _general_copy
from azure.ai.ml.entities._validation import MutableValidationResult, _ValidationResultBuilder
from azure.ai.ml._utils._asset_utils import traverse_directory
from .code import InternalComponentIgnoreFile

ADDITIONAL_INCLUDES_SUFFIX = ".additional_includes"
PLACEHOLDER_FILE_NAME = "_placeholder_spec.yaml"


class _AdditionalIncludes:
    def __init__(
        self,
        code_path: Union[None, str],
        yaml_path: str,
        ignore_file: InternalComponentIgnoreFile = None,
    ):
        self.__yaml_path = yaml_path
        self.__code_path = code_path
        self._ignore_file = ignore_file

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
        return self._yaml_path.with_suffix(ADDITIONAL_INCLUDES_SUFFIX)

    @property
    def code(self) -> Path:
        return self._tmp_code_path if self._tmp_code_path else self._code_path

    def _copy(self, src: Path, dst: Path) -> None:
        if src.is_file():
            _general_copy(src, dst)
        else:
            # use os.walk to replace shutil.copytree, which may raise FileExistsError
            # for same folder, the expected behavior is merging
            # ignore will be also applied during this process
            for root, _, files in os.walk(src):
                dst_root = Path(dst) / Path(root).relative_to(src)
                dst_root_mkdir_flag = dst_root.is_dir()
                for path, _ in traverse_directory(root, files, str(src), "", ignore_file=self._ignore_file):
                    # if there is nothing to copy under current dst_root, no need to create this folder
                    if dst_root_mkdir_flag is False:
                        dst_root.mkdir()
                        dst_root_mkdir_flag = True
                    _general_copy(path, dst_root / Path(path).name)

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
                self._resolve_folder_to_compress(additional_include, Path(tmp_folder_path))
            else:
                dst_path = (tmp_folder_path / src_path.name).resolve()
                self._copy(src_path, dst_path)
        self._tmp_code_path = tmp_folder_path  # point code path to tmp folder
        return

    def _resolve_folder_to_compress(self, include: str, dst_path: Path) -> None:
        """resolve the zip additional include, need to compress corresponding folder."""
        zip_additional_include = (self._additional_includes_file_path.parent / include).resolve()
        folder_to_zip = zip_additional_include.parent / zip_additional_include.stem
        zip_file = dst_path / zip_additional_include.name
        with zipfile.ZipFile(zip_file, "w") as zf:
            zf.write(folder_to_zip, os.path.relpath(folder_to_zip, folder_to_zip.parent))  # write root in zip
            for root, _, files in os.walk(folder_to_zip, followlinks=True):
                for path, _ in traverse_directory(root, files, str(folder_to_zip), "", ignore_file=self._ignore_file):
                    zf.write(path, os.path.relpath(path, folder_to_zip.parent))

    def cleanup(self) -> None:
        """Clean up potential tmp folder generated during resolve as it can be
        very disk consuming."""
        if not self._tmp_code_path:
            return
        if Path(self._tmp_code_path).is_dir():
            shutil.rmtree(self._tmp_code_path)
        self._tmp_code_path = None  # point code path back to real path
