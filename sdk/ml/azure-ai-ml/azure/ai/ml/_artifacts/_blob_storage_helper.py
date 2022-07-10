# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import asyncio
import itertools
import uuid
import logging
import time
import os
import warnings
from datetime import datetime, timedelta
from contextlib import suppress
from typing import Optional, Dict, Any, List, TYPE_CHECKING, Tuple, Union
from pathlib import PurePosixPath, Path
from multiprocessing import cpu_count
from colorama import Fore
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm, TqdmWarning
from platform import system
import sys

from azure.core.exceptions import ResourceNotFoundError

from azure.ai.ml._utils._exception_utils import EmptyDirectoryError
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
    ARTIFACT_ORIGIN,
    LEGACY_ARTIFACT_DIRECTORY,
    EMPTY_DIRECTORY_ERROR,
    PROCESSES_PER_CORE,
    MAX_CONCURRENCY,
    FILE_SIZE_WARNING,
    BLOB_DATASTORE_IS_HDI_FOLDER_KEY,
)
from azure.ai.ml.constants import STORAGE_AUTH_MISMATCH_ERROR
from azure.ai.ml._ml_exceptions import ErrorTarget, ErrorCategory, ValidationException, MlException

if TYPE_CHECKING:
    from azure.storage.blob import BlobProperties

module_logger = logging.getLogger(__name__)


class _BaseBlobStorageClient:
    def __init__(self, container_name: str = None):
        self.upload_to_root_container = None
        self.container = container_name
        self.total_file_count = 1
        self.uploaded_file_count = 0
        self.overwrite = False
        self.indicator_file = None
        self.legacy = False
        self.name = None
        self.version = None

    @property
    def item_path(self):
        return self.container

    def _format_paths(
            self,
            source: str,
            asset_hash: Optional[str],
            show_progress: bool
    ) -> Tuple[str, str, str]:
        asset_id = generate_asset_id(asset_hash, include_directory=True) if not self.upload_to_root_container else ""
        source_name = Path(source).name
        dest = str(PurePosixPath(asset_id, source_name))

        # truncate path longer than 50 chars for terminal display
        if show_progress and len(source_name) >= 50:
            formatted_path = "{:.47}".format(source_name) + "..."
        else:
            formatted_path = source_name
        return dest, formatted_path, asset_id

    def _size_warning(self, source: str, max_size: int):
        file_size, _ = get_directory_size(source)
        file_size_in_mb = file_size / 10**6
        if file_size_in_mb > max_size:
            module_logger.warning(FILE_SIZE_WARNING)

    def _get_progress_cntx(
            self,
            source: str,
            show_progress: Optional[bool],
            in_directory: bool
    ) -> FileUploadProgressBar:
        if show_progress and not in_directory:
            file_size, _ = get_directory_size(source)
            file_size_in_mb = file_size / 10**6
            if file_size_in_mb < 1:
                msg += Fore.GREEN + " (< 1 MB)"
            else:
                msg += Fore.GREEN + f" ({round(file_size_in_mb, 2)} MBs)"
            return FileUploadProgressBar(msg=msg)
        else:
            return suppress()

    def _get_upload_paths(
            self,
            source: str,
            dest: str,
            msg: str,
            ignore_file: IgnoreFile
    ) -> Tuple[List[List[Tuple[str, Union[str, Any]]]], Dict[str, int], int]:
        source_path = Path(source).resolve()
        prefix = "" if dest == "" else dest + "/"
        prefix += os.path.basename(source_path) + "/"

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
            raise EmptyDirectoryError(
                message=EMPTY_DIRECTORY_ERROR.format(source),
                no_personal_data_message=msg.format("[source]"),
                target=ErrorTarget.ARTIFACT,
                error_category=ErrorCategory.USER_ERROR,
            )
        return upload_paths, size_dict, total_size

    def _check_blob_metadata(self, properties: "BlobProperties") -> bool:
        metadata = properties.get("metadata")
        if metadata and UPLOAD_CONFIRMATION.items() <= metadata.items():
            # checks if metadata dictionary includes confirmation key and value
            self.name = metadata.get("name")
            self.version = metadata.get("version")
            self.legacy = True
            raise AssetNotChangedError
        return False

    def _blob_is_hdi_folder(self, blob: "BlobProperties") -> bool:
        """Checks if a given blob actually represents a folder

        Blob datastores do not natively have any conception of a folder. Instead,
        empty blobs with the same name as a "folder" can have additional metadata
        specifying that it is actually a folder.

        :param BlobProperties blob: Blob to check
        :return bool: True if blob represents a folder, False otherwise
        """

        # Metadata isn't always a populated field, and may need to be explicitly
        # requested from whatever function generates the blobproperies object
        #
        # e.g self.container_client.list_blobs(..., include='metadata')
        return bool(blob.metadata and blob.metadata.get(BLOB_DATASTORE_IS_HDI_FOLDER_KEY, None))

    def _indicator_file_client(self, indicator_file: Optional[str] = None) -> None:
        if indicator_file:
            if indicator_file.startswith(self.container):
                indicator_file = indicator_file.split(self.container)[1]
        else:
            indicator_file = self.indicator_file
        return self.container_client.get_blob_client(blob=indicator_file)

    def generate_sas(
            self,
            *,
            account_name: str,
            account_key: str,
            item_path: str,
            item_name: str,
        ):
        from azure.storage.blob import generate_blob_sas, BlobSasPermissions
        return generate_blob_sas(
            account_name=account_name,
            container_name=item_path,
            blob_name=item_name,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(minutes=30),
        )


