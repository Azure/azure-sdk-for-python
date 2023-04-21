# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import time
from datetime import datetime, timedelta

import pytest
import requests
from azure.core.exceptions import HttpResponseError, ResourceExistsError, ResourceNotFoundError
from azure.core.pipeline.transport import AioHttpTransport
from azure.storage.fileshare import (
    AccessPolicy,
    AccountSasPermissions,
    generate_account_sas,
    generate_share_sas,
    ResourceTypes,
    ShareAccessTier,
    ShareProtocols,
    ShareRootSquash,
    ShareSasPermissions
)
from azure.storage.fileshare.aio import ShareClient, ShareFileClient, ShareServiceClient

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage import LogCaptured
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from settings.testcase import FileSharePreparer
# ------------------------------------------------------------------------------
TEST_SHARE_PREFIX = 'share'
TEST_INTENT = "backup"
# ------------------------------------------------------------------------------


class TestStorageShareAsync(AsyncStorageRecordedTestCase):
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

    async def _create_share(self, prefix=TEST_SHARE_PREFIX, **kwargs):
        share_client = self._get_share_reference(prefix)
        try:
            await share_client.create_share(**kwargs)
        except:
            pass
        return share_client

    # --Test cases for shares -----------------------------------------
    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_share(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()

        # Act
        created = await share.create_share()

        # Assert
        assert created
        await self._delete_shares(share.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_share_with_oauth_fails(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        token_credential = self.generate_oauth_token()

        self._setup(storage_account_name, storage_account_key)
        share_name = self.get_resource_name(TEST_SHARE_PREFIX)

        # Act
        with pytest.raises(ValueError):
            share = ShareClient(
                self.account_url(storage_account_name, "file"),
                share_name=share_name,
                credential=token_credential,
                file_request_intent=TEST_INTENT
            )

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_share_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()

        # Act
        created = await share.create_share()
        snapshot = await share.create_snapshot()

        # Assert
        assert created
        assert snapshot['snapshot'] is not None
        assert snapshot['etag'] is not None
        assert snapshot['last_modified'] is not None
        await self._delete_shares(share.share_name)


    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_snapshot_with_metadata(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()
        metadata = {"test1": "foo", "test2": "bar"}
        metadata2 = {"test100": "foo100", "test200": "bar200"}

        # Act
        created = await share.create_share(metadata=metadata)
        snapshot = await share.create_snapshot(metadata=metadata2)

        share_props = await share.get_share_properties()
        snapshot_client = ShareClient(
            self.account_url(storage_account_name, "file"),
            share_name=share.share_name,
            snapshot=snapshot,
            credential=storage_account_key
        )
        snapshot_props = await snapshot_client.get_share_properties()
        # Assert
        assert created
        assert snapshot['snapshot'] is not None
        assert snapshot['etag'] is not None
        assert snapshot['last_modified'] is not None
        assert share_props.metadata == metadata
        assert snapshot_props.metadata == metadata2
        await self._delete_shares(share.share_name)


    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_delete_share_with_snapshots(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()
        await share.create_share()
        snapshot = await share.create_snapshot()

        # Act
        with pytest.raises(HttpResponseError):
            await share.delete_share()

        deleted = await share.delete_share(delete_snapshots=True)
        assert deleted is None
        await self._delete_shares(share.share_name)

    @pytest.mark.playback_test_only
    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_undelete_share(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # share soft delete should enabled by SRP call or use armclient, so make this test as playback only.
        self._setup(storage_account_name, storage_account_key)
        share_client = await self._create_share(prefix="sharerestore")

        # Act
        await share_client.delete_share()
        # to make sure the share deleted
        with pytest.raises(ResourceNotFoundError):
            await share_client.get_share_properties()

        share_list = list()
        async for share in self.fsc.list_shares(include_deleted=True):
            share_list.append(share)
        assert len(share_list) >= 1

        for share in share_list:
            # find the deleted share and restore it
            if share.deleted and share.name == share_client.share_name:
                if self.is_live:
                    time.sleep(60)
                restored_share_client = await self.fsc.undelete_share(share.name, share.version)

                # to make sure the deleted share is restored
                props = await restored_share_client.get_share_properties()
                assert props is not None
                break

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_lease_share_acquire_and_release(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = await self._create_share('test')
        # Act
        lease = await share_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')
        await lease.release()
        # Assert

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_acquire_lease_on_sharesnapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()

        # Act
        await share.create_share()
        snapshot = await share.create_snapshot()

        snapshot_client = ShareClient(
            self.account_url(storage_account_name, "file"),
            share_name=share.share_name,
            snapshot=snapshot,
            credential=storage_account_key
        )

        share_lease = await share.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')
        share_snapshot_lease = await snapshot_client.acquire_lease(lease_id='44444444-3333-2222-1111-000000000000')

        # Assert
        with pytest.raises(HttpResponseError):
            await share.get_share_properties(lease=share_snapshot_lease)

        with pytest.raises(HttpResponseError):
            await snapshot_client.get_share_properties(lease=share_lease)

        assert snapshot['snapshot'] is not None
        assert snapshot['etag'] is not None
        assert snapshot['last_modified'] is not None
        assert share_lease is not None
        assert share_snapshot_lease is not None
        assert share_lease != share_snapshot_lease

        await share_snapshot_lease.release()
        await share_lease.release()
        await self._delete_shares(share.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_lease_share_renew(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = await self._create_share('test')
        lease = await share_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444', lease_duration=15)
        self.sleep(10)
        lease_id_start = lease.id

        # Act
        await lease.renew()

        # Assert
        assert lease.id == lease_id_start
        self.sleep(5)
        with pytest.raises(HttpResponseError):
            await share_client.delete_share()
        self.sleep(12)
        await share_client.delete_share()

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_lease_share_with_duration(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = await self._create_share('test')

        # Act
        lease = await share_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444', lease_duration=15)

        # Assert
        with pytest.raises(HttpResponseError):
            await share_client.acquire_lease(lease_id='44444444-3333-2222-1111-000000000000')
        self.sleep(17)
        await share_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_lease_share_twice(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = await self._create_share('test')

        # Act
        lease = await share_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444', lease_duration=15)

        # Assert
        lease2 = await share_client.acquire_lease(lease_id=lease.id)
        assert lease.id == lease2.id

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_lease_share_with_proposed_lease_id(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = await self._create_share('test')

        # Act
        proposed_lease_id = '55e97f64-73e8-4390-838d-d9e84a374321'
        lease = await share_client.acquire_lease(lease_id=proposed_lease_id)

        # Assert
        assert proposed_lease_id == lease.id

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_lease_share_change_lease_id(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = await self._create_share('test')

        # Act
        lease_id = '29e0b239-ecda-4f69-bfa3-95f6af91464c'
        lease = await share_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')
        lease_id1 = lease.id
        await lease.change(proposed_lease_id=lease_id)
        await lease.renew()
        lease_id2 = lease.id

        # Assert
        assert lease_id1 is not None
        assert lease_id2 is not None
        assert lease_id1 != lease_id
        assert lease_id2 == lease_id

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_set_share_metadata_with_lease_id(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = await self._create_share('test1')
        metadata = {'hello': 'world', 'number': '43'}
        lease_id = await share_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # Act
        await share_client.set_share_metadata(metadata, lease=lease_id)

        # Assert
        props = await share_client.get_share_properties()
        md = props.metadata
        assert md == metadata

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_get_share_metadata_with_lease_id(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = await self._create_share('test')
        metadata = {'hello': 'world', 'number': '43'}
        await share_client.set_share_metadata(metadata)
        lease_id = await share_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # Act
        props = await share_client.get_share_properties(lease=lease_id)
        md = props.metadata

        # Assert
        assert md == metadata

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_get_share_properties_with_lease_id(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = await self._create_share('test')
        metadata = {'hello': 'world', 'number': '43'}
        await share_client.set_share_metadata(metadata)
        lease_id = await share_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # Act
        props = await share_client.get_share_properties(lease=lease_id)
        await lease_id.break_lease()

        # Assert
        assert props is not None
        assert props.metadata == metadata
        assert props.lease.duration == 'infinite'
        assert props.lease.state == 'leased'
        assert props.lease.status == 'locked'

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_get_share_acl_with_lease_id(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = await self._create_share('test')
        lease_id = await share_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # Act
        acl = await share_client.get_share_access_policy(lease=lease_id)

        # Assert
        assert acl is not None
        assert acl.get('public_access') is None

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_set_share_acl_with_lease_id(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop('variables', {})

        self._setup(storage_account_name, storage_account_key)
        share_client = await self._create_share('test')
        lease_id = await share_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # Act
        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(hours=1))
        start_time = self.get_datetime_variable(variables, 'start_time', datetime.utcnow())
        access_policy = AccessPolicy(permission=ShareSasPermissions(read=True),
                                     expiry=expiry_time,
                                     start=start_time)
        signed_identifiers = {'testid': access_policy}

        await share_client.set_share_access_policy(signed_identifiers, lease=lease_id)

        # Assert
        acl = await share_client.get_share_access_policy()
        assert acl is not None
        assert acl.get('public_access') is None

        return variables

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_lease_share_break_period(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = await self._create_share('test')

        # Act
        lease = await share_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444', lease_duration=15)

        # Assert
        await lease.break_lease(lease_break_period=5)
        self.sleep(6)
        with pytest.raises(HttpResponseError):
            await share_client.delete_share(lease=lease)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_delete_share_with_lease_id(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = await self._create_share('test')
        lease = await share_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444', lease_duration=15)

        # Assert
        with pytest.raises(HttpResponseError):
            await share_client.delete_share()

        # Act
        deleted = await share_client.delete_share(lease=lease)

        # Assert
        assert deleted is None
        with pytest.raises(ResourceNotFoundError):
            await share_client.get_share_properties()

    @pytest.mark.playback_test_only
    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_restore_to_existing_share(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # share soft delete should enabled by SRP call or use armclient, so make this test as playback only.
        self._setup(storage_account_name, storage_account_key)
        # Act
        share_client = await self._create_share()
        await share_client.delete_share()
        # to make sure the share deleted
        with pytest.raises(ResourceNotFoundError):
            await share_client.get_share_properties()

        # create a share with the same name as the deleted one
        if self.is_live:
            time.sleep(30)
        await share_client.create_share()

        share_list = []
        async for share in self.fsc.list_shares(include_deleted=True):
            share_list.append(share)
        assert len(share_list) >= 1

        for share in share_list:
            # find the deleted share and restore it
            if share.deleted and share.name == share_client.share_name:
                with pytest.raises(HttpResponseError):
                    await self.fsc.undelete_share(share.name, share.version)
                break

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_delete_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()
        await share.create_share()
        snapshot = await share.create_snapshot()

        # Act
        with pytest.raises(HttpResponseError):
            await share.delete_share()

        snapshot_client = ShareClient(
            self.account_url(storage_account_name, "file"),
            share_name=share.share_name,
            snapshot=snapshot,
            credential=storage_account_key
        )

        deleted = await snapshot_client.delete_share()
        assert deleted is None
        await self._delete_shares(share.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_share_fail_on_exist(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()

        # Act
        created = await share.create_share()

        # Assert
        assert created
        await self._delete_shares(share.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_share_with_already_existing_share_fail_on_exist(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()

        # Act
        created = await share.create_share()
        with pytest.raises(HttpResponseError):
            await share.create_share()

        # Assert
        assert created
        await self._delete_shares(share.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_share_with_metadata(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        client = self._get_share_reference()
        created = await client.create_share(metadata=metadata)

        # Assert
        assert created
        props = await client.get_share_properties()
        assert props.metadata == metadata
        await self._delete_shares(client.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_share_with_quota(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)

        # Act
        client = self._get_share_reference()
        created = await client.create_share(quota=1)

        # Assert
        props = await client.get_share_properties()
        assert created
        assert props.quota == 1
        await self._delete_shares(client.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_share_with_access_tier(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)

        # Act
        client = self._get_share_reference()
        created = await client.create_share(access_tier="Hot")

        # Assert
        props = await client.get_share_properties()
        assert created
        assert props.access_tier == "Hot"
        await self._delete_shares(client.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_share_exists(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share = await self._create_share()

        # Act
        exists = await share.get_share_properties()

        # Assert
        assert exists
        await self._delete_shares(share.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_share_not_exists(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()

        # Act
        with pytest.raises(ResourceNotFoundError):
            await share.get_share_properties()

        # Assert
        await self._delete_shares(share.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_share_snapshot_exists(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share = await self._create_share()
        snapshot = await share.create_snapshot()

        # Act
        snapshot_client = self.fsc.get_share_client(share.share_name, snapshot=snapshot)
        exists = await snapshot_client.get_share_properties()

        # Assert
        assert exists
        await self._delete_shares(share.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_share_snapshot_not_exists(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share = await self._create_share()
        made_up_snapshot = '2017-07-19T06:53:46.0000000Z'

        # Act
        snapshot_client = self.fsc.get_share_client(share.share_name, snapshot=made_up_snapshot)
        with pytest.raises(ResourceNotFoundError):
            await snapshot_client.get_share_properties()

        # Assert
        await self._delete_shares(share.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_unicode_create_share_unicode_name(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_name = u'啊齄丂狛狜'

        # Act
        with pytest.raises(HttpResponseError):
            # not supported - share name must be alphanumeric, lowercase
            client = self.fsc.get_share_client(share_name)
            await client.create_share()

            # Assert
        await self._delete_shares(share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_list_shares_no_options(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share = await self._create_share()
        # Act
        shares = []
        async for s in self.fsc.list_shares():
            shares.append(s)

        # Assert
        assert shares is not None
        assert len(shares) >= 1
        assert shares[0] is not None
        self.assertNamedItemInContainer(shares, share.share_name)
        await self._delete_shares(share.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_list_shares_no_options_for_premium_account(self, **kwargs):
        premium_storage_file_account_name = kwargs.pop("premium_storage_file_account_name")
        premium_storage_file_account_key = kwargs.pop("premium_storage_file_account_key")

        self._setup(premium_storage_file_account_name, premium_storage_file_account_key)
        share = await self._create_share()

        # Act
        shares = []
        async for s in self.fsc.list_shares():
            shares.append(s)

        # Assert
        assert shares is not None
        assert len(shares) >= 1
        assert shares[0] is not None
        assert shares[0].provisioned_iops is not None
        assert shares[0].provisioned_ingress_mbps is not None
        assert shares[0].provisioned_egress_mbps is not None
        assert shares[0].next_allowed_quota_downgrade_time is not None
        assert shares[0].provisioned_bandwidth is not None
        await self._delete_shares(share.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_list_shares_leased_share(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share = await self._create_share()

        # Act
        lease = await share.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')
        resp = []
        async for s in self.fsc.list_shares():
            resp.append(s)

        # Assert
        assert resp is not None
        assert len(resp) >= 1
        assert resp[0] is not None
        assert resp[0].lease.duration == 'infinite'
        assert resp[0].lease.status == 'locked'
        assert resp[0].lease.state == 'leased'
        await lease.release()
        await self._delete_shares()

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_list_shares_with_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share = await self._create_share('random3')
        snapshot1 = await share.create_snapshot()
        snapshot2 = await share.create_snapshot()

        # Act
        shares = self.fsc.list_shares(name_starts_with=share.share_name, include_snapshots=True)

        # Assert
        assert shares is not None
        all_shares = []
        async for s in shares:
            all_shares.append(s)
        assert len(all_shares) == 3
        self.assertNamedItemInContainer(all_shares, share.share_name)
        self.assertNamedItemInContainer(all_shares, snapshot1['snapshot'])
        self.assertNamedItemInContainer(all_shares, snapshot2['snapshot'])
        await self._delete_shares(share.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_list_shares_with_prefix(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        await self._create_share('othershare')
        share = await self._create_share('random4')

        # Act
        shares = []
        async for s in self.fsc.list_shares(name_starts_with=share.share_name):
            shares.append(s)

        # Assert
        assert len(shares) == 1
        assert shares[0] is not None
        assert shares[0].name == share.share_name
        assert shares[0].metadata is None
        await self._delete_shares(share.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_list_shares_with_include_metadata(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        metadata = {'hello': 'world', 'number': '42'}
        share = self._get_share_reference()
        await share.create_share(metadata=metadata)

        # Act
        shares = []
        async for s in self.fsc.list_shares(share.share_name, include_metadata=True):
            shares.append(s)

        # Assert
        assert shares is not None
        assert len(shares) >= 1
        assert shares[0] is not None
        self.assertNamedItemInContainer(shares, share.share_name)
        assert shares[0].metadata == metadata

        await self._delete_shares(share.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_list_shares_with_num_results_and_marker(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
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
        assert shares1 is not None
        assert len(shares1) == 2
        self.assertNamedItemInContainer(shares1, share_names[0])
        self.assertNamedItemInContainer(shares1, share_names[1])
        assert shares2 is not None
        assert len(shares2) == 2
        self.assertNamedItemInContainer(shares2, share_names[2])
        self.assertNamedItemInContainer(shares2, share_names[3])
        await self._delete_shares(prefix)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_list_shares_account_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share = await self._create_share()
        sas_token = self.generate_sas(
            generate_account_sas,
            storage_account_name,
            storage_account_key,
            ResourceTypes(service=True),
            AccountSasPermissions(list=True),
            datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        fsc = ShareServiceClient(self.account_url(storage_account_name, "file"), credential=sas_token)
        shares = []
        async for s in fsc.list_shares():
            shares.append(s)

        # Assert
        assert shares is not None
        assert len(shares) >= 1
        assert shares[0] is not None
        self.assertNamedItemInContainer(shares, share.share_name)
        await self._delete_shares()


    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_set_share_metadata(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share = await self._create_share()
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        await share.set_share_metadata(metadata)

        # Assert
        props = await share.get_share_properties()
        md = props.metadata
        assert md == metadata
        await self._delete_shares(share.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_get_share_metadata(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        client = self._get_share_reference()
        created = await client.create_share(metadata=metadata)

        # Assert
        assert created
        props = await client.get_share_properties()
        assert props.metadata == metadata
        await self._delete_shares(client.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_get_share_metadata_with_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        client = self._get_share_reference()
        created = await client.create_share(metadata=metadata)
        snapshot = await client.create_snapshot()
        snapshot_client = self.fsc.get_share_client(client.share_name, snapshot=snapshot)

        # Assert
        assert created
        props = await snapshot_client.get_share_properties()
        assert props.metadata == metadata
        await self._delete_shares(client.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_set_share_properties(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share1 = await self._create_share("share1")
        share2 = await self._create_share("share2")

        await share1.set_share_quota(3)
        await share1.set_share_properties(access_tier="Hot")

        await share2.set_share_properties(access_tier=ShareAccessTier("Cool"), quota=2)

        # Act
        props1 = await share1.get_share_properties()
        props2 = await share2.get_share_properties()

        share1_quota = props1.quota
        share1_tier = props1.access_tier

        share2_quota = props2.quota
        share2_tier = props2.access_tier

        # Assert
        assert share1_quota == 3
        assert share1_tier == "Hot"
        assert share2_quota == 2
        assert share2_tier == "Cool"
        await self._delete_shares()

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_share_with_protocol(self, **kwargs):
        premium_storage_file_account_name = kwargs.pop("premium_storage_file_account_name")
        premium_storage_file_account_key = kwargs.pop("premium_storage_file_account_key")

        self._setup(premium_storage_file_account_name, premium_storage_file_account_key)

        # Act
        share_client = self._get_share_reference("testshare2")
        with pytest.raises(ValueError):
            await share_client.create_share(protocols="SMB", root_squash=ShareRootSquash.all_squash)
        await share_client.create_share(protocols="NFS", root_squash=ShareRootSquash.root_squash)
        props = await share_client.get_share_properties()
        share_enabled_protocol = props.protocols
        share_root_squash = props.root_squash

        # Assert
        assert share_enabled_protocol == ["NFS"]
        assert share_root_squash == ShareRootSquash.root_squash
        await share_client.delete_share()

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_set_share_properties_with_root_squash(self, **kwargs):
        premium_storage_file_account_name = kwargs.pop("premium_storage_file_account_name")
        premium_storage_file_account_key = kwargs.pop("premium_storage_file_account_key")

        self._setup(premium_storage_file_account_name, premium_storage_file_account_key)
        share1 = await self._create_share("share1", protocols=ShareProtocols.NFS)
        share2 = await self._create_share("share2", protocols=ShareProtocols.NFS)

        await share1.set_share_properties(root_squash="NoRootSquash")

        await share2.set_share_properties(root_squash=ShareRootSquash.root_squash)

        # Act
        props1 = await share1.get_share_properties()
        share1_root_squash = props1.root_squash
        props2 = await share2.get_share_properties()
        share2_root_squash = props2.root_squash

        # Assert
        assert share1_root_squash == ShareRootSquash.no_root_squash
        assert share2_root_squash == ShareRootSquash.root_squash
        await self._delete_shares()

    @pytest.mark.playback_test_only
    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_list_shares_with_root_squash_and_protocols(self, **kwargs):
        premium_storage_file_account_name = kwargs.pop("premium_storage_file_account_name")
        premium_storage_file_account_key = kwargs.pop("premium_storage_file_account_key")

        self._setup(premium_storage_file_account_name, premium_storage_file_account_key)
        await self._create_share(prefix="testshare1", protocols="NFS", root_squash=ShareRootSquash.all_squash)
        await self._create_share(prefix="testshare2", protocols=ShareProtocols.SMB)
        # Act
        shares = []
        async for s in self.fsc.list_shares():
            shares.append(s)
        share1_props = shares[0]
        share2_props = shares[1]

        # Assert
        assert shares is not None
        assert len(shares) >= 2
        assert share1_props.root_squash == ShareRootSquash.all_squash
        assert share1_props.protocols == ["NFS"]
        assert share2_props.root_squash == None
        assert share2_props.protocols == ["SMB"]
        await self._delete_shares()

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_get_share_properties_for_premium_account(self, **kwargs):
        premium_storage_file_account_name = kwargs.pop("premium_storage_file_account_name")
        premium_storage_file_account_key = kwargs.pop("premium_storage_file_account_key")

        self._setup(premium_storage_file_account_name, premium_storage_file_account_key)
        share = await self._create_share()

        # Act
        props = await share.get_share_properties()

        # Assert
        assert props is not None
        assert props.quota is not None
        assert props.quota is not None
        assert props.provisioned_iops is not None
        assert props.provisioned_ingress_mbps is not None
        assert props.provisioned_egress_mbps is not None
        assert props.provisioned_bandwidth is not None
        assert props.next_allowed_quota_downgrade_time is not None

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_delete_share_with_existing_share(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()
        await share.create_share()

        # Act
        deleted = await share.delete_share()

        # Assert
        assert deleted is None
        await self._delete_shares(share.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_delete_share_with_existing_share_fail_not_exist(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        client = self._get_share_reference()

        # Act
        with LogCaptured(self) as log_captured:
            with pytest.raises(HttpResponseError):
                await client.delete_share()

            log_as_str = log_captured.getvalue()
        await self._delete_shares(client.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_delete_share_with_non_existing_share(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        client = self._get_share_reference()

        # Act
        with LogCaptured(self) as log_captured:
            with pytest.raises(HttpResponseError):
                deleted = await client.delete_share()

            log_as_str = log_captured.getvalue()
            assert 'ERROR' not in log_as_str
        await self._delete_shares(client.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_delete_share_with_non_existing_share_fail_not_exist(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        client = self._get_share_reference()

        # Act
        with LogCaptured(self) as log_captured:
            with pytest.raises(HttpResponseError):
                await client.delete_share()

            log_as_str = log_captured.getvalue()
        await self._delete_shares(client.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_get_share_stats(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()
        await share.create_share()

        # Act
        share_usage = await share.get_share_stats()

        # Assert
        assert share_usage == 0
        await self._delete_shares(share.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_set_share_acl(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()
        await share.create_share()

        # Act
        resp = await share.set_share_access_policy(signed_identifiers=dict())

        # Assert
        acl = await share.get_share_access_policy()
        assert acl is not None
        await self._delete_shares(share.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_set_share_acl_with_empty_signed_identifiers(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()
        await share.create_share()

        # Act
        resp = await share.set_share_access_policy(dict())

        # Assert
        acl = await share.get_share_access_policy()
        assert acl is not None
        assert len(acl.get('signed_identifiers')) == 0
        await self._delete_shares(share.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_set_share_acl_with_signed_identifiers(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop('variables', {})

        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()
        await share.create_share()

        # Act
        identifiers = dict()
        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(hours=1))
        start_time = self.get_datetime_variable(variables, 'start_time', datetime.utcnow() - timedelta(minutes=1))
        identifiers['testid'] = AccessPolicy(
            permission=ShareSasPermissions(write=True),
            expiry=expiry_time,
            start=start_time,
        )

        resp = await share.set_share_access_policy(identifiers)

        # Assert
        acl = await share.get_share_access_policy()
        assert acl is not None
        assert len(acl['signed_identifiers']) == 1
        assert acl['signed_identifiers'][0].id == 'testid'
        await self._delete_shares(share.share_name)

        return variables

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_set_share_acl_too_many_ids(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share = self._get_share_reference()
        await share.create_share()

        # Act
        identifiers = dict()
        for i in range(0, 6):
            identifiers['id{}'.format(i)] = AccessPolicy()

        # Assert
        with pytest.raises(ValueError) as e:
            await share.set_share_access_policy(identifiers)
        assert str(e.value.args[0]) == 'Too many access policies provided. The server does not support setting more than 5 access policies on a single resource.'
        await self._delete_shares(share.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_list_directories_and_files(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
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
        assert resp is not None
        assert len(resp) == 3
        assert resp[0] is not None
        self.assertNamedItemInContainer(resp, 'dir1')
        self.assertNamedItemInContainer(resp, 'dir2')
        self.assertNamedItemInContainer(resp, 'file1')
        await self._delete_shares(share)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_list_directories_and_files_with_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
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
        assert resp is not None
        assert len(resp) == 2
        assert resp[0] is not None
        self.assertNamedItemInContainer(resp, 'dir1')
        self.assertNamedItemInContainer(resp, 'dir2')
        await self._delete_shares(share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_list_directories_and_files_with_num_results(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
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
        assert result is not None
        assert len(results) == 2
        self.assertNamedItemInContainer(results, 'dir1')
        self.assertNamedItemInContainer(results, 'filea1')
        await self._delete_shares(share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_list_directories_and_files_with_num_results_and_marker(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
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
        assert len(result1) == 2
        assert len(result2) == 2
        self.assertNamedItemInContainer(result1, 'filea1')
        self.assertNamedItemInContainer(result1, 'filea2')
        self.assertNamedItemInContainer(result2, 'filea3')
        self.assertNamedItemInContainer(result2, 'fileb1')
        assert generator2.continuation_token == None
        await self._delete_shares(share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_list_directories_and_files_with_prefix(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
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
        assert resp is not None
        assert len(resp) == 2
        assert resp[0] is not None
        self.assertNamedItemInContainer(resp, 'pref_file2')
        self.assertNamedItemInContainer(resp, 'pref_dir3')
        await self._delete_shares(share)

    @pytest.mark.live_test_only
    @FileSharePreparer()
    async def test_shared_access_share(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
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
            self.account_url(storage_account_name, "file"),
            share_name=share.share_name,
            file_path=dir_name + '/' + file_name,
            credential=token,
        )

        # Act
        response = requests.get(sas_client.url)

        # Assert
        assert response.ok
        assert data == response.content
        await self._delete_shares(share.share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_permission_for_share(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        user_given_permission = "O:S-1-5-21-2127521184-1604012920-1887927527-21560751G:S-1-5-21-2127521184-" \
                                "1604012920-1887927527-513D:AI(A;;FA;;;SY)(A;;FA;;;BA)(A;;0x1200a9;;;" \
                                "S-1-5-21-397955417-626881126-188441444-3053964)"
        share_client = await self._create_share()
        permission_key = await share_client.create_permission_for_share(user_given_permission)
        assert permission_key is not None

        server_returned_permission = await share_client.get_permission_for_share(permission_key)
        assert server_returned_permission is not None

        permission_key2 = await share_client.create_permission_for_share(server_returned_permission)
        # the permission key obtained from user_given_permission should be the same as the permission key obtained from
        # server returned permission
        assert permission_key == permission_key2
        await self._delete_shares(share_client.share_name)

    @pytest.mark.live_test_only
    @FileSharePreparer()
    async def test_transport_closed_only_once(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        transport = AioHttpTransport()
        url = self.account_url(storage_account_name, "file")
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

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_delete_directory_from_share(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share = await self._create_share()
        await share.create_directory('dir1')
        await share.create_directory('dir2')
        await share.create_directory('dir3')

        # Act
        resp = []
        async for d in share.list_directories_and_files():
            resp.append(d)
        assert len(resp) == 3

        await share.delete_directory('dir3')

        # Assert
        resp = []
        async for d in share.list_directories_and_files():
            resp.append(d)
        assert len(resp) == 2
        await self._delete_shares(share.share_name)

