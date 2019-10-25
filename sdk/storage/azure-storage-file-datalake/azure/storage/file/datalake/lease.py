# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import uuid

from typing import (  # pylint: disable=unused-import
    Union, Optional, Any,
    TypeVar, TYPE_CHECKING
)
from azure.storage.blob import LeaseClient as BlobLeaseClient


if TYPE_CHECKING:
    from datetime import datetime
    FileSystemClient = TypeVar("FileSystemClient")
    DirectoryClient = TypeVar("DirectoryClient")
    FileClient = TypeVar("FileClient")
    PathClient = TypeVar("PathClient")

class DataLakeLeaseClient(object):
    """Creates a new LeaseClient.

    This client provides lease operations on a FileSystemClient, DirectoryClient or FileClient.

    :ivar str id:
        The ID of the lease currently being maintained. This will be `None` if no
        lease has yet been acquired.
    :ivar str etag:
        The ETag of the lease currently being maintained. This will be `None` if no
        lease has yet been acquired or modified.
    :ivar ~datetime.datetime last_modified:
        The last modified timestamp of the lease currently being maintained.
        This will be `None` if no lease has yet been acquired or modified.

    :param client:
        The client of the file system, directory, or file to lease.
    :type client: ~azure.storage.file.datalake.FileSystemClient or
        ~azure.storage.file.datalake.DirectoryClient or ~azure.storage.file.datalake.FileClient
    :param str lease_id:
        A string representing the lease ID of an existing lease. This value does not
        need to be specified in order to acquire a new lease, or break one.
    """
    def __init__(
            self, client, lease_id=None
    ):  # pylint: disable=missing-client-constructor-parameter-credential,missing-client-constructor-parameter-kwargs
        # type: (Union[FileSystemClient, DirectoryClient, FileClient], Optional[str]) -> None
        self.id = lease_id or str(uuid.uuid4())
        self.last_modified = None
        self.etag = None

        if hasattr(client, '_blob_client'):
            _client = client._blob_client  # type: ignore # pylint: disable=protected-access
        elif hasattr(client, '_container_client'):
            _client = client._container_client  # type: ignore # pylint: disable=protected-access
        else:
            raise TypeError("Lease must use any of FileSystemClient DirectoryClient, or FileClient.")

        self._blob_lease_client = BlobLeaseClient(_client, lease_id=lease_id)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.release()

    def acquire(self, lease_duration=-1, **kwargs):
        # type: (int, Optional[int], **Any) -> None
        self._blob_lease_client.acquire(lease_duration=lease_duration, **kwargs)
        self._update_lease_client_attributes()

    def renew(self, **kwargs):
        # type: (Any) -> None
        self._blob_lease_client.renew(**kwargs)
        self._update_lease_client_attributes()

    def release(self, **kwargs):
        # type: (Any) -> None
        self._blob_lease_client.release(**kwargs)
        self._update_lease_client_attributes()

    def change(self, proposed_lease_id, **kwargs):
        # type: (str, Any) -> None
        self._blob_lease_client.change(proposed_lease_id=proposed_lease_id, **kwargs)
        self._update_lease_client_attributes()

    def break_lease(self, lease_break_period=None, **kwargs):
        # type: (Optional[int], Any) -> int
        self._blob_lease_client.break_lease(lease_break_period=lease_break_period, **kwargs)

    def _update_lease_client_attributes(self):
        self.id = self._blob_lease_client.id  # type: str
        self.last_modified = self._blob_lease_client.last_modified  # type: datetime
        self.etag = self._blob_lease_client.etag  # type: str
