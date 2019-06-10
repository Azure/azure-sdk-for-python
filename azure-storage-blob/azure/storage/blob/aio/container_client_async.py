# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from ..common import BlobType


class ContainerClient(object):

    def __init__(self, url, container=None, credentials=None, configuration=None):
        pass

    @staticmethod
    def create_configuration(**kwargs):
        pass

    def generate_shared_access_signature(
            self, resource_types, permission, expiry,
            start=None, ip=None, protocol=None):
        pass

    async def create_container(self, metadata=None, public_access=None, timeout=None):
        """
        :returns: None
        """

    async def delete_container(
            self, lease=None, if_modified_since=None, if_unmodified_since=None,
            if_match=None, if_none_match=None, timeout=None):
        """
        :returns: None
        """

    async def acquire_lease(
            self, lease_duration=-1, proposed_lease_id=None, if_modified_since=None,
            if_unmodified_since=None, if_match=None, if_none_match=None, timeout=None):
        """
        :returns: A LeaseClient object, that can be run in a context manager.
        """

    async def break_lease(
            self, lease_break_period=None, if_modified_since=None, if_unmodified_since=None,
            if_match=None, if_none_match=None, timeout=None):
        """
        :returns: Approximate time remaining in the lease period, in seconds.
        """

    async def get_account_infomation(self, timeout=None):
        """
        :returns: A dict of account information (SKU and account type).
        """

    async def get_container_properties(self, lease=None, timeout=None):
        """
        :returns: ContainerProperties
        """

    async def set_container_metadata(self, metadata=None, lease=None, if_modified_since=None, timeout=None):
        """
        :returns: Container-updated property dict (Etag and last modified).
        """

    async def get_container_acl(self, lease=None, timeout=None):
        """
        :returns: Access policy information in a dict.
        """

    async def set_container_acl(
            self, signed_identifiers=None, public_access=None, lease=None,
            if_modified_since=None, if_unmodified_since=None, timeout=None):
        """
        :returns: Container-updated property dict (Etag and last modified).
        """

    async def list_blobs(self, prefix=None, include=None, timeout=None):
        """
        :returns: An iterable (auto-paging) response of BlobProperties.
        """

    async def walk_blob_propertes(self, prefix=None, include=None, delimiter="/", timeout=None):
        """
        :returns: A generator that honors directory hierarchy.
        """

    async def get_blob_client(self, blob, snapshot=None):
        """
        :returns: A BlobClient.
        """
