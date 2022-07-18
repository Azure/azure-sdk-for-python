# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import os
import uuid
from typing import TYPE_CHECKING, Tuple, Union, Optional, List, Iterable, Dict, Any, cast
from pathlib import Path
import hashlib
from contextlib import suppress
from colorama import Fore
import pathspec
from tqdm import tqdm, TqdmWarning
import warnings
from platform import system
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor, as_completed

from azure.ai.ml._artifacts._constants import (
    CHUNK_SIZE,
    ARTIFACT_ORIGIN,
    UPLOAD_CONFIRMATION,
    AML_IGNORE_FILE_NAME,
    GIT_IGNORE_FILE_NAME,
    EMPTY_DIRECTORY_ERROR,
    PROCESSES_PER_CORE,
    MAX_CONCURRENCY,
    BLOB_STORAGE_CLIENT_NAME,
    GEN2_STORAGE_CLIENT_NAME,
)
from azure.ai.ml.entities._assets.asset import Asset
from azure.ai.ml._restclient.v2021_10_01.models import (
    DatasetVersionData,
    ModelVersionData,
    ModelVersionResourceArmPaginatedResult,
)
from azure.ai.ml._restclient.v2022_02_01_preview.operations import (
    DataVersionsOperations,
    DataContainersOperations,
    ModelVersionsOperations,
    ModelContainersOperations,
    EnvironmentVersionsOperations,
    EnvironmentContainersOperations,
    ComponentVersionsOperations,
    ComponentContainersOperations,
)
from azure.ai.ml.constants import (
    OrderString,
    MAX_AUTOINCREMENT_ATTEMPTS,
)
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.ai.ml._utils.utils import retry, convert_windows_path_to_unix
from azure.ai.ml._ml_exceptions import ValidationException, ErrorCategory, ErrorTarget
from azure.ai.ml._utils._exception_utils import EmptyDirectoryError

if TYPE_CHECKING:
    from azure.ai.ml.operations import (
        DatasetOperations,
        DataOperations,
        ComponentOperations,
        EnvironmentOperations,
        ModelOperations,
    )

hash_type = type(hashlib.md5())

module_logger = logging.getLogger(__name__)


class AssetNotChangedError(Exception):
    pass


class IgnoreFile(object):
    def __init__(self, file_path: Optional[Union[str, Path]] = None):
        """
        Base class for handling .gitignore and .amlignore files

        :param file_path: Relative path, or absolute path to the ignore file.
        """
        path = Path(file_path).resolve() if file_path else None
        self._path = path
        self._path_spec = None

    def _create_pathspec(self) -> Optional[pathspec.PathSpec]:
        """
        Creates path specification based on ignore file contents
        """
        if not self.exists():
            return None
        with open(self._path, "r") as fh:
            return pathspec.PathSpec.from_lines("gitwildmatch", fh)

    def exists(self) -> bool:
        """
        Checks if ignore file exists
        """
        return self._path and self._path.exists()

    def is_file_excluded(self, file_path: Union[str, Path]) -> bool:
        """
        Checks if given file_path is excluded.

        :param file_path: File path to be checked against ignore file specifications
        """
        if not self.exists():
            return False
        if not self._path_spec:
            self._path_spec = self._create_pathspec()
        file_path = Path(file_path)
        if file_path.is_absolute():
            ignore_dirname = self._path.parent
            if len(os.path.commonprefix([file_path, ignore_dirname])) != len(str(ignore_dirname)):
                return True
            file_path = os.path.relpath(file_path, ignore_dirname)

        return self._path_spec.match_file(file_path)

    @property
    def path(self) -> Union[Path, str]:
        return self._path


class AmlIgnoreFile(IgnoreFile):
    def __init__(self, directory_path: Union[Path, str]):
        file_path = Path(directory_path).joinpath(AML_IGNORE_FILE_NAME)
        super(AmlIgnoreFile, self).__init__(file_path)


