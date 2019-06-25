# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

try:
    from urllib.parse import urlparse, quote, unquote
except ImportError:
    from urlparse import urlparse
    from urllib2 import quote, unquote

import six

from .directory_client import DirectoryClient
from .file_client import FileClient
from ._generated import AzureFileStorage
from ._generated.version import VERSION
from ._generated.models import StorageErrorException, SignedIdentifier
from ._shared.utils import (
    StorageAccountHostsMixin,
    serialize_iso,
    return_headers_and_deserialized,
    parse_query,
    return_response_headers,
    add_metadata_headers,
    process_storage_error,
    parse_connection_str)

from ._share_utils import deserialize_share_properties


class ShareClient(StorageAccountHostsMixin):
    """
    A client to interact with the share.
    """
    def __init__(
            self, share_url,  # type: str
            share=None,  # type: Optional[Union[str, ShareProperties]]
            snapshot=None,  # type: Optional[Union[str, Dict[str, Any]]]
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
        ):
        # type: (...) -> ShareClient
        """ Creates a new ShareClient. This client represents interaction with a specific
        share, although that share may not yet exist.
        :param str share_url: The full URI to the share.
        :param share_name: The share with which to interact. If specified, this value will override
         a share value specified in the share URL.
        :type share_name: str or ~azure.storage.file.models.ShareProperties
        :param credential:
        """
        try:
            if not share_url.lower().startswith('http'):
                share_url = "https://" + share_url
        except AttributeError:
            raise ValueError("Share URL must be a string.")
        parsed_url = urlparse(share_url.rstrip('/'))
        if not parsed_url.path and not share:
            raise ValueError("Please specify a share name.")
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(share_url))
        if hasattr(credential, 'get_token'):
            raise ValueError("Token credentials not supported by the File service.")

        path_share = ""
        path_snapshot = None
        if parsed_url.path:
            path_share = parsed_url.path.lstrip('/').partition('/')[0]
        path_snapshot, sas_token = parse_query(parsed_url.query)
        if not sas_token and not credential:
            raise ValueError(
                'You need to provide either an account key or SAS token when creating a storage service.')
        try:
            self.snapshot = snapshot.snapshot
        except AttributeError:
            try:
                self.snapshot = snapshot['snapshot']
            except TypeError:
                self.snapshot = snapshot or path_snapshot
        try:
            self.share_name = share.name
        except AttributeError:
            self.share_name = share or unquote(path_share)
        self._query_str, credential = self._format_query_string(
            sas_token, credential, share_snapshot=self.snapshot)
        super(ShareClient, self).__init__(parsed_url, 'file', credential, **kwargs)
        self._client = AzureFileStorage(version=VERSION, url=self.url, pipeline=self._pipeline)

    def _format_url(self, hostname):
        share_name = self.share_name
        if isinstance(share_name, six.text_type):
            share_name = share_name.encode('UTF-8')
        return "{}://{}/{}{}".format(
            self.scheme,
            hostname,
            quote(share_name),
            self._query_str)

    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            share, # type: Union[str, ShareProperties]
            snapshot=None,  # type: Optional[str]
            credential=None, # type: Optional[Any]
            **kwargs # type: Any
        ):
        # type: (...) -> ShareClient
        """
        Create ShareClient from a Connection String.
        """
        account_url, secondary, credential = parse_connection_str(conn_str, credential, 'file')
        if 'secondary_hostname' not in kwargs:
            kwargs['secondary_hostname'] = secondary
        return cls(
            account_url, share=share, snapshot=snapshot, credential=credential, **kwargs)

    def get_directory_client(self, directory_path=None):
        """Get a client to interact with the specified directory.
        The directory need not already exist.

        :param directory_name:
            The name of the directory.
        :type share: str
        :returns: A Directory Client.
        :rtype: ~azure.core.file.directory_client.DirectoryClient
        """
        return DirectoryClient(
            self.url, directory_path=directory_path, snapshot=self.snapshot, credential=self.credential, _hosts=self._hosts,
            _configuration=self._config, _pipeline=self._pipeline, _location_mode=self._location_mode,
            require_encryption=self.require_encryption, key_encryption_key=self.key_encryption_key,
            key_resolver_function=self.key_resolver_function)

    def get_file_client(self, file_path):
        return FileClient(
            self.url, file_path=file_path, snapshot=self.snapshot, credential=self.credential, _hosts=self._hosts,
            _configuration=self._config, _pipeline=self._pipeline, _location_mode=self._location_mode,
            require_encryption=self.require_encryption, key_encryption_key=self.key_encryption_key,
            key_resolver_function=self.key_resolver_function)

    def create_share(
            self, metadata=None,  # type: Optional[Dict[str, str]]
            quota=None, # type: Optional[int]
            timeout=None, # type: Optional[int]
            **kwargs # type: Optional[Any]
        ):
        # type: (...) -> Dict[str, Any]
        """Creates a new Share.
        :param metadata:
            Name-value pairs associated with the share as metadata.
        :type metadata: dict(str, str)
        :param int quota:
            The quota to be alloted.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Share-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)
        """
        if self.require_encryption and not self.key_encryption_key:
            raise ValueError("Encryption required but no key was provided.")
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))

        try:
            return self._client.share.create(
                timeout=timeout,
                metadata=metadata,
                quota=quota,
                cls=return_response_headers,
                headers=headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def create_snapshot(
            self, metadata=None,  # type: Optional[Dict[str, str]]
            quota=None, # type: Optional[int]
            timeout=None,  # type: Optional[int]
            **kwargs # type: Optional[Any]
        ):
        # type: (...) -> SnapshotProperties
        """
        Creates a snapshot of the share.
        A snapshot is a read-only version of a share that's taken at a point in time.
        It can be read, copied, or deleted, but not modified. Snapshots provide a way
        to back up a share as it appears at a moment in time.
        A snapshot of a share has the same name as the base share from which the snapshot
        is taken, with a DateTime value appended to indicate the time at which the
        snapshot was taken.
        :param metadata:
            Name-value pairs associated with the share as metadata.
        :type metadata: dict(str, str)
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
        :param lease:
            Required if the share has an active lease. Value can be a LeaseClient object
            or the lease ID as a string.
        :type lease: ~azure.storage.share.lease.LeaseClient or str
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: share-updated property dict (Snapshot ID, Etag, and last modified).
        :rtype: dict[str, Any]
        """
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        try:
            return self._client.share.create_snapshot(
                timeout=timeout,
                cls=return_response_headers,
                headers=headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def delete_share(
            self, delete_snapshots=False, # type: Optional[bool]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> None
        """Marks the specified share for deletion. The share is
        later deleted during garbage collection.

        :param delete_snapshots:
            Indicates if snapshots are to be deleted.
        :type delete_snapshots: bool
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :rtype: None
        """
        if delete_snapshots:
            delete_snapshots = "include"
        try:
            self._client.share.delete(
                timeout=timeout,
                sharesnapshot=self.snapshot,
                delete_snapshots=delete_snapshots,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def get_share_properties(self, timeout=None, **kwargs):
        # type: (Optional[int], Any) -> ShareProperties
        """
        :returns: ShareProperties
        """
        try:
            props = self._client.share.get_properties(
                timeout=timeout,
                sharesnapshot=self.snapshot,
                cls=deserialize_share_properties,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)
        props.name = self.share_name
        return props

    def set_share_quota(self, quota, timeout=None, **kwargs):
        # type: (int, Optional[int], Any) ->  Dict[str, Any]
        """ Sets the quota for the share.
        :param int quota:
            The quota to be alloted.
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Share-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)
        """
        try:
            return self._client.share.set_quota(
                timeout=timeout,
                quota=quota,
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def set_share_metadata(self, metadata, timeout=None, **kwargs):
        # type: (Dict[str, Any], Optional[int], Any) ->  Dict[str, Any]
        """ Sets the metadata for the share.
        :param metadata:
            Name-value pairs associated with the share as metadata.
        :type metadata: dict(str, str)
        :param int timeout:
            The timeout parameter is expressed in seconds.
        :returns: Share-updated property dict (Etag and last modified).
        :rtype: dict(str, Any)
        """
        try:
            return self._client.share.set_metadata(
                timeout=timeout,
                cls=return_response_headers,
                metadata=metadata,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def get_share_acl(self, timeout=None, **kwargs):
        # type: (Optional[int]) -> Dict[str, str]
        """
        :returns: Access policy information in a dict.
        """
        try:
            response, identifiers = self._client.share.get_access_policy(
                timeout=timeout,
                cls=return_headers_and_deserialized,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)
        return {
            'public_access': response.get('share_public_access'),
            'signed_identifiers': identifiers or []
        }

    def set_share_access_policy(self, signed_identifiers=None, timeout=None, **kwargs):
        # type: (Optional[Dict[str, Optional[AccessPolicy]]], Optional[int]) -> Dict[str, str]
        """
        :returns: None.
        """
        if signed_identifiers:
            if len(signed_identifiers) > 5:
                raise ValueError(
                    'Too many access policies provided. The server does not support setting '
                    'more than 5 access policies on a single resource.')
            identifiers = []
            for key, value in signed_identifiers.items():
                if value:
                    value.start = serialize_iso(value.start)
                    value.expiry = serialize_iso(value.expiry)
                identifiers.append(SignedIdentifier(id=key, access_policy=value))
            signed_identifiers = identifiers

        try:
            return self._client.share.set_access_policy(
                share_acl=signed_identifiers or None,
                timeout=timeout,
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def get_share_stats(self, timeout=None, **kwargs):
        # type: (Optional[int]) -> Dict[str, str]
        """
        :returns: ShareStats in a dict.
        """
        try:
            return self._client.share.get_statistics(
                timeout=timeout,
                cls=return_response_headers,
                **kwargs)
        except StorageErrorException as error:
            process_storage_error(error)

    def list_directories_and_files(self, directory_name, prefix=None, timeout=None, **kwargs):
        # type: (Optional[str], Optional[int]) -> DirectoryProperties
        """
        :returns: An auto-paging iterable of dict-like DirectoryProperties and FileProperties 
        """
        directory = self.get_directory_client(directory_name)
        return directory.list_directories_and_files(prefix, timeout, **kwargs)

    def create_directory(self, directory_name, metadata=None, timeout=None, **kwargs):
        # type: (str, Optional[Dict[str, Any]], Optional[int], Any) -> DirectoryClient
        """
        :returns: DirectoryClient
        """
        directory = self.get_directory_client(directory_name)
        directory.create_directory(metadata, timeout, **kwargs)
        return directory
