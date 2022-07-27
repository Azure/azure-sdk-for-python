# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import time
import sys
from typing import Optional, Union, Dict, Tuple, Any
from pathlib import PurePosixPath, Path
import logging

from azure.ai.ml._artifacts._constants import (
    ARTIFACT_ORIGIN,
    UPLOAD_CONFIRMATION,
    LEGACY_ARTIFACT_DIRECTORY,
    FILE_SIZE_WARNING,
)
from azure.ai.ml._utils._asset_utils import (
    traverse_directory,
    generate_asset_id,
    _build_metadata_dict,
    IgnoreFile,
    FileUploadProgressBar,
    DirectoryUploadProgressBar,
    get_directory_size,
)
from azure.storage.fileshare import ShareDirectoryClient, ShareFileClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.ai.ml._ml_exceptions import MlException, ErrorCategory, ErrorTarget

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
        asset_hash: str = None,
        show_progress: bool = True,
    ) -> Dict[str, str]:
        """
        Upload a file or directory to a path inside the file system
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
                self.upload_dir(source, asset_id, msg=msg, show_progress=show_progress, ignore_file=ignore_file)
            else:
                self.upload_file(source, asset_id, msg=msg, show_progress=show_progress)

            # upload must be completed before we try to generate confirmation file
            while self.uploaded_file_count < self.total_file_count:
                time.sleep(0.5)
            self._set_confirmation_metadata(source, asset_id, name, version)
        else:
            name = self.name
            version = self.version
            if self.legacy:
                dest = dest.replace(ARTIFACT_ORIGIN, LEGACY_ARTIFACT_DIRECTORY)
        artifact_info = {"remote path": dest, "name": name, "version": version}

        return artifact_info

    def upload_file(
        self,
        source: str,
        dest: str,
        show_progress: Optional[bool] = None,
        msg: Optional[str] = None,
        in_directory: bool = False,
        subdirectory_client: Optional[ShareDirectoryClient] = None,
        callback: Any = None,
    ) -> None:
        """ "
        Upload a single file to a path inside the file system directory
        """
        validate_content = os.stat(source).st_size > 0  # don't do checksum for empty files

        with open(source, "rb") as data:
            if in_directory:
                file_name = dest.rsplit("/")[-1]
                if show_progress:
                    subdirectory_client.upload_file(
                        file_name=file_name, data=data, validate_content=validate_content, raw_response_hook=callback
                    )
                else:
                    subdirectory_client.upload_file(file_name=file_name, data=data, validate_content=validate_content)
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

    def upload_dir(self, source: str, dest: str, msg: str, show_progress: bool, ignore_file: IgnoreFile) -> None:
        """
        Upload a directory to a path inside the fileshare directory
        """
        subdir = self.directory_client.create_subdirectory(dest)
        source_path = Path(source).resolve()
        prefix = "" if dest == "" else dest + "/"
        prefix += os.path.basename(source) + "/"

        upload_paths = []
        for root, dirs, files in os.walk(source_path):
            upload_paths += list(traverse_directory(root, files, source_path, prefix, ignore_file))

        upload_paths = sorted(upload_paths)
        self.total_file_count = len(upload_paths)

        for root, dirs, files in os.walk(source):
            if sys.platform.startswith(("win32", "cygwin")):
                split_char = "\\"
            else:
                split_char = "/"
            trunc_root = root.rsplit(split_char)[-1]
            subdir = subdir.create_subdirectory(trunc_root)

        if show_progress:
            with DirectoryUploadProgressBar(dir_size=get_directory_size(source_path), msg=msg) as pbar:
                for src, dest in upload_paths:
                    self.upload_file(
                        src,
                        dest,
                        in_directory=True,
                        subdirectory_client=subdir,
                        show_progress=show_progress,
                        callback=pbar.update_to,
                    )
        else:
            for src, dest in upload_paths:
                self.upload_file(src, dest, in_directory=True, subdirectory_client=subdir, show_progress=show_progress)

    def exists(self, asset_id: str) -> bool:
        """
        Check if file or directory already exists in fileshare directory
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
            elif not self.legacy:
                delete(client)  # If past upload never reached upload confirmation, delete and proceed to upload
        return False

    def download(self, starts_with: str = "", destination: str = Path.home(), max_concurrency: int = 4) -> None:
        """
        Downloads all contents inside a specified fileshare directory
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
        self, asset_id: str, default_items: Dict[str, bool], legacy_items: Dict[str, bool]
    ) -> Tuple[Union[ShareDirectoryClient, ShareFileClient], Dict]:
        # if asset_id key's value doesn't match either bool, it's not in the dictionary and we check "LocalUpload" dictionary below.

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
            return client, properties  # if found in legacy, no need to look in "LocalUpload"

        if default_items.get(asset_id) is True:
            client = self.directory_client.get_subdirectory_client(asset_id)
            properties = client.get_directory_properties()
        elif default_items.get(asset_id) is False:
            client = self.directory_client.get_file_client(asset_id)
            properties = client.get_file_properties()

        return client, properties


def delete(root_client: Union[ShareDirectoryClient, ShareFileClient]) -> None:
    """
    Deletes a file or directory recursively.

    Azure File Share SDK does not allow overwriting, so if an upload is interrupted
    before it can finish, the files from that upload must be deleted before the upload
    can be re-attempted.
    """
    if isinstance(root_client, ShareFileClient):
        return root_client.delete_file()
    all_contents = list(root_client.list_directories_and_files())
    len_contents = sum(1 for _ in all_contents)
    if len_contents > 0:
        for f in all_contents:
            if f["is_directory"]:
                f_client = root_client.get_subdirectory_client(f["name"])
                delete(f_client)
            else:
                root_client.delete_file(f["name"])
    return root_client.delete_directory()


def recursive_download(
    client: ShareDirectoryClient, destination: str, max_concurrency: int, starts_with: str = ""
) -> None:
    """
    Helper function for `download`. Recursively downloads remote fileshare directory locally
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
    except Exception:
        msg = f"Saving fileshare directory with prefix {starts_with} was unsuccessful."
        raise MlException(
            message=msg.format(starts_with),
            no_personal_data_message=msg.format("[prefix]"),
            target=ErrorTarget.ARTIFACT,
            error_category=ErrorCategory.SYSTEM_ERROR,
        )
