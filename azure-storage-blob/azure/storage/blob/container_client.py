# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, Iterable, AnyStr, Dict, List, Tuple,
    TYPE_CHECKING
)

from azure.core import Configuration

from .common import BlobType
from .lease import Lease
from .blob_client import BlobClient
from .models import ContainerProperties, BlobProperties

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
        pass

    @staticmethod
    def create_configuration(**kwargs):
        # type: (**Any) -> Configuration
        pass

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

    def create_container(self, metadata=None, public_access=None, timeout=None):
        # type: (Optional[Dict[str, str]], Optional[Union[PublicAccess, str]], Optional[int]) -> None
        """
        :returns: None
        """

    def delete_container(
            self, lease=None,  # type: Optional[Union[Lease, str]]
            if_modified_since=None,  # type: Optional[datetime]
            if_unmodified_since=None,  # type: Optional[datetime]
            if_match=None,  # type: Optional[str]
            if_none_match=None,  # type: Optional[str]
            timeout=None  # type: Optional[int]
        ):
        # type: (...) -> None
        """
        :returns: None
        """

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

    def get_account_infomation(self, timeout=None):
        # type: (Optional[int]) -> Dict[str, str]
        """
        :returns: A dict of account information (SKU and account type).
        """

    def get_container_properties(self, lease=None, timeout=None):
        # type: (Optional[Union[Lease, str]], Optional[int]) -> ContainerProperties
        """
        :returns: ContainerProperties
        """

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

    def list_blob_properties(self, prefix=None, include=None, timeout=None):
        # type: (Optional[str], Optional[str], Optional[int]) -> Iterable[BlobProperties]
        """
        :returns: An iterable (auto-paging) response of BlobProperties.
        """

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