class GitIgnoreFile(IgnoreFile):
    def __init__(self, directory_path: Union[Path, str]):
        file_path = Path(directory_path).joinpath(GIT_IGNORE_FILE_NAME)
        super(GitIgnoreFile, self).__init__(file_path)


def get_ignore_file(directory_path: Union[Path, str]) -> Optional[IgnoreFile]:
    """
    Finds and returns IgnoreFile object based on ignore file found in directory_path
    .amlignore takes precedence over .gitignore and if no file is found, an empty
    IgnoreFile object will be returned.

    The ignore file must be in the root directory.

    :param directory_path: Path to the (root) directory where ignore file is located
    """
    aml_ignore = AmlIgnoreFile(directory_path)
    git_ignore = GitIgnoreFile(directory_path)

    if aml_ignore.exists():
        return aml_ignore
    elif git_ignore.exists():
        return git_ignore
    else:
        return IgnoreFile()


def _validate_path(path: Union[str, os.PathLike]) -> None:
    path = Path(path)  # Okay to do this since Path is idempotent
    if not path.is_file() and not path.is_dir():
        msg = "{} not found, local path must point to a file or directory. Path must follow proper formatting for datastore, job or run uri's."
        raise ValidationException(
            message=msg.format(path), no_personal_data_message=msg.format("[path]"), target=ErrorTarget.ASSET
        )


def _parse_name_version(
    name: str = None, version_as_int: bool = True
) -> Tuple[Optional[str], Optional[Union[str, int]]]:
    if not name:
        return None, None

    token_list = name.split(":")
    if len(token_list) == 1:
        return name, None
    else:
        *name, version = token_list
        if version_as_int:
            version = int(version)
        return ":".join(name), version


