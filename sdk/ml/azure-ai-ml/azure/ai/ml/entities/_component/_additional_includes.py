# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import os
import shutil
import tempfile
import zipfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from multiprocessing import cpu_count
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from azure.ai.ml.constants._common import AzureDevopsArtifactsType
from azure.ai.ml.entities._validation import MutableValidationResult, _ValidationResultBuilder

from ..._utils._artifact_utils import ArtifactCache
from ..._utils._asset_utils import IgnoreFile, traverse_directory
from ..._utils.utils import is_concurrent_component_registration_enabled, is_private_preview_enabled
from ...entities._util import _general_copy
from .._assets import Code
from .code import ComponentCodeMixin, ComponentIgnoreFile

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
        return len(self.origin_configs) != 0

    @classmethod
    def _get_artifacts_by_config(cls, artifact_config):
        # config key existence has been validated in _validate_additional_include_config
        return ArtifactCache().get(
            organization=artifact_config.get("organization", None),
            project=artifact_config.get("project", None),
            feed=artifact_config["feed"],
            name=artifact_config["name"],
            version=artifact_config["version"],
            scope=artifact_config.get("scope", "organization"),
            resolve=True,
        )

    def _validate_additional_include_config(self, additional_include_config):
        validation_result = _ValidationResultBuilder.success()
        if (
            isinstance(additional_include_config, dict)
            and additional_include_config.get("type") == AzureDevopsArtifactsType.ARTIFACT
        ):
            # for artifact additional include, we validate the required fields in config but won't validate the
            # artifact content to avoid downloading it in validation stage
            # note that runtime error will be thrown when loading the artifact
            for item in ["feed", "name", "version"]:
                if item not in additional_include_config:
                    # TODO: add yaml path after we support list index in yaml path
                    validation_result.append_error(
                        "{} are required for artifacts config but got {}.".format(
                            item, json.dumps(additional_include_config)
                        )
                    )
        elif isinstance(additional_include_config, str):
            validation_result.merge_with(self._validate_local_additional_include_config(additional_include_config))
        else:
            validation_result.append_error(
                message=f"Unexpected format in additional_includes, {additional_include_config}"
            )
        return validation_result

    @classmethod
    def _resolve_artifact_additional_include_config(cls, artifact_additional_include_config) -> List[Tuple[str, str]]:
        """Resolve an artifact additional include config into a list of (local_path, config_info) tuples.
        Configured artifact will be downloaded to local path first; the config_info will be in below format:
        %name%:%version% in %feed%
        """
        result = []
        # Note that we don't validate the artifact config here, since it has already been validated in
        # _validate_additional_include_config
        artifact_path = cls._get_artifacts_by_config(artifact_additional_include_config)
        for item in os.listdir(artifact_path):
            config_info = (
                f"{artifact_additional_include_config['name']}:{artifact_additional_include_config['version']} in "
                f"{artifact_additional_include_config['feed']}"
            )
            result.append((os.path.join(artifact_path, item), config_info))
        return result

    def _resolve_artifact_additional_include_configs(self, artifact_additional_includes_configs: List[Dict[str, str]]):
        additional_include_info_tuples = []
        # Unlike component registration, artifact downloading is a pure download progress; so we can use
        # more threads to speed up the downloading process.
        # We use 5 threads per CPU core plus 5 extra threads, and the max number of threads is 64.
        num_threads = min(64, (int(cpu_count()) * 5) + 5)
        if (
            len(artifact_additional_includes_configs) > 1
            and is_concurrent_component_registration_enabled()
            and is_private_preview_enabled()
        ):
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                all_artifact_pairs = executor.map(
                    self._resolve_artifact_additional_include_config, artifact_additional_includes_configs
                )
        else:
            all_artifact_pairs = list(
                map(self._resolve_artifact_additional_include_config, artifact_additional_includes_configs)
            )
        for artifact_pairs in all_artifact_pairs:
            additional_include_info_tuples.extend(artifact_pairs)
        return additional_include_info_tuples

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

    def _get_resolved_additional_include_configs(self) -> List[str]:
        """
        Resolve additional include configs to a list of local_paths and return it.

        Addition includes is a list of include files, including local paths and Azure Devops Artifacts.
        Yaml format of additional_includes looks like below:
            additional_includes:
             - your/local/path
             - type: artifact
               organization: devops_organization
               project: devops_project
               feed: artifacts_feed_name
               name: universal_package_name
               version: package_version
               scope: scope_type
        The artifacts package will be downloaded from devops to the local in this function and transferred to
        the local paths of downloaded artifacts;
        The local paths will be returned directly.
        If there are conflicts among artifacts, runtime error will be raised. Note that we won't check the
        conflicts between artifacts and local paths and conflicts among local paths. Reasons are:
        1. There can be ignore_file in local paths, which makes it hard to check the conflict and may lead to breaking
        changes;
        2. Conflicts among artifacts are more likely to happen, since user may refer to 2 artifacts of the same name
        but with different version & feed.
        3. According to current design, folders in local paths will be merged; while artifact conflicts can be
        identified by folder name conflicts and are not allowed.

        :return additional_includes: Path list of additional_includes
        :rtype additional_includes: List[str]
        """
        additional_include_configs_in_local_path = []

        artifact_additional_include_configs = []
        for additional_include_config in self.origin_configs:
            if isinstance(additional_include_config, str):
                # add local additional include configs directly
                additional_include_configs_in_local_path.append(additional_include_config)
            else:
                # artifact additional include config will be downloaded and resolved to a local path later
                # note that there is no more validation for artifact additional include config here, since it has
                # already been validated in _validate_additional_include_config
                artifact_additional_include_configs.append(additional_include_config)

        artifact_additional_include_info_tuples = self._resolve_artifact_additional_include_configs(
            artifact_additional_include_configs
        )
        additional_include_configs_in_local_path.extend(
            local_path for local_path, _ in artifact_additional_include_info_tuples
        )

        # check file conflicts among artifact package
        # given this is not in validate stage, we will raise error if there are conflict files
        conflict_files = defaultdict(set)
        for local_path, config_info in artifact_additional_include_info_tuples:
            file_name = Path(local_path).name
            conflict_files[file_name].add(config_info)

        conflict_files = {k: v for k, v in conflict_files.items() if len(v) > 1}
        if conflict_files:
            raise RuntimeError(f"There are conflict files in additional include: {conflict_files}")

        return additional_include_configs_in_local_path

    def _validate_local_additional_include_config(self, local_path: str, config_info: str = None):
        """Validate local additional include config.

        Note that we will check the file conflicts between each local additional includes and origin code, but
        won't check the file conflicts among local additional includes fo now.
        """
        validation_result = _ValidationResultBuilder.success()
        include_path = self.base_path / local_path
        # if additional include has not supported characters, resolve will fail and raise OSError
        try:
            src_path = include_path.resolve()
        except OSError:
            # no need to include potential yaml file name in error message as it will be covered by
            # validation message construction.
            error_msg = (
                f"Failed to resolve additional include " f"{config_info or local_path} " f"based on {self.base_path}."
            )
            validation_result.append_error(message=error_msg)
            return validation_result

        if not src_path.exists() and not self._is_folder_to_compress(src_path):
            error_msg = f"Unable to find additional include {config_info or local_path}"
            validation_result.append_error(message=error_msg)
            return validation_result

        if len(src_path.parents) == 0:
            error_msg = "Root directory is not supported for additional includes."
            validation_result.append_error(message=error_msg)
            return validation_result

        dst_path = Path(self.resolved_code_path) / src_path.name if self.resolved_code_path else None
        if dst_path:
            if dst_path.is_symlink():
                # if destination path is symbolic link, check if it points to the same file/folder as source path
                if dst_path.resolve() != src_path.resolve():
                    error_msg = f"A symbolic link already exists for additional include {config_info or local_path}."
                    validation_result.append_error(message=error_msg)
                    return validation_result
            elif dst_path.exists():
                error_msg = f"A file already exists for additional include {config_info or local_path}."
                validation_result.append_error(message=error_msg)
        return validation_result

    def validate(self) -> MutableValidationResult:
        validation_result = _ValidationResultBuilder.success()
        for additional_include_config in self.origin_configs:
            validation_result.merge_with(self._validate_additional_include_config(additional_include_config))
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
    def merge_local_code_and_additional_includes(self) -> Path:
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
        for additional_include_local_path in self._get_resolved_additional_include_configs():
            src_path = Path(additional_include_local_path)
            if not src_path.is_absolute():
                src_path = (base_path / additional_include_local_path).resolve()
            dst_path = (tmp_folder_path / src_path.name).resolve()

            root_ignore_file.rebase(src_path.parent)
            if self._is_folder_to_compress(src_path):
                self._resolve_folder_to_compress(
                    additional_include_local_path,
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
                raise ValueError(f"Unable to find additional include {additional_include_local_path}.")

        yield tmp_folder_path.absolute()

        # clean up tmp folder as it can be very disk space consuming
        shutil.rmtree(tmp_folder_path, ignore_errors=True)
        return


class AdditionalIncludesMixin(ComponentCodeMixin):
    @classmethod
    def _get_additional_includes_field_name(cls) -> str:
        """Get the field name for additional includes."""
        return "additional_includes"

    def _get_all_additional_includes_configs(self) -> List:
        """Get all additional include configs."""
        return getattr(self, self._get_additional_includes_field_name(), [])

    def _append_diagnostics_and_check_if_origin_code_reliable_for_local_path_validation(
        self, base_validation_result: MutableValidationResult = None
    ) -> bool:
        is_reliable = super()._append_diagnostics_and_check_if_origin_code_reliable_for_local_path_validation(
            base_validation_result
        )
        additional_includes_obj = self._generate_additional_includes_obj()
        base_validation_result.merge_with(
            additional_includes_obj.validate(), field_name=self._get_additional_includes_field_name()
        )
        # if additional includes is specified, origin code will be merged with additional includes into a temp folder
        # before registered as a code asset, so origin code value is not reliable for local path validation
        if additional_includes_obj.with_includes:
            return False
        return is_reliable

    def _generate_additional_includes_obj(self):
        return AdditionalIncludes(
            base_path=self._get_base_path_for_code(),
            configs=self._get_all_additional_includes_configs(),
            origin_code_value=self._get_origin_code_value(),
        )

    @contextmanager
    def _try_build_local_code(self) -> Optional[Code]:
        """Build final code when origin code is a local code.
        Will merge code path with additional includes into a temp folder if additional includes is specified.
        """
        # will try to merge code and additional includes even if code is None
        with self._generate_additional_includes_obj().merge_local_code_and_additional_includes() as tmp_code_dir:
            if tmp_code_dir is None:
                yield None
            else:
                yield Code(
                    base_path=self._get_base_path_for_code(),
                    path=tmp_code_dir,
                    ignore_file=ComponentIgnoreFile(tmp_code_dir),
                )
