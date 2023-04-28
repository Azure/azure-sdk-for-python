# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access,too-many-lines

import hashlib
import logging
import os
import uuid
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import suppress
from multiprocessing import cpu_count
from os import PathLike
from pathlib import Path
from platform import system
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Tuple, Union, cast

from colorama import Fore
from tqdm import TqdmWarning, tqdm

from azure.ai.ml._restclient.v2023_04_01.models import PendingUploadRequestDto
from azure.ai.ml._artifacts._constants import (
    AML_IGNORE_FILE_NAME,
    ARTIFACT_ORIGIN,
    BLOB_STORAGE_CLIENT_NAME,
    CHUNK_SIZE,
    DEFAULT_CONNECTION_TIMEOUT,
    EMPTY_DIRECTORY_ERROR,
    GEN2_STORAGE_CLIENT_NAME,
    GIT_IGNORE_FILE_NAME,
    MAX_CONCURRENCY,
    PROCESSES_PER_CORE,
    UPLOAD_CONFIRMATION,
    WORKSPACE_MANAGED_DATASTORE,
    WORKSPACE_MANAGED_DATASTORE_WITH_SLASH,
    AUTO_DELETE_SETTING_NOT_ALLOWED_ERROR_NO_PERSONAL_DATA,
    INVALID_MANAGED_DATASTORE_PATH_ERROR_NO_PERSONAL_DATA,
)
from azure.ai.ml._restclient.v2022_05_01.models import (
    DataVersionBaseData,
    ModelVersionData,
    ModelVersionResourceArmPaginatedResult,
)
from azure.ai.ml._restclient.v2022_02_01_preview.operations import (  # pylint: disable = unused-import
    ComponentContainersOperations,
    ComponentVersionsOperations,
    DataContainersOperations,
    DataVersionsOperations,
    EnvironmentContainersOperations,
    EnvironmentVersionsOperations,
    ModelContainersOperations,
    ModelVersionsOperations,
)
from azure.ai.ml._utils._pathspec import GitWildMatchPattern, normalize_file
from azure.ai.ml._utils.utils import convert_windows_path_to_unix, retry, snake_to_camel
from azure.ai.ml.constants._common import MAX_AUTOINCREMENT_ATTEMPTS, OrderString
from azure.ai.ml.entities._assets.asset import Asset
from azure.ai.ml.exceptions import (
    AssetPathException,
    EmptyDirectoryError,
    ErrorCategory,
    ErrorTarget,
    ValidationErrorType,
    ValidationException,
)
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError

if TYPE_CHECKING:
    from azure.ai.ml.operations import ComponentOperations, DataOperations, EnvironmentOperations, ModelOperations

hash_type = type(hashlib.md5())  # nosec

module_logger = logging.getLogger(__name__)


class AssetNotChangedError(Exception):
    pass


class IgnoreFile(object):
    def __init__(self, file_path: Optional[Union[str, Path]] = None):
        """Base class for handling .gitignore and .amlignore files.

        :param file_path: Relative path, or absolute path to the ignore file.
        """
        path = Path(file_path).resolve() if file_path else None
        self._path = path
        self._path_spec = None

    def exists(self) -> bool:
        """Checks if ignore file exists."""
        return self._file_exists()

    def _file_exists(self) -> bool:
        return self._path and self._path.exists()

    @property
    def base_path(self) -> Path:
        return self._path.parent

    def _get_ignore_list(self) -> List[str]:
        """Get ignore list from ignore file contents."""
        if not self.exists():
            return []
        if self._file_exists():
            with open(self._path, "r") as fh:
                return [line.rstrip() for line in fh if line]
        return []

    def _create_pathspec(self) -> List[GitWildMatchPattern]:
        """Creates path specification based on ignore list."""
        return [GitWildMatchPattern(ignore) for ignore in self._get_ignore_list()]

    def _get_rel_path(self, file_path: Union[str, Path]) -> Optional[str]:
        """Get relative path of given file_path."""
        file_path = Path(file_path).absolute()
        try:
            # use os.path.relpath instead of Path.relative_to in case file_path is not a child of self.base_path
            return os.path.relpath(file_path, self.base_path)
        except ValueError:
            # 2 paths are on different drives
            return None

    def is_file_excluded(self, file_path: Union[str, Path]) -> bool:
        """Checks if given file_path is excluded.

        :param file_path: File path to be checked against ignore file specifications
        """
        # TODO: current design of ignore file can't distinguish between files and directories of the same name
        if self._path_spec is None:
            self._path_spec = self._create_pathspec()
        if not self._path_spec:
            return False
        file_path = self._get_rel_path(file_path)
        if file_path is None:
            return True

        norm_file = normalize_file(file_path)
        matched = False
        for pattern in self._path_spec:
            if pattern.include is not None:
                if pattern.match_file(norm_file) is not None:
                    matched = pattern.include

        return matched

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
    """Finds and returns IgnoreFile object based on ignore file found in directory_path.

    .amlignore takes precedence over .gitignore and if no file is found, an empty
    IgnoreFile object will be returned.

    The ignore file must be in the root directory.

    :param directory_path: Path to the (root) directory where ignore file is located
    """
    aml_ignore = AmlIgnoreFile(directory_path)
    git_ignore = GitIgnoreFile(directory_path)

    if aml_ignore.exists():
        return aml_ignore
    if git_ignore.exists():
        return git_ignore
    return IgnoreFile()


