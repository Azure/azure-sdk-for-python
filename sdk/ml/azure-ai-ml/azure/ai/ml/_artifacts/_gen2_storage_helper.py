# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import uuid
import logging
import time
import os
import warnings
from contextlib import suppress
from typing import Optional, Dict, Any, List
from pathlib import PurePosixPath, Path
from multiprocessing import cpu_count
from attr import validate
from colorama import Fore
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm, TqdmWarning
from platform import system
import sys

from azure.ai.ml._utils._exception_utils import EmptyDirectoryError
from azure.storage.filedatalake import (
    DataLakeServiceClient,
    generate_file_sas,
    FileSasPermissions
)
from azure.core.exceptions import ResourceExistsError
from azure.ai.ml._utils._asset_utils import (
    generate_asset_id,
    traverse_directory,
    AssetNotChangedError,
    _build_metadata_dict,
    IgnoreFile,
    FileUploadProgressBar,
    get_directory_size,
)
from azure.ai.ml._artifacts._constants import (
    UPLOAD_CONFIRMATION,
    EMPTY_DIRECTORY_ERROR,
    PROCESSES_PER_CORE,
    MAX_CONCURRENCY,
)
from azure.ai.ml.constants import STORAGE_AUTH_MISMATCH_ERROR
from azure.ai.ml._ml_exceptions import ErrorTarget, ErrorCategory, ValidationException, MlException

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

    @property
    def item_path(self):
        return self.file_system

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
        Upload a file or directory to a path inside the filesystem.
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

            # start upload
            self.directory_client = self.file_system_client.get_directory_client(asset_id)
            self.check_blob_exists()

            if os.path.isdir(source):
                self.upload_dir(source, asset_id, msg, show_progress, ignore_file=ignore_file)
            else:
                self.upload_file(source, msg, show_progress)
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

    def upload_file(
        self,
        source: str,
        msg: Optional[str] = None,
        show_progress: Optional[bool] = None,
        in_directory: bool = False,
        callback: Any = None,
    ) -> None:
        """
        Upload a single file to a path inside the filesystem.
        """
        validate_content = os.stat(source).st_size > 0  # don't do checksum for empty files

        if in_directory:
            self.file_client = self.sub_directory_client.create_file(source.split("/")[-1])
        else:
            self.file_client = self.directory_client.create_file(source.split("/")[-1])

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
                self.file_client.upload_data(
                    data=data.read(),
                    overwrite=True,
                    validate_content=validate_content,
                    raw_response_hook=callback,
                    max_concurrency=MAX_CONCURRENCY,
                )

        self.uploaded_file_count += 1

    def upload_dir(self, source: str, dest: str, msg: str, show_progress: bool, ignore_file: IgnoreFile) -> None:
        """
        Upload a directory to a path inside the filesystem.
        """
        source_path = Path(source).resolve()
        prefix = "" if dest == "" else dest + "/"
        prefix += os.path.basename(source_path) + "/"
        self.sub_directory_client = self.directory_client.create_sub_directory(prefix.strip("/").split("/")[-1])

        # get all paths in directory and each file's size
        upload_paths = []
        size_dict = {}
        total_size = 0
        for root, _, files in os.walk(source_path):
            upload_paths += list(traverse_directory(root, files, source_path, prefix, ignore_file=ignore_file))

        for path, _ in upload_paths:
            path_size = os.path.getsize(path)
            size_dict[path] = path_size
            total_size += path_size

        upload_paths = sorted(upload_paths)
        if len(upload_paths) == 0:
            raise EmptyDirectoryError(EMPTY_DIRECTORY_ERROR.format(source))

        self.total_file_count = len(upload_paths)

        # submit paths to workers for upload
        num_cores = int(cpu_count()) * PROCESSES_PER_CORE
        with ThreadPoolExecutor(max_workers=num_cores) as ex:
            futures_dict = {
                ex.submit(self.upload_file, src, dest, in_directory=True, show_progress=show_progress): (src, dest)
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

    def check_blob_exists(self) -> None:
        """
        Throw error if file or directory already exists.

        Check if file or directory already exists in filesystem by checking the metadata for
        existence and confirmation data. If confirmation data is missing, file or directory does not exist
        or was only partially uploaded and the partial upload will be overwritten with a complete
        upload.
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
        """
        Downloads all items inside a specified filesystem directory with the prefix `starts_with` to the destination folder.
        """
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
        """
        Lists all file names in the specified filesystem with the prefix `starts_with`
        """
        return [f.get("name") for f in self.file_system_client.get_paths(path=starts_with)]

    def exists(self, path: str) -> bool:
        """
        Returns whether there exists a file named `path`
        """
        file_client = self.file_system_client.get_file_client(path)
        return file_client.exists()

    def generate_sas(
            self,
            *,
            account_name: str,
            account_key: str,
            item_path: str,
            item_name: str,
        ):
        return generate_blob_sas(
            account_name=account_name,
            container_name=item_path,
            blob_name=item_name,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(minutes=30),
        )

    def update_metadata(self, name: str, version: str, indicator_file: str) -> None:
        artifact_directory_client = self.file_system_client.get_directory_client(indicator_file)
        artifact_directory_client.set_metadata(_build_metadata_dict(name=name, version=version))
