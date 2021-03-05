# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from enum import Enum
from time import sleep

import pytest
from devtools_testutils import StorageAccountPreparer

from _shared.asynctestcase import AsyncStorageTestCase

try:
    from urllib.parse import quote
except ImportError:
    from urllib2 import quote

from _shared.testcase import GlobalStorageAccountPreparer, GlobalResourceGroupPreparer
from azure.core.exceptions import (
    ResourceExistsError, ResourceModifiedError, HttpResponseError)
from azure.storage.blob import BlobBlock
from azure.storage.blob.aio import BlobServiceClient
#------------------------------------------------------------------------------

TEST_CONTAINER_PREFIX = 'container'
TEST_BLOB_PREFIX = 'blob'
#------------------------------------------------------------------------------

class StorageBlobTagsTest(AsyncStorageTestCase):

    async def _setup(self, storage_account, key):
        self.bsc = BlobServiceClient(self.account_url(storage_account, "blob"), credential=key)
        self.container_name = self.get_resource_name("container")
        if self.is_live:
            container = self.bsc.get_container_client(self.container_name)
            try:
                await container.create_container(timeout=5)
            except ResourceExistsError:
                pass
        self.byte_data = self.get_random_bytes(1024)

    #--Helpers-----------------------------------------------------------------
    def _get_blob_reference(self):
        return self.get_resource_name(TEST_BLOB_PREFIX)

    async def _create_block_blob(self, tags=None, container_name=None, blob_name=None):
        blob_name = blob_name or self._get_blob_reference()
        blob_client = self.bsc.get_blob_client(container_name or self.container_name, blob_name)
        resp = await blob_client.upload_blob(self.byte_data, length=len(self.byte_data), overwrite=True, tags=tags)
        return blob_client, resp

    async def _create_empty_block_blob(self, tags=None):
        blob_name = self._get_blob_reference()
        blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = await blob_client.upload_blob(b'', length=0, overwrite=True, tags=tags)
        return blob_client, resp

    async def _create_append_blob(self, tags=None):
        blob_name = self._get_blob_reference()
        blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = await blob_client.create_append_blob(tags=tags)
        return blob_client, resp

    async def _create_page_blob(self, tags=None):
        blob_name = self._get_blob_reference()
        blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = await blob_client.create_page_blob(tags=tags, size=512)
        return blob_client, resp

    async def _create_container(self, prefix="container"):
        container_name = self.get_resource_name(prefix)
        try:
            await self.bsc.create_container(container_name)
        except:
            pass
        return container_name

    #-- test cases for blob tags ----------------------------------------------

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='pytagstorage')
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_blob_tags(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        blob_client, _ = await self._create_block_blob()

        # Act
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        resp = await blob_client.set_blob_tags(tags)

        # Assert
        self.assertIsNotNone(resp)

    @pytest.mark.playback_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_blob_tags_with_lease(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        blob_client, _ = await self._create_block_blob()
        lease = await blob_client.acquire_lease()

        # Act
        blob_tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}

        with self.assertRaises(HttpResponseError):
            await blob_client.set_blob_tags(blob_tags)
        await blob_client.set_blob_tags(blob_tags, lease=lease)

        await blob_client.get_blob_tags()
        with self.assertRaises(HttpResponseError):
            await blob_client.get_blob_tags(lease="'d92e6954-3274-4715-811c-727ca7145303'")
        resp = await blob_client.get_blob_tags(lease=lease)

        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), 3)

        await blob_client.delete_blob(lease=lease)

    @pytest.mark.playback_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_blob_tags_for_a_version(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        # use this version to set tag
        blob_client, resp = await self._create_block_blob()
        await self._create_block_blob()
        # TODO: enable versionid for this account and test set tag for a version

        # Act
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        resp = await blob_client.set_blob_tags(tags, version_id=resp['version_id'])

        # Assert
        self.assertIsNotNone(resp)

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='pytagstorage')
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_tags(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        blob_client, resp = await self._create_block_blob()

        # Act
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        await blob_client.set_blob_tags(tags)

        resp = await blob_client.get_blob_tags()

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), 3)
        for key, value in resp.items():
            self.assertEqual(tags[key], value)

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='pytagstorage')
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_tags_for_a_snapshot(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        tags = {"+-./:=_ ": "firsttag", "tag2": "+-./:=_", "+-./:=_1": "+-./:=_"}
        blob_client, resp = await self._create_block_blob(tags=tags)

        snapshot = await blob_client.create_snapshot()
        snapshot_client = self.bsc.get_blob_client(self.container_name, blob_client.blob_name, snapshot=snapshot)

        resp = await snapshot_client.get_blob_tags()

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), 3)
        for key, value in resp.items():
            self.assertEqual(tags[key], value)

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='pytagstorage')
    @AsyncStorageTestCase.await_prepared_test
    async def test_upload_block_blob_with_tags(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob_client, resp = await self._create_block_blob(tags=tags)

        resp = await blob_client.get_blob_tags()

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), 3)

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='pytagstorage')
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_blob_properties_returns_tags_num(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob_client, resp = await self._create_block_blob(tags=tags)

        resp = await blob_client.get_blob_properties()
        downloaded = await blob_client.download_blob()

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(resp.tag_count, len(tags))
        self.assertEqual(downloaded.properties.tag_count, len(tags))

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='pytagstorage')
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_append_blob_with_tags(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        tags = {"+-./:=_ ": "firsttag", "tag2": "+-./:=_", "+-./:=_1": "+-./:=_"}
        blob_client, resp = await self._create_append_blob(tags=tags)

        resp = await blob_client.get_blob_tags()

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), 3)

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='pytagstorage')
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_page_blob_with_tags(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob_client, resp = await self._create_page_blob(tags=tags)

        resp = await blob_client.get_blob_tags()

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), 3)

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='pytagstorage')
    @AsyncStorageTestCase.await_prepared_test
    async def test_commit_block_list_with_tags(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob_client, resp = await self._create_empty_block_blob(tags={'condition tag': 'test tag'})

        await blob_client.stage_block('1', b'AAA')
        await blob_client.stage_block('2', b'BBB')
        await blob_client.stage_block('3', b'CCC')

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        with self.assertRaises(ResourceModifiedError):
            await blob_client.commit_block_list(block_list, tags=tags, if_tags_match_condition="\"condition tag\"='wrong tag'")
        await blob_client.commit_block_list(block_list, tags=tags, if_tags_match_condition="\"condition tag\"='test tag'")

        resp = await blob_client.get_blob_tags()

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), len(tags))

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='pytagstorage')
    @AsyncStorageTestCase.await_prepared_test
    async def test_start_copy_from_url_with_tags(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob_client, resp = await self._create_block_blob()

        # Act
        sourceblob = '{0}/{1}/{2}'.format(
            self.account_url(storage_account, "blob"), self.container_name, blob_client.blob_name)

        copyblob = self.bsc.get_blob_client(self.container_name, 'blob1copy')
        copy = await copyblob.start_copy_from_url(sourceblob, tags=tags)

        # Assert
        self.assertIsNotNone(copy)
        self.assertEqual(copy['copy_status'], 'success')
        self.assertFalse(isinstance(copy['copy_status'], Enum))
        self.assertIsNotNone(copy['copy_id'])

        copy_content = await (await copyblob.download_blob()).readall()
        self.assertEqual(copy_content, self.byte_data)

        resp = await copyblob.get_blob_tags()

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), len(tags))

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='pytagstorage')
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_blobs_returns_tags(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        await self._create_block_blob(tags=tags)
        container = self.bsc.get_container_client(self.container_name)
        blob_list = container.list_blobs(include="tags")

        #Assert
        async for blob in blob_list:
            self.assertEqual(blob.tag_count, len(tags))
            for key, value in blob.tags.items():
                self.assertEqual(tags[key], value)

    @pytest.mark.playback_test_only
    @GlobalStorageAccountPreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_filter_blobs(self, resource_group, location, storage_account, storage_account_key):
        await self._setup(storage_account, storage_account_key)
        container_name1 = await self._create_container(prefix="container1")
        container_name2 = await self._create_container(prefix="container2")
        container_name3 = await self._create_container(prefix="container3")

        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        await self._create_block_blob(tags=tags, blob_name="blob1")
        await self._create_block_blob(tags=tags, blob_name="blob2", container_name=container_name1)
        await self._create_block_blob(tags=tags, blob_name="blob3", container_name=container_name2)
        await self._create_block_blob(tags=tags, blob_name="blob4", container_name=container_name3)

        if self.is_live:
            sleep(10)

        where = "\"tag1\"='firsttag' and \"tag2\"='secondtag'"
        blob_list = self.bsc.find_blobs_by_tags(filter_expression=where, results_per_page=2).by_page()
        first_page = await blob_list.__anext__()
        items_on_page1 = list()
        async for item in first_page:
            items_on_page1.append(item)
        second_page = await blob_list.__anext__()
        items_on_page2 = list()
        async for item in second_page:
            items_on_page2.append(item)

        self.assertEqual(2, len(items_on_page1))
        self.assertEqual(2, len(items_on_page2))
        self.assertEqual(len(items_on_page2[0]['tags']), 2)
        self.assertEqual(items_on_page2[0]['tags']['tag1'], 'firsttag')
        self.assertEqual(items_on_page2[0]['tags']['tag2'], 'secondtag')
#------------------------------------------------------------------------------