def _validate_path(path: Union[str, os.PathLike], _type: str) -> None:
    path = Path(path)  # Okay to do this since Path is idempotent
    if not path.is_file() and not path.is_dir():
        raise ValidationException(
            message=f"No such file or directory: {path}",
            target=_type,
            error_type=ValidationErrorType.FILE_OR_FOLDER_NOT_FOUND,
            no_personal_data_message="No such file or directory",
            error_category=ErrorCategory.USER_ERROR,
        )


def _parse_name_version(
    name: Optional[str] = None, version_as_int: bool = True
) -> Tuple[Optional[str], Optional[Union[str, int]]]:
    if not name:
        return None, None

    token_list = name.split(":")
    if len(token_list) == 1:
        return name, None
    *name, version = token_list
    if version_as_int:
        version = int(version)
    return ":".join(name), version


def _get_file_hash(filename: Union[str, Path], _hash: hash_type) -> hash_type:
    with open(str(filename), "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            _hash.update(chunk)
    return _hash


def _get_dir_hash(directory: Union[str, Path], _hash: hash_type, ignore_file: IgnoreFile) -> hash_type:
    dir_contents = Path(directory).iterdir()
    sorted_contents = sorted(dir_contents, key=lambda path: str(path).lower())
    for path in sorted_contents:
        if ignore_file.is_file_excluded(path):
            continue
        _hash.update(path.name.encode())
        if os.path.islink(path):  # ensure we're hashing the contents of the linked file
            path = Path(os.readlink(convert_windows_path_to_unix(path)))
        if path.is_file():
            _hash = _get_file_hash(path, _hash)
        elif path.is_dir():
            _hash = _get_dir_hash(path, _hash, ignore_file)
    return _hash


def _build_metadata_dict(name: str, version: str) -> Dict[str, str]:
    """Build metadata dictionary to attach to uploaded data.

    Metadata includes an upload confirmation field, and for code uploads only, the name and version of the code asset
    being created for that data.
    """
    if name:
        linked_asset_arm_id = {"name": name, "version": version}
    else:
        msg = "'name' cannot be NoneType for asset artifact upload."
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.ASSET,
            error_category=ErrorCategory.USER_ERROR,
            error_type=ValidationErrorType.INVALID_VALUE,
        )

    metadata_dict = {**UPLOAD_CONFIRMATION, **linked_asset_arm_id}
    return metadata_dict


def get_object_hash(path: Union[str, Path], ignore_file: IgnoreFile = IgnoreFile()) -> str:
    _hash = hashlib.md5(b"Initialize for october 2021 AML CLI version")  # nosec
    if Path(path).is_dir():
        object_hash = _get_dir_hash(directory=path, _hash=_hash, ignore_file=ignore_file)
    else:
        if os.path.islink(path):  # ensure we're hashing the contents of the linked file
            path = Path(os.readlink(convert_windows_path_to_unix(path)))
        object_hash = _get_file_hash(filename=path, _hash=_hash)
    return str(object_hash.hexdigest())


def get_content_hash_version():
    return 202208


