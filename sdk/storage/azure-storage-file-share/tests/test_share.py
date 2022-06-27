# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import time
import unittest
from datetime import datetime, timedelta

import pytest
import requests
from azure.core.pipeline.transport import RequestsTransport
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

from azure.storage.fileshare import (
    AccessPolicy,
    AccountSasPermissions,
    ResourceTypes,
    ShareAccessTier,
    ShareClient,
    ShareFileClient,
    ShareSasPermissions,
    ShareServiceClient,
    ShareProtocols,
    ShareRootSquash,
    generate_account_sas,
    generate_share_sas,)

from devtools_testutils.storage import StorageTestCase, LogCaptured
from settings.testcase import FileSharePreparer

# ------------------------------------------------------------------------------
TEST_SHARE_PREFIX = 'share'
# ------------------------------------------------------------------------------

class StorageShareTest(StorageTestCase):
    def _setup(self, storage_account_name, storage_account_key):
        file_url = self.account_url(storage_account_name, "file")
        credentials = storage_account_key
        self.fsc = ShareServiceClient(account_url=file_url, credential=credentials)
        self.test_shares = []

    def _teardown(self, FILE_PATH):
        if os.path.isfile(FILE_PATH):
            try:
                os.remove(FILE_PATH)
            except:
                pass
    # --Helpers-----------------------------------------------------------------
    def _get_share_reference(self, prefix=TEST_SHARE_PREFIX):
        share_name = self.get_resource_name(prefix)
        share = self.fsc.get_share_client(share_name)
        self.test_shares.append(share_name)
        return share

    def _create_share(self, prefix=TEST_SHARE_PREFIX, **kwargs):
        share_client = self._get_share_reference(prefix)
        try:
            share_client.create_share(**kwargs)
        except:
            pass
        return share_client

    def _create_share_if_not_exists(self, prefix=TEST_SHARE_PREFIX, **kwargs):
        share_client = self._get_share_reference(prefix)
        return share_client.create_share_if_not_exists(**kwargs)
    
    def _delete_shares(self, prefix=TEST_SHARE_PREFIX):
        for l in self.fsc.list_shares(include_snapshots=True):
            try:
                self.fsc.delete_share(l.name, delete_snapshots=True)
            except:
                pass

    # --Test cases for shares -----------------------------------------
    def test_create_share_client(self):
        share_client = ShareClient.from_share_url("http://127.0.0.1:11002/account/customized/path/share?snapshot=baz&", credential={"account_name": "myaccount", "account_key": "key"})
        self.assertEqual(share_client.share_name, "share")
        self.assertEqual(share_client.snapshot, "baz")

        share_client = ShareClient.from_share_url("http://127.0.0.1:11002/account/share?snapshot=baz&", credential="credential")
        self.assertEqual(share_client.share_name, "share")
        self.assertEqual(share_client.snapshot, "baz")

    @FileSharePreparer()
    def test_create_share(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()

        # Act
        created = self._create_share()

        # Assert
        self.assertTrue(created)
        self._delete_shares(share.share_name)

    @FileSharePreparer()
    def test_create_share_snapshot(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()

        # Act
        created = share.create_share()
        snapshot = share.create_snapshot()

        # Assert
        self.assertTrue(created)
        self.assertIsNotNone(snapshot['snapshot'])
        self.assertIsNotNone(snapshot['etag'])
        self.assertIsNotNone(snapshot['last_modified'])
        self._delete_shares(share.share_name)

    @FileSharePreparer()
    def test_create_snapshot_with_metadata(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()
        metadata = {"test1": "foo", "test2": "bar"}
        metadata2 = {"test100": "foo100", "test200": "bar200"}

        # Act
        created = share.create_share(metadata=metadata)
        snapshot = share.create_snapshot(metadata=metadata2)

        share_props = share.get_share_properties()
        snapshot_client = ShareClient(
            self.account_url(storage_account_name, "file"),
            share_name=share.share_name,
            snapshot=snapshot,
            credential=storage_account_key
        )
        snapshot_props = snapshot_client.get_share_properties()
        # Assert
        self.assertTrue(created)
        self.assertIsNotNone(snapshot['snapshot'])
        self.assertIsNotNone(snapshot['etag'])
        self.assertIsNotNone(snapshot['last_modified'])
        self.assertEqual(share_props.metadata, metadata)
        self.assertEqual(snapshot_props.metadata, metadata2)
        self._delete_shares(share.share_name)

    @FileSharePreparer()
    def test_delete_share_with_snapshots(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()
        share.create_share()
        snapshot = share.create_snapshot()

        # Act
        with self.assertRaises(HttpResponseError):
            share.delete_share()

        deleted = share.delete_share(delete_snapshots=True)
        self.assertIsNone(deleted)
        self._delete_shares()

    @pytest.mark.playback_test_only
    @FileSharePreparer()
    def test_undelete_share(self, storage_account_name, storage_account_key):
        # share soft delete should enabled by SRP call or use armclient, so make this test as playback only.
        self._setup(storage_account_name, storage_account_key)
        share_client = self._create_share(prefix="sharerestore")

        # Act
        share_client.delete_share()
        # to make sure the share deleted
        with self.assertRaises(ResourceNotFoundError):
            share_client.get_share_properties()

        share_list = list(self.fsc.list_shares(include_deleted=True, include_snapshots=True, include_metadata=True))
        self.assertTrue(len(share_list) >= 1)

        for share in share_list:
            # find the deleted share and restore it
            if share.deleted and share.name == share_client.share_name:
                if self.is_live:
                    time.sleep(60)
                restored_share_client = self.fsc.undelete_share(share.name, share.version)

                # to make sure the deleted share is restored
                props = restored_share_client.get_share_properties()
                self.assertIsNotNone(props)

    @FileSharePreparer()
    def test_lease_share_acquire_and_release(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self._create_share('test')
        # Act
        lease = share_client.acquire_lease()
        lease.release()
        # Assert

    @FileSharePreparer()
    def test_acquire_lease_on_sharesnapshot(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference("testshare1")

        # Act
        share.create_share()
        snapshot = share.create_snapshot()

        snapshot_client = ShareClient(
            self.account_url(storage_account_name, "file"),
            share_name=share.share_name,
            snapshot=snapshot,
            credential=storage_account_key
        )

        share_lease = share.acquire_lease()
        share_snapshot_lease = snapshot_client.acquire_lease()

        # Assert
        with self.assertRaises(HttpResponseError):
            share.get_share_properties(lease=share_snapshot_lease)

        with self.assertRaises(HttpResponseError):
            snapshot_client.get_share_properties(lease=share_lease)

        self.assertIsNotNone(snapshot['snapshot'])
        self.assertIsNotNone(snapshot['etag'])
        self.assertIsNotNone(snapshot['last_modified'])
        self.assertIsNotNone(share_lease)
        self.assertIsNotNone(share_snapshot_lease)
        self.assertNotEqual(share_lease, share_snapshot_lease)

        share_snapshot_lease.release()
        share_lease.release()
        self._delete_shares(share.share_name)

    @FileSharePreparer()
    def test_lease_share_renew(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self._create_share('test')
        lease = share_client.acquire_lease(lease_duration=15)
        self.sleep(10)
        lease_id_start = lease.id

        # Act
        lease.renew()

        # Assert
        self.assertEqual(lease.id, lease_id_start)
        self.sleep(5)
        with self.assertRaises(HttpResponseError):
            share_client.delete_share()
        self.sleep(10)
        share_client.delete_share()

    @FileSharePreparer()
    def test_lease_share_with_duration(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self._create_share('test')

        # Act
        lease = share_client.acquire_lease(lease_duration=15)

        # Assert
        with self.assertRaises(HttpResponseError):
            share_client.acquire_lease()
        self.sleep(17)
        share_client.acquire_lease()

    @FileSharePreparer()
    def test_lease_share_twice(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self._create_share('test')

        # Act
        lease = share_client.acquire_lease(lease_duration=15)

        # Assert
        lease2 = share_client.acquire_lease(lease_id=lease.id)
        self.assertEqual(lease.id, lease2.id)

    @FileSharePreparer()
    def test_lease_share_with_proposed_lease_id(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self._create_share('test')

        # Act
        proposed_lease_id = '55e97f64-73e8-4390-838d-d9e84a374321'
        lease = share_client.acquire_lease(lease_id=proposed_lease_id)

        # Assert
        self.assertEqual(proposed_lease_id, lease.id)

    @FileSharePreparer()
    def test_lease_share_change_lease_id(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self._create_share('test')

        # Act
        lease_id = '29e0b239-ecda-4f69-bfa3-95f6af91464c'
        lease = share_client.acquire_lease()
        lease_id1 = lease.id
        lease.change(proposed_lease_id=lease_id)
        lease.renew()
        lease_id2 = lease.id

        # Assert
        self.assertIsNotNone(lease_id1)
        self.assertIsNotNone(lease_id2)
        self.assertNotEqual(lease_id1, lease_id)
        self.assertEqual(lease_id2, lease_id)

    @FileSharePreparer()
    def test_set_share_metadata_with_lease_id(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self._create_share('test')
        metadata = {'hello': 'world', 'number': '43'}
        lease_id = share_client.acquire_lease()

        # Act
        share_client.set_share_metadata(metadata, lease=lease_id)

        # Assert
        md = share_client.get_share_properties().metadata
        self.assertDictEqual(md, metadata)

    @FileSharePreparer()
    def test_get_share_metadata_with_lease_id(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self._create_share('test')
        metadata = {'hello': 'world', 'number': '43'}
        share_client.set_share_metadata(metadata)
        lease_id = share_client.acquire_lease()

        # Act
        md = share_client.get_share_properties(lease=lease_id).metadata

        # Assert
        self.assertDictEqual(md, metadata)

    @FileSharePreparer()
    def test_get_share_properties_with_lease_id(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self._create_share('test')
        metadata = {'hello': 'world', 'number': '43'}
        share_client.set_share_metadata(metadata)
        lease_id = share_client.acquire_lease()

        # Act
        props = share_client.get_share_properties(lease=lease_id)
        lease_id.break_lease()

        # Assert
        self.assertIsNotNone(props)
        self.assertDictEqual(props.metadata, metadata)
        self.assertEqual(props.lease.duration, 'infinite')
        self.assertEqual(props.lease.state, 'leased')
        self.assertEqual(props.lease.status, 'locked')

    @FileSharePreparer()
    def test_get_share_acl_with_lease_id(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self._create_share('test')
        lease_id = share_client.acquire_lease()

        # Act
        acl = share_client.get_share_access_policy(lease=lease_id)

        # Assert
        self.assertIsNotNone(acl)
        self.assertIsNone(acl.get('public_access'))

    @FileSharePreparer()
    def test_set_share_acl_with_lease_id(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self._create_share('test')
        lease_id = share_client.acquire_lease()

        # Act
        access_policy = AccessPolicy(permission=ShareSasPermissions(read=True),
                                     expiry=datetime.utcnow() + timedelta(hours=1),
                                     start=datetime.utcnow())
        signed_identifiers = {'testid': access_policy}

        share_client.set_share_access_policy(signed_identifiers, lease=lease_id)

        # Assert
        acl = share_client.get_share_access_policy()
        self.assertIsNotNone(acl)
        self.assertIsNone(acl.get('public_access'))

    @FileSharePreparer()
    def test_lease_share_break_period(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self._create_share('test')

        # Act
        lease = share_client.acquire_lease(lease_duration=15)

        # Assert
        lease.break_lease(lease_break_period=5)
        self.sleep(6)
        with self.assertRaises(HttpResponseError):
            share_client.delete_share(lease=lease)

    @FileSharePreparer()
    def test_delete_share_with_lease_id(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self._create_share('test')
        lease = share_client.acquire_lease(lease_duration=15)

        # Assert
        with self.assertRaises(HttpResponseError):
            share_client.delete_share()

        # Act
        deleted = share_client.delete_share(lease=lease)

        # Assert
        self.assertIsNone(deleted)
        with self.assertRaises(ResourceNotFoundError):
            share_client.get_share_properties()

    @pytest.mark.playback_test_only
    @FileSharePreparer()
    def test_restore_to_existing_share(self, storage_account_name, storage_account_key):
        # share soft delete should enabled by SRP call or use armclient, so make this test as playback only.
        self._setup(storage_account_name, storage_account_key)
        # Act
        share_client = self._create_share()
        share_client.delete_share()
        # to make sure the share deleted
        with self.assertRaises(ResourceNotFoundError):
            share_client.get_share_properties()

        # create a share with the same name as the deleted one
        if self.is_live:
            time.sleep(30)
        share_client.create_share()

        share_list = list(self.fsc.list_shares(include_deleted=True))
        self.assertTrue(len(share_list) >= 1)

        for share in share_list:
            # find the deleted share and restore it
            if share.deleted and share.name == share_client.share_name:
                with self.assertRaises(HttpResponseError):
                    self.fsc.undelete_share(share.name, share.version)

    @FileSharePreparer()
    def test_delete_snapshot(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()
        share.create_share()
        snapshot = share.create_snapshot()

        # Act
        with self.assertRaises(HttpResponseError):
            share.delete_share()

        snapshot_client = ShareClient(
            self.account_url(storage_account_name, "file"),
            share_name=share.share_name,
            snapshot=snapshot,
            credential=storage_account_key
        )

        deleted = snapshot_client.delete_share()
        self.assertIsNone(deleted)
        self._delete_shares()

    @FileSharePreparer()
    def test_create_share_fail_on_exist(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()

        # Act
        created = share.create_share()

        # Assert
        self.assertTrue(created)
        self._delete_shares()

    @FileSharePreparer()
    def test_create_share_with_already_existing_share_fail_on_exist(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()

        # Act
        created = share.create_share()
        with self.assertRaises(HttpResponseError):
            share.create_share()

        # Assert
        self.assertTrue(created)
        self._delete_shares()

    @FileSharePreparer()
    def test_create_share_with_metadata(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        client = self._get_share_reference()
        created = client.create_share(metadata=metadata)

        # Assert
        self.assertTrue(created)
        md = client.get_share_properties().metadata
        self.assertDictEqual(md, metadata)
        self._delete_shares()

    @FileSharePreparer()
    def test_create_share_with_quota(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)

        # Act
        client = self._get_share_reference()
        created = client.create_share(quota=1)

        # Assert
        props = client.get_share_properties()
        self.assertTrue(created)
        self.assertEqual(props.quota, 1)
        self._delete_shares()

    @FileSharePreparer()
    def test_create_share_with_access_tier(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)

        # Act
        client = self._get_share_reference()
        created = client.create_share(access_tier="Hot")

        # Assert
        props = client.get_share_properties()
        self.assertTrue(created)
        self.assertEqual(props.access_tier, "Hot")
        self._delete_shares()

    @FileSharePreparer()
    def test_share_exists(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share = self._create_share()

        # Act
        exists = share.get_share_properties()

        # Assert
        self.assertTrue(exists)
        self._delete_shares()

    @FileSharePreparer()
    def test_share_not_exists(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()

        # Act
        with self.assertRaises(ResourceNotFoundError):
            share.get_share_properties()

        # Assert
        self._delete_shares()

    @FileSharePreparer()
    def test_share_snapshot_exists(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share = self._create_share()
        snapshot = share.create_snapshot()

        # Act
        snapshot_client = self.fsc.get_share_client(share.share_name, snapshot=snapshot)
        exists = snapshot_client.get_share_properties()

        # Assert
        self.assertTrue(exists)
        self._delete_shares()

    @FileSharePreparer()
    def test_share_snapshot_not_exists(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share = self._create_share()
        made_up_snapshot = '2017-07-19T06:53:46.0000000Z'

        # Act
        snapshot_client = self.fsc.get_share_client(share.share_name, snapshot=made_up_snapshot)
        with self.assertRaises(ResourceNotFoundError):
            snapshot_client.get_share_properties()

        # Assert
        self._delete_shares()

    @FileSharePreparer()
    def test_unicode_create_share_unicode_name(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_name = u'啊齄丂狛狜'

        # Act
        with self.assertRaises(HttpResponseError):
            # not supported - share name must be alphanumeric, lowercase
            client = self.fsc.get_share_client(share_name)
            client.create_share()

            # Assert
        self._delete_shares()

    @FileSharePreparer()
    def test_list_shares_no_options(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share = self._create_share()
        # Act
        shares = list(self.fsc.list_shares())

        # Assert
        self.assertIsNotNone(shares)
        self.assertGreaterEqual(len(shares), 1)
        self.assertIsNotNone(shares[0])
        self.assertNamedItemInContainer(shares, share.share_name)
        self._delete_shares()

    @FileSharePreparer()
    def test_list_shares_no_options_for_premium_account(self, premium_storage_file_account_name, premium_storage_file_account_key):
        self._setup(premium_storage_file_account_name, premium_storage_file_account_key)
        share = self._create_share()

        # Act
        shares = list(self.fsc.list_shares())

        # Assert
        self.assertIsNotNone(shares)
        self.assertGreaterEqual(len(shares), 1)
        self.assertIsNotNone(shares[0])
        self.assertIsNotNone(shares[0].provisioned_iops)
        self.assertIsNotNone(shares[0].provisioned_ingress_mbps)
        self.assertIsNotNone(shares[0].provisioned_egress_mbps)
        self.assertIsNotNone(shares[0].next_allowed_quota_downgrade_time)
        self.assertIsNotNone(shares[0].provisioned_bandwidth)
        self._delete_shares()

    @FileSharePreparer()
    def test_list_shares_leased_share(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share = self._create_share("test1")

        # Act
        lease = share.acquire_lease()
        resp = list(self.fsc.list_shares())

        # Assert
        self.assertIsNotNone(resp)
        self.assertGreaterEqual(len(resp), 1)
        self.assertIsNotNone(resp[0])
        self.assertEqual(resp[0].lease.duration, 'infinite')
        self.assertEqual(resp[0].lease.status, 'locked')
        self.assertEqual(resp[0].lease.state, 'leased')
        lease.release()
        self._delete_shares()

    @pytest.mark.playback_test_only
    @FileSharePreparer()
    def test_list_shares_with_snapshot(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        #share = self._get_share_reference()
        share = self._create_share('random')
        snapshot1 = share.create_snapshot()
        snapshot2 = share.create_snapshot()

        # Act
        shares = self.fsc.list_shares(include_snapshots=True)
        # Assert
        self.assertIsNotNone(shares)
        all_shares = list(shares)
        self.assertEqual(len(all_shares), 3)
        self.assertNamedItemInContainer(all_shares, share.share_name)
        self.assertNamedItemInContainer(all_shares, snapshot1['snapshot'])
        self.assertNamedItemInContainer(all_shares, snapshot2['snapshot'])
        share.delete_share(delete_snapshots=True)
        self._delete_shares()

    @pytest.mark.playback_test_only
    @FileSharePreparer()
    def test_list_shares_with_prefix(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()
        share.create_share()

        # Act
        shares = list(self.fsc.list_shares(name_starts_with=share.share_name))

        # Assert
        self.assertEqual(len(shares), 1)
        self.assertIsNotNone(shares[0])
        self.assertEqual(shares[0].name, share.share_name)
        self.assertIsNone(shares[0].metadata)
        self._delete_shares()

    @FileSharePreparer()
    def test_list_shares_with_include_metadata(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        metadata = {'hello': 'world', 'number': '42'}
        share = self._get_share_reference()
        share.create_share(metadata=metadata)

        # Act

        shares = list(self.fsc.list_shares(share.share_name, include_metadata=True))

        # Assert
        self.assertIsNotNone(shares)
        self.assertGreaterEqual(len(shares), 1)
        self.assertIsNotNone(shares[0])
        self.assertNamedItemInContainer(shares, share.share_name)
        self.assertDictEqual(shares[0].metadata, metadata)
        self._delete_shares()

    @FileSharePreparer()
    def test_list_shares_with_num_results_and_marker(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        prefix = 'listshare'
        share_names = []
        for i in range(0, 4):
            share_names.append(self._create_share(prefix + str(i)).share_name)

        #share_names.sort()

        # Act
        generator1 = self.fsc.list_shares(prefix, results_per_page=2).by_page()
        shares1 = list(next(generator1))

        generator2 = self.fsc.list_shares(
            prefix, results_per_page=2).by_page(continuation_token=generator1.continuation_token)
        shares2 = list(next(generator2))

        # Assert
        self.assertIsNotNone(shares1)
        self.assertEqual(len(shares1), 2)
        self.assertNamedItemInContainer(shares1, share_names[0])
        self.assertNamedItemInContainer(shares1, share_names[1])
        self.assertIsNotNone(shares2)
        self.assertEqual(len(shares2), 2)
        self.assertNamedItemInContainer(shares2, share_names[2])
        self.assertNamedItemInContainer(shares2, share_names[3])
        self._delete_shares()

    @pytest.mark.live_test_only
    @FileSharePreparer()
    def test_list_shares_account_sas(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share = self._create_share()
        sas_token = generate_account_sas(
            storage_account_name,
            storage_account_key,
            ResourceTypes(service=True),
            AccountSasPermissions(list=True),
            datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        fsc = ShareServiceClient(self.account_url(storage_account_name, "file"), credential=sas_token)
        shares = list(fsc.list_shares())

        # Assert
        self.assertIsNotNone(shares)
        self.assertGreaterEqual(len(shares), 1)
        self.assertIsNotNone(shares[0])
        self.assertNamedItemInContainer(shares, share.share_name)
        self._delete_shares()

    @FileSharePreparer()
    def test_set_share_metadata(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share = self._create_share()
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        share.set_share_metadata(metadata)

        # Assert
        md = share.get_share_properties().metadata
        self.assertDictEqual(md, metadata)
        self._delete_shares()

    @FileSharePreparer()
    def test_get_share_metadata(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        client = self._get_share_reference()
        created = client.create_share(metadata=metadata)

        # Assert
        self.assertTrue(created)
        md = client.get_share_properties().metadata
        self.assertDictEqual(md, metadata)
        self._delete_shares()

    @FileSharePreparer()
    def test_get_share_metadata_with_snapshot(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        client = self._get_share_reference()
        created = client.create_share(metadata=metadata)
        snapshot = client.create_snapshot()
        snapshot_client = self.fsc.get_share_client(client.share_name, snapshot=snapshot)

        # Assert
        self.assertTrue(created)
        md = snapshot_client.get_share_properties().metadata
        self.assertDictEqual(md, metadata)
        self._delete_shares()

    @FileSharePreparer()
    def test_set_share_properties(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share1 = self._create_share("share1")
        share2 = self._create_share("share2")

        share1.set_share_quota(3)
        share1.set_share_properties(access_tier="Hot")

        share2.set_share_properties(access_tier=ShareAccessTier("Cool"), quota=2)

        # Act
        props1 = share1.get_share_properties()
        props2 = share2.get_share_properties()

        share1_quota = props1.quota
        share1_tier = props1.access_tier

        share2_quota = props2.quota
        share2_tier = props2.access_tier

        # Assert
        self.assertEqual(share1_quota, 3)
        self.assertEqual(share1_tier, "Hot")
        self.assertEqual(share2_quota, 2)
        self.assertEqual(share2_tier, "Cool")
        self._delete_shares()

    @pytest.mark.playback_test_only
    @FileSharePreparer()
    def test_create_share_with_protocol(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)

        # Act
        share_client = self._get_share_reference("testshare2")
        with self.assertRaises(ValueError):
            share_client.create_share(protocols="SMB", root_squash=ShareRootSquash.all_squash)
        share_client.create_share(protocols="NFS", root_squash=ShareRootSquash.root_squash)
        share_enabled_protocol = share_client.get_share_properties().protocols
        share_root_squash = share_client.get_share_properties().root_squash

        # Assert
        self.assertEqual(share_enabled_protocol, ["NFS"])
        self.assertEqual(share_root_squash, ShareRootSquash.root_squash)
        share_client.delete_share()

    @pytest.mark.playback_test_only
    @FileSharePreparer()
    def test_set_share_properties_with_root_squash(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share1 = self._create_share("share1", protocols=ShareProtocols.NFS)
        share2 = self._create_share("share2", protocols=ShareProtocols.NFS)

        share1.set_share_properties(root_squash="NoRootSquash")
        share2.set_share_properties(root_squash=ShareRootSquash.root_squash)

        # Act
        share1_props = share1.get_share_properties()
        share2_props = share2.get_share_properties()

        # # Assert
        self.assertEqual(share1_props.root_squash, ShareRootSquash.no_root_squash)
        self.assertEqual(share1_props.protocols, ['NFS'])
        self.assertEqual(share2_props.root_squash, ShareRootSquash.root_squash)
        self.assertEqual(share2_props.protocols, ['NFS'])

    @pytest.mark.playback_test_only
    @FileSharePreparer()
    def test_list_shares_with_root_squash_and_protocols(
            self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        self._create_share(prefix="testshare1", protocols="NFS", root_squash=ShareRootSquash.all_squash)
        self._create_share(prefix="testshare2", protocols=ShareProtocols.SMB)
        # Act
        shares = list(self.fsc.list_shares())
        share1_props = shares[0]
        share2_props = shares[1]

        # Assert
        self.assertIsNotNone(shares)
        self.assertGreaterEqual(len(shares), 2)
        self.assertEqual(share1_props.root_squash, ShareRootSquash.all_squash)
        self.assertEqual(share1_props.protocols, ["NFS"])
        self.assertEqual(share2_props.root_squash, None)
        self.assertEqual(share2_props.protocols, ["SMB"])
        self._delete_shares()

    @FileSharePreparer()
    def test_get_share_properties_for_premium_account(self, premium_storage_file_account_name, premium_storage_file_account_key):
        self._setup(premium_storage_file_account_name, premium_storage_file_account_key)
        share = self._create_share()

        # Act
        props = share.get_share_properties()

        # Assert
        self.assertIsNotNone(props)
        self.assertIsNotNone(props.quota)
        self.assertIsNotNone(props.provisioned_iops)
        self.assertIsNotNone(props.provisioned_ingress_mbps)
        self.assertIsNotNone(props.provisioned_egress_mbps)
        self.assertIsNotNone(props.next_allowed_quota_downgrade_time)
        self.assertIsNotNone(props.provisioned_bandwidth)
        self._delete_shares()

    @FileSharePreparer()
    def test_delete_share_with_existing_share(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()
        share.create_share()

        # Act
        deleted = share.delete_share()

        # Assert
        self.assertIsNone(deleted)
        self._delete_shares()

    @FileSharePreparer()
    def test_delete_share_with_existing_share_fail_not_exist(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        client = self._get_share_reference()

        # Act
        with LogCaptured(self) as log_captured:
            with self.assertRaises(HttpResponseError):
                client.delete_share()

            log_as_str = log_captured.getvalue()
        self._delete_shares()

    @FileSharePreparer()
    def test_delete_share_with_non_existing_share(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        client = self._get_share_reference()

        # Act
        with LogCaptured(self) as log_captured:
            with self.assertRaises(HttpResponseError):
                deleted = client.delete_share()

            log_as_str = log_captured.getvalue()
            self.assertTrue('ERROR' not in log_as_str)
        self._delete_shares()

    @FileSharePreparer()
    def test_delete_share_with_non_existing_share_fail_not_exist(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        client = self._get_share_reference()

        # Act
        with LogCaptured(self) as log_captured:
            with self.assertRaises(HttpResponseError):
                client.delete_share()

            log_as_str = log_captured.getvalue()
        self._delete_shares()

    @FileSharePreparer()
    def test_get_share_stats(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()
        share.create_share()

        # Act
        share_usage = share.get_share_stats()

        # Assert
        self.assertEqual(share_usage, 0)
        self._delete_shares()

    @FileSharePreparer()
    def test_set_share_acl(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()
        share.create_share()

        # Act
        resp = share.set_share_access_policy(signed_identifiers=dict())

        # Assert
        acl = share.get_share_access_policy()
        self.assertIsNotNone(acl)
        self._delete_shares()

    @FileSharePreparer()
    def test_set_share_acl_with_empty_signed_identifiers(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()
        share.create_share()

        # Act
        resp = share.set_share_access_policy(dict())

        # Assert
        acl = share.get_share_access_policy()
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl.get('signed_identifiers')), 0)
        self._delete_shares()

    @FileSharePreparer()
    def test_set_share_acl_with_signed_identifiers(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()
        share.create_share()

        # Act
        identifiers = dict()
        identifiers['testid'] = AccessPolicy(
            permission=ShareSasPermissions(write=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            start=datetime.utcnow() - timedelta(minutes=1),
        )

        resp = share.set_share_access_policy(identifiers)

        # Assert
        acl = share.get_share_access_policy()
        self.assertIsNotNone(acl)
        self.assertEqual(len(acl['signed_identifiers']), 1)
        self.assertEqual(acl['signed_identifiers'][0].id, 'testid')
        self._delete_shares()

    @FileSharePreparer()
    def test_set_share_acl_too_many_ids(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()
        share.create_share()

        # Act
        identifiers = dict()
        for i in range(0, 6):
            identifiers['id{}'.format(i)] = AccessPolicy()

        # Assert
        with self.assertRaises(ValueError) as e:
            share.set_share_access_policy(identifiers)
        self.assertEqual(
            str(e.exception),
            'Too many access policies provided. The server does not support setting more than 5 access policies on a single resource.'
        )
        self._delete_shares()

    @FileSharePreparer()
    def test_list_directories_and_files(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share = self._create_share()
        dir0 = share.get_directory_client()
        dir0.upload_file('file1', 'data1')
        dir1 = share.get_directory_client('dir1')
        dir1.create_directory()
        dir1.upload_file('file2', 'data2')
        dir2 = share.get_directory_client('dir2')
        dir2.create_directory()

        # Act
        resp = list(share.list_directories_and_files())

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), 3)
        self.assertIsNotNone(resp[0])
        self.assertNamedItemInContainer(resp, 'dir1')
        self.assertNamedItemInContainer(resp, 'dir2')
        self.assertNamedItemInContainer(resp, 'file1')
        self._delete_shares()

    @FileSharePreparer()
    def test_list_directories_and_files_with_snapshot(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_name = self._create_share()
        dir1 = share_name.get_directory_client('dir1')
        dir1.create_directory()
        dir2 = share_name.get_directory_client('dir2')
        dir2.create_directory()
        snapshot1 = share_name.create_snapshot()
        dir3 = share_name.get_directory_client('dir3')
        dir3.create_directory()
        file1 = share_name.get_file_client('file1')
        file1.upload_file('data')


        # Act
        snapshot_client = self.fsc.get_share_client(share_name.share_name, snapshot=snapshot1)
        resp = list(snapshot_client.list_directories_and_files())

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), 2)
        self.assertIsNotNone(resp[0])
        self.assertNamedItemInContainer(resp, 'dir1')
        self.assertNamedItemInContainer(resp, 'dir2')
        self._delete_shares()

    @FileSharePreparer()
    def test_list_directories_and_files_with_num_results(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_name = self._create_share()
        dir1 = share_name.create_directory('dir1')
        root = share_name.get_directory_client()
        root.upload_file('filea1', '1024')
        root.upload_file('filea2', '1024')
        root.upload_file('filea3', '1024')
        root.upload_file('fileb1', '1024')

        # Act
        result = share_name.list_directories_and_files(results_per_page=2).by_page()
        result = list(next(result))

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertNamedItemInContainer(result, 'dir1')
        self.assertNamedItemInContainer(result, 'filea1')
        self._delete_shares()

    @FileSharePreparer()
    def test_list_directories_and_files_with_num_results_and_marker(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_name = self._create_share()
        dir1 = share_name.get_directory_client('dir1')
        dir1.create_directory()
        dir1.upload_file('filea1', '1024')
        dir1.upload_file('filea2', '1024')
        dir1.upload_file('filea3', '1024')
        dir1.upload_file('fileb1', '1024')

        # Act
        generator1 = share_name.list_directories_and_files(
            'dir1', results_per_page=2).by_page()
        result1 = list(next(generator1))

        generator2 = share_name.list_directories_and_files(
            'dir1', results_per_page=2).by_page(continuation_token=generator1.continuation_token)
        result2 = list(next(generator2))

        # Assert
        self.assertEqual(len(result1), 2)
        self.assertEqual(len(result2), 2)
        self.assertNamedItemInContainer(result1, 'filea1')
        self.assertNamedItemInContainer(result1, 'filea2')
        self.assertNamedItemInContainer(result2, 'filea3')
        self.assertNamedItemInContainer(result2, 'fileb1')
        self.assertEqual(generator2.continuation_token, None)
        self._delete_shares()

    @FileSharePreparer()
    def test_list_directories_and_files_with_prefix(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share = self._create_share()
        dir1 = share.create_directory('dir1')
        share.create_directory('dir1/pref_dir3')
        share.create_directory('dir2')

        root = share.get_directory_client()
        root.upload_file('file1', '1024')
        dir1.upload_file('pref_file2', '1025')
        dir1.upload_file('file3', '1025')

        # Act
        resp = list(share.list_directories_and_files('dir1', name_starts_with='pref'))

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), 2)
        self.assertIsNotNone(resp[0])
        self.assertNamedItemInContainer(resp, 'pref_file2')
        self.assertNamedItemInContainer(resp, 'pref_dir3')
        self._delete_shares()

    @FileSharePreparer()
    def test_shared_access_share(self, storage_account_name, storage_account_key):
        # SAS URL is calculated from storage key, so this test runs live only
        if not self.is_live:
            return

        self._setup(storage_account_name, storage_account_key)
        file_name = 'file1'
        dir_name = 'dir1'
        data = b'hello world'

        share = self._create_share()
        dir1 = share.create_directory(dir_name)
        dir1.upload_file(file_name, data)

        token = generate_share_sas(
            share.account_name,
            share.share_name,
            share.credential.account_key,
            expiry=datetime.utcnow() + timedelta(hours=1),
            permission=ShareSasPermissions(read=True),
        )
        sas_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=share.share_name,
            file_path=dir_name + '/' + file_name,
            credential=token,
        )

        # Act
        print(sas_client.url)
        response = requests.get(sas_client.url)

        # Assert
        self.assertTrue(response.ok)
        self.assertEqual(data, response.content)
        self._delete_shares()

    @FileSharePreparer()
    def test_create_permission_for_share(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        user_given_permission = "O:S-1-5-21-2127521184-1604012920-1887927527-21560751G:S-1-5-21-2127521184-" \
                                "1604012920-1887927527-513D:AI(A;;FA;;;SY)(A;;FA;;;BA)(A;;0x1200a9;;;" \
                                "S-1-5-21-397955417-626881126-188441444-3053964)"
        share_client = self._create_share()
        permission_key = share_client.create_permission_for_share(user_given_permission)
        self.assertIsNotNone(permission_key)

        server_returned_permission = share_client.get_permission_for_share(permission_key)
        self.assertIsNotNone(server_returned_permission)

        permission_key2 = share_client.create_permission_for_share(server_returned_permission)
        # the permission key obtained from user_given_permission should be the same as the permission key obtained from
        # server returned permission
        self.assertEqual(permission_key, permission_key2)

    @FileSharePreparer()
    def test_transport_closed_only_once(self, storage_account_name, storage_account_key):
        if not self.is_live:
            return
        self._setup(storage_account_name, storage_account_key)
        transport = RequestsTransport()
        url = self.account_url(storage_account_name, "file")
        credential = storage_account_key
        prefix = TEST_SHARE_PREFIX
        share_name = self.get_resource_name(prefix)
        with ShareServiceClient(url, credential=credential, transport=transport) as fsc:
            fsc.get_service_properties()
            assert transport.session is not None
            with fsc.get_share_client(share_name) as fc:
                assert transport.session is not None
            fsc.get_service_properties()
            assert transport.session is not None

    @FileSharePreparer()
    def test_delete_directory_from_share(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share = self._create_share()
        dir1 = share.create_directory('dir1')
        share.create_directory('dir2')
        share.create_directory('dir3')

        # Act
        resp = list(share.list_directories_and_files())
        self.assertEqual(len(resp), 3)

        share.delete_directory('dir3')

        # Assert
        resp = list(share.list_directories_and_files())
        self.assertEqual(len(resp), 2)

        self._delete_shares()

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
