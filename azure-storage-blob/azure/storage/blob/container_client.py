# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import functools
from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, Iterable, AnyStr, Dict, List, Tuple,
    TYPE_CHECKING
)
try:
    from urllib.parse import urlparse, quote, unquote
except ImportError:
    from urlparse import urlparse
    from urllib2 import quote, unquote

from azure.core import Configuration

from .common import BlobType
from .lease import Lease
from .blob_client import BlobClient
from .models import ContainerProperties, BlobProperties, BlobPropertiesPaged
from ._utils import (
    create_client,
    create_configuration,
    create_pipeline,
    basic_error_map,
    get_access_conditions,
    get_modification_conditions,
    return_response_headers,
    add_metadata_headers,
    process_storage_error,
    encode_base64
)
from ._deserialize import (
    deserialize_container_properties,
    deserialize_metadata
)
from ._generated.models import BlobHTTPHeaders, StorageErrorException

if TYPE_CHECKING:
    from azure.core.pipeline.transport import HttpTransport
    from azure.core.pipeline.policies import HTTPPolicy
    from .common import PublicAccess
    from .models import ContainerPermissions
    from datetime import datetime


class ContainerClient(object):

    def __init__(
            self, url,  # type: str
            container=None,  # type: Union[ContainerProperties, str]
            credentials=None,  # type: Optional[HTTPPolicy]
            configuration=None,  # type: Optional[Configuration]
            **kwargs  # type: Any
        ):
        # type: (...) -> None
        parsed_url = urlparse(url)

        if not parsed_url.path and not container:
            raise ValueError("Please specify a container name.")
        path_container = ""
        if parsed_url.path:
            path_container = parsed_url.path.partition('/')[0]
        try:
            self.name = container.name
        except AttributeError:
            self.name = container or unquote(path_container)

        self.scheme = parsed_url.scheme
        self.account = parsed_url.hostname.split(".blob.core.")[0]
        self.url = url if parsed_url.path else "{}://{}/{}".format(
            self.scheme,
            parsed_url.hostname,
            quote(self.name)
        )
        self._config, self._pipeline = create_pipeline(configuration, credentials, **kwargs)
        self._client = create_client(self.url, self._pipeline)

    @staticmethod
    def create_configuration(**kwargs):
        # type: (**Any) -> Configuration
        return create_configuration(**kwargs)

    def make_url(self, protocol=None, sas_token=None):
        # type: (Optional[str], Optional[str]) -> str
        pass

    def generate_shared_access_signature(
            self, permission=None,  # type: Optional[Union[ContainerPermissions, str]]
            expiry=None,  # type: Optional[Union[datetime, str]]
            start=None,  # type: Optional[Union[datetime, str]]
            policy_id=None,  # type: Optional[str]
            ip=None,  # type: Optional[str]
            protocol=None,  # type: Optional[str]
            cache_control=None,  # type: Optional[str]
            content_disposition=None,  # type: Optional[str]
            content_encoding=None,  # type: Optional[str]
            content_language=None,  # type: Optional[str]
            content_type=None  # type: Optional[str]
        ):
        # type: (...) -> str
        pass

    def create_container(self, metadata=None, public_access=None, timeout=None, **kwargs):
        # type: (Optional[Dict[str, str]], Optional[Union[PublicAccess, str]], Optional[int]) -> None
        """
        :returns: None
        """
        headers = kwargs.pop('headers', {})
        headers.update(add_metadata_headers(metadata))
        return self._client.container.create(
            timeout=timeout,
            access=public_access,
            cls=return_response_headers,
            headers=headers,
            **kwargs)

    def delete_container(
            self, lease=None,  # type: Optional[Union[Lease, str]]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None,  # type: Optional[int]
            **kwargs
        ):
        # type: (...) -> None
        """
        :returns: None
        """
        access_conditions = get_access_conditions(lease)
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)
        self._client.container.delete(
            timeout=timeout,
            lease_access_conditions=access_conditions,
            modified_access_conditions=mod_conditions,
            error_map=basic_error_map(),
            **kwargs)

    def acquire_lease(
            self, lease_duration=-1,  # type: int
            proposed_lease_id=None,  # type: Optional[str]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None  # type: Optional[int]
        ):
        # type: (...) -> Lease
        """
        :returns: A Lease object, that can be run in a context manager.
        """
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)
        response = self._client.container.acquire_lease(
            timeout=timeout,
            duration=lease_duration,
            proposed_lease_id=proposed_lease_id,
            modified_access_conditions=mod_conditions,
            cls=return_response_headers,
            **kwargs)
        return Lease(self._client.container, **response)

    def break_lease(
            self, lease_break_period=None,  # type: Optional[int]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None  # type: Optional[int]
        ):
        # type: (...) -> int
        """
        :returns: Approximate time remaining in the lease period, in seconds.
        """
        mod_conditions = get_modification_conditions(
            if_modified_since, if_unmodified_since, if_match, if_none_match)
        response = self._client.container.break_lease(
            timeout=timeout,
            break_period=lease_break_period,
            modified_access_conditions=mod_conditions,
            cls=return_response_headers,
            **kwargs)
        return response.get('x-ms-lease-time')

    def get_account_infomation(self, timeout=None):
        # type: (Optional[int]) -> Dict[str, str]
        """
        :returns: A dict of account information (SKU and account type).
        """
        response = self._client.service.get_account_info(cls=return_response_headers)
        return {
            'SKU': response.get('x-ms-sku-name'),
            'AccountType': response.get('x-ms-account-kind')
        }

    def get_container_properties(self, lease=None, timeout=None, **kwargs):
        # type: (Optional[Union[Lease, str]], Optional[int], **Any) -> ContainerProperties
        """
        :returns: ContainerProperties
        """
        access_conditions = get_access_conditions(lease)
        response = self._client.container.get_properties(
            timeout=timeout,
            lease_access_conditions=access_conditions,
            cls=deserialize_container_properties,
            **kwargs)
        response.name = self.name
        return response

    def get_container_metadata(self, lease=None, timeout=None):
        # type: (Optional[Union[Lease, str]], Optional[int]) -> Dict[str, str]
        """
        :returns: A dict of metadata.
        """

    def set_container_metadata(
            self, metadata=None,  # type: Optional[Dict[str, str]]
            lease=None,  # type: Optional[Union[str, Lease]]
            if_modified_since=None,  # type: Optional[datetime]
            timeout=None  # type: Optional[int]
        ):
        # type: (...) -> Dict[str, Union[str, datetime]]
        """
        :returns: Container-updated property dict (Etag and last modified).
        """

    def get_container_acl(self, lease=None, timeout=None):
        # type: (Optional[Union[Lease, str]], Optional[int]) -> Dict[str, str]
        """
        :returns: Access policy information in a dict.
        """

    def set_container_acl(
            self, signed_identifiers=None,  # type: Optional[Dict[str, Optional[Tuple[Any, Any, Any]]]]
            public_access=None,  # type: Optional[Union[str, PublicAccess]]
            lease=None,  # type: Optional[Union[str, Lease]]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            timeout=None  # type: Optional[int]
        ):
        """
        :returns: Container-updated property dict (Etag and last modified).
        """

    def list_blob_properties(self, prefix=None, include=None, timeout=None, **kwargs):
        # type: (Optional[str], Optional[str], Optional[int]) -> Iterable[BlobProperties]
        """
        :returns: An iterable (auto-paging) response of BlobProperties.
        """
        if include and not isinstance(include, list):
            include = [include]
        results_per_page = kwargs.pop('results_per_page', None)
        command = functools.partial(
            self._client.container.list_blob_flat_segment,
            include=include,
            timeout=timeout,
            **kwargs)
        return BlobPropertiesPaged(command, prefix=prefix, results_per_page=results_per_page)

    def walk_blob_propertes(self, prefix=None, include=None, delimiter="/", timeout=None):
        # type: (Optional[str], Optional[str], str, Optional[int]) -> Iterable[BlobProperties]
        """
        :returns: A generator that honors directory hierarchy.
        """

    def get_blob_client(
            self, blob,  # type: Union[str, BlobProperties]
            blob_type=BlobType.BlockBlob,  # type: Union[BlobType, str]
            snapshot=None  # type: str
        ):
        # type: (...) -> BlobClient
        """
        :returns: A BlobClient.
        """
        return BlobClient(
            self.url, container=self.name, blob=blob, blob_type=blob_type,
            snapshot=snapshot, configuration=self._config, _pipeline=self._pipeline)
