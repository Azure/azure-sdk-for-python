# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
from datetime import datetime, timedelta
import asyncio
import pytest
import requests
from azure.core.pipeline.transport import AioHttpTransport
from azure.core.pipeline.transport import AsyncioRequestsTransport
from multidict import CIMultiDict, CIMultiDictProxy
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ResourceExistsError)

from azure.storage.fileshare import (
    AccessPolicy,
    ShareSasPermissions,
    generate_share_sas,
)
from azure.storage.fileshare.aio import (
    ShareServiceClient,
    ShareDirectoryClient,
    ShareFileClient,
    ShareClient
)
from azure.storage.fileshare._generated.models import DeleteSnapshotsOptionType, ListSharesIncludeType
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer
from _shared.testcase import (
    LogCaptured,
    GlobalStorageAccountPreparer,
    GlobalResourceGroupPreparer
)
from _shared.asynctestcase import AsyncStorageTestCase

# ------------------------------------------------------------------------------
TEST_SHARE_PREFIX = 'share'


# ------------------------------------------------------------------------------


class AiohttpTestTransport(AioHttpTransport):
    """Workaround to vcrpy bug: https://github.com/kevin1024/vcrpy/pull/461
    """
    async def send(self, request, **config):
        response = await super(AiohttpTestTransport, self).send(request, **config)
        if not isinstance(response.headers, CIMultiDictProxy):
            response.headers = CIMultiDictProxy(CIMultiDict(response.internal_response.headers))
            response.content_type = response.headers.get("content-type")
        return response