class BlobStorageClient(_BaseBlobStorageClient):
    def __init__(self, credential: str, account_url: str, container_name: str = None):
        super().__init__(container_name=container_name)

        from azure.storage.blob import BlobServiceClient, ContainerClient
        self.service_client = BlobServiceClient(account_url=account_url, credential=credential)
        if container_name:
            self.container_client = self.service_client.get_container_client(container=container_name)
        else:
            self.container_client = ContainerClient.from_container_url(account_url)
            self.upload_to_root_container = True
            self.container = self.container_client.container_name

    def _set_metadata(self, name: str, version: str, indicator_file: Optional[str] = None) -> None:
        blob_client = self._indicator_file_client(indicator_file=indicator_file)
        blob_client.set_blob_metadata(_build_metadata_dict(name, version))

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
        Upload a file or directory to a path inside the container
        """
        if name and version is None:
            version = str(uuid.uuid4())  # placeholder for auto-increment artifacts
        dest, formatted_path, asset_id = self._format_source_dest(source, asset_hash, show_progress)
        try:
            # configure progress bar description
            msg = Fore.GREEN + f"Uploading {formatted_path}"

            # warn if large file (> 100 MB)
            self._size_warning(source, 100)

            # start upload
            if os.path.isdir(source):
                self.upload_dir(source, asset_id, msg, show_progress, ignore_file=ignore_file)
            else:
                self.indicator_file = dest
                self.check_blob_exists()
                self.upload_file(source, dest, msg, show_progress)
            print(Fore.RESET + "\n", file=sys.stderr)

            # upload must be completed before we try to generate confirmation file
            while self.uploaded_file_count < self.total_file_count:
                time.sleep(0.5)
            self._set_metadata(name, version)
        except AssetNotChangedError:
            name = self.name
            version = self.version
            if self.legacy:
                dest = dest.replace(ARTIFACT_ORIGIN, LEGACY_ARTIFACT_DIRECTORY)

        artifact_info = {"remote path": dest, "name": name, "version": version, "indicator file": self.indicator_file}
        return artifact_info

    def upload_file(
        self,
        source: str,
        dest: str,
        msg: Optional[str] = None,
        show_progress: Optional[bool] = None,
        in_directory: bool = False,
        callback: Any = None,
    ) -> None:
        """
        Upload a single file to a path inside the container
        """
        validate_content = os.stat(source).st_size > 0  # don't do checksum for empty files

        with open(source, "rb") as data:
            cntx_manager = self._get_progress_cntx(source, show_progress, in_directory)
            with cntx_manager as c:
                callback = c.update_to if (show_progress and not in_directory) else None
                self.container_client.upload_blob(
                    name=dest,
                    data=data,
                    validate_content=validate_content,
                    overwrite=self.overwrite,
                    raw_response_hook=callback,
                    max_concurrency=MAX_CONCURRENCY,
                )

        self.uploaded_file_count += 1

    def upload_dir(self, source: str, dest: str, msg: str, show_progress: bool, ignore_file: IgnoreFile) -> None:
        """
        Upload a directory to a path inside the container

        Azure Blob doesn't allow metadata setting at the directory level, so the first
        file in the directory is designated as the file where the confirmation metadata
        will be added at the end of the upload.
        """
        upload_paths, size_dict, total_size = self._get_upload_paths(source, dest, msg, ignore_file)

        self.indicator_file = upload_paths[0][1]
        self.check_blob_exists()
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
        Throw error if blob already exists.

        Check if blob already exists in container by checking the metadata for
        existence and confirmation data. If confirmation data is missing, blob does not exist
        or was only partially uploaded and the partial upload will be overwritten with a complete
        upload.
        """

        try:
            blob_client = self._indicator_file_client()
            legacy_blob_client = self._indicator_file_client(self.indicator_file.replace(ARTIFACT_ORIGIN, LEGACY_ARTIFACT_DIRECTORY))
            properties = blob_client.get_blob_properties()

            # first check legacy folder's metadata to see if artifact is stored there
            try:
                legacy_properties = legacy_blob_client.get_blob_properties()
                self._check_blob_metadata(legacy_properties)
            except ResourceNotFoundError:
                pass

            # check LocalUpload folder's metadata if not found in legacy metadata
            if not self._check_blob_metadata(properties):
                self.overwrite = True  # if upload never confirmed, approve overriding the partial upload
        except ResourceNotFoundError:
            pass
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

    def download(
        self, starts_with: str, destination: str = Path.home(), max_concurrency: int = MAX_CONCURRENCY
    ) -> None:
        """
        Downloads all blobs inside a specified container to the destination folder
        :param starts_with: Indicates the blob name starts with to search.
        :param destination: Indicates path to download in local
        :param max_concurrency: Indicates concurrent connections to download a blob.
        """
        try:
            my_list = list(self.container_client.list_blobs(name_starts_with=starts_with, include="metadata"))
            for item in my_list:
                blob_name = item.name[len(starts_with) :].lstrip("/") or Path(starts_with).name
                target_path = Path(destination, blob_name).resolve()

                if self._blob_is_hdi_folder(item):
                    target_path.mkdir(parents=True, exist_ok=True)
                    continue

                blob_content = self.container_client.download_blob(item, max_concurrency=max_concurrency)
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with target_path.open("wb") as file:
                    blob_content.readinto(file)
        except OSError as ex:
            raise ex
        except Exception as e:
            msg = "Saving blob with prefix {} was unsuccessful. exception={}"
            raise MlException(
                message=msg.format(starts_with, e),
                no_personal_data_message=msg.format("[starts_with]", "[exception]"),
                target=ErrorTarget.ARTIFACT,
                error_category=ErrorCategory.USER_ERROR,
                error=e,
            )

    def list(self, starts_with: str) -> List[str]:
        """
        Lists all blob names in the specified container
        :param starts_with: Indicates the blob name starts with to search.
        :return: the list of blob paths in container
        """
        blobs = self.container_client.list_blobs(name_starts_with=starts_with)
        return [blob.name for blob in blobs]

    def exists(self, blobpath: str, delimeter: str = "/") -> bool:
        """Returns whether there exists a blob named `blobpath`, or if there
           exists a virtual directory given path delimeter `delimeter`

           e.g:
                Given blob store with blobs
                    foobar/baz.txt
                    foobar/baz.txt

                self.exists("foobar")          -> True
                self.exists("foobar/baz.txt")  -> True
                self.exists("foobar/blah.txt") -> False
                self.exists("foo")             -> False


        :param str blobpath: prefix matched against blob names
        :param str delimiter: The path delimeter (defaults to /)
        :return bool: True if file or virtual directory exists, False otherwise
        """
        if self.container_client.get_blob_client(blobpath).exists():
            return True

        ensure_delimeter = delimeter if not blobpath.endswith(delimeter) else ""

        # Virtual directory only exists if there is atleast one blob with it
        result = next(
            self.container_client.walk_blobs(name_starts_with=blobpath + ensure_delimeter, delimiter=delimeter), None
        )
        return result is not None

    def update_metadata(self, name: str, version: str, indicator_file: str) -> None:
        self._set_metadata(name, version, indicator_file)


