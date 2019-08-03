# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, IO, Iterable, AnyStr, Dict, List, Tuple,
    TypeVar, TYPE_CHECKING
)

from .._shared.response_handlers import return_response_headers, process_storage_error
from .._generated.models import (
    StorageErrorException,
    ModifiedAccessConditions,
    LeaseAccessConditions)
from ..lease import LeaseClient as LeaseClientBase

if TYPE_CHECKING:
    from datetime import datetime
    from .._generated.operations import BlobOperations, ContainerOperations
    BlobClient = TypeVar("BlobClient")
    ContainerClient = TypeVar("ContainerClient")


class LeaseClient(LeaseClientBase):
    """Creates a new LeaseClient.

    This client provides lease operations on a BlobClient or ContainerClient.

    :ivar str id:
        The ID of the lease currently being maintained. This will be `None` if no
        lease has yet been acquired.
    :ivar str etag:
        The ETag of the lease currently being maintained. This will be `None` if no
        lease has yet been acquired or modified.
    :ivar datetime last_modified:
        The last modified timestampt of the lease currently being maintained.
        This will be `None` if no lease has yet been acquired or modified.

    :param client:
        The client of the blob or container to lease.
    :type client: ~azure.storage.blob.blob_client.BlobClient or
        ~azure.storage.blob.container_client.ContainerClient
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

    async def acquire(self, lease_duration=-1, timeout=None, **kwargs):
        # type: (int, Optional[int], Any) -> None
        """Requests a new lease.

        If the container does not have an active lease, the Blob service creates a
        lease on the container and returns a new lease ID.

        :param int lease_duration:
            Specifies the duration of the lease, in seconds, or negative one
            (-1) for a lease that never expires. A non-infinite lease can be
            between 15 and 60 seconds. A lease duration cannot be changed
            using renew or change. Default is -1 (infinite lease).
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None
        """
        mod_conditions = ModifiedAccessConditions(
            if_modified_since=kwargs.pop('if_modified_since', None),
            if_unmodified_since=kwargs.pop('if_unmodified_since', None),
            if_match=kwargs.pop('if_match', None),
            if_none_match=kwargs.pop('if_none_match', None))
        try:
            response = await self._client.acquire_lease(
                timeout=timeout,
                duration=lease_duration,
                proposed_lease_id=self.id,
                modified_access_conditions=mod_conditions,
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)
        self.id = response.get('lease_id')  # type: str
        self.last_modified = response.get('last_modified')   # type: datetime
        self.etag = kwargs.get('etag')  # type: str

    async def renew(self, timeout=None, **kwargs):
        # type: (Optional[int], Any) -> None
        """Renews the lease.

        The lease can be renewed if the lease ID specified in the
        lease client matches that associated with the container or blob. Note that
        the lease may be renewed even if it has expired as long as the container
        or blob has not been leased again since the expiration of that lease. When you
        renew a lease, the lease duration clock resets.

        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: None
        """
        mod_conditions = ModifiedAccessConditions(
            if_modified_since=kwargs.pop('if_modified_since', None),
            if_unmodified_since=kwargs.pop('if_unmodified_since', None),
            if_match=kwargs.pop('if_match', None),
            if_none_match=kwargs.pop('if_none_match', None))
        try:
            response = await self._client.renew_lease(
                lease_id=self.id,
                timeout=timeout,
                modified_access_conditions=mod_conditions,
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)
        self.etag = response.get('etag')  # type: str
        self.id = response.get('lease_id')  # type: str
        self.last_modified = response.get('last_modified')   # type: datetime

    async def release(self, timeout=None, **kwargs):
        # type: (Optional[int], Any) -> None
        """Release the lease.

        The lease may be released if the client lease id specified matches
        that associated with the container or blob. Releasing the lease allows another client
        to immediately acquire the lease for the container or blob as soon as the release is complete.

        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: None
        """
        mod_conditions = ModifiedAccessConditions(
            if_modified_since=kwargs.pop('if_modified_since', None),
            if_unmodified_since=kwargs.pop('if_unmodified_since', None),
            if_match=kwargs.pop('if_match', None),
            if_none_match=kwargs.pop('if_none_match', None))
        try:
            response = await self._client.release_lease(
                lease_id=self.id,
                timeout=timeout,
                modified_access_conditions=mod_conditions,
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)
        self.etag = response.get('etag')  # type: str
        self.id = response.get('lease_id')  # type: str
        self.last_modified = response.get('last_modified')   # type: datetime

    async def change(self, proposed_lease_id, timeout=None, **kwargs):
        # type: (str, Optional[int], Any) -> None
        """Change the lease ID of an active lease.

        :param str proposed_lease_id:
            Proposed lease ID, in a GUID string format. The Blob service returns 400
            (Invalid request) if the proposed lease ID is not in the correct format.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param str if_match:
            An ETag value, or the wildcard character (*). Specify this header to perform
            the operation only if the resource's ETag matches the value specified.
        :param str if_none_match:
            An ETag value, or the wildcard character (*). Specify this header
            to perform the operation only if the resource's ETag does not match
            the value specified. Specify the wildcard character (*) to perform
            the operation only if the resource does not exist, and fail the
            operation if it does exist.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: None
        """
        mod_conditions = ModifiedAccessConditions(
            if_modified_since=kwargs.pop('if_modified_since', None),
            if_unmodified_since=kwargs.pop('if_unmodified_since', None),
            if_match=kwargs.pop('if_match', None),
            if_none_match=kwargs.pop('if_none_match', None))
        try:
            response = await self._client.change_lease(
                lease_id=self.id,
                proposed_lease_id=proposed_lease_id,
                timeout=timeout,
                modified_access_conditions=mod_conditions,
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)
        self.etag = response.get('etag')  # type: str
        self.id = response.get('lease_id')  # type: str
        self.last_modified = response.get('last_modified')   # type: datetime

    async def break_lease(self, lease_break_period=None, timeout=None, **kwargs):
        # type: (Optional[int], Optional[int], Any) -> int
        """Break the lease, if the container or blob has an active lease.

        Once a lease is broken, it cannot be renewed. Any authorized request can break the lease;
        the request is not required to specify a matching lease ID. When a lease
        is broken, the lease break period is allowed to elapse, during which time
        no lease operation except break and release can be performed on the container or blob.
        When a lease is successfully broken, the response indicates the interval
        in seconds until a new lease can be acquired.

        :param int lease_break_period:
            This is the proposed duration of seconds that the lease
            should continue before it is broken, between 0 and 60 seconds. This
            break period is only used if it is shorter than the time remaining
            on the lease. If longer, the time remaining on the lease is used.
            A new lease will not be available before the break period has
            expired, but the lease may be held for longer than the break
            period. If this header does not appear with a break
            operation, a fixed-duration lease breaks after the remaining lease
            period elapses, and an infinite lease breaks immediately.
        :param datetime if_modified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only
            if the resource has been modified since the specified time.
        :param datetime if_unmodified_since:
            A DateTime value. Azure expects the date value passed in to be UTC.
            If timezone is included, any non-UTC datetimes will be converted to UTC.
            If a date is passed in without timezone info, it is assumed to be UTC.
            Specify this header to perform the operation only if
            the resource has not been modified since the specified date/time.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :return: Approximate time remaining in the lease period, in seconds.
        :rtype: int
        """
        mod_conditions = ModifiedAccessConditions(
            if_modified_since=kwargs.pop('if_modified_since', None),
            if_unmodified_since=kwargs.pop('if_unmodified_since', None))
        try:
            response = await self._client.break_lease(
                timeout=timeout,
                break_period=lease_break_period,
                modified_access_conditions=mod_conditions,
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)
        return response.get('lease_time') # type: ignore
