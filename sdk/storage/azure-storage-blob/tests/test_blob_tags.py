# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import pytest
from datetime import datetime, timedelta
from enum import Enum
from time import sleep

from azure.core.exceptions import ResourceExistsError, ResourceModifiedError, HttpResponseError
from azure.storage.blob import (
    AccountSasPermissions,
    BlobBlock,
    BlobClient,
    BlobSasPermissions,
    BlobServiceClient,
    generate_account_sas,
    generate_blob_sas,
    ResourceTypes
)

from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer

#------------------------------------------------------------------------------
TEST_CONTAINER_PREFIX = 'container'
TEST_BLOB_PREFIX = 'blob'
#------------------------------------------------------------------------------

class TestStorageBlobTags(StorageRecordedTestCase):

    def _setup(self, storage_account_name, key):
        self.bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=key)
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

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_blob_tags(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_client, _ = self._create_block_blob()

        # Act
        blob_tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        resp = blob_client.set_blob_tags(blob_tags)

        # Assert
        assert resp is not None

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_blob_tags_with_lease(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_client, _ = self._create_block_blob()
        lease = blob_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # Act
        blob_tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        with pytest.raises(HttpResponseError):
            blob_client.set_blob_tags(blob_tags)
        blob_client.set_blob_tags(blob_tags, lease=lease)

        blob_client.get_blob_tags()
        with pytest.raises(HttpResponseError):
            blob_client.get_blob_tags(lease="'d92e6954-3274-4715-811c-727ca7145303'")
        resp = blob_client.get_blob_tags(lease=lease)

        assert resp is not None
        assert len(resp) == 3

        blob_client.delete_blob(lease=lease)

    @BlobPreparer()
    @recorded_by_proxy
    def test_set_blob_tags_for_a_version(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")

        self._setup(versioned_storage_account_name, versioned_storage_account_key)
        # use this version to set tag
        blob_client, resp = self._create_block_blob()
        self._create_block_blob()

        # Act
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        resp = blob_client.set_blob_tags(tags, version_id=resp['version_id'])

        # Assert
        assert resp is not None

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_tags(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_client, resp = self._create_block_blob()

        # Act
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob_client.set_blob_tags(tags)

        resp = blob_client.get_blob_tags()

        # Assert
        assert resp is not None
        assert len(resp) == 3
        for key, value in resp.items():
            assert tags[key] == value

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_tags_for_a_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        tags = {"+-./:=_ ": "firsttag", "tag2": "+-./:=_", "+-./:=_1": "+-./:=_"}
        blob_client, resp = self._create_block_blob(tags=tags)

        snapshot = blob_client.create_snapshot()
        snapshot_client = self.bsc.get_blob_client(self.container_name, blob_client.blob_name, snapshot=snapshot)

        resp = snapshot_client.get_blob_tags()

        # Assert
        assert resp is not None
        assert len(resp) == 3
        for key, value in resp.items():
            assert tags[key] == value

    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_block_blob_with_tags(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob_client, resp = self._create_block_blob(tags=tags)

        resp = blob_client.get_blob_tags()

        # Assert
        assert resp is not None
        assert len(resp) == 3

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_blob_properties_returns_tags_num(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob_client, resp = self._create_block_blob(tags=tags)

        resp = blob_client.get_blob_properties()
        downloaded = blob_client.download_blob()

        # Assert
        assert resp is not None
        assert resp.tag_count == len(tags)
        assert downloaded.properties.tag_count == len(tags)

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_append_blob_with_tags(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        tags = {"+-./:=_ ": "firsttag", "tag2": "+-./:=_", "+-./:=_1": "+-./:=_"}
        blob_client, resp = self._create_append_blob(tags=tags)

        resp = blob_client.get_blob_tags()

        # Assert
        assert resp is not None
        assert len(resp) == 3

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_page_blob_with_tags(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob_client, resp = self._create_page_blob(tags=tags)

        resp = blob_client.get_blob_tags()

        # Assert
        assert resp is not None
        assert len(resp) == 3

    @BlobPreparer()
    @recorded_by_proxy
    def test_commit_block_list_with_tags(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob_client, resp = self._create_empty_block_blob(tags={'condition tag': 'test tag'})

        blob_client.stage_block('1', b'AAA')
        blob_client.stage_block('2', b'BBB')
        blob_client.stage_block('3', b'CCC')

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        with pytest.raises(ResourceModifiedError):
            blob_client.commit_block_list(block_list, tags=tags, if_tags_match_condition="\"condition tag\"='wrong tag'")
        blob_client.commit_block_list(block_list, tags=tags, if_tags_match_condition="\"condition tag\"='test tag'")

        resp = blob_client.get_blob_tags()

        # Assert
        assert resp is not None
        assert len(resp) == len(tags)

    @BlobPreparer()
    @recorded_by_proxy
    def test_start_copy_from_url_with_tags(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob_client, resp = self._create_block_blob()

        # Act
        sourceblob = '{0}/{1}/{2}'.format(
            self.account_url(storage_account_name, "blob"), self.container_name, blob_client.blob_name)

        copyblob = self.bsc.get_blob_client(self.container_name, 'blob1copy')
        copy = copyblob.start_copy_from_url(sourceblob, tags=tags)

        # Assert
        assert copy is not None
        assert copy['copy_status'] == 'success'
        assert not isinstance(copy['copy_status'], Enum)
        assert copy['copy_id'] is not None

        copy_content = copyblob.download_blob().readall()
        assert copy_content == self.byte_data

        resp = copyblob.get_blob_tags()

        # Assert
        assert resp is not None
        assert len(resp) == len(tags)

    @BlobPreparer()
    @recorded_by_proxy
    def test_start_copy_from_url_with_tags_copy_tags(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        source_blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        source_blob.upload_blob(b'Hello World', overwrite=True, tags=tags)

        source_sas = self.generate_sas(
            generate_blob_sas,
            storage_account_name,
            self.container_name,
            source_blob.blob_name,
            account_key=storage_account_key,
            permission=BlobSasPermissions(read=True, tag=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        source_url = source_blob.url + '?' + source_sas
        dest_blob = self.bsc.get_blob_client(self.container_name, 'blob1copy')

        # Act
        with pytest.raises(ValueError):
            dest_blob.start_copy_from_url(source_url, tags="COPY")

        copy = dest_blob.start_copy_from_url(source_url, tags="COPY", requires_sync=True)

        # Assert
        assert copy is not None
        assert copy['copy_status'] == 'success'
        assert not isinstance(copy['copy_status'], Enum)
        assert copy['copy_id'] is not None

        copy_tags = dest_blob.get_blob_tags()

        # Assert
        assert copy_tags is not None
        assert tags == copy_tags

    @BlobPreparer()
    @recorded_by_proxy
    def test_start_copy_from_url_with_tags_replace_tags(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        tags2 = {"hello": "world"}
        source_blob = self.bsc.get_blob_client(self.container_name, self._get_blob_reference())
        source_blob.upload_blob(b'Hello World', overwrite=True, tags=tags)

        source_sas = self.generate_sas(
            generate_blob_sas,
            storage_account_name,
            self.container_name,
            source_blob.blob_name,
            account_key=storage_account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        source_url = source_blob.url + '?' + source_sas
        dest_blob = self.bsc.get_blob_client(self.container_name, 'blob1copy')

        # Act
        copy = dest_blob.start_copy_from_url(source_url, tags=tags2, requires_sync=True)

        # Assert
        assert copy is not None
        assert copy['copy_status'] == 'success'
        assert not isinstance(copy['copy_status'], Enum)
        assert copy['copy_id'] is not None

        copy_tags = dest_blob.get_blob_tags()

        # Assert
        assert copy_tags is not None
        assert tags2 == copy_tags

    @BlobPreparer()
    @recorded_by_proxy
    def test_list_blobs_returns_tags(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        self._create_block_blob(tags=tags)
        container = self.bsc.get_container_client(self.container_name)
        blob_list = container.list_blobs(include="tags")

        #Assert
        for blob in blob_list:
            assert blob.tag_count == len(tags)
            for key, value in blob.tags.items():
                assert tags[key] == value

    @BlobPreparer()
    @recorded_by_proxy
    def test_filter_blobs(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
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
        where = "tag1='firsttag' and tag2='secondtag'"
        blob_list = self.bsc.find_blobs_by_tags(filter_expression=where, results_per_page=2).by_page()
        first_page = next(blob_list)
        items_on_page1 = list(first_page)
        second_page = next(blob_list)
        items_on_page2 = list(second_page)

        assert 2 == len(items_on_page1)
        assert 2 == len(items_on_page2)
        assert len(items_on_page2[0]['tags']) == 2
        assert items_on_page2[0]['tags']['tag1'] == 'firsttag'
        assert items_on_page2[0]['tags']['tag2'] == 'secondtag'

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_filter_blobs_using_account_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        token = generate_account_sas(
            storage_account_name,
            storage_account_key,
            ResourceTypes(service=True, container=True, object=True),
            AccountSasPermissions(write=True, list=True, read=True, delete_previous_version=True, tag=True,
                                  filter_by_tags=True),
            datetime.utcnow() + timedelta(hours=1),
        )
        self._setup(storage_account_name, token)

        tags = {"year": '1000', "tag2": "secondtag", "tag3": "thirdtag", "habitat_type": 'Shallow Lowland Billabongs'}
        blob_client, _ = self._create_block_blob(tags=tags, container_name=self.container_name)
        blob_client.set_blob_tags(tags=tags)
        tags_on_blob = blob_client.get_blob_tags()
        assert len(tags_on_blob) == len(tags)

        if self.is_live:
            sleep(10)

        # To filter in a specific container use:
        # where = "@container='{}' and tag1='1000' and tag2 = 'secondtag'".format(container_name1)
        where = "\"year\"='1000' and tag2 = 'secondtag' and tag3='thirdtag'"

        blob_list = self.bsc.find_blobs_by_tags(filter_expression=where, results_per_page=3).by_page()
        first_page = next(blob_list)
        items_on_page1 = list(first_page)
        assert 1 == len(items_on_page1)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_set_blob_tags_using_blob_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        token = generate_account_sas(
            storage_account_name,
            storage_account_key,
            ResourceTypes(service=True, container=True, object=True),
            AccountSasPermissions(write=True, list=True, read=True, delete_previous_version=True, tag=True,
                                  filter_by_tags=True),
            datetime.utcnow() + timedelta(hours=1),
        )
        self._setup(storage_account_name, token)

        tags = {"year": '2000', "tag2": "tagtwo", "tag3": "tagthree", "habitat_type": 'Shallow Lowland Billabongs'}
        blob_client, _ = self._create_block_blob(tags=tags, container_name=self.container_name)
        token1 = generate_blob_sas(
            storage_account_name,
            self.container_name,
            blob_client.blob_name,
            account_key=storage_account_key,
            permission=BlobSasPermissions(delete_previous_version=True, tag=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        blob_client=BlobClient.from_blob_url(blob_client.url, token1)
        blob_client.set_blob_tags(tags=tags)
        tags_on_blob = blob_client.get_blob_tags()
        assert len(tags_on_blob) == len(tags)

        if self.is_live:
            sleep(15)

        # To filter in a specific container use:
        # where = "@container='{}' and tag1='1000' and tag2 = 'secondtag'".format(container_name1)
        where = "\"year\"='2000' and tag2 = 'tagtwo' and tag3='tagthree'"

        blob_list = self.bsc.find_blobs_by_tags(filter_expression=where, results_per_page=3).by_page()
        first_page = next(blob_list)
        items_on_page1 = list(first_page)
        assert 1 == len(items_on_page1)
#------------------------------------------------------------------------------
