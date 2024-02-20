# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=client-accepts-api-version-keyword,too-many-instance-attributes,client-method-missing-type-annotations,missing-client-constructor-parameter-kwargs

import logging
import os
import sys
import time
from pathlib import Path, PurePosixPath
from typing import Callable, Dict, Optional, Tuple, Union

from typing_extensions import Literal

from azure.ai.ml._artifacts._constants import (
    ARTIFACT_ORIGIN,
    FILE_SIZE_WARNING,
    LEGACY_ARTIFACT_DIRECTORY,
    UPLOAD_CONFIRMATION,
)
from azure.ai.ml._utils._asset_utils import (
    DirectoryUploadProgressBar,
    FileUploadProgressBar,
    IgnoreFile,
    _build_metadata_dict,
    generate_asset_id,
    get_directory_size,
    get_upload_files_from_folder,
)
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, MlException
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.storage.fileshare import ShareDirectoryClient, ShareFileClient

module_logger = logging.getLogger(__name__)


class FileStorageClient:
    def __init__(self, credential: str, file_share_name: str, account_url: str):
        self.directory_client = ShareDirectoryClient(
            account_url=account_url,
            credential=credential,
            share_name=file_share_name,
            directory_path=ARTIFACT_ORIGIN,
        )
        self.legacy_directory_client = ShareDirectoryClient(
            account_url=account_url,
            credential=credential,
            share_name=file_share_name,
            directory_path=LEGACY_ARTIFACT_DIRECTORY,
        )
        self.file_share = file_share_name
        self.total_file_count = 1
        self.uploaded_file_count = 0
        self.name = None
        self.version = None
        self.legacy = False

        try:
            self.directory_client.create_directory()
        except ResourceExistsError:
            pass

        self.subdirectory_client = None

    def upload(
        self,
        source: str,
        name: str,
        version: str,
        ignore_file: IgnoreFile = IgnoreFile(None),
        asset_hash: Optional[str] = None,
        show_progress: bool = True,
    ) -> Dict[Literal["remote path", "name", "version"], str]:
        """Upload a file or directory to a path inside the file system.

        :param source: The path to either a file or directory to upload
        :type source: str
        :param name: The asset name
        :type name: str
        :param version: The asset version
        :type version: str
        :param ignore_file: The IgnoreFile that specifies which files, if any, to ignore when uploading files
        :type ignore_file: IgnoreFile
        :param asset_hash: The asset hash
        :type asset_hash: Optional[str]
        :param show_progress: Whether to show progress on the console. Defaults to True.
        :type show_progress: bool
        :return: A dictionary containing info of the uploaded artifact
        :rtype: Dict[Literal["remote path", "name", "version"], str]
        """
        asset_id = generate_asset_id(asset_hash, include_directory=False)
        source_name = Path(source).name
        dest = str(PurePosixPath(asset_id, source_name))

        if not self.exists(asset_id):
            # truncate path longer than 50 chars for terminal display
            if show_progress and len(source_name) >= 50:
                formatted_path = "{:.47}".format(source_name) + "..."
            else:
                formatted_path = source_name
            msg = f"Uploading {formatted_path}"

            # warn if large file (> 100 MB)
            file_size, _ = get_directory_size(source)
            file_size_in_mb = file_size / 10**6
            if file_size_in_mb > 100:
                module_logger.warning(FILE_SIZE_WARNING)

            # start upload
            if os.path.isdir(source):
                self.upload_dir(
                    source,
                    asset_id,
                    msg=msg,
                    show_progress=show_progress,
                    ignore_file=ignore_file,
                )
            else:
                self.upload_file(source, asset_id, msg=msg, show_progress=show_progress)

            # upload must be completed before we try to generate confirmation file
            while self.uploaded_file_count < self.total_file_count:
                time.sleep(0.5)
            self._set_confirmation_metadata(source, asset_id, name, version)
        else:
            name = str(self.name)
            version = str(self.version)
            if self.legacy:
                dest = dest.replace(ARTIFACT_ORIGIN, LEGACY_ARTIFACT_DIRECTORY)
        artifact_info: Dict = {"remote path": dest, "name": name, "version": version}

        return artifact_info

    def upload_file(
        self,
        source: Union[str, os.PathLike],
        dest: str,
        show_progress: bool = False,
        msg: Optional[str] = None,
        in_directory: bool = False,
        subdirectory_client: Optional[ShareDirectoryClient] = None,
        callback: Optional[Callable[[Dict], None]] = None,
    ) -> None:
        """Upload a single file to a path inside the file system directory.

        :param source: The file to upload
        :type source: Union[str, os.PathLike]
        :param dest: The destination in the fileshare to upload to
        :type dest: str
        :param show_progress: Whether to show progress on the console. Defaults to False.
        :type show_progress: bool
        :param msg: Message to display on progress bar. Defaults to None.
        :type msg: Optional[str]
        :param in_directory: Whether this function is being called by :attr:`FileStorageClient.upload_dir`. Defaults
            to False.
        :type in_directory: bool
        :param subdirectory_client: The subdirectory client.
        :type subdirectory_client: Optional[ShareDirectoryClient]
        :param callback: A callback that receives the raw requests returned by the service during the upload process.
            Only used if `in_directory` and `show_progress` are True.
        :type callback: Optional[Callable[[Dict], None]]
        """
        validate_content = os.stat(source).st_size > 0  # don't do checksum for empty files

        with open(source, "rb") as data:
            if in_directory:
                file_name = dest.rsplit("/")[-1]
                if subdirectory_client is not None:
                    if show_progress:
                        subdirectory_client.upload_file(
                            file_name=file_name,
                            data=data,
                            validate_content=validate_content,
                            raw_response_hook=callback,
                        )
                    else:
                        subdirectory_client.upload_file(
                            file_name=file_name,
                            data=data,
                            validate_content=validate_content,
                        )
            else:
                if show_progress:
                    with FileUploadProgressBar(msg=msg) as pbar:
                        self.directory_client.upload_file(
                            file_name=dest,
                            data=data,
                            validate_content=validate_content,
                            raw_response_hook=pbar.update_to,
                        )
                else:
                    self.directory_client.upload_file(file_name=dest, data=data, validate_content=validate_content)
        self.uploaded_file_count = self.uploaded_file_count + 1

    def upload_dir(
        self,
        source: Union[str, os.PathLike],
        dest: str,
        msg: str,
        show_progress: bool,
        ignore_file: IgnoreFile,
    ) -> None:
        """Upload a directory to a path inside the fileshare directory.

        :param source: The directory to upload
        :type source: Union[str, os.PathLike]
        :param dest: The destination in the fileshare to upload to
        :type dest: str
        :param msg: Message to display on progress bar
        :type msg: str
        :param show_progress: Whether to show progress on the console.
        :type show_progress: bool
        :param ignore_file: The IgnoreFile that specifies which files, if any, to ignore when uploading files
        :type ignore_file: IgnoreFile
        """
        subdir = self.directory_client.create_subdirectory(dest)
        source_path = Path(source).resolve()
        prefix = "" if dest == "" else dest + "/"
        prefix += os.path.basename(source) + "/"

        upload_paths = sorted(get_upload_files_from_folder(source_path, prefix=prefix, ignore_file=ignore_file))
        self.total_file_count = len(upload_paths)

        for root, *_ in os.walk(source):  # type: ignore[type-var]
            if sys.platform.startswith(("win32", "cygwin")):
                split_char = "\\"
            else:
                split_char = "/"
            trunc_root = root.rsplit(split_char)[-1]  # type: ignore[union-attr]
            subdir = subdir.create_subdirectory(trunc_root)

        if show_progress:
            with DirectoryUploadProgressBar(dir_size=get_directory_size(source_path), msg=msg) as pbar:
                for src, destination in upload_paths:
                    self.upload_file(
                        src,
                        destination,
                        in_directory=True,
                        subdirectory_client=subdir,
                        show_progress=show_progress,
                        callback=pbar.update_to,
                    )
        else:
            for src, destination in upload_paths:
                self.upload_file(
                    src,
                    destination,
                    in_directory=True,
                    subdirectory_client=subdir,
                    show_progress=show_progress,
                )

    def exists(self, asset_id: str) -> bool:
        """Check if file or directory already exists in fileshare directory.

        :param asset_id: The file or directory
        :type asset_id: str
        :return: True if the file or directory exists, False otherwise
        :rtype: bool
        """
        # get dictionary of asset ids and if each asset is a file or directory (e.g. {"ijd930j23d8": True})
        default_directory_items = {
            item["name"]: item["is_directory"] for item in self.directory_client.list_directories_and_files()
        }
        try:
            legacy_directory_items = {
                item["name"]: item["is_directory"] for item in self.legacy_directory_client.list_directories_and_files()
            }
        except ResourceNotFoundError:
            # if the legacy directory does not exist, a ResourceNotFoundError is thrown. For a new file share
            # without this directory, this will fail an upload into this file share. We catch the error here
            # so that uploading a file into a file share that does not have this directory will not fail.
            # We don't have this issue with the default directory since the constructor of this class creates
            # the default directory if it does not already exist.
            legacy_directory_items = {}
        existing_items = {**default_directory_items, **legacy_directory_items}

        if asset_id in existing_items:
            client, properties = self._get_asset_metadata(asset_id, default_directory_items, legacy_directory_items)
            metadata = properties.get("metadata")
            if metadata and UPLOAD_CONFIRMATION.items() <= metadata.items():
                self.name = metadata.get("name")
                self.version = metadata.get("version")
                return True
            if not self.legacy:
                delete(client)  # If past upload never reached upload confirmation, delete and proceed to upload
        return False

    def download(
        self,
        starts_with: str = "",
        destination: str = str(Path.home()),
        max_concurrency: int = 4,
    ) -> None:
        """Downloads all contents inside a specified fileshare directory.

        :param starts_with: The prefix used to filter files to download
        :type starts_with: str
        :param destination: The destination to download to. Default to user's home directory.
        :type destination: str
        :param max_concurrency: The maximum number of concurrent downloads. Defaults to 4.
        :type max_concurrency: int
        """
        recursive_download(
            client=self.directory_client,
            starts_with=starts_with,
            destination=destination,
            max_concurrency=max_concurrency,
        )

    def _set_confirmation_metadata(self, source: str, dest: str, name: str, version: str) -> None:
        metadata_dict = _build_metadata_dict(name, version)
        if os.path.isdir(source):
            properties = self.directory_client.get_subdirectory_client(dest)
            properties.set_directory_metadata(metadata_dict)
        else:
            properties = self.directory_client.get_file_client(dest)
            properties.set_file_metadata(metadata_dict)

    def _get_asset_metadata(
        self,
        asset_id: str,
        default_items: Dict[str, bool],
        legacy_items: Dict[str, bool],
    ) -> Tuple:
        # if asset_id key's value doesn't match either bool,
        # it's not in the dictionary and we check "LocalUpload" dictionary below.

        client, properties = None, None

        if legacy_items.get(asset_id) is True:
            self.legacy = True
            client = self.legacy_directory_client.get_subdirectory_client(asset_id)
            properties = client.get_directory_properties()
        elif legacy_items.get(asset_id) is False:
            self.legacy = True
            client = self.legacy_directory_client.get_file_client(asset_id)
            properties = client.get_file_properties()
        if client and properties:
            return (
                client,
                properties,
            )  # if found in legacy, no need to look in "LocalUpload"

        if default_items.get(asset_id) is True:
            client = self.directory_client.get_subdirectory_client(asset_id)
            properties = client.get_directory_properties()
        elif default_items.get(asset_id) is False:
            client = self.directory_client.get_file_client(asset_id)
            properties = client.get_file_properties()

        return client, properties


