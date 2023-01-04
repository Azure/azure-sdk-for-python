# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Optional, Union

import yaml

from azure.ai.ml._utils._asset_utils import IgnoreFile, traverse_directory
from azure.ai.ml.entities._util import _general_copy
from azure.ai.ml.entities._validation import MutableValidationResult, _ValidationResultBuilder

from ._artifact_cache import ArtifactCache
from .code import InternalComponentIgnoreFile

ADDITIONAL_INCLUDES_SUFFIX = ".additional_includes"
PLACEHOLDER_FILE_NAME = "_placeholder_spec.yaml"
ADDITIONAL_INCLUDES_KEY = "additional_includes"
ARTIFACT_KEY = "artifact"


class _AdditionalIncludes:
    def __init__(
        self,
        code_path: Union[None, str],
        yaml_path: str,
        ignore_file: Optional[InternalComponentIgnoreFile] = None,
    ):
        self.__yaml_path = yaml_path
        self.__code_path = code_path
        self._ignore_file = ignore_file

        self._tmp_code_path = None
        self.__includes = None
        self._is_artifact_includes = False
        self._artifact_validate_result = _ValidationResultBuilder.success()

    @property
    def _includes(self):
        if not self._additional_includes_file_path.is_file():
            return []
        if self.__includes is None:
            self._is_artifact_includes = self._is_yaml_format_additional_includes()
            if self._is_artifact_includes:
                self.__includes = self._load_yaml_format_additional_includes()
            else:
                with open(self._additional_includes_file_path, "r") as f:
                    lines = f.readlines()
                    self.__includes = [line.strip() for line in lines if len(line.strip()) > 0]
        return self.__includes

    @property
    def with_includes(self):
        return len(self._includes) != 0 or not self._artifact_validate_result.passed

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

    def _copy(self, src: Path, dst: Path, ignore_file=None) -> None:
        if src.is_file():
            _general_copy(src, dst)
        else:
            # use os.walk to replace shutil.copytree, which may raise FileExistsError
            # for same folder, the expected behavior is merging
            # ignore will be also applied during this process
            for root, _, files in os.walk(src):
                dst_root = Path(dst) / Path(root).relative_to(src)
                dst_root_mkdir_flag = dst_root.is_dir()
                for path, _ in traverse_directory(
                    root, files, str(src), "", ignore_file=ignore_file or self._ignore_file
                ):
                    # if there is nothing to copy under current dst_root, no need to create this folder
                    if dst_root_mkdir_flag is False:
                        dst_root.mkdir(parents=True)
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
        validation_result.merge_with(self._artifact_validate_result)
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
            src_path = Path(additional_include)
            if not src_path.is_absolute():
                src_path = (base_path / additional_include).resolve()
            if self._is_folder_to_compress(src_path):
                self._resolve_folder_to_compress(additional_include, Path(tmp_folder_path))
            else:
                dst_path = (tmp_folder_path / src_path.name).resolve()
                self._copy(src_path, dst_path, ignore_file=IgnoreFile() if self._is_artifact_includes else None)
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

    def _is_yaml_format_additional_includes(self):
        try:
            with open(self._additional_includes_file_path) as f:
                additional_includes_configs = yaml.safe_load(f)
                return (
                    isinstance(additional_includes_configs, dict)
                    and ADDITIONAL_INCLUDES_KEY in additional_includes_configs
                )
        except Exception:  # pylint: disable=broad-except
            return False

    def _load_yaml_format_additional_includes(self):
        """
        Load the additional includes by yaml format.

        Addition includes is a list of include files, such as local paths and Azure Devops Artifacts.
        Yaml format of additional_includes likes below:
            additional_includes:
             - your/local/path
             - type: artifact
               organization: devops_organization
               project: devops_project
               feed: artifacts_feed_name
               name: universal_package_name
               version: package_version
               scope: scope_type
        If will get the artifacts package from devops to the local, and merge them with the local path into
        additional include list. If there are files conflict in the artifacts, user error will be raised.

        :return additional_includes: Path list of additional_includes
        :rtype additional_includes: List[str]
        """
        additional_includes, conflict_files = [], {}
        self._artifact_validate_result = _ValidationResultBuilder.success()

        def merge_local_path_to_additional_includes(local_path, config_info):
            additional_includes.append(local_path)
            file_name = Path(local_path).name
            conflicts = conflict_files.get(file_name, set())
            conflicts.add(config_info)
            conflict_files[file_name] = conflicts

        def get_artifacts_by_config(artifact_config):
            artifact_cache = ArtifactCache()
            if any(item not in artifact_config for item in ["feed", "name", "version"]):
                raise RuntimeError("Feed, name and version are required for artifacts config.")
            artifact_path = artifact_cache.get(
                organization=artifact_config.get("organization", None),
                project=artifact_config.get("project", None),
                feed=artifact_config["feed"],
                name=artifact_config["name"],
                version=artifact_config["version"],
                scope=artifact_config.get("scope", "organization"),
                resolve=True,
            )
            return artifact_path

        # Load the artifacts config from additional_includes
        with open(self._additional_includes_file_path) as f:
            additional_includes_configs = yaml.safe_load(f)
            additional_includes_configs = additional_includes_configs.get(ADDITIONAL_INCLUDES_KEY, [])

        for additional_include in additional_includes_configs:
            if isinstance(additional_include, dict) and additional_include.get("type") == ARTIFACT_KEY:
                try:
                    # Get the artifacts package from devops to the local
                    artifact_path = get_artifacts_by_config(additional_include)
                    for item in os.listdir(artifact_path):
                        config_info = (
                            f"{additional_include['name']}:{additional_include['version']} in "
                            f"{additional_include['feed']}"
                        )
                        merge_local_path_to_additional_includes(
                            local_path=os.path.join(artifact_path, item), config_info=config_info
                        )
                except Exception as e:  # pylint: disable=broad-except
                    self._artifact_validate_result.append_error(message=e.args[0])
            elif isinstance(additional_include, str):
                merge_local_path_to_additional_includes(local_path=additional_include, config_info=additional_include)
            else:
                self._artifact_validate_result.append_error(
                    message=f"Unexpected format in additional_includes, {additional_include}"
                )

        # Check the file conflict in local path and artifact package.
        conflict_files = {k: v for k, v in conflict_files.items() if len(v) > 1}
        if conflict_files:
            self._artifact_validate_result.append_error(
                message=f"There are conflict files in additional include: {conflict_files}"
            )
        return additional_includes
