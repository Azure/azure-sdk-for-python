# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import functools
from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, Iterable, Dict, List, cast,
    TYPE_CHECKING
)

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse # type: ignore

from azure.core.paging import ItemPaged
from azure.core.pipeline import Pipeline
from azure.core.tracing.decorator import distributed_trace

from ._shared.models import LocationMode
from ._shared.base_client import StorageAccountHostsMixin, TransportWrapper, parse_connection_str, parse_query
from ._shared.parser import _to_utc_datetime
from ._shared.response_handlers import return_response_headers, process_storage_error, \
    parse_to_internal_user_delegation_key
from ._generated import AzureBlobStorage, VERSION
from ._generated.models import StorageErrorException, StorageServiceProperties, KeyInfo
from ._container_client import ContainerClient
from ._blob_client import BlobClient
from ._models import ContainerPropertiesPaged
from ._serialize import get_api_version
from ._deserialize import service_stats_deserialize, service_properties_deserialize

if TYPE_CHECKING:
    from datetime import datetime
    from azure.core.pipeline.transport import HttpTransport
    from azure.core.pipeline.policies import HTTPPolicy
    from ._shared.models import UserDelegationKey
    from ._lease import BlobLeaseClient
    from ._models import (
        BlobProperties,
        ContainerProperties,
        PublicAccess,
        BlobAnalyticsLogging,
        Metrics,
        CorsRule,
        RetentionPolicy,
        StaticWebsite,
    )


class BlobServiceClientBase(StorageAccountHostsMixin):
    """A client to interact with the Blob Service at the account level.

    This client provides operations to retrieve and configure the account properties
    as well as list, create and delete containers within the account.
    For operations relating to a specific container or blob, clients for those entities
    can also be retrieved using the `get_client` functions.

    :param str account_url:
        The URL to the blob storage account. Any other entities included
        in the URL path (e.g. container or blob) will be discarded. This URL can be optionally
        authenticated with a SAS token.
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

        .. literalinclude:: ../samples/blob_samples_authentication.py
            :start-after: [START create_blob_service_client]
            :end-before: [END create_blob_service_client]
            :language: python
            :dedent: 8
            :caption: Creating the BlobServiceClient with account url and credential.

        .. literalinclude:: ../samples/blob_samples_authentication.py
            :start-after: [START create_blob_service_client_oauth]
            :end-before: [END create_blob_service_client_oauth]
            :language: python
            :dedent: 8
            :caption: Creating the BlobServiceClient with Azure Identity credentials.
    """
    def __init__(
            self, account_url,  # type: str
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
        ):
        # type: (...) -> None
        try:
            if not account_url.lower().startswith('http'):
                account_url = "https://" + account_url
        except AttributeError:
            raise ValueError("Account URL must be a string.")
        parsed_url = urlparse(account_url.rstrip('/'))
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(account_url))

        _, sas_token = parse_query(parsed_url.query)
        self._query_str, credential = self._format_query_string(sas_token, credential)
        super(BlobServiceClientBase, self).__init__(parsed_url, service='blob', credential=credential, **kwargs)
        self._client = AzureBlobStorage(self.url, pipeline=self._pipeline)
        self._client._config.version = get_api_version(kwargs, VERSION)  # pylint: disable=protected-access

    def _format_url(self, hostname):
        """Format the endpoint URL according to the current location
        mode hostname.
        """
        return "{}://{}/{}".format(self.scheme, hostname, self._query_str)
