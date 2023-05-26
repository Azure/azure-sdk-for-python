# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import shutil
import tempfile
import zipfile
from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from multiprocessing import cpu_count
from pathlib import Path
from typing import List, Optional, Union

from azure.ai.ml.constants._common import AzureDevopsArtifactsType
from azure.ai.ml.entities._validation import MutableValidationResult, _ValidationResultBuilder

from ..._utils._artifact_utils import ArtifactCache
from ..._utils._asset_utils import IgnoreFile, traverse_directory
from ..._utils.utils import is_concurrent_component_registration_enabled, is_private_preview_enabled
from ...entities._util import _general_copy
from .._assets import Code
from .code import CodeType, ComponentCodeMixin, ComponentIgnoreFile

PLACEHOLDER_FILE_NAME = "_placeholder_spec.yaml"


class AdditionalIncludes:
    def __init__(
        self,
        *,
        origin_code_value: Union[None, str],
        base_path: Path,
        configs: List[Union[str, dict]] = None,
    ):
        self._base_path = base_path
        self._origin_code_value = origin_code_value
        self._origin_configs = configs

        self._tmp_code_path = None
        # artifact validation is done on loading now, so need a private variable to store the result
        self._artifact_validation_result = None

    @property
    def origin_configs(self):
        """The origin additional include configs.
        Artifact additional include configs haven't been resolved in this property.
        """
        return self._origin_configs or []

    @property
    def resolved_code_path(self) -> Union[None, Path]:
        """The resolved origin code path based on base path, if code path is not specified, return None.
        We shouldn't change this property name given it's referenced in mldesigner.
        """
        if self._origin_code_value is None:
            return None
        if os.path.isabs(self._origin_code_value):
            return Path(self._origin_code_value)
        return (self.base_path / self._origin_code_value).resolve()

    @property
    def base_path(self) -> Path:
        """Base path for origin code path and additional include configs."""
        return self._base_path

    @property
    def with_includes(self):
        """Whether the additional include configs have been provided."""
        return len(self.includes) != 0 or not self._validate_artifact_additional_includes().passed

    @property
    def _is_artifact_includes(self):
        return any(
            map(
                lambda x: isinstance(x, dict) and x.get("type", None) == AzureDevopsArtifactsType.ARTIFACT,
                self.origin_configs,
            )
        )

    @property
    def includes(self):
        """The resolved additional include configs.
        Artifact additional include configs have been resolved in this property.
        """
        if self._is_artifact_includes:
            return self._load_artifact_additional_includes()
        return self.origin_configs

    def _validate_artifact_additional_includes(self):
        if not self._is_artifact_includes:
            return _ValidationResultBuilder.success()
        if self._artifact_validation_result is None:
            # artifact validation is done on loading now, so trigger it here
            self._load_artifact_additional_includes()
        return self._artifact_validation_result

    @classmethod
    def _merge_local_path_to_additional_includes(cls, local_path, config_info, conflict_files):
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
        validation_result = _ValidationResultBuilder.success()
        if (
            isinstance(additional_include_config, dict)
            and additional_include_config.get("type") == AzureDevopsArtifactsType.ARTIFACT
        ):
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
                validation_result.append_error(message=e.args[0])
        elif isinstance(additional_include_config, str):
            result.append((additional_include_config, additional_include_config))
        else:
            validation_result.append_error(
                message=f"Unexpected format in additional_includes, {additional_include_config}"
            )
        return result, validation_result

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
                AdditionalIncludes._copy(name, dst / name.name, ignore_file=ignore_file.merge(name))

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

    def _resolve_folder_to_compress(self, include: str, dst_path: Path, ignore_file: IgnoreFile) -> None:
        """resolve the zip additional include, need to compress corresponding folder."""
        zip_additional_include = (self.base_path / include).resolve()
        folder_to_zip = zip_additional_include.parent / zip_additional_include.stem
        zip_file = dst_path / zip_additional_include.name
        with zipfile.ZipFile(zip_file, "w") as zf:
            zf.write(folder_to_zip, os.path.relpath(folder_to_zip, folder_to_zip.parent))  # write root in zip
            for root, _, files in os.walk(folder_to_zip, followlinks=True):
                for path, _ in traverse_directory(root, files, str(folder_to_zip), "", ignore_file=ignore_file):
                    zf.write(path, os.path.relpath(path, folder_to_zip.parent))

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
        all_validation_result = _ValidationResultBuilder.success()
        additional_includes, conflict_files = [], {}

        # Load the artifacts config from additional_includes
        if self.origin_configs:
            additional_includes_configs = self.origin_configs
        else:
            return additional_includes

        # Unlike component registration, artifact downloading is a pure download progress; so we can use
        # more threads to speed up the downloading process.
        # We use 5 threads per CPU core plus 5 extra threads, and the max number of threads is 64.
        num_threads = min(64, (int(cpu_count()) * 5) + 5)
        if (
            len(additional_includes_configs) > 1
            and is_concurrent_component_registration_enabled()
            and is_private_preview_enabled()
        ):
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                for result, validation_result in executor.map(
                    self._resolve_additional_include_config, additional_includes_configs
                ):
                    all_validation_result.merge_with(validation_result)
                    for local_path, config_info in result:
                        additional_includes.append(local_path)
                        self._merge_local_path_to_additional_includes(
                            local_path=local_path, config_info=config_info, conflict_files=conflict_files
                        )
        else:
            for result, validation_result in map(self._resolve_additional_include_config, additional_includes_configs):
                all_validation_result.merge_with(validation_result)
                for local_path, config_info in result:
                    additional_includes.append(local_path)
                    self._merge_local_path_to_additional_includes(
                        local_path=local_path, config_info=config_info, conflict_files=conflict_files
                    )

        # Check the file conflict in local path and artifact package.
        conflict_files = {k: v for k, v in conflict_files.items() if len(v) > 1}
        if conflict_files:
            all_validation_result.append_error(
                message=f"There are conflict files in additional include: {conflict_files}"
            )
        self._artifact_validation_result = all_validation_result
        return additional_includes

    def validate(self) -> MutableValidationResult:
        # use a new validation result to merge artifact validation result to avoid updating the original one
        validation_result = _ValidationResultBuilder.success()
        validation_result.merge_with(self._validate_artifact_additional_includes())
        if not self.with_includes:
            return validation_result
        for additional_include in self.includes:
            include_path = self.base_path / additional_include
            # if additional include has not supported characters, resolve will fail and raise OSError
            try:
                src_path = include_path.resolve()
            except OSError:
                # no need to include potential yaml file name in error message as it will be covered by
                # validation message construction.
                error_msg = f"Failed to resolve additional include " f"{additional_include} based on {self.base_path}."
                validation_result.append_error(message=error_msg)
                continue

            if not src_path.exists() and not self._is_folder_to_compress(src_path):
                error_msg = f"Unable to find additional include {additional_include}"
                validation_result.append_error(message=error_msg)
                continue

            if len(src_path.parents) == 0:
                error_msg = "Root directory is not supported for additional includes."
                validation_result.append_error(message=error_msg)
                continue

            dst_path = Path(self.resolved_code_path) / src_path.name if self.resolved_code_path else None
            if dst_path:
                if dst_path.is_symlink():
                    # if destination path is symbolic link, check if it points to the same file/folder as source path
                    if dst_path.resolve() != src_path.resolve():
                        error_msg = f"A symbolic link already exists for additional include {additional_include}."
                        validation_result.append_error(message=error_msg)
                        continue
                elif dst_path.exists():
                    error_msg = f"A file already exists for additional include {additional_include}."
                    validation_result.append_error(message=error_msg)
        return validation_result

    def _copy_origin_code(self, target_path):
        """Copy origin code to target path."""
        # code can be either file or folder, as additional includes exists, need to copy to temporary folder
        if self.resolved_code_path is None:
            # if additional include configs exist but no origin code path, return a dummy ignore file
            return ComponentIgnoreFile(
                self.base_path,
            )

        if Path(self.resolved_code_path).is_file():
            # use a dummy ignore file to save base path
            root_ignore_file = ComponentIgnoreFile(
                Path(self.resolved_code_path).parent,
                skip_ignore_file=True,
            )
            self._copy(
                Path(self.resolved_code_path),
                target_path / Path(self.resolved_code_path).name,
                ignore_file=root_ignore_file,
            )
        else:
            # current implementation of ignore file is based on absolute path, so it cannot be shared
            root_ignore_file = ComponentIgnoreFile(self.resolved_code_path)
            self._copy(self.resolved_code_path, target_path, ignore_file=root_ignore_file)
        return root_ignore_file

    @contextmanager
    def resolve(self) -> Path:
        """Merge code and potential additional includes into a temp folder and return the absolute path of it.
        If no additional includes is specified, just return absolute path of original code path;
        If no original code path is specified, just return None.
        """
        if not self.with_includes:
            if self.resolved_code_path is None:
                yield None
            else:
                yield self.resolved_code_path.absolute()
            return

        tmp_folder_path = Path(tempfile.mkdtemp())
        root_ignore_file = self._copy_origin_code(tmp_folder_path)

        # resolve additional includes
        base_path = self.base_path
        # additional includes from artifact will be downloaded to a temp local path on calling
        # self.includes, so no need to add specific logic for artifact

        # TODO: skip ignored files defined in code when copying additional includes
        # copy additional includes disregarding ignore files as current ignore file implementation
        # is based on absolute path, which is not suitable for additional includes
        for additional_include in self.includes:
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

            # no need to check if src_path exists as it is already validated
            if src_path.is_file():
                self._copy(src_path, dst_path, ignore_file=root_ignore_file)
            elif src_path.is_dir():
                self._copy(
                    src_path,
                    dst_path,
                    # root ignore file on parent + ignore file on src_path
                    ignore_file=root_ignore_file.merge(src_path),
                )
            else:
                raise ValueError(f"Unable to find additional include {additional_include}.")

        self._tmp_code_path = tmp_folder_path  # point code path to tmp folder
        yield tmp_folder_path.absolute()

        # clean up tmp folder as it can be very disk space consuming
        shutil.rmtree(tmp_folder_path, ignore_errors=True)
        return