def _get_file_hash(filename: Union[str, Path], hash: hash_type) -> hash_type:
    with open(str(filename), "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            hash.update(chunk)
    return hash


def _get_dir_hash(directory: Union[str, Path], hash: hash_type, ignore_file: IgnoreFile) -> hash_type:
    dir_contents = Path(directory).iterdir()
    sorted_contents = sorted(dir_contents, key=lambda path: str(path).lower())
    for path in sorted_contents:
        if ignore_file.is_file_excluded(path):
            continue
        hash.update(path.name.encode())
        if os.path.islink(path):  # ensure we're hashing the contents of the linked file
            path = Path(os.readlink(convert_windows_path_to_unix(path)))
        if path.is_file():
            hash = _get_file_hash(path, hash)
        elif path.is_dir():
            hash = _get_dir_hash(path, hash, ignore_file)
    return hash


def _build_metadata_dict(name: str, version: str) -> Dict[str, str]:
    """
    Build metadata dictionary to attach to uploaded data.

    Metadata includes an upload confirmation field, and for code uploads only,
    the name and version of the code asset being created for that data.
    """
    if name:
        linked_asset_arm_id = {"name": name, "version": version}
    else:
        msg = "'name' cannot be NoneType for asset artifact upload."
        raise ValidationException(
            message=msg, no_personal_data_message=msg, target=ErrorTarget.ASSET, error_category=ErrorCategory.USER_ERROR
        )

    metadata_dict = {**UPLOAD_CONFIRMATION, **linked_asset_arm_id}
    return metadata_dict


def get_object_hash(path: Union[str, Path], ignore_file: IgnoreFile = IgnoreFile()) -> str:
    hash = hashlib.md5(b"Initialize for october 2021 AML CLI version")
    if Path(path).is_dir():
        object_hash = _get_dir_hash(directory=path, hash=hash, ignore_file=ignore_file)
    else:
        if os.path.islink(path):  # ensure we're hashing the contents of the linked file
            path = Path(os.readlink(convert_windows_path_to_unix(path)))
        object_hash = _get_file_hash(filename=path, hash=hash)
    return str(object_hash.hexdigest())


def traverse_directory(
    root: str, files: List[str], source: str, prefix: str, ignore_file: IgnoreFile = IgnoreFile()
) -> Iterable[Tuple[str, Union[str, Any]]]:
    """
    Enumerate all files in the given directory and compose paths for them to be uploaded to in the remote storage.
    e.g. [/mnt/c/Users/dipeck/upload_files/my_file1.txt, /mnt/c/Users/dipeck/upload_files/my_file2.txt] -->
        [(/mnt/c/Users/dipeck/upload_files/my_file1.txt, LocalUpload/<guid>/upload_files/my_file1.txt),
        (/mnt/c/Users/dipeck/upload_files/my_file2.txt, LocalUpload/<guid>/upload_files/my_file2.txt))]

    :param root: Root directory path
    :type root: str
    :param files: List of all file paths in the directory
    :type files: List[str]
    :param source: Local path to project directory
    :type source: str
    :param prefix: Remote upload path for project directory (e.g. LocalUpload/<guid>/project_dir)
    :type prefix: str
    :param ignore_file: The .amlignore or .gitignore file in the project directory
    :type ignore_file: azure.ai.ml._utils._asset_utils.IgnoreFile
    :return: Zipped list of tuples representing the local path and remote destination path for each file
    :rtype: Iterable[Tuple[str, Union[str, Any]]]
    """
    # Normalize Windows paths
    root = convert_windows_path_to_unix(root)
    source = convert_windows_path_to_unix(source)
    working_dir = convert_windows_path_to_unix(os.getcwd())
    project_dir = root[len(str(working_dir)) :] + "/"
    file_paths = [
        convert_windows_path_to_unix(os.path.join(root, name))
        for name in files
        if not ignore_file.is_file_excluded(os.path.join(root, name))
    ]  # get all files not excluded by the ignore file
    file_paths_including_links = {fp: None for fp in file_paths}

    for path in file_paths:
        target_prefix = ""
        symlink_prefix = ""

        # check for symlinks to get their true paths
        if os.path.islink(path):
            target_absolute_path = os.path.join(working_dir, os.readlink(path))
            target_prefix = "/".join([root, str(os.readlink(path))]).replace(project_dir, "/")

            # follow and add child links if the directory is a symlink
            if os.path.isdir(target_absolute_path):
                symlink_prefix = path.replace(root + "/", "")

                for r, _, f in os.walk(target_absolute_path, followlinks=True):
                    target_file_paths = {
                        os.path.join(r, name): symlink_prefix + os.path.join(r, name).replace(target_prefix, "")
                        for name in f
                    }  # for each symlink, store its target_path as key and symlink path as value
                    file_paths_including_links.update(target_file_paths)  # Add discovered symlinks to file paths list
            else:
                file_path_info = {
                    target_absolute_path: path.replace(root + "/", "")
                }  # for each symlink, store its target_path as key and symlink path as value
                file_paths_including_links.update(file_path_info)  # Add discovered symlinks to file paths list
            del file_paths_including_links[path]  # Remove original symlink entry now that detailed entry has been added
        else:
            pass

    file_paths = sorted(
        file_paths_including_links
    )  # sort files to keep consistent order in case of repeat upload comparisons
    dir_parts = [os.path.relpath(root, source) for _ in file_paths]
    dir_parts = ["" if dir_part == "." else dir_part + "/" for dir_part in dir_parts]
    blob_paths = []

    for (dir_part, name) in zip(dir_parts, file_paths):
        if file_paths_including_links.get(
            name
        ):  # for symlinks, use symlink name and structure in directory to create remote upload path
            blob_path = prefix + dir_part + file_paths_including_links.get(name)
        else:
            blob_path = prefix + dir_part + name.replace(root + "/", "")
        blob_paths.append(blob_path)

    return zip(file_paths, blob_paths)


def generate_asset_id(asset_hash: str, include_directory=True) -> str:
    asset_id = asset_hash or str(uuid.uuid4())
    if include_directory:
        asset_id = "/".join((ARTIFACT_ORIGIN, asset_id))
    return asset_id


def get_directory_size(root: os.PathLike) -> Tuple[int, Dict[str, int]]:
    """Returns total size of a directory and a dictionary itemizing each sub-path and its size."""
    total_size = 0
    size_list = {}
    for dirpath, _, filenames in os.walk(root, followlinks=True):
        for name in filenames:
            full_path = os.path.join(dirpath, name)
            if not os.path.islink(full_path):
                path_size = os.path.getsize(full_path)
            else:
                path_size = os.path.getsize(
                    os.readlink(convert_windows_path_to_unix(full_path))
                )  # ensure we're counting the size of the linked file
            size_list[full_path] = path_size
            total_size += path_size
    return total_size, size_list


def upload_file(
    storage_client: Union["BlobStorageClient", "Gen2StorageClient"],
    source: str,
    dest: str = None,
    msg: Optional[str] = None,
    size: int = 0,
    show_progress: Optional[bool] = None,
    in_directory: bool = False,
    callback: Any = None,
) -> None:
    """
    Upload a single file to remote storage.

    :param storage_client: Storage client object
    :type storage_client: Union[azure.ai.ml._artifacts._blob_storage_helper.BlobStorageClient, azure.ai.ml._artifacts._gen2_storage_helper.Gen2StorageClient]
    :param source: Local path to project directory
    :type source: str
    :param dest: Remote upload path for project directory (e.g. LocalUpload/<guid>/project_dir)
    :type dest: str
    :param msg: Message to be shown with progress bar (e.g. "Uploading <source>")
    :type msg: str
    :param size: Size of the file in bytes
    :type size: int
    :param show_progress: Whether to show progress bar or not
    :type show_progress: bool
    :param in_directory: Whether the file is part of a directory of files
    :type in_directory: bool
    :param callback: Callback to progress bar
    :type callback: Any
    :return: None
    """
    validate_content = size > 0  # don't do checksum for empty files

    if (
        type(storage_client).__name__ == GEN2_STORAGE_CLIENT_NAME
    ):  # Only for Gen2StorageClient, Blob Storage doesn't have true directories
        if in_directory:
            storage_client.file_client = storage_client.sub_directory_client.create_file(source.split("/")[-1])
        else:
            storage_client.file_client = storage_client.directory_client.create_file(source.split("/")[-1])

    with open(source, "rb") as data:
        if show_progress and not in_directory:
            file_size, _ = get_directory_size(source)
            file_size_in_mb = file_size / 10**6
            if file_size_in_mb < 1:
                msg += Fore.GREEN + " (< 1 MB)"
            else:
                msg += Fore.GREEN + f" ({round(file_size_in_mb, 2)} MBs)"
            cntx_manager = FileUploadProgressBar(msg=msg)
        else:
            cntx_manager = suppress()

        with cntx_manager as c:
            callback = c.update_to if (show_progress and not in_directory) else None
            if type(storage_client).__name__ == GEN2_STORAGE_CLIENT_NAME:
                storage_client.file_client.upload_data(
                    data=data.read(),
                    overwrite=True,
                    validate_content=validate_content,
                    raw_response_hook=callback,
                    max_concurrency=MAX_CONCURRENCY,
                )
            elif type(storage_client).__name__ == BLOB_STORAGE_CLIENT_NAME:
                storage_client.container_client.upload_blob(
                    name=dest,
                    data=data,
                    validate_content=validate_content,
                    overwrite=storage_client.overwrite,
                    raw_response_hook=callback,
                    max_concurrency=MAX_CONCURRENCY,
                )

    storage_client.uploaded_file_count += 1


def upload_directory(
    storage_client: Union["BlobStorageClient", "Gen2StorageClient"],
    source: str,
    dest: str,
    msg: str,
    show_progress: bool,
    ignore_file: IgnoreFile,
) -> None:
    """
    Upload directory to remote storage.

    :param storage_client: Storage client object
    :type storage_client: Union[azure.ai.ml._artifacts._blob_storage_helper.BlobStorageClient, azure.ai.ml._artifacts._gen2_storage_helper.Gen2StorageClient]
    :param source: Local path to project directory
    :type source: str
    :param dest: Remote upload path for project directory (e.g. LocalUpload/<guid>/project_dir)
    :type dest: str
    :param msg: Message to be shown with progress bar (e.g. "Uploading <source>")
    :type msg: str
    :param show_progress: Whether to show progress bar or not
    :type show_progress: bool
    :param ignore_file: The .amlignore or .gitignore file in the project directory
    :type ignore_file: azure.ai.ml._utils._asset_utils.IgnoreFile
    :return: None
    """
    source_path = Path(source).resolve()
    prefix = "" if dest == "" else dest + "/"
    prefix += os.path.basename(source_path) + "/"

    if (
        type(storage_client).__name__ == GEN2_STORAGE_CLIENT_NAME
    ):  # Only for Gen2StorageClient, Blob Storage doesn't have true directories
        storage_client.sub_directory_client = storage_client.directory_client.create_sub_directory(
            prefix.strip("/").split("/")[-1]
        )

    # Enumerate all files in the given directory and compose paths for them to be uploaded to in the remote storage
    upload_paths = []
    size_dict = {}
    total_size = 0
    for root, _, files in os.walk(source_path, followlinks=True):
        upload_paths += list(traverse_directory(root, files, source_path, prefix, ignore_file=ignore_file))

    # Get each file's size for progress bar tracking
    for path, _ in upload_paths:
        if os.path.islink(path):
            path_size = os.path.getsize(
                os.readlink(convert_windows_path_to_unix(path))
            )  # ensure we're counting the size of the linked file
        else:
            path_size = os.path.getsize(path)
        size_dict[path] = path_size
        total_size += path_size

    upload_paths = sorted(upload_paths)
    if len(upload_paths) == 0:
        raise EmptyDirectoryError(
            message=EMPTY_DIRECTORY_ERROR.format(source),
            no_personal_data_message=msg.format("[source]"),
            target=ErrorTarget.ARTIFACT,
            error_category=ErrorCategory.USER_ERROR,
        )
    storage_client.total_file_count = len(upload_paths)

    if (
        type(storage_client).__name__ == BLOB_STORAGE_CLIENT_NAME
    ):  # Only for Gen2StorageClient, Blob Storage doesn't have true directories
        # Only for BlobStorageClient
        # Azure Blob doesn't allow metadata setting at the directory level, so the first
        # file in the directory is designated as the file where the confirmation metadata
        # will be added at the end of the upload.
        storage_client.indicator_file = upload_paths[0][1]
        storage_client.check_blob_exists()

    # Submit paths to workers for upload
    num_cores = int(cpu_count()) * PROCESSES_PER_CORE
    with ThreadPoolExecutor(max_workers=num_cores) as ex:
        futures_dict = {
            ex.submit(
                upload_file,
                storage_client=storage_client,
                source=src,
                dest=dest,
                size=size_dict.get(src),
                in_directory=True,
                show_progress=show_progress,
            ): (src, dest)
            for (src, dest) in upload_paths
        }
        if show_progress:
            warnings.simplefilter("ignore", category=TqdmWarning)
            msg += f" ({round(total_size/10**6, 2)} MBs)"
            ascii = system() == "Windows"  # Default unicode progress bar doesn't display well on Windows
            with tqdm(total=total_size, desc=msg, ascii=ascii) as pbar:
                for future in as_completed(futures_dict):
                    file_path_name = futures_dict[future][0]
                    pbar.update(size_dict.get(file_path_name) or 0)


@retry(
    exceptions=ResourceExistsError,
    failure_msg="Asset creation exceeded maximum retries.",
    logger=module_logger,
    max_attempts=MAX_AUTOINCREMENT_ATTEMPTS,
)
def _create_or_update_autoincrement(
    name: str,
    body: Any,
    version_operation: Any,
    container_operation: Any,
    resource_group_name: str,
    workspace_name: str,
    **kwargs,
) -> Any:
    try:
        container = container_operation.get(
            name=name,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
            **kwargs,
        )
        version = container.properties.next_version

    except ResourceNotFoundError:
        version = "1"

    result = version_operation.create_or_update(
        name=name,
        version=version,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name,
        body=body,
        **kwargs,
    )
    return result


def _get_latest(
    asset_name: str,
    version_operation: Any,
    resource_group_name: str,
    workspace_name: str,
    order_by: str = OrderString.CREATED_AT_DESC,
    **kwargs,
) -> Union[ModelVersionData, DatasetVersionData]:
    """Returns the latest version of the asset with the given name.

    Latest is defined as the most recently created, not the most recently updated.
    """
    try:
        latest = version_operation.list(
            name=asset_name,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
            order_by=order_by,
            top=1,
            **kwargs,
        ).next()
    except StopIteration:
        latest = None

    if latest and isinstance(latest, ModelVersionResourceArmPaginatedResult):
        # Data list return object doesn't require this since its elements are already DatasetVersionResources
        latest = cast(ModelVersionData, latest)
    if not latest:
        raise ResourceNotFoundError(f"Asset {asset_name} does not exist in workspace {workspace_name}.")

    return latest


def _archive_or_restore(
    asset_operations: Union["DataOperations", "EnvironmentOperations", "ModelOperations", "ComponentOperations"],
    version_operation: Union[
        "DataVersionsOperations",
        "EnvironmentVersionsOperations",
        "ModelVersionsOperations",
        "ComponentVersionsOperations",
    ],
    container_operation: Union[
        "DataContainersOperations",
        "EnvironmentContainersOperations",
        "ModelContainersOperations",
        "ComponentContainersOperations",
    ],
    is_archived: bool,
    name: str,
    version: str = None,
    label: str = None,
) -> None:

    resource_group_name = asset_operations._operation_scope._resource_group_name
    workspace_name = asset_operations._workspace_name
    if version and label:
        msg = "Cannot specify both version and label."
        raise ValidationException(
            message=msg, no_personal_data_message=msg, target=ErrorTarget.ASSET, error_category=ErrorCategory.USER_ERROR
        )
    if label:
        version = _resolve_label_to_asset(asset_operations, name, label).version

    if version:
        version_resource = version_operation.get(
            name=name,
            version=version,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
        )
        version_resource.properties.is_archived = is_archived
        version_operation.create_or_update(
            name=name,
            version=version,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
            body=version_resource,
        )
    else:
        container_resource = container_operation.get(
            name=name,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
        )
        container_resource.properties.is_archived = is_archived
        container_operation.create_or_update(
            name=name,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
            body=container_resource,
        )


def _resolve_label_to_asset(
    assetOperations: Union[
        "DatasetOperations", "DataOperations", "ComponentOperations", "EnvironmentOperations", "ModelOperations"
    ],
    name: str,
    label: str,
) -> Asset:
    """Returns the asset referred to by the given label.

    Throws if label does not refer to a version of the named asset
    """

    resolver = assetOperations._managed_label_resolver.get(label, None)
    if not resolver:
        msg = 'No version corresponds to label "{}" for asset {}'
        raise ValidationException(
            message=msg.format(label, name),
            no_personal_data_message=msg.format("[label]", "[name]"),
            target=ErrorTarget.ASSET,
        )
    return resolver(name)


class FileUploadProgressBar(tqdm):
    def __init__(self, msg: str = None):
        warnings.simplefilter("ignore", category=TqdmWarning)
        ascii = system() == "Windows"  # Default unicode progress bar doesn't display well on Windows
        super().__init__(unit="B", unit_scale=True, desc=msg, ascii=ascii)

    def update_to(self, response):
        current = response.context["upload_stream_current"]
        self.total = response.context["data_stream_total"]
        if current:
            self.update(current - self.n)


class DirectoryUploadProgressBar(tqdm):
    def __init__(self, dir_size: int, msg: str = None):
        super().__init__(unit="B", unit_scale=True, desc=msg, colour="green")
        self.total = dir_size
        self.completed = 0

    def update_to(self, response):
        current = None
        if response.context["upload_stream_current"]:
            current = response.context["upload_stream_current"] + self.completed
            self.completed = current
        if current:
            self.update(current - self.n)


def _is_local_path(path: Union[os.PathLike, str]) -> bool:
    path = Path(path)
    return path.exists()