def get_content_hash(path: Union[str, Path], ignore_file: IgnoreFile = IgnoreFile()) -> str:
    """Generating sha256 hash for file/folder, e.g. Code snapshot fingerprints to prevent tampering.
    The process of hashing is:
    1. If it's a link, get the actual path of the link.
    2. If it's a file, append file content.
    3. If it's a folder:
        1. list all files under the folder
        2. convert file count to str and append to hash
        3. sort the files by lower case of relative path
        4. for each file append '#'+relative path+'#' and file size to hash
        5. do another iteration on file list to append each files content to hash.
        The example of absolute path to relative path mapping is:
        [
            ('/mnt/c/codehash/code/file1.txt', 'file1.txt'),
            ('/mnt/c/codehash/code/folder1/file1.txt', 'folder1/file1.txt'),
            ('/mnt/c/codehash/code/Folder2/file1.txt', 'Folder2/file1.txt'),
            ('/mnt/c/codehash/code/Folder2/folder1/file1.txt', 'Folder2/folder1/file1.txt')
        ]
    4. Hash the content and convert to hex digest string.
    """
    # DO NOT change this function unless you change the verification logic together
    actual_path = path
    if os.path.islink(path):
        link_path = os.readlink(path)
        actual_path = link_path if os.path.isabs(link_path) else os.path.join(os.path.dirname(path), link_path)
    if os.path.isdir(actual_path):
        return _get_file_list_content_hash(_get_upload_files_from_folder(actual_path, ignore_file=ignore_file))
    if os.path.isfile(actual_path):
        return _get_file_list_content_hash([(actual_path, Path(actual_path).name)])
    return None


def _get_upload_files_from_folder(path: Union[str, Path], ignore_file: IgnoreFile = IgnoreFile()) -> List[str]:
    upload_paths = []
    for root, _, files in os.walk(path, followlinks=True):
        upload_paths += list(traverse_directory(root, files, Path(path).resolve(), "", ignore_file=ignore_file))
    return upload_paths


def _get_file_list_content_hash(file_list) -> str:
    # file_list is a list of tuples, (absolute_path, relative_path)

    _hash = hashlib.sha256()
    # Add file count to the hash and add '#' around file name then add each file's size to avoid collision like:
    # Case 1:
    # 'a.txt' with contents 'a'
    # 'b.txt' with contents 'b'
    #
    # Case 2:
    # cspell:disable-next-line
    # 'a.txt' with contents 'ab.txtb'
    _hash.update(str(len(file_list)).encode())
    # Sort by "destination" path, since in this function destination prefix is empty and keep the link name in path.
    for file_path, file_name in sorted(file_list, key=lambda x: str(x[1]).lower()):
        _hash.update(("#" + file_name + "#").encode())
        _hash.update(str(os.path.getsize(file_path)).encode())
    for file_path, file_name in sorted(file_list, key=lambda x: str(x[1]).lower()):
        _hash = _get_file_hash(file_path, _hash)
    return str(_hash.hexdigest())