class AdditionalIncludesMixin(ComponentCodeMixin):
    def __init__(self):
        self.__used_base_path = None
        self.__used_additional_includes = None
        self.__used_code_value = None
        self.__obj: Optional[AdditionalIncludes] = None

    @property
    def _additional_includes(self) -> AdditionalIncludes:
        """Get additional includes object."""
        # reset obj if base path or additional includes changed
        if self.__obj is not None and (
            self.__used_base_path != self._get_base_path_for_code()
            or self.__used_additional_includes != self._get_all_additional_includes_configs()
            or self.__used_code_value != self._get_origin_code_value()
        ):
            self.__obj = None

        if self.__obj is None:
            self.__used_base_path = self._get_base_path_for_code()
            self.__used_additional_includes = self._get_all_additional_includes_configs()
            self.__used_code_value = self._get_origin_code_value()
            self.__obj = AdditionalIncludes(
                base_path=self.__used_base_path,
                configs=self.__used_additional_includes,
                origin_code_value=self.__used_code_value,
            )
        return self.__obj

    @abstractmethod
    def _get_all_additional_includes_configs(self) -> List:
        """Get all additional include configs."""

    @contextmanager
    def _merge_additional_includes(self) -> Optional[Path]:
        """Copy both additional includes and origin code (if exists) to a temp folder and yield the path to it.

        It's already called in self._build_code, so no need to call it again unless _build_code is overridden.
        """
        # merge code path with additional includes into a temp folder if additional includes is specified
        with self._additional_includes.resolve() as code_path:
            yield code_path

    def _validate_additional_includes(self):
        """Validate additional includes.

        This is not called in _validate_code to allow passing different field names for validation results of code and
        additional includes.
        """
        return self._additional_includes.validate()

    def _with_additional_includes(self):
        """Whether the component has additional includes."""
        # Ignore additional includes if origin code is not a local path
        return self._additional_includes.with_includes

    def _get_code_type(self):
        origin_code_value = self._get_origin_code_value()
        if origin_code_value is None and self._additional_includes.with_includes:
            return CodeType.LOCAL
        return super()._get_code_type()

    @contextmanager
    def _build_code(self) -> Optional[Code]:
        """Create a Code object if necessary based on origin code value and yield it.

        If built code is the same as its origin value, do nothing and yield None.
        Otherwise, yield a Code object pointing to the code.
        Will merge code path with additional includes into a temp folder if additional includes is specified.
        """
        # if origin code is not a local path, ignore additional includes
        # note that this condition will be True if origin code value is not a local path even if additional includes
        # is specified; On the other hand, artifact additional includes will be treated as local code
        if not self._with_local_code():
            with super()._build_code() as code:
                yield code
                return

        with self._merge_additional_includes() as tmp_code_dir:
            if tmp_code_dir is None:
                yield None
                return

            yield Code(
                base_path=self._get_base_path_for_code(),
                path=tmp_code_dir,
                ignore_file=ComponentIgnoreFile(tmp_code_dir),
            )
