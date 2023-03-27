# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import shutil
import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
from pathlib import Path
from typing import Union

import yaml

from ..._artifacts._constants import PROCESSES_PER_CORE
from ..._utils._asset_utils import IgnoreFile, traverse_directory
from ..._utils.utils import is_concurrent_component_registration_enabled, is_private_preview_enabled
from ...entities._util import _general_copy
from ...entities._validation import MutableValidationResult, _ValidationResultBuilder
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
    ):
        self.__yaml_path = yaml_path
        self.__code_path = code_path

        self._tmp_code_path = None
        self.__includes = None
        # artifact validation is done on loading now, so need a private variable to store the result
        self.__artifact_validate_result = None

    @property
    def _includes(self):
        if not self._additional_includes_file_path.is_file():
            return []
        if self.__includes is None:
            if self._is_artifact_includes:
                self.__includes = self._load_artifact_additional_includes()
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

    @staticmethod
    def _copy(src: Path, dst: Path, *, ignore_file=None) -> None:
        if ignore_file and ignore_file.is_file_excluded(src):
            return
        if not src.exists():
            raise ValueError(f"Path {src} does not exist.")
        if src.is_file():
            _general_copy(src, dst)
        if src.is_dir():
            # TODO: should we cover empty folder?
            # use os.walk to replace shutil.copytree, which may raise FileExistsError
            # for same folder, the expected behavior is merging
            # ignore will be also applied during this process
            for name in src.glob("*"):
                _AdditionalIncludes._copy(name, dst / name.name, ignore_file=ignore_file.merge(name))

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
            # use a dummy ignore file to save base path
            root_ignore_file = InternalComponentIgnoreFile(
                Path(self._code_path).parent,
                additional_includes_file_name=self._additional_includes_file_path.name,
                skip_ignore_file=True,
            )
            self._copy(
                Path(self._code_path), tmp_folder_path / Path(self._code_path).name, ignore_file=root_ignore_file
            )
        else:
            # current implementation of ignore file is based on absolute path, so it cannot be shared
            root_ignore_file = InternalComponentIgnoreFile(
                self._code_path,
                additional_includes_file_name=self._additional_includes_file_path.name,
            )
            self._copy(self._code_path, tmp_folder_path, ignore_file=root_ignore_file)

        # additional includes
        base_path = self._additional_includes_file_path.parent
        # additional includes from artifact will be downloaded to a temp local path on calling
        # self._includes, so no need to add specific logic for artifact

        # TODO: skip ignored files defined in code when copying additional includes
        # copy additional includes disregarding ignore files as current ignore file implementation
        # is based on absolute path, which is not suitable for additional includes
        for additional_include in self._includes:
            src_path = Path(additional_include)
            if not src_path.is_absolute():
                src_path = (base_path / additional_include).resolve()
            dst_path = (tmp_folder_path / src_path.name).resolve()

            root_ignore_file.rebase(src_path.parent)
            if self._is_folder_to_compress(src_path):
                self._resolve_folder_to_compress(
                    additional_include,
                    Path(tmp_folder_path),
                    # actual src path is without .zip suffix
                    ignore_file=root_ignore_file.merge(src_path.parent / src_path.stem),
                )
                # early continue as the folder is compressed as a zip file
                continue

            if not src_path.exists():
                raise ValueError(f"Unable to find additional include {additional_include} for {self._yaml_name}.")

            if src_path.is_file():
                self._copy(src_path, dst_path, ignore_file=root_ignore_file)
            if src_path.is_dir():
                self._copy(
                    src_path,
                    dst_path,
                    # root ignore file on parent + ignore file on src_path
                    ignore_file=root_ignore_file.merge(src_path),
                )

        self._tmp_code_path = tmp_folder_path  # point code path to tmp folder
        return

    def _resolve_folder_to_compress(self, include: str, dst_path: Path, ignore_file: IgnoreFile) -> None:
        """resolve the zip additional include, need to compress corresponding folder."""
        zip_additional_include = (self._additional_includes_file_path.parent / include).resolve()
        folder_to_zip = zip_additional_include.parent / zip_additional_include.stem
        zip_file = dst_path / zip_additional_include.name
        with zipfile.ZipFile(zip_file, "w") as zf:
            zf.write(folder_to_zip, os.path.relpath(folder_to_zip, folder_to_zip.parent))  # write root in zip
            for root, _, files in os.walk(folder_to_zip, followlinks=True):
                for path, _ in traverse_directory(root, files, str(folder_to_zip), "", ignore_file=ignore_file):
                    zf.write(path, os.path.relpath(path, folder_to_zip.parent))

    def cleanup(self) -> None:
        """Clean up potential tmp folder generated during resolve as it can be
        very disk consuming."""
        if not self._tmp_code_path:
            return
        if Path(self._tmp_code_path).is_dir():
            shutil.rmtree(self._tmp_code_path)
        self._tmp_code_path = None  # point code path back to real path

    @property
    def _is_artifact_includes(self):
        try:
            with open(self._additional_includes_file_path) as f:
                additional_includes_configs = yaml.safe_load(f)
                return (
                    isinstance(additional_includes_configs, dict)
                    and ADDITIONAL_INCLUDES_KEY in additional_includes_configs
                )
        except Exception:  # pylint: disable=broad-except
            return False

    @property
    def _artifact_validate_result(self):
        if not self._is_artifact_includes:
            return _ValidationResultBuilder.success()
        if self.__artifact_validate_result is None:
            # artifact validation is done on loading now, so trigger it here
            self._load_artifact_additional_includes()
        return self.__artifact_validate_result

    @classmethod
    def merge_local_path_to_additional_includes(cls, local_path, config_info, conflict_files):
        file_name = Path(local_path).name
        conflicts = conflict_files.get(file_name, set())
        conflicts.add(config_info)
        conflict_files[file_name] = conflicts

    @classmethod
    def _get_artifacts_by_config(cls, artifact_config):
        artifact_cache = ArtifactCache()
        if any(item not in artifact_config for item in ["feed", "name", "version"]):
            raise RuntimeError("Feed, name and version are required for artifacts config.")
        return artifact_cache.get(
            organization=artifact_config.get("organization", None),
            project=artifact_config.get("project", None),
            feed=artifact_config["feed"],
            name=artifact_config["name"],
            version=artifact_config["version"],
            scope=artifact_config.get("scope", "organization"),
            resolve=True,
        )

    def _resolve_additional_include_config(self, additional_include_config):
        result = []
        if isinstance(additional_include_config, dict) and additional_include_config.get("type") == ARTIFACT_KEY:
            try:
                # Get the artifacts package from devops to the local
                artifact_path = self._get_artifacts_by_config(additional_include_config)
                for item in os.listdir(artifact_path):
                    config_info = (
                        f"{additional_include_config['name']}:{additional_include_config['version']} in "
                        f"{additional_include_config['feed']}"
                    )
                    result.append((os.path.join(artifact_path, item), config_info))
            except Exception as e:  # pylint: disable=broad-except
                self._artifact_validate_result.append_error(message=e.args[0])
        elif isinstance(additional_include_config, str):
            result.append((additional_include_config, additional_include_config))
        else:
            self._artifact_validate_result.append_error(
                message=f"Unexpected format in additional_includes, {additional_include_config}"
            )
        return result

    def _load_artifact_additional_includes(self):
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
        self.__artifact_validate_result = _ValidationResultBuilder.success()

        # Load the artifacts config from additional_includes
        with open(self._additional_includes_file_path) as f:
            additional_includes_configs = yaml.safe_load(f)
            additional_includes_configs = additional_includes_configs.get(ADDITIONAL_INCLUDES_KEY, [])

        additional_includes, conflict_files = [], {}
        num_threads = int(cpu_count()) * PROCESSES_PER_CORE
        if (
            len(additional_includes_configs) > 1
            and is_concurrent_component_registration_enabled()
            and is_private_preview_enabled()
        ):
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                for local_path, config_info in executor.map(
                    self._resolve_additional_include_config, additional_includes_configs
                ):
                    additional_includes.append(local_path)
                    self.merge_local_path_to_additional_includes(
                        local_path=local_path, config_info=config_info, conflict_files=conflict_files
                    )
        else:
            for local_path, config_info in map(self._resolve_additional_include_config, additional_includes_configs):
                additional_includes.append(local_path)
                self.merge_local_path_to_additional_includes(
                    local_path=local_path, config_info=config_info, conflict_files=conflict_files
                )

        # Check the file conflict in local path and artifact package.
        conflict_files = {k: v for k, v in conflict_files.items() if len(v) > 1}
        if conflict_files:
            self._artifact_validate_result.append_error(
                message=f"There are conflict files in additional include: {conflict_files}"
            )
        return additional_includes