def traverse_directory(
    root: str,
    files: List[str],
    source: str,
    prefix: str,
    ignore_file: IgnoreFile = IgnoreFile(),
) -> Iterable[Tuple[str, Union[str, Any]]]:
    """Enumerate all files in the given directory and compose paths for them to be uploaded to in the remote storage.
    e.g.

    [/mnt/c/Users/dipeck/upload_files/my_file1.txt,
    /mnt/c/Users/dipeck/upload_files/my_file2.txt] -->

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

    file_paths = sorted(
        file_paths_including_links
    )  # sort files to keep consistent order in case of repeat upload comparisons
    dir_parts = [convert_windows_path_to_unix(os.path.relpath(root, source)) for _ in file_paths]
    dir_parts = ["" if dir_part == "." else dir_part + "/" for dir_part in dir_parts]
    blob_paths = []

    for dir_part, name in zip(dir_parts, file_paths):
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


def get_directory_size(root: os.PathLike, ignore_file: IgnoreFile = IgnoreFile(None)) -> Tuple[int, Dict[str, int]]:
    """Returns total size of a directory and a dictionary itemizing each sub- path and its size.

    If an optional ignore_file argument is provided, then files specified in the ignore file are not included in the
    directory size calculation.
    """
    total_size = 0
    size_list = {}
    for dirpath, _, filenames in os.walk(root, followlinks=True):
        for name in filenames:
            full_path = os.path.join(dirpath, name)
            # Don't count files that are excluded by an ignore file
            if ignore_file.is_file_excluded(full_path):
                continue
            if not os.path.islink(full_path):
                path_size = os.path.getsize(full_path)
            else:
                # ensure we're counting the size of the linked file
                # os.readlink returns a file path relative to dirpath, and must be
                # re-joined to get a workable result
                path_size = os.path.getsize(os.path.join(dirpath, os.readlink(convert_windows_path_to_unix(full_path))))
            size_list[full_path] = path_size
            total_size += path_size
    return total_size, size_list


def upload_file(
    storage_client: Union["BlobStorageClient", "Gen2StorageClient"],
    source: str,
    dest: Optional[str] = None,
    msg: Optional[str] = None,
    size: int = 0,
    show_progress: Optional[bool] = None,
    in_directory: bool = False,
    callback: Optional[Any] = None,
) -> None:
    """Upload a single file to remote storage.

    :param storage_client: Storage client object
    :type storage_client: Union[
        azure.ai.ml._artifacts._blob_storage_helper.BlobStorageClient,
        azure.ai.ml._artifacts._gen2_storage_helper.Gen2StorageClient]
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
            storage_client.temp_sub_directory_client = None
            file_name_tail = dest.split(os.path.sep)[-1]
            # Indexing from 2 because the first two parts of the remote path will always be LocalUpload/<asset_id>
            all_sub_folders = dest.split(os.path.sep)[2:-1]

            # Create remote directories for each nested directory if file is in a nested directory
            for sub_folder in all_sub_folders:
                if storage_client.temp_sub_directory_client:
                    storage_client.temp_sub_directory_client = (
                        storage_client.temp_sub_directory_client.create_sub_directory(sub_folder)
                    )
                else:
                    storage_client.temp_sub_directory_client = storage_client.directory_client.create_sub_directory(
                        sub_folder
                    )

            storage_client.file_client = storage_client.temp_sub_directory_client.create_file(file_name_tail)
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
                    connection_timeout=DEFAULT_CONNECTION_TIMEOUT,
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
    """Upload directory to remote storage.

    :param storage_client: Storage client object
    :type storage_client: Union[
        azure.ai.ml._artifacts._blob_storage_helper.BlobStorageClient,
        azure.ai.ml._artifacts._gen2_storage_helper.Gen2StorageClient]
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
            is_windows = system() == "Windows"  # Default unicode progress bar doesn't display well on Windows
            with tqdm(total=total_size, desc=msg, ascii=is_windows) as pbar:
                for future in as_completed(futures_dict):
                    future.result()  # access result to propagate any exceptions
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


def _get_next_version_from_container(
    name: str,
    container_operation: Any,
    resource_group_name: str,
    workspace_name: str,
    registry_name: str = None,
    **kwargs,
) -> str:
    try:
        container = (
            container_operation.get(
                name=name,
                resource_group_name=resource_group_name,
                registry_name=registry_name,
                **kwargs,
            )
            if registry_name
            else container_operation.get(
                name=name,
                resource_group_name=resource_group_name,
                workspace_name=workspace_name,
                **kwargs,
            )
        )
        version = container.properties.next_version

    except ResourceNotFoundError:
        version = "1"
    return version


def _get_latest_version_from_container(
    asset_name: str,
    container_operation: Any,
    resource_group_name: str,
    workspace_name: Optional[str] = None,
    registry_name: Optional[str] = None,
    **kwargs,
) -> str:
    try:
        container = (
            container_operation.get(
                name=asset_name,
                resource_group_name=resource_group_name,
                registry_name=registry_name,
                **kwargs,
            )
            if registry_name
            else container_operation.get(
                name=asset_name,
                resource_group_name=resource_group_name,
                workspace_name=workspace_name,
                **kwargs,
            )
        )
        version = container.properties.latest_version

    except ResourceNotFoundError:
        message = (
            f"Asset {asset_name} does not exist in registry {registry_name}."
            if registry_name
            else f"Asset {asset_name} does not exist in workspace {workspace_name}."
        )
        no_personal_data_message = (
            "Asset {asset_name} does not exist in registry {registry_name}."
            if registry_name
            else "Asset {asset_name} does not exist in workspace {workspace_name}."
        )
        raise ValidationException(
            message=message,
            no_personal_data_message=no_personal_data_message,
            target=ErrorTarget.ASSET,
            error_category=ErrorCategory.USER_ERROR,
            error_type=ValidationErrorType.RESOURCE_NOT_FOUND,
        )
    return version


def _get_latest(
    asset_name: str,
    version_operation: Any,
    resource_group_name: str,
    workspace_name: Optional[str] = None,
    registry_name: Optional[str] = None,
    order_by: str = OrderString.CREATED_AT_DESC,
    **kwargs,
) -> Union[ModelVersionData, DataVersionBaseData]:
    """Returns the latest version of the asset with the given name.

    Latest is defined as the most recently created, not the most recently updated.
    """
    result = (
        version_operation.list(
            name=asset_name,
            resource_group_name=resource_group_name,
            registry_name=registry_name,
            order_by=order_by,
            top=1,
            **kwargs,
        )
        if registry_name
        else version_operation.list(
            name=asset_name,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
            order_by=order_by,
            top=1,
            **kwargs,
        )
    )
    try:
        latest = result.next()
    except StopIteration:
        latest = None

    if latest and isinstance(latest, ModelVersionResourceArmPaginatedResult):
        # Data list return object doesn't require this since its elements are already DatasetVersionResources
        latest = cast(ModelVersionData, latest)
    if not latest:
        message = (
            f"Asset {asset_name} does not exist in registry {registry_name}."
            if registry_name
            else f"Asset {asset_name} does not exist in workspace {workspace_name}."
        )
        no_personal_data_message = (
            "Asset {asset_name} does not exist in registry {registry_name}."
            if registry_name
            else "Asset {asset_name} does not exist in workspace {workspace_name}."
        )
        raise ValidationException(
            message=message,
            no_personal_data_message=no_personal_data_message,
            target=ErrorTarget.ASSET,
            error_category=ErrorCategory.USER_ERROR,
            error_type=ValidationErrorType.RESOURCE_NOT_FOUND,
        )
    return latest


def _archive_or_restore(
    asset_operations: Union[
        "DataOperations",
        "EnvironmentOperations",
        "ModelOperations",
        "ComponentOperations",
    ],
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
    version: Optional[str] = None,
    label: Optional[str] = None,
) -> None:
    resource_group_name = asset_operations._operation_scope._resource_group_name
    workspace_name = asset_operations._workspace_name
    registry_name = asset_operations._registry_name
    if version and label:
        msg = "Cannot specify both version and label."
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.ASSET,
            error_category=ErrorCategory.USER_ERROR,
            error_type=ValidationErrorType.RESOURCE_NOT_FOUND,
        )
    if label:
        version = _resolve_label_to_asset(asset_operations, name, label).version

    if version:
        version_resource = (
            version_operation.get(
                name=name,
                version=version,
                resource_group_name=resource_group_name,
                registry_name=registry_name,
            )
            if registry_name
            else version_operation.get(
                name=name,
                version=version,
                resource_group_name=resource_group_name,
                workspace_name=workspace_name,
            )
        )
        version_resource.properties.is_archived = is_archived
        version_operation.begin_create_or_update(  # pylint: disable=expression-not-assigned
            name=name,
            version=version,
            resource_group_name=resource_group_name,
            registry_name=registry_name,
            body=version_resource,
        ) if registry_name else version_operation.create_or_update(
            name=name,
            version=version,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
            body=version_resource,
        )
    else:
        container_resource = (
            container_operation.get(
                name=name,
                resource_group_name=resource_group_name,
                registry_name=registry_name,
            )
            if registry_name
            else container_operation.get(
                name=name,
                resource_group_name=resource_group_name,
                workspace_name=workspace_name,
            )
        )
        container_resource.properties.is_archived = is_archived
        container_operation.create_or_update(  # pylint: disable=expression-not-assigned
            name=name,
            resource_group_name=resource_group_name,
            registry_name=registry_name,
            body=container_resource,
        ) if registry_name else container_operation.create_or_update(
            name=name,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
            body=container_resource,
        )


def _resolve_label_to_asset(
    assetOperations: Union[
        "DataOperations",
        "ComponentOperations",
        "EnvironmentOperations",
        "ModelOperations",
    ],
    name: str,
    label: str,
) -> Asset:
    """Returns the asset referred to by the given label.

    Throws if label does not refer to a version of the named asset
    """

    resolver = assetOperations._managed_label_resolver.get(label, None)
    if not resolver:
        scope = "registry" if assetOperations._registry_name else "workspace"
        msg = "Asset {} with version label {} does not exist in {}."
        raise ValidationException(
            message=msg.format(name, label, scope),
            no_personal_data_message=msg.format("[name]", "[label]", "[scope]"),
            target=ErrorTarget.ASSET,
            error_type=ValidationErrorType.RESOURCE_NOT_FOUND,
        )
    return resolver(name)


def _check_or_modify_auto_delete_setting(
    autoDeleteSetting: Union[Dict, "AutoDeleteSetting"],
):
    if autoDeleteSetting is not None:
        if hasattr(autoDeleteSetting, "condition"):
            condition = getattr(autoDeleteSetting, "condition")
            condition = snake_to_camel(condition)
            setattr(autoDeleteSetting, "condition", condition)
        elif "condition" in autoDeleteSetting:
            autoDeleteSetting["condition"] = snake_to_camel(autoDeleteSetting["condition"])


def _validate_workspace_managed_datastore(path: Optional[Union[str, PathLike]]) -> Optional[Union[str, PathLike]]:
    # block cumtomer specified path on managed datastore
    if path.startswith(WORKSPACE_MANAGED_DATASTORE_WITH_SLASH) or path == WORKSPACE_MANAGED_DATASTORE:
        path = path.rstrip("/")

        if path != WORKSPACE_MANAGED_DATASTORE:
            raise AssetPathException(
                message=INVALID_MANAGED_DATASTORE_PATH_ERROR_NO_PERSONAL_DATA,
                tartget=ErrorTarget.DATA,
                no_personal_data_message=INVALID_MANAGED_DATASTORE_PATH_ERROR_NO_PERSONAL_DATA,
                error_category=ErrorCategory.USER_ERROR,
            )

        return path + "/paths"
    return path


def _validate_auto_delete_setting_in_data_output(
    auto_delete_setting: Optional[Union[Dict, "AutoDeleteSetting"]]
) -> None:
    # avoid specifying auto_delete_setting in job output now
    if auto_delete_setting:
        raise ValidationException(
            message=AUTO_DELETE_SETTING_NOT_ALLOWED_ERROR_NO_PERSONAL_DATA,
            tartget=ErrorTarget.DATA,
            no_personal_data_message=AUTO_DELETE_SETTING_NOT_ALLOWED_ERROR_NO_PERSONAL_DATA,
            error_category=ErrorCategory.USER_ERROR,
        )


class FileUploadProgressBar(tqdm):
    def __init__(self, msg: Optional[str] = None):
        warnings.simplefilter("ignore", category=TqdmWarning)
        is_windows = system() == "Windows"  # Default unicode progress bar doesn't display well on Windows
        super().__init__(unit="B", unit_scale=True, desc=msg, ascii=is_windows)

    def update_to(self, response):
        current = response.context["upload_stream_current"]
        self.total = response.context["data_stream_total"]
        if current:
            self.update(current - self.n)


class DirectoryUploadProgressBar(tqdm):
    def __init__(self, dir_size: int, msg: Optional[str] = None):
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


def get_storage_info_for_non_registry_asset(
    service_client, workspace_name, name, version, resource_group
) -> Dict[str, str]:
    """Get SAS uri and blob uri for non-registry asset.
    :param service_client: Service client
    :type service_client: AzureMachineLearningWorkspaces
    :param name: Asset name
    :type name: str
    :param version: Asset version
    :type version: str
    :param resource_group: Resource group
    :rtype: Dict[str, str]
    """
    request_body = PendingUploadRequestDto(pending_upload_type="TemporaryBlobReference")
    response = service_client.code_versions.create_or_get_start_pending_upload(
        resource_group_name=resource_group,
        workspace_name=workspace_name,
        name=name,
        version=version,
        body=request_body,
    )

    sas_info = {
        "sas_uri": response.blob_reference_for_consumption.credential.sas_uri,
        "blob_uri": response.blob_reference_for_consumption.blob_uri,
    }

    return sas_info


def _get_existing_asset_name_and_version(existing_asset):
    import re

    regex = r"/codes/([^/]+)/versions/([^/]+)"

    arm_id = existing_asset.id
    match = re.search(regex, arm_id)
    name = match.group(1)
    version = match.group(2)

    return name, version