def delete(root_client: Union[ShareDirectoryClient, ShareFileClient]) -> None:
    """Deletes a file or directory recursively.

    Azure File Share SDK does not allow overwriting, so if an upload is
    interrupted before it can finish, the files from that upload must be
    deleted before the upload can be re-attempted.

    :param root_client: The client used to delete the file or directory
    :type root_client: Union[ShareDirectoryClient, ShareFileClient]
    """
    if isinstance(root_client, ShareFileClient):
        root_client.delete_file()
        return

    all_contents = list(root_client.list_directories_and_files())
    len_contents = sum(1 for _ in all_contents)
    if len_contents > 0:
        for f in all_contents:
            if f["is_directory"]:
                f_client = root_client.get_subdirectory_client(f["name"])
                delete(f_client)
            else:
                root_client.delete_file(f["name"])
    root_client.delete_directory()


def recursive_download(
    client: ShareDirectoryClient,
    destination: str,
    max_concurrency: int,
    starts_with: str = "",
) -> None:
    """Helper function for `download`.

    Recursively downloads remote fileshare directory locally

    :param client: The share directory client
    :type client: ShareDirectoryClient
    :param destination: The destination path to download to
    :type destination: str
    :param max_concurrency: The maximum number of concurrent downloads
    :type max_concurrency: int
    :param starts_with: The prefix used to filter files to download. Defaults to ""
    :type starts_with: str
    """
    try:
        items = list(client.list_directories_and_files(name_starts_with=starts_with))
        files = [item for item in items if not item["is_directory"]]
        folders = [item for item in items if item["is_directory"]]

        for f in files:
            Path(destination).mkdir(parents=True, exist_ok=True)
            file_name = f["name"]
            file_client = client.get_file_client(file_name)
            file_content = file_client.download_file(max_concurrency=max_concurrency)
            local_path = Path(destination, file_name)
            with open(local_path, "wb") as file_data:
                file_data.write(file_content.readall())

        for f in folders:
            sub_client = client.get_subdirectory_client(f["name"])
            destination = "/".join((destination, f["name"]))
            recursive_download(sub_client, destination=destination, max_concurrency=max_concurrency)
    except Exception as e:
        msg = f"Saving fileshare directory with prefix {starts_with} was unsuccessful."
        raise MlException(
            message=msg.format(starts_with),
            no_personal_data_message=msg.format("[prefix]"),
            target=ErrorTarget.ARTIFACT,
            error_category=ErrorCategory.SYSTEM_ERROR,
        ) from e
