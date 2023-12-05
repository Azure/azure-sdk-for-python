# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=client-accepts-api-version-keyword,too-many-instance-attributes,client-method-missing-type-annotations,missing-client-constructor-parameter-kwargs,logging-format-interpolation

import logging
import os
import sys
import time
import uuid
from pathlib import Path, PurePosixPath
from typing import Dict, List, Optional, Union
from typing_extensions import Literal
from colorama import Fore

from azure.ai.ml._artifacts._constants import UPLOAD_CONFIRMATION, FILE_SIZE_WARNING
from azure.ai.ml._utils._asset_utils import (
    AssetNotChangedError,
    IgnoreFile,
    _build_metadata_dict,
    generate_asset_id,
    get_directory_size,
    upload_directory,
    upload_file,
)
from azure.ai.ml._azure_environments import _get_cloud_details
from azure.ai.ml.constants._common import STORAGE_AUTH_MISMATCH_ERROR
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, MlException, ValidationException
from azure.core.exceptions import ResourceExistsError
from azure.storage.filedatalake import DataLakeServiceClient

module_logger = logging.getLogger(__name__)


class Gen2StorageClient:
    def __init__(self, credential: str, file_system: str, account_url: str):
        service_client = DataLakeServiceClient(account_url=account_url, credential=credential)
        self.account_name = account_url.split(".")[0].split("//")[1]
        self.file_system = file_system
        self.file_system_client = service_client.get_file_system_client(file_system=file_system)
        try:
            self.file_system_client.create_file_system()
        except ResourceExistsError:
            pass

        self.directory_client = None
        self.sub_directory_client = None
        self.temp_sub_directory_client = None
        self.file_client = None
        self.total_file_count = 1
        self.uploaded_file_count = 0
        self.name = None
        self.version = None

    def upload(
        self,
        source: str,
        name: str,
        version: str,
        ignore_file: IgnoreFile = IgnoreFile(None),
        asset_hash: Optional[str] = None,
        show_progress: bool = True,
    ) -> Dict[Literal["remote path", "name", "version", "indicator file"], str]:
        """Upload a file or directory to a path inside the filesystem.

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
        :rtype: Dict[Literal["remote path", "name", "version", "indicator file"], str]
        """
        if name and version is None:
            version = str(uuid.uuid4())  # placeholder for auto-increment artifacts

        asset_id = generate_asset_id(asset_hash, include_directory=True)
        source_name = Path(source).name
        dest = str(PurePosixPath(asset_id, source_name))

        try:
            # truncate path longer than 50 chars for terminal display
            if show_progress and len(source_name) >= 50:
                formatted_path = "{:.47}".format(source_name) + "..."
            else:
                formatted_path = source_name

            # configure progress bar description
            msg = Fore.GREEN + f"Uploading {formatted_path}"

            # warn if large file (> 100 MB)
            file_size, _ = get_directory_size(source)
            file_size_in_mb = file_size / 10**6

            cloud = _get_cloud_details()
            cloud_endpoint = cloud["storage_endpoint"]  # make sure proper cloud endpoint is used
            full_storage_url = f"https://{self.account_name}.dfs.{cloud_endpoint}/{self.file_system}/{dest}"
            if file_size_in_mb > 100:
                module_logger.warning(FILE_SIZE_WARNING.format(source=source, destination=full_storage_url))

            # start upload
            self.directory_client = self.file_system_client.get_directory_client(asset_id)
            self.check_blob_exists()

            if os.path.isdir(source):
                upload_directory(
                    storage_client=self,
                    source=source,
                    dest=asset_id,
                    msg=msg,
                    show_progress=show_progress,
                    ignore_file=ignore_file,
                )
            else:
                upload_file(
                    storage_client=self,
                    source=source,
                    msg=msg,
                    show_progress=show_progress,
                )
            print(Fore.RESET + "\n", file=sys.stderr)

            # upload must be completed before we try to generate confirmation file
            while self.uploaded_file_count < self.total_file_count:
                time.sleep(0.5)
            self._set_confirmation_metadata(name, version)
        except AssetNotChangedError:
            name = self.name
            version = self.version

        artifact_info = {
            "remote path": dest,
            "name": name,
            "version": version,
            "indicator file": asset_id,
        }

        return artifact_info

    def check_blob_exists(self) -> None:
        """Throw error if file or directory already exists.

        Check if file or directory already exists in filesystem by
        checking the metadata for existence and confirmation data. If
        confirmation data is missing, file or directory does not exist
        or was only partially uploaded and the partial upload will be
        overwritten with a complete upload.
        """
        try:
            if self.directory_client.exists():
                metadata = self.directory_client.get_directory_properties().metadata

                if (
                    metadata and UPLOAD_CONFIRMATION.items() <= metadata.items()
                ):  # checks if metadata dictionary includes confirmation key and value
                    self.name = metadata.get("name")
                    self.version = metadata.get("version")
                    raise AssetNotChangedError
        except Exception as e:  # pylint: disable=broad-except
            # pylint: disable=no-member
            if hasattr(e, "error_code") and e.error_code == STORAGE_AUTH_MISMATCH_ERROR:
                msg = (
                    "You don't have permission to alter this storage account. "
                    "Ensure that you have been assigned both "
                    "Storage Blob Data Reader and Storage Blob Data Contributor roles."
                )
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.ARTIFACT,
                    error_category=ErrorCategory.USER_ERROR,
                ) from e
            raise e

    def _set_confirmation_metadata(self, name: str, version: str) -> None:
        self.directory_client.set_metadata(_build_metadata_dict(name, version))

    def download(self, starts_with: str, destination: Union[str, os.PathLike] = Path.home()) -> None:
        """Downloads all items inside a specified filesystem directory with the prefix `starts_with` to the destination
        folder.

        :param starts_with: The prefix used to filter items to download
        :type starts_with: str
        :param destination: The path to download items to
        :type destination: Union[str, os.PathLike]
        """
        try:
            mylist = self.file_system_client.get_paths(path=starts_with)
            download_size_in_mb = 0
            for item in mylist:
                file_name = item.name[len(starts_with) :].lstrip("/") or Path(starts_with).name
                target_path = Path(destination, file_name)

                if item.is_directory:
                    target_path.mkdir(parents=True, exist_ok=True)
                    continue

                file_client = self.file_system_client.get_file_client(item.name)

                # check if total size of download has exceeded 100 MB
                cloud = _get_cloud_details()
                cloud_endpoint = cloud["storage_endpoint"]  # make sure proper cloud endpoint is used
                full_storage_url = f"https://{self.account_name}.dfs.{cloud_endpoint}/{self.file_system}/{starts_with}"
                download_size_in_mb += file_client.get_file_properties().size / 10**6
                if download_size_in_mb > 100:
                    module_logger.warning(FILE_SIZE_WARNING.format(source=full_storage_url, destination=destination))

                file_content = file_client.download_file().readall()
                try:
                    os.makedirs(str(target_path.parent), exist_ok=True)
                except FileExistsError:
                    pass
                with target_path.open("wb") as f:
                    f.write(file_content)
        except OSError as ex:
            raise ex
        except Exception as e:
            msg = "Saving output with prefix {} was unsuccessful. exception={}"
            raise MlException(
                message=msg.format(starts_with, e),
                no_personal_data_message=msg.format("[starts_with]", "[exception]"),
                target=ErrorTarget.ARTIFACT,
                error_category=ErrorCategory.USER_ERROR,
                error=e,
            ) from e

    def list(self, starts_with: str) -> List[str]:
        """Lists all file names in the specified filesystem with the prefix
        `starts_with`

        :param starts_with: The prefix used to filter results
        :type starts_with: str
        :return: The list of filenames that start with the prefix
        :rtype: List[str]
        """
        return [f.get("name") for f in self.file_system_client.get_paths(path=starts_with)]

    def exists(self, path: str) -> bool:
        """Returns whether there exists a file named `path`

        :param path: The path to check
        :type path: str
        :return: True if `path` exists, False otherwise
        :rtype: bool
        """
        file_client = self.file_system_client.get_file_client(path)
        return file_client.exists()