class StorageShareTest(AsyncStorageTestCase):
    def _setup(self, storage_account, storage_account_key):
        file_url = self.account_url(storage_account, "file")
        credentials = storage_account_key
        self.fsc = ShareServiceClient(account_url=file_url, credential=credentials, transport=AiohttpTestTransport())
        self.test_shares = []

    def _teardown(self, FILE_PATH):
        if os.path.isfile(FILE_PATH):
            try:
                os.remove(FILE_PATH)
            except:
                pass

    async def _delete_shares(self, prefix=TEST_SHARE_PREFIX):
        async for l in self.fsc.list_shares(include_snapshots=True):
            try:
                await self.fsc.delete_share(l.name, delete_snapshots=True)
            except:
                pass
    # --Helpers-----------------------------------------------------------------
    def _get_share_reference(self, prefix=TEST_SHARE_PREFIX):
        share_name = self.get_resource_name(prefix)
        share = self.fsc.get_share_client(share_name)
        self.test_shares.append(share)
        return share

    async def _create_share(self, prefix=TEST_SHARE_PREFIX):
        share_client = self._get_share_reference(prefix)
        share = await share_client.create_share()
        return share_client

    # --Test cases for shares -----------------------------------------
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_share_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share = self._get_share_reference()

        # Act
        created = await share.create_share()

        # Assert
        self.assertTrue(created)
        await self._delete_shares(share.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_share_snapshot_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share = self._get_share_reference()

        # Act
        created = await share.create_share()
        snapshot = await share.create_snapshot()

        # Assert
        self.assertTrue(created)
        self.assertIsNotNone(snapshot['snapshot'])
        self.assertIsNotNone(snapshot['etag'])
        self.assertIsNotNone(snapshot['last_modified'])
        await self._delete_shares(share.share_name)


    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_snapshot_with_metadata_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share = self._get_share_reference()
        metadata = {"test1": "foo", "test2": "bar"}
        metadata2 = {"test100": "foo100", "test200": "bar200"}

        # Act
        created = await share.create_share(metadata=metadata)
        snapshot = await share.create_snapshot(metadata=metadata2)

        share_props = await share.get_share_properties()
        snapshot_client = ShareClient(
            self.account_url(storage_account, "file"),
            share_name=share.share_name,
            snapshot=snapshot,
            credential=storage_account_key
        )
        snapshot_props = await snapshot_client.get_share_properties()
        # Assert
        self.assertTrue(created)
        self.assertIsNotNone(snapshot['snapshot'])
        self.assertIsNotNone(snapshot['etag'])
        self.assertIsNotNone(snapshot['last_modified'])
        self.assertEqual(share_props.metadata, metadata)
        self.assertEqual(snapshot_props.metadata, metadata2)
        await self._delete_shares(share.share_name)


    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_share_with_snapshots_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share = self._get_share_reference()
        await share.create_share()
        snapshot = await share.create_snapshot()

        # Act
        with self.assertRaises(HttpResponseError):
            await share.delete_share()

        deleted = await share.delete_share(delete_snapshots=True)
        self.assertIsNone(deleted)
        await self._delete_shares(share.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_snapshot_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share = self._get_share_reference()
        await share.create_share()
        snapshot = await share.create_snapshot()

        # Act
        with self.assertRaises(HttpResponseError):
            await share.delete_share()

        snapshot_client = ShareClient(
            self.account_url(storage_account, "file"),
            share_name=share.share_name,
            snapshot=snapshot,
            credential=storage_account_key
        )

        deleted = await snapshot_client.delete_share()
        self.assertIsNone(deleted)
        await self._delete_shares(share.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_share_fail_on_exist(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share = self._get_share_reference()

        # Act
        created = await share.create_share()

        # Assert
        self.assertTrue(created)
        await self._delete_shares(share.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_share_with_already_existing_share_fail_on_exist_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share = self._get_share_reference()

        # Act
        created = await share.create_share()
        with self.assertRaises(HttpResponseError):
            await share.create_share()

        # Assert
        self.assertTrue(created)
        await self._delete_shares(share.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_share_with_metadata_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        client = self._get_share_reference()
        created = await client.create_share(metadata=metadata)

        # Assert
        self.assertTrue(created)
        props = await client.get_share_properties()
        self.assertDictEqual(props.metadata, metadata)
        await self._delete_shares(client.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_share_with_quota_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)

        # Act
        client = self._get_share_reference()
        created = await client.create_share(quota=1)

        # Assert
        props = await client.get_share_properties()
        self.assertTrue(created)
        self.assertEqual(props.quota, 1)
        await self._delete_shares(client.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_share_exists_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share = await self._create_share()

        # Act
        exists = await share.get_share_properties()

        # Assert
        self.assertTrue(exists)
        await self._delete_shares(share.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_share_not_exists_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share = self._get_share_reference()

        # Act
        with self.assertRaises(ResourceNotFoundError):
            await share.get_share_properties()

        # Assert
        await self._delete_shares(share.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_share_snapshot_exists_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share = await self._create_share()
        snapshot = await share.create_snapshot()

        # Act
        snapshot_client = self.fsc.get_share_client(share.share_name, snapshot=snapshot)
        exists = await snapshot_client.get_share_properties()

        # Assert
        self.assertTrue(exists)
        await self._delete_shares(share.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_share_snapshot_not_exists_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share = await self._create_share()
        made_up_snapshot = '2017-07-19T06:53:46.0000000Z'

        # Act
        snapshot_client = self.fsc.get_share_client(share.share_name, snapshot=made_up_snapshot)
        with self.assertRaises(ResourceNotFoundError):
            await snapshot_client.get_share_properties()

        # Assert
        await self._delete_shares(share.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_unicode_create_share_unicode_name_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share_name = u'啊齄丂狛狜'

        # Act
        with self.assertRaises(HttpResponseError):
            # not supported - share name must be alphanumeric, lowercase
            client = self.fsc.get_share_client(share_name)
            await client.create_share()

            # Assert
        await self._delete_shares(share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_shares_no_options_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share = await self._create_share()
        # Act
        shares = []
        async for s in self.fsc.list_shares():
            shares.append(s)

        # Assert
        self.assertIsNotNone(shares)
        self.assertGreaterEqual(len(shares), 1)
        self.assertIsNotNone(shares[0])
        self.assertNamedItemInContainer(shares, share.share_name)
        await self._delete_shares(share.share_name)

    @pytest.mark.live_test_only
    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, sku='premium_LRS', name_prefix='pyacrstorage', kind='FileStorage')
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_shares_no_options_for_premium_account_async(self, resource_group, location, storage_account, storage_account_key):
        # TODO: add recordings to this test
        self._setup(storage_account, storage_account_key)
        share = await self._create_share()

        # Act
        shares = []
        async for s in self.fsc.list_shares():
            shares.append(s)

        # Assert
        self.assertIsNotNone(shares)
        self.assertGreaterEqual(len(shares), 1)
        self.assertIsNotNone(shares[0])
        self.assertIsNotNone(shares[0].provisioned_iops)
        self.assertIsNotNone(shares[0].provisioned_ingress_mbps)
        self.assertIsNotNone(shares[0].provisioned_egress_mbps)
        self.assertIsNotNone(shares[0].next_allowed_quota_downgrade_time)
        await self._delete_shares(share.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_shares_with_snapshot_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share = self._get_share_reference()
        await share.create_share()
        snapshot1 = await share.create_snapshot()
        snapshot2 = await share.create_snapshot()

        # Act
        shares = self.fsc.list_shares(include_snapshots=True)

        # Assert
        self.assertIsNotNone(shares)
        all_shares = []
        async for s in shares:
            all_shares.append(s)
        self.assertEqual(len(all_shares), 3)
        self.assertNamedItemInContainer(all_shares, share.share_name)
        self.assertNamedItemInContainer(all_shares, snapshot1['snapshot'])
        self.assertNamedItemInContainer(all_shares, snapshot2['snapshot'])
        await self._delete_shares(share.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_shares_with_prefix_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share = self._get_share_reference()
        await share.create_share()

        # Act
        shares = []
        async for s in self.fsc.list_shares(name_starts_with=share.share_name):
            shares.append(s)

        # Assert
        self.assertEqual(len(shares), 1)
        self.assertIsNotNone(shares[0])
        self.assertEqual(shares[0].name, share.share_name)
        self.assertIsNone(shares[0].metadata)
        await self._delete_shares(share.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_shares_with_include_metadata_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        metadata = {'hello': 'world', 'number': '42'}
        share = self._get_share_reference()
        await share.create_share(metadata=metadata)

        # Act
        shares = []
        async for s in self.fsc.list_shares(share.share_name, include_metadata=True):
            shares.append(s)

        # Assert
        self.assertIsNotNone(shares)
        self.assertGreaterEqual(len(shares), 1)
        self.assertIsNotNone(shares[0])
        self.assertNamedItemInContainer(shares, share.share_name)
        self.assertDictEqual(shares[0].metadata, metadata)

        await self._delete_shares(share.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_shares_with_num_results_and_marker_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        prefix = 'listshare'
        share_names = []
        for i in range(0, 4):
            share = await self._create_share(prefix + str(i))
            share_names.append(share.share_name)

        share_names.sort()

        # Act
        generator1 = self.fsc.list_shares(prefix, results_per_page=2).by_page()
        shares1 = []
        async for s in await generator1.__anext__():
            shares1.append(s)
        generator2 = self.fsc.list_shares(
            prefix, results_per_page=2).by_page(continuation_token=generator1.continuation_token)
        shares2 = []
        async for s in await generator2.__anext__():
            shares2.append(s)

        # Assert
        self.assertIsNotNone(shares1)
        self.assertEqual(len(shares1), 2)
        self.assertNamedItemInContainer(shares1, share_names[0])
        self.assertNamedItemInContainer(shares1, share_names[1])
        self.assertIsNotNone(shares2)
        self.assertEqual(len(shares2), 2)
        self.assertNamedItemInContainer(shares2, share_names[2])
        self.assertNamedItemInContainer(shares2, share_names[3])
        await self._delete_shares(prefix)


    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_share_metadata_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share = await self._create_share()
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        await share.set_share_metadata(metadata)

        # Assert
        props = await share.get_share_properties()
        md = props.metadata
        self.assertDictEqual(md, metadata)
        await self._delete_shares(share.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_share_metadata_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        client = self._get_share_reference()
        created = await client.create_share(metadata=metadata)

        # Assert
        self.assertTrue(created)
        props = await client.get_share_properties()
        self.assertDictEqual(props.metadata, metadata)
        await self._delete_shares(client.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_share_metadata_with_snapshot_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        client = self._get_share_reference()
        created = await client.create_share(metadata=metadata)
        snapshot = await client.create_snapshot()
        snapshot_client = self.fsc.get_share_client(client.share_name, snapshot=snapshot)

        # Assert
        self.assertTrue(created)
        props = await snapshot_client.get_share_properties()
        self.assertDictEqual(props.metadata, metadata)
        await self._delete_shares(client.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_share_properties_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share = await self._create_share()
        await share.set_share_quota(1)

        # Act
        props = await share.get_share_properties()

        # Assert
        self.assertIsNotNone(props)
        self.assertEqual(props.quota, 1)
        await self._delete_shares(share.share_name)

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, sku='premium_LRS', name_prefix='pyacrstorage', kind='FileStorage')
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_share_properties_for_premium_account_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share = await self._create_share()

        # Act
        props = await share.get_share_properties()

        # Assert
        self.assertIsNotNone(props)
        self.assertIsNotNone(props.quota)
        self.assertIsNotNone(props.quota)
        self.assertIsNotNone(props.provisioned_iops)
        self.assertIsNotNone(props.provisioned_ingress_mbps)
        self.assertIsNotNone(props.provisioned_egress_mbps)
        self.assertIsNotNone(props.next_allowed_quota_downgrade_time)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_share_with_existing_share_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share = self._get_share_reference()
        await share.create_share()

        # Act
        deleted = await share.delete_share()

        # Assert
        self.assertIsNone(deleted)
        await self._delete_shares(share.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_share_with_existing_share_fail_not_exist_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        client = self._get_share_reference()

        # Act
        with LogCaptured(self) as log_captured:
            with self.assertRaises(HttpResponseError):
                await client.delete_share()

            log_as_str = log_captured.getvalue()
        await self._delete_shares(client.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_share_with_non_existing_share_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        client = self._get_share_reference()

        # Act
        with LogCaptured(self) as log_captured:
            with self.assertRaises(HttpResponseError):
                deleted = await client.delete_share()

            log_as_str = log_captured.getvalue()
            self.assertTrue('ERROR' not in log_as_str)
        await self._delete_shares(client.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_share_with_non_existing_share_fail_not_exist_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        client = self._get_share_reference()

        # Act
        with LogCaptured(self) as log_captured:
            with self.assertRaises(HttpResponseError):
                await client.delete_share()

            log_as_str = log_captured.getvalue()
        await self._delete_shares(client.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_share_stats_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share = self._get_share_reference()
        await share.create_share()

        # Act
        share_usage = await share.get_share_stats()

        # Assert
        self.assertEqual(share_usage, 0)
        await self._delete_shares(share.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_share_acl_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share = self._get_share_reference()
        await share.create_share()

        # Act
        resp = await share.set_share_access_policy(signed_identifiers=dict())

        # Assert
        acl = await share.get_share_access_policy()
        self.assertIsNotNone(acl)
        await self._delete_shares(share.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_share_acl_with_empty_signed_identifiers_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share = self._get_share_reference()
        await share.create_share()

        # Act
        resp = await share.set_share_access_policy(dict())

        # Assert
        acl = await share.get_share_access_policy()
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.get('signed_identifiers')), 0)
        await self._delete_shares(share.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_share_acl_with_signed_identifiers_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share = self._get_share_reference()
        await share.create_share()

        # Act
        identifiers = dict()
        identifiers['testid'] = AccessPolicy(
            permission=ShareSasPermissions(write=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            start=datetime.utcnow() - timedelta(minutes=1),
        )

        resp = await share.set_share_access_policy(identifiers)

        # Assert
        acl = await share.get_share_access_policy()
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl['signed_identifiers']), 1)
        self.assertEqual(acl['signed_identifiers'][0].id, 'testid')
        await self._delete_shares(share.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_share_acl_too_many_ids_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share = self._get_share_reference()
        await share.create_share()

        # Act
        identifiers = dict()
        for i in range(0, 6):
            identifiers['id{}'.format(i)] = AccessPolicy()

        # Assert
        with self.assertRaises(ValueError) as e:
            await share.set_share_access_policy(identifiers)
        self.assertEqual(
            str(e.exception),
            'Too many access policies provided. The server does not support setting more than 5 access policies on a single resource.'
        )
        await self._delete_shares(share.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_directories_and_files_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share = await self._create_share()
        dir0 = share.get_directory_client()
        await dir0.upload_file('file1', 'data1')
        dir1 = share.get_directory_client('dir1')
        await dir1.create_directory()
        await dir1.upload_file('file2', 'data2')
        dir2 = share.get_directory_client('dir2')
        await dir2.create_directory()

        # Act
        resp = []
        async for d in share.list_directories_and_files():
            resp.append(d)

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), 3)
        self.assertIsNotNone(resp[0])
        self.assertNamedItemInContainer(resp, 'dir1')
        self.assertNamedItemInContainer(resp, 'dir2')
        self.assertNamedItemInContainer(resp, 'file1')
        await self._delete_shares(share)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_directories_and_files_with_snapshot_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share_name = await self._create_share()
        dir1 = share_name.get_directory_client('dir1')
        await dir1.create_directory()
        dir2 = share_name.get_directory_client('dir2')
        await dir2.create_directory()
        snapshot1 = await share_name.create_snapshot()
        dir3 = share_name.get_directory_client('dir3')
        await dir3.create_directory()
        file1 = share_name.get_file_client('file1')
        await file1.upload_file('data')


        # Act
        snapshot_client = self.fsc.get_share_client(share_name.share_name, snapshot=snapshot1)
        resp = []
        async for d in snapshot_client.list_directories_and_files():
            resp.append(d)

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), 2)
        self.assertIsNotNone(resp[0])
        self.assertNamedItemInContainer(resp, 'dir1')
        self.assertNamedItemInContainer(resp, 'dir2')
        await self._delete_shares(share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_directories_and_files_with_num_results_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share_name = await self._create_share()
        dir1 = await share_name.create_directory('dir1')
        root = share_name.get_directory_client()
        await root.upload_file('filea1', '1024')
        await root.upload_file('filea2', '1024')
        await root.upload_file('filea3', '1024')
        await root.upload_file('fileb1', '1024')

        # Act
        result = share_name.list_directories_and_files(results_per_page=2).by_page()
        results = []
        async for r in await result.__anext__():
            results.append(r)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(len(results), 2)
        self.assertNamedItemInContainer(results, 'dir1')
        self.assertNamedItemInContainer(results, 'filea1')
        await self._delete_shares(share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_directories_and_files_with_num_results_and_marker_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share_name = await self._create_share()
        dir1 = share_name.get_directory_client('dir1')
        await dir1.create_directory()
        await dir1.upload_file('filea1', '1024')
        await dir1.upload_file('filea2', '1024')
        await dir1.upload_file('filea3', '1024')
        await dir1.upload_file('fileb1', '1024')

        # Act
        generator1 = share_name.list_directories_and_files(
            'dir1', results_per_page=2).by_page()
        result1 = []
        async for r in await generator1.__anext__():
            result1.append(r)

        generator2 = share_name.list_directories_and_files(
            'dir1', results_per_page=2).by_page(continuation_token=generator1.continuation_token)
        result2 = []
        async for r in await generator2.__anext__():
            result2.append(r)

        # Assert
        self.assertEqual(len(result1), 2)
        self.assertEqual(len(result2), 2)
        self.assertNamedItemInContainer(result1, 'filea1')
        self.assertNamedItemInContainer(result1, 'filea2')
        self.assertNamedItemInContainer(result2, 'filea3')
        self.assertNamedItemInContainer(result2, 'fileb1')
        self.assertEqual(generator2.continuation_token, None)
        await self._delete_shares(share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_directories_and_files_with_prefix_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share = await self._create_share()
        dir1 = await share.create_directory('dir1')
        await share.create_directory('dir1/pref_dir3')
        await share.create_directory('dir2')

        root = share.get_directory_client()
        await root.upload_file('file1', '1024')
        await dir1.upload_file('pref_file2', '1025')
        await dir1.upload_file('file3', '1025')

        # Act
        resp = []
        async for d in share.list_directories_and_files('dir1', name_starts_with='pref'):
            resp.append(d)

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), 2)
        self.assertIsNotNone(resp[0])
        self.assertNamedItemInContainer(resp, 'pref_file2')
        self.assertNamedItemInContainer(resp, 'pref_dir3')
        await self._delete_shares(share)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_shared_access_share_async(self, resource_group, location, storage_account, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        if not self.is_live:
            return

        self._setup(storage_account, storage_account_key)
        file_name = 'file1'
        dir_name = 'dir1'
        data = b'hello world'

        share = await self._create_share()
        dir1 = await share.create_directory(dir_name)
        await dir1.upload_file(file_name, data)

        token = generate_share_sas(
            share.account_name,
            share.share_name,
            share.credential.account_key,
            expiry=datetime.utcnow() + timedelta(hours=1),
            permission=ShareSasPermissions(read=True),
        )
        sas_client = ShareFileClient(
            self.account_url(storage_account, "file"),
            share_name=share.share_name,
            file_path=dir_name + '/' + file_name,
            credential=token,
        )

        # Act
        response = requests.get(sas_client.url)

        # Assert
        self.assertTrue(response.ok)
        self.assertEqual(data, response.content)
        await self._delete_shares(share.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_permission_for_share(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        user_given_permission = "O:S-1-5-21-2127521184-1604012920-1887927527-21560751G:S-1-5-21-2127521184-" \
                                "1604012920-1887927527-513D:AI(A;;FA;;;SY)(A;;FA;;;BA)(A;;0x1200a9;;;" \
                                "S-1-5-21-397955417-626881126-188441444-3053964)"
        share_client = await self._create_share()
        permission_key = await share_client.create_permission_for_share(user_given_permission)
        self.assertIsNotNone(permission_key)

        server_returned_permission = await share_client.get_permission_for_share(permission_key)
        self.assertIsNotNone(server_returned_permission)

        permission_key2 = await share_client.create_permission_for_share(server_returned_permission)
        # the permission key obtained from user_given_permission should be the same as the permission key obtained from
        # server returned permission
        self.assertEqual(permission_key, permission_key2)
        await self._delete_shares(share_client.share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_transport_closed_only_once_async(self, resource_group, location, storage_account, storage_account_key):
        if not self.is_live:
            return
        self._setup(storage_account, storage_account_key)
        transport = AioHttpTransport()
        url = self.account_url(storage_account, "file")
        credential = storage_account_key
        prefix = TEST_SHARE_PREFIX
        share_name = self.get_resource_name(prefix)
        async with ShareServiceClient(url, credential=credential, transport=transport) as fsc:
            await fsc.get_service_properties()
            assert transport.session is not None
            async with fsc.get_share_client(share_name) as fc:
                assert transport.session is not None
            await fsc.get_service_properties()
            assert transport.session is not None
        await self._delete_shares(share_name)

    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_directory_from_share_async(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        share = await self._create_share()
        await share.create_directory('dir1')
        await share.create_directory('dir2')
        await share.create_directory('dir3')

        # Act
        resp = []
        async for d in share.list_directories_and_files():
            resp.append(d)
        self.assertEqual(len(resp), 3)

        await share.delete_directory('dir3')

        # Assert
        resp = []
        async for d in share.list_directories_and_files():
            resp.append(d)
        self.assertEqual(len(resp), 2)
        await self._delete_shares(share.share_name)

