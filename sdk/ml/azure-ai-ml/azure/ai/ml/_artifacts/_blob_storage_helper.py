# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import uuid
import logging
import time
import os
from typing import Dict, List, TYPE_CHECKING
from pathlib import PurePosixPath, Path
from colorama import Fore
import sys

from azure.storage.blob import BlobServiceClient, ContainerClient
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.ml._utils._asset_utils import (
    generate_asset_id,
    upload_directory,
    upload_file,
    AssetNotChangedError,
    _build_metadata_dict,
    IgnoreFile,
    get_directory_size,
)
from azure.ai.ml._artifacts._constants import (
    UPLOAD_CONFIRMATION,
    ARTIFACT_ORIGIN,
    LEGACY_ARTIFACT_DIRECTORY,
    MAX_CONCURRENCY,
    FILE_SIZE_WARNING,
    BLOB_DATASTORE_IS_HDI_FOLDER_KEY,
)
from azure.ai.ml.constants import STORAGE_AUTH_MISMATCH_ERROR
from azure.ai.ml._ml_exceptions import ErrorTarget, ErrorCategory, ValidationException, MlException

if TYPE_CHECKING:
    from azure.storage.blob import BlobProperties

module_logger = logging.getLogger(__name__)


class BlobStorageClient:
    def __init__(self, credential: str, account_url: str, container_name: str = None):
        self.service_client = BlobServiceClient(account_url=account_url, credential=credential)
        self.upload_to_root_container = None
        if container_name:
            self.container_client = self.service_client.get_container_client(container=container_name)
        else:
            self.container_client = ContainerClient.from_container_url(account_url)
            self.upload_to_root_container = True
        self.container = container_name if container_name else self.container_client.container_name
        self.total_file_count = 1
        self.uploaded_file_count = 0
        self.overwrite = False
        self.indicator_file = None
        self.legacy = False
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
        """
        Upload a file or directory to a path inside the container
        """
        if name and version is None:
            version = str(uuid.uuid4())  # placeholder for auto-increment artifacts

        asset_id = generate_asset_id(asset_hash, include_directory=True) if not self.upload_to_root_container else ""
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
            if file_size_in_mb > 100:
                module_logger.warning(FILE_SIZE_WARNING)

            # start upload
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
                self.indicator_file = dest
                self.check_blob_exists()
                upload_file(storage_client=self, source=source, dest=dest, msg=msg, show_progress=show_progress)
            print(Fore.RESET + "\n", file=sys.stderr)

            # upload must be completed before we try to generate confirmation file
            while self.uploaded_file_count < self.total_file_count:
                time.sleep(0.5)
            self._set_confirmation_metadata(name, version)
        except AssetNotChangedError:
            name = self.name
            version = self.version
            if self.legacy:
                dest = dest.replace(ARTIFACT_ORIGIN, LEGACY_ARTIFACT_DIRECTORY)

        artifact_info = {"remote path": dest, "name": name, "version": version, "indicator file": self.indicator_file}

        return artifact_info

    def check_blob_exists(self) -> None:
        """
        Throw error if blob already exists.

        Check if blob already exists in container by checking the metadata for
        existence and confirmation data. If confirmation data is missing, blob does not exist
        or was only partially uploaded and the partial upload will be overwritten with a complete
        upload.
        """

        try:
            legacy_indicator_file = self.indicator_file.replace(ARTIFACT_ORIGIN, LEGACY_ARTIFACT_DIRECTORY)
            blob_client = self.container_client.get_blob_client(blob=self.indicator_file)
            legacy_blob_client = self.container_client.get_blob_client(blob=legacy_indicator_file)

            properties = blob_client.get_blob_properties()
            metadata = properties.get("metadata")

            # first check legacy folder's metadata to see if artifact is stored there
            try:
                legacy_properties = legacy_blob_client.get_blob_properties()
                legacy_metadata = legacy_properties.get("metadata")

                if (
                    legacy_metadata and UPLOAD_CONFIRMATION.items() <= legacy_metadata.items()
                ):  # checks if metadata dictionary includes confirmation key and value
                    self.name = legacy_metadata.get("name")
                    self.version = legacy_metadata.get("version")
                    self.legacy = True

                    raise AssetNotChangedError
            except ResourceNotFoundError:
                pass

            # check LocalUpload folder's metadata if not found in legacy metadata
            if metadata and UPLOAD_CONFIRMATION.items() <= metadata.items():
                self.name = metadata.get("name")
                self.version = metadata.get("version")
                raise AssetNotChangedError
            else:
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

    def _set_confirmation_metadata(self, name: str, version: str) -> None:
        blob_client = self.container_client.get_blob_client(blob=self.indicator_file)
        metadata_dict = _build_metadata_dict(name, version)
        blob_client.set_blob_metadata(metadata_dict)

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

                blob_content = self.container_client.download_blob(item)
                blob_content = blob_content.content_as_bytes(max_concurrency)
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with target_path.open("wb") as file:
                    file.write(blob_content)
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
