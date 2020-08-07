# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
from datetime import datetime, timedelta
from enum import Enum
from time import sleep

import pytest
from devtools_testutils import StorageAccountPreparer

try:
    from urllib.parse import quote
except ImportError:
    from urllib2 import quote

from _shared.testcase import StorageTestCase, GlobalStorageAccountPreparer, GlobalResourceGroupPreparer
from azure.core.exceptions import (
    ResourceExistsError, ResourceModifiedError)
from azure.storage.blob import (
    BlobServiceClient,
    BlobBlock, generate_account_sas, ResourceTypes, AccountSasPermissions, generate_container_sas,
    ContainerSasPermissions, BlobClient, generate_blob_sas, BlobSasPermissions)

#------------------------------------------------------------------------------

TEST_CONTAINER_PREFIX = 'container'
TEST_BLOB_PREFIX = 'blob'
#------------------------------------------------------------------------------

class StorageBlobTagsTest(StorageTestCase):

    def _setup(self, storage_account, key):
        self.bsc = BlobServiceClient(self.account_url(storage_account, "blob"), credential=key)
        self.container_name = self.get_resource_name("container")
        if self.is_live:
            container = self.bsc.get_container_client(self.container_name)
            try:
                container.create_container(timeout=5)
            except ResourceExistsError:
                pass
        self.byte_data = self.get_random_bytes(1024)


    def _teardown(self, FILE_PATH):
        if os.path.isfile(FILE_PATH):
            try:
                os.remove(FILE_PATH)
            except:
                pass

    #--Helpers-----------------------------------------------------------------
    def _get_blob_reference(self):
        return self.get_resource_name(TEST_BLOB_PREFIX)

    def _create_block_blob(self, tags=None, container_name=None, blob_name=None):
        blob_name = blob_name or self._get_blob_reference()
        blob_client = self.bsc.get_blob_client(container_name or self.container_name, blob_name)
        resp = blob_client.upload_blob(self.byte_data, length=len(self.byte_data), overwrite=True, tags=tags)
        return blob_client, resp

    def _create_empty_block_blob(self, tags=None):
        blob_name = self._get_blob_reference()
        blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = blob_client.upload_blob(b'', length=0, overwrite=True, tags=tags)
        return blob_client, resp

    def _create_append_blob(self, tags=None):
        blob_name = self._get_blob_reference()
        blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = blob_client.create_append_blob(tags=tags)
        return blob_client, resp

    def _create_page_blob(self, tags=None):
        blob_name = self._get_blob_reference()
        blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = blob_client.create_page_blob(tags=tags, size=512)
        return blob_client, resp

    def _create_container(self, prefix="container"):
        container_name = self.get_resource_name(prefix)
        try:
            self.bsc.create_container(container_name)
        except:
            pass
        return container_name

    #-- test cases for blob tags ----------------------------------------------

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='pytagstorage')
    def test_set_blob_tags(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_client, _ = self._create_block_blob()

        # Act
        blob_tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        resp = blob_client.set_blob_tags(blob_tags)

        # Assert
        self.assertIsNotNone(resp)

    @pytest.mark.playback_test_only
    @GlobalStorageAccountPreparer()
    def test_set_blob_tags_for_a_version(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        # use this version to set tag
        blob_client, resp = self._create_block_blob()
        self._create_block_blob()
        # TODO: enable versionid for this account and test set tag for a version

        # Act
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        resp = blob_client.set_blob_tags(tags, version_id=resp['version_id'])

        # Assert
        self.assertIsNotNone(resp)

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='pytagstorage')
    def test_get_blob_tags(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        blob_client, resp = self._create_block_blob()

        # Act
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob_client.set_blob_tags(tags)

        resp = blob_client.get_blob_tags()

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), 3)
        for key, value in resp.items():
            self.assertEqual(tags[key], value)

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='pytagstorage')
    def test_get_blob_tags_for_a_snapshot(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        tags = {"+-./:=_ ": "firsttag", "tag2": "+-./:=_", "+-./:=_1": "+-./:=_"}
        blob_client, resp = self._create_block_blob(tags=tags)

        snapshot = blob_client.create_snapshot()
        snapshot_client = self.bsc.get_blob_client(self.container_name, blob_client.blob_name, snapshot=snapshot)

        resp = snapshot_client.get_blob_tags()

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), 3)
        for key, value in resp.items():
            self.assertEqual(tags[key], value)

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='pytagstorage')
    def test_upload_block_blob_with_tags(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob_client, resp = self._create_block_blob(tags=tags)

        resp = blob_client.get_blob_tags()

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), 3)

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='pytagstorage')
    def test_get_blob_properties_returns_tags_num(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob_client, resp = self._create_block_blob(tags=tags)

        resp = blob_client.get_blob_properties()
        downloaded = blob_client.download_blob()

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(resp.tag_count, len(tags))
        self.assertEqual(downloaded.properties.tag_count, len(tags))

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='pytagstorage')
    def test_create_append_blob_with_tags(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        tags = {"+-./:=_ ": "firsttag", "tag2": "+-./:=_", "+-./:=_1": "+-./:=_"}
        blob_client, resp = self._create_append_blob(tags=tags)

        resp = blob_client.get_blob_tags()

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), 3)

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='pytagstorage')
    def test_create_page_blob_with_tags(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob_client, resp = self._create_page_blob(tags=tags)

        resp = blob_client.get_blob_tags()

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), 3)

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='pytagstorage')
    def test_commit_block_list_with_tags(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob_client, resp = self._create_empty_block_blob(tags={'condition tag': 'test tag'})

        blob_client.stage_block('1', b'AAA')
        blob_client.stage_block('2', b'BBB')
        blob_client.stage_block('3', b'CCC')

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        with self.assertRaises(ResourceModifiedError):
            blob_client.commit_block_list(block_list, tags=tags, if_tags_match_condition="\"condition tag\"='wrong tag'")
        blob_client.commit_block_list(block_list, tags=tags, if_tags_match_condition="\"condition tag\"='test tag'")

        resp = blob_client.get_blob_tags()

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), len(tags))

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='pytagstorage')
    def test_start_copy_from_url_with_tags(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob_client, resp = self._create_block_blob()

        # Act
        sourceblob = '{0}/{1}/{2}'.format(
            self.account_url(storage_account, "blob"), self.container_name, blob_client.blob_name)

        copyblob = self.bsc.get_blob_client(self.container_name, 'blob1copy')
        copy = copyblob.start_copy_from_url(sourceblob, tags=tags)

        # Assert
        self.assertIsNotNone(copy)
        self.assertEqual(copy['copy_status'], 'success')
        self.assertFalse(isinstance(copy['copy_status'], Enum))
        self.assertIsNotNone(copy['copy_id'])

        copy_content = copyblob.download_blob().readall()
        self.assertEqual(copy_content, self.byte_data)

        resp = copyblob.get_blob_tags()

        # Assert
        self.assertIsNotNone(resp)
        self.assertEqual(len(resp), len(tags))

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='pytagstorage')
    def test_list_blobs_returns_tags(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        self._create_block_blob(tags=tags)
        container = self.bsc.get_container_client(self.container_name)
        blob_list = container.list_blobs(include="tags")

        #Assert
        for blob in blob_list:
            self.assertEqual(blob.tag_count, len(tags))
            for key, value in blob.tags.items():
                self.assertEqual(tags[key], value)

    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='pytagstorage')
    def test_filter_blobs(self, resource_group, location, storage_account, storage_account_key):
        self._setup(storage_account, storage_account_key)
        container_name1 = self._create_container(prefix="container1")
        container_name2 = self._create_container(prefix="container2")
        container_name3 = self._create_container(prefix="container3")

        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        self._create_block_blob(tags=tags, blob_name="blob1")
        self._create_block_blob(tags=tags, blob_name="blob2", container_name=container_name1)
        self._create_block_blob(tags=tags, blob_name="blob3", container_name=container_name2)
        self._create_block_blob(tags=tags, blob_name="blob4", container_name=container_name3)

        if self.is_live:
            sleep(10)
        where = "tag1='firsttag'"
        blob_list = self.bsc.find_blobs_by_tags(filter_expression=where, results_per_page=2).by_page()
        first_page = next(blob_list)
        items_on_page1 = list(first_page)
        second_page = next(blob_list)
        items_on_page2 = list(second_page)

        self.assertEqual(2, len(items_on_page1))
        self.assertEqual(2, len(items_on_page2))

    @pytest.mark.live_test_only
    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='pytagstorage')
    def test_filter_blobs_using_account_sas(self, resource_group, location, storage_account, storage_account_key):
        token = generate_account_sas(
            storage_account.name,
            storage_account_key,
            ResourceTypes(service=True, container=True, object=True),
            AccountSasPermissions(write=True, list=True, read=True, delete_previous_version=True, tag=True,
                                  filter_by_tags=True),
            datetime.utcnow() + timedelta(hours=1),
        )
        self._setup(storage_account, token)

        tags = {"year": '1000', "tag2": "secondtag", "tag3": "thirdtag", "habitat_type": 'Shallow Lowland Billabongs'}
        blob_client, _ = self._create_block_blob(tags=tags, container_name=self.container_name)
        blob_client.set_blob_tags(tags=tags)
        tags_on_blob = blob_client.get_blob_tags()
        self.assertEqual(len(tags_on_blob), len(tags))

        if self.is_live:
            sleep(10)

        # To filter in a specific container use:
        # where = "@container='{}' and tag1='1000' and tag2 = 'secondtag'".format(container_name1)
        where = "\"year\"='1000' and tag2 = 'secondtag' and tag3='thirdtag'"

        blob_list = self.bsc.find_blobs_by_tags(filter_expression=where, results_per_page=2).by_page()
        first_page = next(blob_list)
        items_on_page1 = list(first_page)
        self.assertEqual(1, len(items_on_page1))

    @pytest.mark.live_test_only
    @GlobalResourceGroupPreparer()
    @StorageAccountPreparer(random_name_enabled=True, location="canadacentral", name_prefix='pytagstorage')
    def test_set_blob_tags_using_blob_sas(self, resource_group, location, storage_account, storage_account_key):
        token = generate_account_sas(
            storage_account.name,
            storage_account_key,
            ResourceTypes(service=True, container=True, object=True),
            AccountSasPermissions(write=True, list=True, read=True, delete_previous_version=True, tag=True,
                                  filter_by_tags=True),
            datetime.utcnow() + timedelta(hours=1),
        )
        self._setup(storage_account, token)

        tags = {"year": '1000', "tag2": "secondtag", "tag3": "thirdtag", "habitat_type": 'Shallow Lowland Billabongs'}
        blob_client, _ = self._create_block_blob(tags=tags, container_name=self.container_name)
        token1 = generate_blob_sas(
            storage_account.name,
            self.container_name,
            blob_client.blob_name,
            account_key=storage_account_key,
            permission=BlobSasPermissions(delete_previous_version=True, tag=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        blob_client=BlobClient.from_blob_url(blob_client.url, token1)
        blob_client.set_blob_tags(tags=tags)
        tags_on_blob = blob_client.get_blob_tags()
        self.assertEqual(len(tags_on_blob), len(tags))

        if self.is_live:
            sleep(10)

        # To filter in a specific container use:
        # where = "@container='{}' and tag1='1000' and tag2 = 'secondtag'".format(container_name1)
        where = "\"year\"='1000' and tag2 = 'secondtag' and tag3='thirdtag'"

        blob_list = self.bsc.find_blobs_by_tags(filter_expression=where, results_per_page=2).by_page()
        first_page = next(blob_list)
        items_on_page1 = list(first_page)
        self.assertEqual(1, len(items_on_page1))
#------------------------------------------------------------------------------
