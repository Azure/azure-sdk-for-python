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

from .directory_client import DirectoryClient

from ._generated import AzureFileStorage
from ._generated.version import VERSION
from ._shared.utils import (
    StorageAccountHostsMixin,
    parse_query,
    parse_connection_str)


class ShareClient(StorageAccountHostsMixin):
    """
    A client to interact with the share.
    """
    def __init__(
            self, share_url,  # type: str
            share_name=None,  # type: Optional[Union[str, ShareProperties]]
            snapshot=None,  # type: Optional[Union[str, Dict[str, Any]]]
            credential=None,  # type: Optional[Any]
            configuration=None,  # type: Optional[Configuration]
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
        :param configuration: A optional pipeline configuration.
         This can be retrieved with :func:`ShareClient.create_configuration()`
        """
        try:
            if not share_url.lower().startswith('http'):
                share_url = "https://" + share_url
        except AttributeError:
            raise ValueError("Share URL must be a string.")
        parsed_url = urlparse(share_url.rstrip('/'))
        if not parsed_url.path and not (share_name):
            raise ValueError("Please specify a share name.")
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(share_url))

        path_share = ""
        path_snapshot = None
        if parsed_url.path:
            path_share, _, _ = parsed_url.path.lstrip('/').partition('/')
        path_snapshot, sas_token = parse_query(parsed_url.query)

        try:
            self.snapshot = snapshot.snapshot
        except AttributeError:
            try:
                self.snapshot = snapshot['snapshot']
            except TypeError:
                self.snapshot = snapshot or path_snapshot
        try:
            self.share_name = share_name
        except AttributeError:
            self.share_name = share_name or unquote(path_share)
        self._query_str, credential = self._format_query_string(sas_token, credential, self.snapshot)
        super(ShareClient, self).__init__(parsed_url, credential, configuration, **kwargs)
        self._client = AzureFileStorage(version=VERSION, url=self.url, pipeline=self._pipeline)
    
    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            share_name, # type: Union[str, ShareProperties]
            credential=None, # type: Optional[Any]
            configuration=None, # type: Optional[Configuration]
            **kwargs # type: Any
        ):
        # type: (...) -> ShareClient
        """
        Create ShareClient from a Connection String.
        """
        account_url, credential = parse_connection_str(conn_str, credential)
        return cls(
            share_url=account_url, share_name=share_name, credential=credential,
            configuration=configuration, **kwargs)

    def get_directory_client(self, directory_name=""):
        """Get a client to interact with the specified directory.
        The directory need not already exist.

        :param directory_name:
            The name of the directory.
        :type share: str
        :returns: A Directory Client.
        :rtype: ~azure.core.file.directory_client.DirectoryClient
        """
        return DirectoryClient(self.share_name, directory_name, self.credential, self._config)
    
    def create_share(
            self, metadata=None,  # type: Optional[Dict[str, str]]
            quota=None, # type: Optional[int]
            timeout=None # type: Optional[int]
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

    def create_snapshot(
            self, metadata=None,  # type: Optional[Dict[str, str]]
            quota=None, # type: Optional[int]
            timeout=None,  # type: Optional[int]
            **kwargs # type: Optional[Any]
        ):
        # type: (...) -> SnapshotProperties
        """
        :returns: SnapshotProperties
        """

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
    
    def get_share_properties(self, timeout=None, **kwargs):
        # type: (Optional[int], Any) -> ShareProperties
        """
        :returns: ShareProperties
        """

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

    def get_share_acl(self, timeout=None, **kwargs):
        # type: (Optional[int]) -> Dict[str, str]
        """
        :returns: Access policy information in a dict.
        """
    
    def set_share_acl(self, signed_identifiers=None, timeout=None, **kwargs):
        # type: (Optional[Dict[str, Optional[AccessPolicy]]], Optional[int]) -> Dict[str, str]
        """
        :returns: None.
        """

    def get_share_stats(self, timeout=None, **kwargs):
        # type: (Optional[int]) -> Dict[str, str]
        """
        :returns: ShareStats in a dict.
        """

    def list_directies_and_files(self, prefix=None, timeout=None, **kwargs):
        # type: (Optional[str], Optional[int]) -> DirectoryProperties
        """
        :returns: An auto-paging iterable of dict-like DirectoryProperties and FileProperties 
        """
    
    def create_directory(self, directory_name, metadata=None, timeout=None):
        # type: (str, Optional[Dict[str, Any]], Optional[int]) -> DirectoryClient
        """
        :returns: DirectoryClient
        """
