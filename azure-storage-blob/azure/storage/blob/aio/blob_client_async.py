# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import (
    Union, Optional,
    TYPE_CHECKING
)

from ..common import BlobType

if TYPE_CHECKING:
    from azure.core import Configuration
    from ..authentication import SharedKeyCredentials
    from ..models import ContainerProperties, BlobProperties # pylint: disable=unused-import


class BlobClient:  # pylint: disable=too-many-public-methods

    def __init__(
            self, url: str,
            container: Optional[Union[str, ContainerProperties]] = None,
            blob: Optional[Union[str, BlobProperties]] = None,
            snapshot: Optional[str] = None,
            blob_type: Union[str, BlobType] = BlobType.BlockBlob,
            credentials: Optional[SharedKeyCredentials] = None,
            configuration: Optional[Configuration] = None) -> None:
        pass

    @staticmethod
    def create_configuration(**kwargs):
        pass

    def make_url(self, protocol=None, sas_token=None):
        pass

    def generate_shared_access_signature(
            self, resource_types, permission, expiry,
            start=None, ip=None, protocol=None):
        pass

    async def upload_blob(
            self, data, length=None, metadata=None, content_settings=None, validate_content=False,
            lease=None, if_modified_since=None, if_unmodified_since=None, if_match=None,
            if_none_match=None, timeout=None, premium_page_blob_tier=None, sequence_number=None,
            maxsize_condition=None, appendpos_condition=None):
        """
        By default, uploads as a BlockBlob, unless alternative blob_type is specified.
        :returns: A BlobClient
        """

    async def download_blob(
            self, offset=None, length=None, validate_content=False, lease=None,
            if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None,
            timeout=None):
        """
        :returns: A iterable data generator (stream)
        """

    async def delete_blob(
            self, lease=None, delete_snapshots=None, if_modified_since=None, if_unmodified_since=None,
            if_match=None, if_none_match=None, timeout=None):
        """
        :returns: None
        """

    async def undelete_blob(self, timeout=None):
        """
        :returns: None
        """

    async def get_blob_properties(
            self, lease=None, if_modified_since=None, if_unmodified_since=None,
            if_match=None, if_none_match=None, timeout=None):
        """
        :returns: BlobProperties
        """

    async def set_blob_properties(
            self, content_settings=None, lease=None, if_modified_since=None,
            if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None):
        """
        :returns: Blob-updated property dict (Etag and last modified)
        """

    async def get_blob_metadata(
            self, lease=None, if_modified_since=None, if_unmodified_since=None,
            if_match=None, if_none_match=None, timeout=None):
        """
        :returns: A dict of metadata
        """

    async def set_blob_metadata(
            self, metadata=None, lease=None, if_modified_since=None, if_unmodified_since=None,
            if_match=None, if_none_match=None, timeout=None):
        """
        :returns: Blob-updated property dict (Etag and last modified)
        """

    async def create_blob(
            self, content_length=None, content_settings=None, sequence_number=None,
            metadata=None, lease_id=None, if_modified_since=None, if_unmodified_since=None,
            if_match=None, if_none_match=None, timeout=None, premium_page_blob_tier=None):
        """
        :returns: Blob-updated property dict (Etag and last modified).
        """

    async def create_snapshot(
            self, metadata=None, if_modified_since=None, if_unmodified_since=None,
            if_match=None, if_none_match=None, lease=None, timeout=None):
        """
        :returns: SnapshotProperties
        """

    async def copy_blob_from_url(
            self, source_url, metadata=None, source_if_modified_since=None,
            source_if_unmodified_since=None, source_if_match=None, source_if_none_match=None,
            destination_if_modified_since=None, destination_if_unmodified_since=None,
            destination_if_match=None, destination_if_none_match=None, destination_lease=None,
            source_lease=None, timeout=None, premium_page_blob_tier=None, requires_sync=None):
        """
        :returns: A pollable object to check copy operation status (and abort).
        """

    async def acquire_lease(
            self, lease_duration=-1, proposed_lease_id=None, if_modified_since=None,
            if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None):
        """
        :returns: A Lease object.
        """

    async def break_lease(
            self, lease_break_period=None, if_modified_since=None, if_unmodified_since=None,
            if_match=None, if_none_match=None, timeout=None):
        """
        :returns: Approximate time remaining in the lease period, in seconds.
        """

    async def set_standard_blob_tier(self, standard_blob_tier, timeout=None):
        """
        :raises: TypeError when blob client type is not BlockBlob.
        :returns: None
        """

    async def stage_block(self, block_id, data, validate_content=False, lease=None, timeout=None):
        """
        :raises: TypeError when blob client type is not BlockBlob.
        :returns: None
        """

    async def stage_block_from_url(
            self, block_id, copy_source_url, source_range_start, source_range_end,
            source_content_md5=None, lease=None, timeout=None):
        """
        :raises: TypeError when blob client type is not BlockBlob.
        :returns: None
        """

    async def get_block_list(self, block_list_type=None, snapshot=None, lease=None, timeout=None):
        """
        :raises: TypeError when blob client type is not BlockBlob.
        :returns: A tuple of two sets - committed and uncommitted blocks
        """

    async def commit_block_list(
            self, block_list, lease=None, content_settings=None, metadata=None,
            validate_content=False, if_modified_since=None, if_unmodified_since=None,
            if_match=None, if_none_match=None, timeout=None):
        """
        :raises: TypeError when blob client type is not BlockBlob.
        :returns: Blob-updated property dict (Etag and last modified).
        """

    async def set_premium_page_blob_tier(self, premium_page_blob_tier, timeout=None):
        """
        :raises: TypeError when blob client type is not PageBlob.
        :returns: None
        """

    async def get_page_ranges(
            self, start_range=None, end_range=None, snapshot=None, lease=None,
            previous_snapshot_diff=None, if_modified_since=None, if_unmodified_since=None,
            if_match=None, if_none_match=None, timeout=None):
        """
        :raises: TypeError when blob client type is not PageBlob.
        :returns: A list of page ranges.
        """

    async def set_sequence_number(
            self, sequence_number_action, sequence_number=None, lease=None, if_modified_since=None,
            if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None):
        """
        :raises: TypeError when blob client type is not PageBlob.
        :returns: Blob-updated property dict (Etag and last modified).
        """

    async def resize_blob(
            self, content_length, lease=None, if_modified_since=None, if_unmodified_since=None,
            if_match=None, if_none_match=None, timeout=None):
        """
        :raises: TypeError when blob client type is not PageBlob.
        :returns: Blob-updated property dict (Etag and last modified).
        """

    async def update_page(
            self, page, start_range, end_range, lease=None, validate_content=False,
            if_sequence_number_lte=None, if_sequence_number_lt=None, if_sequence_number_eq=None,
            if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None):
        """
        :raises: TypeError when blob client type is not PageBlob.
        :returns: Blob-updated property dict (Etag and last modified).
        """

    async def clear_page(
            self, start_range, end_range, lease=None, if_sequence_number_lte=None,
            if_sequence_number_lt=None, if_sequence_number_eq=None, if_modified_since=None,
            if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None):
        """
        :raises: TypeError when blob client type is not PageBlob.
        :returns: Blob-updated property dict (Etag and last modified).
        """

    async def incremental_copy(
            self, copy_source, metadata=None, destination_if_modified_since=None,
            destination_if_unmodified_since=None, destination_if_match=None, destination_if_none_match=None,
            destination_lease=None, source_lease=None, timeout=None):
        """
        :raises: TypeError when blob client type is not PageBlob.
        :returns: A pollable object to check copy operation status (and abort).
        """

    async def append_block(
            self, data, validate_content=False, maxsize_condition=None, appendpos_condition=None,
            if_modified_since=None, if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None):
        """
        :raises: TypeError when blob client type is not AppendBlob.
        :returns: Blob-updated property dict (Etag, last modified, append offset, committed block count).
        """