class AsyncBlobStorageClient(_BaseBlobStorageClient):
    # TODO: The credential type for Storage should not be a string. While it will work
    # and the Storage SDK will not drop support for it - it's not best practice.
    def __init__(
            self,
            credential: Optional[str],
            account_url: Optional[str],
            container_name: Optional[str] = None,
            client: Optional["BlobServiceClient"] = None):
        super().__init__(container_name=container_name)
        if client:
            self.service_client = client
        else:
            from azure.storage.blob.aio import BlobServiceClient, ContainerClient
            self.service_client = BlobServiceClient(account_url=account_url, credential=credential)
        if container_name:
            self.container_client = self.service_client.get_container_client(container=container_name)
        else:
            # TODO: This part isn't going to work well if a client is passed in - so will need to
            # find a solution where maybe we take the container name from the url.
            self.container_client = ContainerClient.from_container_url(account_url)
            self.upload_to_root_container = True
            self.container = self.container_client.container_name

    async def _set_metadata(self, name: str, version: str, indicator_file: Optional[str] = None) -> None:
        blob_client = self._indicator_file_client(indicator_file=indicator_file)
        await blob_client.set_blob_metadata(_build_metadata_dict(name, version))

    async def upload(
        self,
        source: str,
        name: str,
        version: str,
        ignore_file: IgnoreFile = IgnoreFile(None),
        asset_hash: Optional[str] = None,
        show_progress: bool = True,
    ) -> Dict[str, str]:
        """
        Upload a file or directory to a path inside the container
        """
        if name and version is None:
            version = str(uuid.uuid4())  # placeholder for auto-increment artifacts
        dest, formatted_path, asset_id = self._format_source_dest(source, asset_hash, show_progress)
        try:
            # configure progress bar description
            msg = Fore.GREEN + f"Uploading {formatted_path}"

            # warn if large file (> 100 MB)
            self._size_warning(source, 100)

            # start upload
            if os.path.isdir(source):
                await self.upload_dir(source, asset_id, msg, show_progress, ignore_file=ignore_file)
            else:
                self.indicator_file = dest
                await self.check_blob_exists()
                await self.upload_file(source, dest, msg, show_progress)
            print(Fore.RESET + "\n", file=sys.stderr)

            # upload must be completed before we try to generate confirmation file
            while self.uploaded_file_count < self.total_file_count:
                await asyncio.sleep(0.5)
            await self._set_metadata(name, version)
        except AssetNotChangedError:
            name = self.name
            version = self.version
            if self.legacy:
                dest = dest.replace(ARTIFACT_ORIGIN, LEGACY_ARTIFACT_DIRECTORY)

        artifact_info = {"remote path": dest, "name": name, "version": version, "indicator file": self.indicator_file}
        return artifact_info

    async def upload_file(
        self,
        source: str,
        dest: str,
        msg: Optional[str] = None,
        show_progress: Optional[bool] = None,
        in_directory: bool = False,
        callback: Any = None,
    ) -> Tuple[str, str]:
        """
        Upload a single file to a path inside the container
        """
        validate_content = os.stat(source).st_size > 0  # don't do checksum for empty files

        with open(source, "rb") as data:
            cntx_manager = self._get_progress_cntx(source, show_progress, in_directory)
            with cntx_manager as c:
                callback = c.update_to if (show_progress and not in_directory) else None
                await self.container_client.upload_blob(
                    name=dest,
                    data=data,
                    validate_content=validate_content,
                    overwrite=self.overwrite,
                    raw_response_hook=callback,  # TODO: This should be updated to the new 'progress_hook' field.
                    max_concurrency=MAX_CONCURRENCY,
                )
        self.uploaded_file_count += 1
        return source, dest

    async def upload_dir(self, source: str, dest: str, msg: str, show_progress: bool, ignore_file: IgnoreFile) -> None:
        """
        Upload a directory to a path inside the container

        Azure Blob doesn't allow metadata setting at the directory level, so the first
        file in the directory is designated as the file where the confirmation metadata
        will be added at the end of the upload.
        """
        if show_progress:
            warnings.simplefilter("ignore", category=TqdmWarning)
            msg += f" ({round(total_size/10**6, 2)} MBs)"
            ascii = system() == "Windows"  # Default unicode progress bar doesn't display well on Windows

        upload_paths, size_dict, total_size = self._get_upload_paths(source, dest, msg, ignore_file)
        self.indicator_file = upload_paths[0][1]
        await self.check_blob_exists()
        self.total_file_count = len(upload_paths)

        # submit paths to workers for upload
        num_cores = int(cpu_count()) * PROCESSES_PER_CORE

        # Build a generator for starting the upload coroutines
        pending = (asyncio.ensure_future(self.upload_file(src, dest, in_directory=True, show_progress=show_progress)) for (src, dest) in upload_paths)
        # Start the first n uploads
        running = list(itertools.islice(pending, num_cores))
        while True:
            if show_progress:
                with tqdm(total=total_size, desc=msg, ascii=ascii) as pbar:
                    # Wait for some upload to finish before adding a new one
                    done, running = await asyncio.wait(running, return_when=asyncio.FIRST_COMPLETED)
                    try:
                        for uploaded in range(done):
                            running.add(next(pending))
                            file_path_name = uploaded.result()  # TODO: If an exception occurred in upload_file, it will reraise here.
                            pbar.update(size_dict.get(file_path_name) or 0)
                    except StopIteration:
                        # All uploads have been started. Wait on any that haven't finished yet.
                        while running:
                            done, running = await asyncio.wait(running, return_when=asyncio.FIRST_COMPLETED)
                            for uploaded in range(done):
                                file_path_name = uploaded.result()
                                pbar.update(size_dict.get(file_path_name) or 0)
                        break            
            else:
                done, running = await asyncio.wait(running, return_when=asyncio.FIRST_COMPLETED)
                try:
                    for _ in range(done):
                        running.add(next(pending))
                except StopIteration:
                    if running:
                        await asyncio.wait(running, return_when=asyncio.ALL_COMPLETED)
                    break

    async def check_blob_exists(self) -> None:
        """
        Throw error if blob already exists.

        Check if blob already exists in container by checking the metadata for
        existence and confirmation data. If confirmation data is missing, blob does not exist
        or was only partially uploaded and the partial upload will be overwritten with a complete
        upload.
        """

        try:
            blob_client = self._indicator_file_client()
            legacy_blob_client = self._indicator_file_client(self.indicator_file.replace(ARTIFACT_ORIGIN, LEGACY_ARTIFACT_DIRECTORY))
            properties = await blob_client.get_blob_properties()

            # first check legacy folder's metadata to see if artifact is stored there
            try:
                legacy_properties = await legacy_blob_client.get_blob_properties()
                self._check_blob_metadata(legacy_properties)
            except ResourceNotFoundError:
                pass

            # check LocalUpload folder's metadata if not found in legacy metadata
            if not self._check_blob_metadata(properties):
                self.overwrite = True  # if upload never confirmed, approve overriding the partial upload
        except ResourceNotFoundError:
            pass
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

    async def download(
        self, starts_with: str, destination: str = Path.home(), max_concurrency: int = MAX_CONCURRENCY
    ) -> None:
        """
        Downloads all blobs inside a specified container to the destination folder
        :param starts_with: Indicates the blob name starts with to search.
        :param destination: Indicates path to download in local
        :param max_concurrency: Indicates concurrent connections to download a blob.
        """
        try:
            my_list = await self.list(starts_with=starts_with, include="metadata")
            for item in my_list:
                blob_name = item.name[len(starts_with) :].lstrip("/") or Path(starts_with).name
                target_path = Path(destination, blob_name).resolve()

                if self._blob_is_hdi_folder(item):
                    target_path.mkdir(parents=True, exist_ok=True)
                    continue

                blob_content = await self.container_client.download_blob(item, max_concurrency=max_concurrency)
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with target_path.open("wb") as file:
                    await blob_content.readinto(file)
        except OSError as ex:
            raise ex
        except Exception as e:
            msg = "Saving blob with prefix {} was unsuccessful. exception={}"
            raise MlException(
                message=msg.format(starts_with, e),
                no_personal_data_message=msg.format("[starts_with]", "[exception]"),
                target=ErrorTarget.ARTIFACT,
                error_category=ErrorCategory.USER_ERROR,
                error=e,
            )

    async def list(self, starts_with: str, **kwargs) -> List[str]:
        """
        Lists all blob names in the specified container
        :param starts_with: Indicates the blob name starts with to search.
        :return: the list of blob paths in container
        """
        blobs = self.container_client.list_blobs(name_starts_with=starts_with, **kwargs)
        return [blob.name async for blob in blobs]

    async def exists(self, blobpath: str, delimeter: str = "/") -> bool:
        """Returns whether there exists a blob named `blobpath`, or if there
           exists a virtual directory given path delimeter `delimeter`

           e.g:
                Given blob store with blobs
                    foobar/baz.txt
                    foobar/baz.txt

                self.exists("foobar")          -> True
                self.exists("foobar/baz.txt")  -> True
                self.exists("foobar/blah.txt") -> False
                self.exists("foo")             -> False


        :param str blobpath: prefix matched against blob names
        :param str delimiter: The path delimeter (defaults to /)
        :return bool: True if file or virtual directory exists, False otherwise
        """
        if await self.container_client.get_blob_client(blobpath).exists():
            return True

        ensure_delimeter = delimeter if not blobpath.endswith(delimeter) else ""

        # Virtual directory only exists if there is atleast one blob with it
        result = await self.container_client.walk_blobs(
            name_starts_with=blobpath + ensure_delimeter,
            delimiter=delimeter).__anext__()
        return result is not None
    
    async def update_metadata(self, name: str, version: str, indicator_file: str) -> None:
        await self._set_metadata(name, version, indicator_file)
