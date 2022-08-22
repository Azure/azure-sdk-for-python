# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import os
import sys
import time
import uuid
from pathlib import Path, PurePosixPath
from typing import Dict, List

from colorama import Fore

from azure.ai.ml._artifacts._constants import UPLOAD_CONFIRMATION
from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, MlException, ValidationException
from azure.ai.ml._utils._asset_utils import (
    AssetNotChangedError,
    IgnoreFile,
    _build_metadata_dict,
    generate_asset_id,
    upload_directory,
    upload_file,
)
from azure.ai.ml.constants import STORAGE_AUTH_MISMATCH_ERROR
from azure.core.exceptions import ResourceExistsError
from azure.storage.filedatalake import DataLakeServiceClient

module_logger = logging.getLogger(__name__)


class Gen2StorageClient:
    def __init__(self, credential: str, file_system: str, account_url: str):
        service_client = DataLakeServiceClient(account_url=account_url, credential=credential)
        self.file_system = file_system
        self.file_system_client = service_client.get_file_system_client(file_system=file_system)
        try:
            self.file_system_client.create_file_system()
        except ResourceExistsError:
            pass

        self.directory_client = None
        self.sub_directory_client = None
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
        asset_hash: str = None,
        show_progress: bool = True,
    ) -> Dict[str, str]:
        """Upload a file or directory to a path inside the filesystem."""
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
        except Exception as e:
            if hasattr(e, "error_code") and e.error_code == STORAGE_AUTH_MISMATCH_ERROR:
                msg = "You don't have permission to alter this storage account. Ensure that you have been assigned both Storage Blob Data Reader and Storage Blob Data Contributor roles."
                raise ValidationException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.ARTIFACT,
                    error_category=ErrorCategory.USER_ERROR,
                )
            else:
                raise e

    def _set_confirmation_metadata(self, name: str, version: str) -> None:
        self.directory_client.set_metadata(_build_metadata_dict(name, version))

    def download(self, starts_with: str, destination: str = Path.home()) -> None:
        """Downloads all items inside a specified filesystem directory with the
        prefix `starts_with` to the destination folder."""
        try:
            mylist = self.file_system_client.get_paths(path=starts_with)
            for item in mylist:
                file_name = item.name[len(starts_with) :].lstrip("/") or Path(starts_with).name

                if item.is_directory:
                    os.makedirs(file_name)
                    continue

                target_path = Path(destination, file_name)
                file_client = self.file_system_client.get_file_client(item.name)
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
            )

    def list(self, starts_with: str) -> List[str]:
        """Lists all file names in the specified filesystem with the prefix
        `starts_with`"""
        return [f.get("name") for f in self.file_system_client.get_paths(path=starts_with)]

    def exists(self, path: str) -> bool:
        """Returns whether there exists a file named `path`"""
        file_client = self.file_system_client.get_file_client(path)
        return file_client.exists()
