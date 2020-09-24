# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=invalid-overridden-method
from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, IO, Iterable, AnyStr, Dict, List, Tuple,
    TypeVar, TYPE_CHECKING
)

from azure.core.tracing.decorator_async import distributed_trace_async

from .._shared.response_handlers import return_response_headers, process_storage_error
from .._generated.models import (
    StorageErrorException)
from .._generated.aio.operations_async._file_operations_async import FileOperations
from .._lease import ShareLeaseClient as LeaseClientBase

if TYPE_CHECKING:
    from datetime import datetime
    ShareFileClient = TypeVar("ShareFileClient")
    ShareClient = TypeVar("ShareClient")


class ShareLeaseClient(LeaseClientBase):
    """Creates a new ShareLeaseClient.

    This client provides lease operations on a ShareFileClient.

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
        The client of the file to lease.
    :type client: ~azure.storage.fileshare.aio.ShareFileClient
    :param str lease_id:
        A string representing the lease ID of an existing lease. This value does not
        need to be specified in order to acquire a new lease, or break one.
    """

    def __enter__(self):
        raise TypeError("Async lease must use 'async with'.")

    def __exit__(self, *args):
        self.release()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.release()

    @distributed_trace_async
    async def acquire(self, lease_duration=-1, **kwargs):
        # type: (int, **Any) -> None
        """Requests a new lease. This operation establishes and manages a lock on a
        file or share for write and delete operations. If the file or share does not have an active lease,
        the File or Share service creates a lease on the file or share. If the file has an active lease,
        you can only request a new lease using the active lease ID.


        If the file or share does not have an active lease, the File or Share service creates a
        lease on the file and returns a new lease ID.

        :param int lease_duration:
            Specifies the duration of the lease, in seconds, or negative one
            (-1) for a lease that never expires. File leases never expire. A non-infinite share lease can be
            between 15 and 60 seconds. A share lease duration cannot be changed
            using renew or change. Default is -1 (infinite share lease).

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None
        """
        try:
            response = await self._client.acquire_lease(
                timeout=kwargs.pop('timeout', None),
                duration=lease_duration,
                proposed_lease_id=self.id,
                cls=return_response_headers,
                **kwargs)

        except StorageErrorException as error:
            process_storage_error(error)
        self.id = response.get('lease_id')  # type: str
        self.last_modified = response.get('last_modified')   # type: datetime
        self.etag = response.get('etag')  # type: str

    @distributed_trace_async
    async def renew(self, **kwargs):
        # type: (Any) -> None
        """Renews the share lease.

        The share lease can be renewed if the lease ID specified in the
        lease client matches that associated with the share. Note that
        the lease may be renewed even if it has expired as long as the share
        has not been leased again since the expiration of that lease. When you
        renew a lease, the lease duration clock resets.

        :keyword str etag:
            An ETag value, or the wildcard character (*). Used to check if the resource has changed,
            and act according to the condition specified by the `match_condition` parameter.
        :keyword ~azure.core.MatchConditions match_condition:
            The match condition to use upon the etag.
        :keyword str if_tags_match_condition
            Specify a SQL where clause on share tags to operate only on share with a matching value.
            eg. "\"tagname\"='my tag'"

            .. versionadded:: 12.4.0

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: None
        """
        if isinstance(self._client, FileOperations):
            raise TypeError("Lease renewal operations are only valid for ShareClient.")
        try:
            response = await self._client.renew_lease(
                lease_id=self.id,
                timeout=kwargs.pop('timeout', None),
                sharesnapshot=self.snapshot,
                cls=return_response_headers,
                **kwargs)

        except StorageErrorException as error:
            process_storage_error(error)
        self.etag = response.get('etag')  # type: str
        self.id = response.get('lease_id')  # type: str
        self.last_modified = response.get('last_modified')   # type: datetime

    @distributed_trace_async
    async def release(self, **kwargs):
        # type: (Any) -> None
        """Releases the lease. The lease may be released if the lease ID specified on the request matches
        that associated with the share or file. Releasing the lease allows another client to immediately acquire
        the lease for the share or file as soon as the release is complete.

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: None
        """
        try:
            response = await self._client.release_lease(
                lease_id=self.id,
                timeout=kwargs.pop('timeout', None),
                cls=return_response_headers,
                **kwargs)

        except StorageErrorException as error:
            process_storage_error(error)
        self.etag = response.get('etag')  # type: str
        self.id = response.get('lease_id')  # type: str
        self.last_modified = response.get('last_modified')   # type: datetime

    @distributed_trace_async
    async def change(self, proposed_lease_id, **kwargs):
        # type: (str, Any) -> None
        """ Changes the lease ID of an active lease. A change must include the current lease ID in x-ms-lease-id and
        a new lease ID in x-ms-proposed-lease-id.


        :param str proposed_lease_id:
            Proposed lease ID, in a GUID string format. The File or Share service returns 400
            (Invalid request) if the proposed lease ID is not in the correct format.
        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: None
        """
        try:
            response = await self._client.change_lease(
                lease_id=self.id,
                proposed_lease_id=proposed_lease_id,
                timeout=kwargs.pop('timeout', None),
                cls=return_response_headers,
                **kwargs)

        except StorageErrorException as error:
            process_storage_error(error)
        self.etag = response.get('etag')  # type: str
        self.id = response.get('lease_id')  # type: str
        self.last_modified = response.get('last_modified')   # type: datetime

    @distributed_trace_async
    async def break_lease(self, **kwargs):
        # type: (Optional[int], Any) -> int
        """Force breaks the lease if the file or share has an active lease. Any authorized request can break the lease;
        the request is not required to specify a matching lease ID. An infinite lease breaks immediately.

        Once a lease is broken, it cannot be changed. Any authorized request can break the lease;
        the request is not required to specify a matching lease ID.
        When a lease is successfully broken, the response indicates the interval
        in seconds until a new lease can be acquired.

        :keyword int timeout:
            The timeout parameter is expressed in seconds.
        :return: Approximate time remaining in the lease period, in seconds.
        :rtype: int
        """
        try:
            response = await self._client.break_lease(
                timeout=kwargs.pop('timeout', None),
                cls=return_response_headers,
                **kwargs)
            
        except StorageErrorException as error:
            process_storage_error(error)
        return response.get('lease_time') # type: ignore
