# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=docstring-keyword-should-match-keyword-only

import uuid
from typing import Any, cast, Optional, Union, TYPE_CHECKING

from azure.core.exceptions import HttpResponseError
from azure.core.tracing.decorator import distributed_trace
from ._generated.operations import FileOperations, ShareOperations
from ._shared.response_handlers import return_response_headers, process_storage_error

if TYPE_CHECKING:
    from datetime import datetime
    from azure.storage.fileshare import ShareClient, ShareFileClient


class ShareLeaseClient:  # pylint: disable=client-accepts-api-version-keyword
    """Creates a new ShareLeaseClient.

    This client provides lease operations on a ShareClient or ShareFileClient.

    :param client:
        The client of the file or share to lease.
    :type client: ~azure.storage.fileshare.ShareFileClient or
        ~azure.storage.fileshare.ShareClient
    :param str lease_id:
        A string representing the lease ID of an existing lease. This value does not
        need to be specified in order to acquire a new lease, or break one.
    """

    id: str
    """The ID of the lease currently being maintained. This will be `None` if no
        lease has yet been acquired."""
    etag: Optional[str]
    """The ETag of the lease currently being maintained. This will be `None` if no
        lease has yet been acquired or modified."""
    last_modified: Optional["datetime"]
    """The last modified timestamp of the lease currently being maintained.
        This will be `None` if no lease has yet been acquired or modified."""

    def __init__(  # pylint: disable=missing-client-constructor-parameter-credential, missing-client-constructor-parameter-kwargs
        self, client: Union["ShareFileClient", "ShareClient"],
        lease_id: Optional[str] = None
    ) -> None:
        self.id = lease_id or str(uuid.uuid4())
        self.last_modified = None
        self.etag = None
        if hasattr(client, 'file_name'):
            self._client = client._client.file  # type: ignore
            self._snapshot = None
        elif hasattr(client, 'share_name'):
            self._client = client._client.share
            self._snapshot = client.snapshot
        else:
            raise TypeError("Lease must use ShareFileClient or ShareClient.")

    def __enter__(self):
        return self

    def __exit__(self, *args: Any):
        self.release()

    @distributed_trace
    def acquire(self, **kwargs: Any) -> None:
        """Requests a new lease. This operation establishes and manages a lock on a
        file or share for write and delete operations. If the file or share does not have an active lease,
        the File or Share service creates a lease on the file or share. If the file has an active lease,
        you can only request a new lease using the active lease ID.


        If the file or share does not have an active lease, the File or Share service creates a
        lease on the file and returns a new lease ID.

        :keyword int lease_duration:
            Specifies the duration of the lease, in seconds, or negative one
            (-1) for a lease that never expires. File leases never expire. A non-infinite share lease can be
            between 15 and 60 seconds. A share lease duration cannot be changed
            using renew or change. Default is -1 (infinite share lease).

        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :rtype: None
        """
        try:
            lease_duration = kwargs.pop('lease_duration', -1)
            if self._snapshot:
                kwargs['sharesnapshot'] = self._snapshot
            response = self._client.acquire_lease(
                timeout=kwargs.pop('timeout', None),
                duration=lease_duration,
                proposed_lease_id=self.id,
                cls=return_response_headers,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)
        self.id = response.get('lease_id')
        self.last_modified = response.get('last_modified')
        self.etag = response.get('etag')

    @distributed_trace
    def renew(self, **kwargs: Any) -> None:
        """Renews the share lease.

        The share lease can be renewed if the lease ID specified in the
        lease client matches that associated with the share. Note that
        the lease may be renewed even if it has expired as long as the share
        has not been leased again since the expiration of that lease. When you
        renew a lease, the lease duration clock resets.

        .. versionadded:: 12.6.0

        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :return: None
        """
        if isinstance(self._client, FileOperations):
            raise TypeError("Lease renewal operations are only valid for ShareClient.")
        try:
            response = self._client.renew_lease(
                lease_id=self.id,
                timeout=kwargs.pop('timeout', None),
                sharesnapshot=self._snapshot,
                cls=return_response_headers,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)
        self.etag = response.get('etag')
        self.id = response.get('lease_id')
        self.last_modified = response.get('last_modified')

    @distributed_trace
    def release(self, **kwargs: Any) -> None:
        """Releases the lease. The lease may be released if the lease ID specified on the request matches
        that associated with the share or file. Releasing the lease allows another client to immediately acquire
        the lease for the share or file as soon as the release is complete.

        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :return: None
        """
        try:
            if self._snapshot:
                kwargs['sharesnapshot'] = self._snapshot
            response = self._client.release_lease(
                lease_id=self.id,
                timeout=kwargs.pop('timeout', None),
                cls=return_response_headers,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)
        self.etag = response.get('etag')
        self.id = response.get('lease_id')
        self.last_modified = response.get('last_modified')

    @distributed_trace
    def change(self, proposed_lease_id: str, **kwargs: Any) -> None:
        """ Changes the lease ID of an active lease. A change must include the current lease ID in x-ms-lease-id and
        a new lease ID in x-ms-proposed-lease-id.

        :param str proposed_lease_id:
            Proposed lease ID, in a GUID string format. The File or Share service will raise an error
            (Invalid request) if the proposed lease ID is not in the correct format.
        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :return: None
        """
        try:
            if self._snapshot:
                kwargs['sharesnapshot'] = self._snapshot
            response = self._client.change_lease(
                lease_id=self.id,
                proposed_lease_id=proposed_lease_id,
                timeout=kwargs.pop('timeout', None),
                cls=return_response_headers,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)
        self.etag = response.get('etag')
        self.id = response.get('lease_id')
        self.last_modified = response.get('last_modified')

    @distributed_trace
    def break_lease(self, **kwargs: Any) -> int:
        """Force breaks the lease if the file or share has an active lease. Any authorized request can break the lease;
        the request is not required to specify a matching lease ID. An infinite lease breaks immediately.

        Once a lease is broken, it cannot be changed. Any authorized request can break the lease;
        the request is not required to specify a matching lease ID.
        When a lease is successfully broken, the response indicates the interval
        in seconds until a new lease can be acquired.

        :keyword int lease_break_period:
            This is the proposed duration of seconds that the share lease
            should continue before it is broken, between 0 and 60 seconds. This
            break period is only used if it is shorter than the time remaining
            on the share lease. If longer, the time remaining on the share lease is used.
            A new share lease will not be available before the break period has
            expired, but the share lease may be held for longer than the break
            period. If this header does not appear with a break
            operation, a fixed-duration share lease breaks after the remaining share lease
            period elapses, and an infinite share lease breaks immediately.

            .. versionadded:: 12.6.0

        :keyword int timeout:
            Sets the server-side timeout for the operation in seconds. For more details see
            https://learn.microsoft.com/rest/api/storageservices/setting-timeouts-for-file-service-operations.
            This value is not tracked or validated on the client. To configure client-side network timesouts
            see `here <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-file-share
            #other-client--per-operation-configuration>`__.
        :return: Approximate time remaining in the lease period, in seconds.
        :rtype: int
        """
        try:
            lease_break_period = kwargs.pop('lease_break_period', None)
            if self._snapshot:
                kwargs['sharesnapshot'] = self._snapshot
            if isinstance(self._client, ShareOperations):
                kwargs['break_period'] = lease_break_period
            if isinstance(self._client, FileOperations) and lease_break_period:
                raise TypeError("Setting a lease break period is only applicable to Share leases.")

            response = self._client.break_lease(
                timeout=kwargs.pop('timeout', None),
                cls=return_response_headers,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)
        return cast(int, response.get('lease_time'))
