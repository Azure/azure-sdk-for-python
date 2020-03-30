# pylint: disable=too-many-lines
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, Iterable, AnyStr, Dict, List, Tuple, IO, Iterator, cast,
    TYPE_CHECKING
)

try:
    from urllib.parse import urlparse, quote
except ImportError:
    from urlparse import urlparse # type: ignore
    from urllib2 import quote # type: ignore

import six

from ._shared.base_client import StorageAccountHostsMixin, parse_query
from ._generated import AzureBlobStorage, VERSION
from ._serialize import get_api_version
from ._models import ( # pylint: disable=unused-import
    ContainerProperties,
    BlobProperties,
    BlobPropertiesPaged,
    BlobType,
    BlobPrefix)

if TYPE_CHECKING:
    from azure.core.pipeline.transport import HttpTransport, HttpResponse  # pylint: disable=ungrouped-imports
    from azure.core.pipeline.policies import HTTPPolicy # pylint: disable=ungrouped-imports
    from datetime import datetime
    from ._download import StorageStreamDownloader
    from ._models import (  # pylint: disable=unused-import
        PublicAccess,
        AccessPolicy,
        ContentSettings,
        StandardBlobTier,
        PremiumPageBlobTier)


class ContainerClientBase(StorageAccountHostsMixin):
    """A client to interact with a specific container, although that container
    may not yet exist.

    For operations relating to a specific blob within this container, a blob client can be
    retrieved using the :func:`~get_blob_client` function.

    :param str account_url:
        The URI to the storage account. In order to create a client given the full URI to the container,
        use the :func:`from_container_url` classmethod.
    :param container_name:
        The name of the container for the blob.
    :type container_name: str
    :param credential:
        The credentials with which to authenticate. This is optional if the
        account URL already has a SAS token. The value can be a SAS token string, an account
        shared access key, or an instance of a TokenCredentials class from azure.identity.
        If the URL already has a SAS token, specifying an explicit credential will take priority.
    :keyword str api_version:
        The Storage API version to use for requests. Default value is '2019-07-07'.
        Setting to an older version may result in reduced feature compatibility.

        .. versionadded:: 12.2.0

    :keyword str secondary_hostname:
        The hostname of the secondary endpoint.
    :keyword int max_block_size: The maximum chunk size for uploading a block blob in chunks.
        Defaults to 4*1024*1024, or 4MB.
    :keyword int max_single_put_size: If the blob size is less than max_single_put_size, then the blob will be
        uploaded with only one http PUT request. If the blob size is larger than max_single_put_size,
        the blob will be uploaded in chunks. Defaults to 64*1024*1024, or 64MB.
    :keyword int min_large_block_upload_threshold: The minimum chunk size required to use the memory efficient
        algorithm when uploading a block blob. Defaults to 4*1024*1024+1.
    :keyword bool use_byte_buffer: Use a byte buffer for block blob uploads. Defaults to False.
    :keyword int max_page_size: The maximum chunk size for uploading a page blob. Defaults to 4*1024*1024, or 4MB.
    :keyword int max_single_get_size: The maximum size for a blob to be downloaded in a single call,
        the exceeded part will be downloaded in chunks (could be parallel). Defaults to 32*1024*1024, or 32MB.
    :keyword int max_chunk_get_size: The maximum chunk size used for downloading a blob. Defaults to 4*1024*1024,
        or 4MB.

    .. admonition:: Example:

        .. literalinclude:: ../samples/blob_samples_containers.py
            :start-after: [START create_container_client_from_service]
            :end-before: [END create_container_client_from_service]
            :language: python
            :dedent: 8
            :caption: Get a ContainerClient from an existing BlobServiceClient.

        .. literalinclude:: ../samples/blob_samples_containers.py
            :start-after: [START create_container_client_sasurl]
            :end-before: [END create_container_client_sasurl]
            :language: python
            :dedent: 8
            :caption: Creating the container client directly.
    """
    def __init__(
            self, account_url,  # type: str
            container_name,  # type: str
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
        ):
        # type: (...) -> None
        try:
            if not account_url.lower().startswith('http'):
                account_url = "https://" + account_url
        except AttributeError:
            raise ValueError("Container URL must be a string.")
        parsed_url = urlparse(account_url.rstrip('/'))
        if not container_name:
            raise ValueError("Please specify a container name.")
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(account_url))

        _, sas_token = parse_query(parsed_url.query)
        self.container_name = container_name
        self._query_str, credential = self._format_query_string(sas_token, credential)
        super(ContainerClientBase, self).__init__(parsed_url, service='blob', credential=credential, **kwargs)
        self._client = AzureBlobStorage(self.url, pipeline=self._pipeline)
        self._client._config.version = get_api_version(kwargs, VERSION)  # pylint: disable=protected-access

    def _format_url(self, hostname):
        container_name = self.container_name
        if isinstance(container_name, six.text_type):
            container_name = container_name.encode('UTF-8')
        return "{}://{}/{}{}".format(
            self.scheme,
            hostname,
            quote(container_name),
            self._query_str)


    def _generate_delete_blobs_options(
        self, snapshot=None,
        delete_snapshots=None,
        request_id=None,
        lease_access_conditions=None,
        modified_access_conditions=None,
        **kwargs
    ):
        """This code is a copy from _generated.

        Once Autorest is able to provide request preparation this code should be removed.
        """
        lease_id = None
        if lease_access_conditions is not None:
            lease_id = lease_access_conditions.lease_id
        if_modified_since = None
        if modified_access_conditions is not None:
            if_modified_since = modified_access_conditions.if_modified_since
        if_unmodified_since = None
        if modified_access_conditions is not None:
            if_unmodified_since = modified_access_conditions.if_unmodified_since
        if_match = None
        if modified_access_conditions is not None:
            if_match = modified_access_conditions.if_match
        if_none_match = None
        if modified_access_conditions is not None:
            if_none_match = modified_access_conditions.if_none_match

        # Construct parameters
        timeout = kwargs.pop('timeout', None)
        query_parameters = {}
        if snapshot is not None:
            query_parameters['snapshot'] = self._client._serialize.query("snapshot", snapshot, 'str')  # pylint: disable=protected-access
        if timeout is not None:
            query_parameters['timeout'] = self._client._serialize.query("timeout", timeout, 'int', minimum=0)  # pylint: disable=protected-access

        # Construct headers
        header_parameters = {}
        if delete_snapshots is not None:
            header_parameters['x-ms-delete-snapshots'] = self._client._serialize.header(  # pylint: disable=protected-access
                "delete_snapshots", delete_snapshots, 'DeleteSnapshotsOptionType')
        if request_id is not None:
            header_parameters['x-ms-client-request-id'] = self._client._serialize.header(  # pylint: disable=protected-access
                "request_id", request_id, 'str')
        if lease_id is not None:
            header_parameters['x-ms-lease-id'] = self._client._serialize.header(  # pylint: disable=protected-access
                "lease_id", lease_id, 'str')
        if if_modified_since is not None:
            header_parameters['If-Modified-Since'] = self._client._serialize.header(  # pylint: disable=protected-access
                "if_modified_since", if_modified_since, 'rfc-1123')
        if if_unmodified_since is not None:
            header_parameters['If-Unmodified-Since'] = self._client._serialize.header(  # pylint: disable=protected-access
                "if_unmodified_since", if_unmodified_since, 'rfc-1123')
        if if_match is not None:
            header_parameters['If-Match'] = self._client._serialize.header(  # pylint: disable=protected-access
                "if_match", if_match, 'str')
        if if_none_match is not None:
            header_parameters['If-None-Match'] = self._client._serialize.header(  # pylint: disable=protected-access
                "if_none_match", if_none_match, 'str')

        return query_parameters, header_parameters

    def _generate_set_tier_options(
        self, tier, rehydrate_priority=None, request_id=None, lease_access_conditions=None, **kwargs
    ):
        """This code is a copy from _generated.

        Once Autorest is able to provide request preparation this code should be removed.
        """
        lease_id = None
        if lease_access_conditions is not None:
            lease_id = lease_access_conditions.lease_id

        comp = "tier"
        timeout = kwargs.pop('timeout', None)
        # Construct parameters
        query_parameters = {}
        if timeout is not None:
            query_parameters['timeout'] = self._client._serialize.query("timeout", timeout, 'int', minimum=0)  # pylint: disable=protected-access
        query_parameters['comp'] = self._client._serialize.query("comp", comp, 'str')  # pylint: disable=protected-access, specify-parameter-names-in-call

        # Construct headers
        header_parameters = {}
        header_parameters['x-ms-access-tier'] = self._client._serialize.header("tier", tier, 'str')  # pylint: disable=protected-access, specify-parameter-names-in-call
        if rehydrate_priority is not None:
            header_parameters['x-ms-rehydrate-priority'] = self._client._serialize.header(  # pylint: disable=protected-access
                "rehydrate_priority", rehydrate_priority, 'str')
        if request_id is not None:
            header_parameters['x-ms-client-request-id'] = self._client._serialize.header(  # pylint: disable=protected-access
                "request_id", request_id, 'str')
        if lease_id is not None:
            header_parameters['x-ms-lease-id'] = self._client._serialize.header("lease_id", lease_id, 'str')  # pylint: disable=protected-access

        return query_parameters, header_parameters
