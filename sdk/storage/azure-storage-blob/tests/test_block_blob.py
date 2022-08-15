# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import uuid
from datetime import datetime, timedelta
from io import BytesIO

import pytest
from azure.core.exceptions import HttpResponseError, ResourceExistsError, ResourceModifiedError, ResourceNotFoundError
from azure.mgmt.storage import StorageManagementClient
from azure.storage.blob import (
    BlobBlock,
    BlobClient,
    BlobImmutabilityPolicyMode,
    BlobSasPermissions,
    BlobServiceClient,
    BlobType,
    ContentSettings,
    CustomerProvidedEncryptionKey,
    generate_blob_sas,
    ImmutabilityPolicy,
    StandardBlobTier,
)
from azure.storage.blob._shared.policies import StorageContentValidation

from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer
from test_helpers import NonSeekableStream, ProgressTracker

#------------------------------------------------------------------------------
TEST_BLOB_PREFIX = 'blob'
LARGE_BLOB_SIZE = 5 * 1024 + 5
#------------------------------------------------------------------------------


class TestStorageBlockBlob(StorageRecordedTestCase):
    # --Helpers-----------------------------------------------------------------
    def _setup(self, storage_account_name, key, container_name='utcontainer'):
        # test chunking functionality by reducing the size of each chunk,
        # otherwise the tests would take too long to execute
        self.bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=key,
            max_single_put_size=1024,
            max_block_size=1024)
        self.config = self.bsc._config
        self.container_name = self.get_resource_name(container_name)
        self.source_container_name = self.get_resource_name('utcontainersource1')

        if self.is_live:
            try:
                self.bsc.create_container(self.container_name)
            except:
                pass
            try:
                self.bsc.create_container(self.source_container_name)
            except:
                pass

    def _teardown(self, FILE_PATH):
        if os.path.isfile(FILE_PATH):
            try:
                os.remove(FILE_PATH)
            except:
                pass

    def _get_blob_reference(self, prefix=TEST_BLOB_PREFIX):
        return self.get_resource_name(prefix)

    def _create_blob(self, tags=None, data=b'', **kwargs):
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.upload_blob(data, tags=tags, overwrite=True, **kwargs)
        return blob

    def _create_source_blob(self, data):
        blob_client = self.bsc.get_blob_client(self.source_container_name, self.get_resource_name(TEST_BLOB_PREFIX+"1"))
        blob_client.upload_blob(data, overwrite=True)
        return blob_client

    def assertBlobEqual(self, container_name, blob_name, expected_data):
        blob = self.bsc.get_blob_client(container_name, blob_name)
        actual_data = blob.download_blob()
        assert actual_data.readall() == expected_data

    #--Test cases for block blobs --------------------------------------------
    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_blob_from_url_with_oauth(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        self._setup(storage_account_name, storage_account_key)
        source_blob_data = self.get_random_bytes(LARGE_BLOB_SIZE)
        source_blob_client = self._create_source_blob(data=source_blob_data)
        destination_blob_client = self._create_blob()
        token = "Bearer {}".format(self.generate_oauth_token().get_token("https://storage.azure.com/.default").token)

        # Assert this operation fails without a credential
        with pytest.raises(HttpResponseError):
            destination_blob_client.upload_blob_from_url(source_blob_client.url)
        # Assert it passes after passing an oauth credential
        destination_blob_client.upload_blob_from_url(source_blob_client.url, source_authorization=token, overwrite=True)
        destination_blob_data = destination_blob_client.download_blob().readall()
        assert source_blob_data == destination_blob_data

    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_blob_with_and_without_overwrite(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob = self._create_blob(data=b"source blob data")
        # Act
        sas = self.generate_sas(
            generate_blob_sas,
            account_name=storage_account_name,
            account_key=storage_account_key,
            container_name=self.container_name,
            blob_name=blob.blob_name,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        source_blob = '{0}/{1}/{2}?{3}'.format(
            self.account_url(storage_account_name, "blob"), self.container_name, blob.blob_name, sas)

        blob_name = self.get_resource_name("blobcopy")
        new_blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
        new_blob_client.upload_blob(b'destination blob data')
        # Assert
        with pytest.raises(ResourceExistsError):
            new_blob_client.upload_blob_from_url(source_blob, overwrite=False)
        new_blob = new_blob_client.upload_blob_from_url(source_blob, overwrite=True)
        assert new_blob is not None
        new_blob_content = new_blob_client.download_blob().readall()
        assert new_blob_content == b'source blob data'

    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_blob_from_url_with_existing_blob(
            self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        blob = self._create_blob(data=b"test data")
        # Act
        sas = self.generate_sas(
            generate_blob_sas,
            account_name=storage_account_name,
            account_key=storage_account_key,
            container_name=self.container_name,
            blob_name=blob.blob_name,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        source_blob = '{0}/{1}/{2}?{3}'.format(
            self.account_url(storage_account_name, "blob"), self.container_name, blob.blob_name, sas)

        blob_name = self.get_resource_name("blobcopy")
        new_blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
        new_blob = new_blob_client.upload_blob_from_url(source_blob)
        # Assert
        assert new_blob is not None
        new_blob_content = new_blob_client.download_blob().readall()
        assert new_blob_content == b'test data'

    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_blob_from_url_with_standard_tier_specified(
            self, storage_account_name, storage_account_key):
        # Arrange
        self._setup(storage_account_name, storage_account_key, container_name="testcontainer")
        blob = self._create_blob()
        self.bsc.get_blob_client(self.container_name, blob.blob_name)
        sas = self.generate_sas(
            generate_blob_sas,
            account_name=storage_account_name,
            account_key=storage_account_key,
            container_name=self.container_name,
            blob_name=blob.blob_name,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        # Act
        source_blob = '{0}/{1}/{2}?{3}'.format(
            self.account_url(storage_account_name, "blob"), self.container_name, blob.blob_name, sas)

        blob_name = self.get_resource_name("blobcopy")
        new_blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob_tier = StandardBlobTier.Hot
        new_blob.upload_blob_from_url(source_blob, standard_blob_tier=blob_tier)

        new_blob_properties = new_blob.get_blob_properties()

        # Assert
        assert new_blob_properties.blob_tier == blob_tier

    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_blob_with_destination_lease(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        source_blob = self._create_blob()
        sas = self.generate_sas(
            generate_blob_sas,
            account_name=storage_account_name,
            account_key=storage_account_key,
            container_name=self.container_name,
            blob_name=source_blob.blob_name,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        source_blob_url = '{0}/{1}/{2}?{3}'.format(
            self.account_url(storage_account_name, "blob"), self.container_name, source_blob.blob_name, sas)
        blob_name = self.get_resource_name("blobcopy")
        new_blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
        new_blob_client.upload_blob(data="test")
        new_blob_lease = new_blob_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')
        with pytest.raises(HttpResponseError):
            new_blob_client.upload_blob_from_url(
                source_blob_url, destination_lease="baddde9e-8247-4276-8bfa-c7a8081eba1d", overwrite=True)
        with pytest.raises(HttpResponseError):
            new_blob_client.upload_blob_from_url(source_blob_url)
        new_blob_client.upload_blob_from_url(
            source_blob_url, destination_lease=new_blob_lease)

    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_blob_from_url_if_match_condition(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        # Act
        self._setup(storage_account_name, storage_account_key)
        source_blob = self._create_blob()
        early_test_datetime = self.get_datetime_variable(
            variables, "early_test_dt", (datetime.utcnow() - timedelta(minutes=15)))
        late_test_datetime = self.get_datetime_variable(
            variables, "late_test_dt", (datetime.utcnow() + timedelta(minutes=15)))
        sas = self.generate_sas(
            generate_blob_sas,
            account_name=storage_account_name,
            account_key=storage_account_key,
            container_name=self.container_name,
            blob_name=source_blob.blob_name,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        source_blob_url = '{0}/{1}/{2}?{3}'.format(
            self.account_url(storage_account_name, "blob"), self.container_name, source_blob.blob_name, sas)
        blob_name = self.get_resource_name("blobcopy")
        new_blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
        new_blob_client.upload_blob(data="fake data")

        # Assert
        with pytest.raises(ResourceModifiedError):
            new_blob_client.upload_blob_from_url(
                source_blob_url, if_modified_since=late_test_datetime, overwrite=True)
        new_blob_client.upload_blob_from_url(
            source_blob_url, if_modified_since=early_test_datetime, overwrite=True)
        with pytest.raises(ResourceModifiedError):
            new_blob_client.upload_blob_from_url(
                source_blob_url, if_unmodified_since=early_test_datetime, overwrite=True)
        new_blob_client.upload_blob_from_url(
            source_blob_url, if_unmodified_since=late_test_datetime, overwrite=True)
        with pytest.raises(ResourceNotFoundError):
            new_blob_client.upload_blob_from_url(
                source_blob_url, source_if_modified_since=late_test_datetime, overwrite=True)
        new_blob_client.upload_blob_from_url(
            source_blob_url, source_if_modified_since=early_test_datetime, overwrite=True)
        with pytest.raises(ResourceNotFoundError):
            new_blob_client.upload_blob_from_url(
                source_blob_url, source_if_unmodified_since=early_test_datetime, overwrite=True)
        new_blob_client.upload_blob_from_url(
            source_blob_url, source_if_unmodified_since=late_test_datetime, overwrite=True)

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_blob_from_url_with_cpk(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Act
        self._setup(storage_account_name, storage_account_key)
        source_blob = self._create_blob(data=b"This is test data to be copied over.")
        test_cpk = CustomerProvidedEncryptionKey(key_value="MDEyMzQ1NjcwMTIzNDU2NzAxMjM0NTY3MDEyMzQ1Njc=",
                                                 key_hash="3QFFFpRA5+XANHqwwbT4yXDmrT/2JaLt/FKHjzhOdoE=")
        sas = self.generate_sas(
            generate_blob_sas,
            account_name=storage_account_name,
            account_key=storage_account_key,
            container_name=self.container_name,
            blob_name=source_blob.blob_name,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        source_blob_url = '{0}/{1}/{2}?{3}'.format(
            self.account_url(storage_account_name, "blob"), self.container_name, source_blob.blob_name, sas)
        blob_name = self.get_resource_name("blobcopy")
        new_blob = self.bsc.get_blob_client(self.container_name, blob_name)
        new_blob.upload_blob_from_url(
            source_blob_url, include_source_blob_properties=True, cpk=test_cpk)

        # Assert
        with pytest.raises(HttpResponseError):
            new_blob.create_snapshot()
        new_blob.create_snapshot(cpk=test_cpk)
        assert new_blob.create_snapshot is not None

    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_blob_from_url_overwrite_properties(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Act
        self._setup(storage_account_name, storage_account_key)
        source_blob_content_settings = ContentSettings(content_language='spanish')
        new_blob_content_settings = ContentSettings(content_language='english')
        source_blob_tags = {"tag1": "sourcetag", "tag2": "secondsourcetag"}
        new_blob_tags = {"tag1": "copytag"}
        new_blob_cpk = CustomerProvidedEncryptionKey(key_value="MDEyMzQ1NjcwMTIzNDU2NzAxMjM0NTY3MDEyMzQ1Njc=",
                                                     key_hash="3QFFFpRA5+XANHqwwbT4yXDmrT/2JaLt/FKHjzhOdoE=")
        source_blob = self._create_blob(
            data=b"This is test data to be copied over.",
            tags=source_blob_tags,
            content_settings=source_blob_content_settings)
        sas = self.generate_sas(
            generate_blob_sas,
            account_name=storage_account_name,
            account_key=storage_account_key,
            container_name=self.container_name,
            blob_name=source_blob.blob_name,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        source_blob_url = '{0}/{1}/{2}?{3}'.format(
            self.account_url(storage_account_name, "blob"), self.container_name, source_blob.blob_name, sas)

        blob_name = self.get_resource_name("blobcopy")
        new_blob = self.bsc.get_blob_client(self.container_name, blob_name)
        new_blob.upload_blob_from_url(source_blob_url,
                                      include_source_blob_properties=True,
                                      tags=new_blob_tags,
                                      content_settings=new_blob_content_settings,
                                      overwrite=True,
                                      cpk=new_blob_cpk)
        new_blob_props = new_blob.get_blob_properties(cpk=new_blob_cpk)

        # Assert that source blob properties did not take precedence.
        assert new_blob_props.tag_count == 1
        assert new_blob_props.content_settings.content_language == new_blob_content_settings.content_language

    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_blob_from_url_with_source_content_md5(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Act
        self._setup(storage_account_name, storage_account_key)
        source_blob = self._create_blob(data=b"This is test data to be copied over.")
        source_blob_props = source_blob.get_blob_properties()
        source_md5 = source_blob_props.content_settings.content_md5
        bad_source_md5 = StorageContentValidation.get_content_md5(b"this is bad data")
        sas = self.generate_sas(
            generate_blob_sas,
            account_name=storage_account_name,
            account_key=storage_account_key,
            container_name=self.container_name,
            blob_name=source_blob.blob_name,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        source_blob_url = '{0}/{1}/{2}?{3}'.format(
            self.account_url(storage_account_name, "blob"), self.container_name, source_blob.blob_name, sas)
        blob_name = self.get_resource_name("blobcopy")
        new_blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Assert
        new_blob.upload_blob_from_url(
            source_blob_url, include_source_blob_properties=True, source_content_md5=source_md5)
        with pytest.raises(HttpResponseError):
            new_blob.upload_blob_from_url(
                source_blob_url, include_source_blob_properties=False, source_content_md5=bad_source_md5)
        new_blob_content_md5 = new_blob.get_blob_properties().content_settings.content_md5
        assert new_blob_content_md5 == source_md5

    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_blob_from_url_source_and_destination_properties(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Act
        self._setup(storage_account_name, storage_account_key)
        content_settings = ContentSettings(
            content_type='application/octet-stream',
            content_language='spanish',
            content_disposition='inline'
        )
        source_blob = self._create_blob(
             data=b"This is test data to be copied over.",
             tags={"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"},
             content_settings=content_settings,
             standard_blob_tier=StandardBlobTier.Cool)
        source_blob.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')
        source_blob_props = source_blob.get_blob_properties()
        sas = self.generate_sas(
            generate_blob_sas,
            account_name=storage_account_name,
            account_key=storage_account_key,
            container_name=self.container_name,
            blob_name=source_blob.blob_name,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        source_blob_url = '{0}/{1}/{2}?{3}'.format(
            self.account_url(storage_account_name, "blob"), self.container_name, source_blob.blob_name, sas)
        blob_name = self.get_resource_name("blobcopy")
        new_blob_copy1 = self.bsc.get_blob_client(self.container_name, blob_name)
        new_blob_copy2 = self.bsc.get_blob_client(self.container_name, 'blob2copy')
        new_blob_copy1.upload_blob_from_url(
            source_blob_url, include_source_blob_properties=True)
        new_blob_copy2.upload_blob_from_url(
            source_blob_url, include_source_blob_properties=False)

        new_blob_copy1_props = new_blob_copy1.get_blob_properties()
        new_blob_copy2_props = new_blob_copy2.get_blob_properties()

        # Assert
        assert new_blob_copy1_props.content_settings.content_language == \
               source_blob_props.content_settings.content_language
        assert new_blob_copy2_props.content_settings.content_language != \
               source_blob_props.content_settings.content_language

        assert source_blob_props.lease.status == 'locked'
        assert new_blob_copy1_props.lease.status == 'unlocked'
        assert new_blob_copy2_props.lease.status == 'unlocked'

        assert source_blob_props.blob_tier == 'Cool'
        assert new_blob_copy1_props.blob_tier == 'Hot'
        assert new_blob_copy2_props.blob_tier == 'Hot'

        assert source_blob_props.tag_count == 3
        assert new_blob_copy1_props.tag_count is None
        assert new_blob_copy2_props.tag_count is None

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_block(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob = self._create_blob()

        # Act
        for i in range(5):
            headers = blob.stage_block(i, 'block {0}'.format(i).encode('utf-8'))
            assert 'content_crc64' in headers

        # Assert

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_block_with_response(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob = self._create_blob()

        def return_response(resp, _, headers):
            return (resp, headers)

        # Act
        resp, headers = blob.stage_block(0, 'block 0', cls=return_response)

        # Assert
        # This has changed to resp.http_response.status_code since now we return the pipeline response
        assert 201 == resp.http_response.status_code
        assert 'x-ms-content-crc64' in headers

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_block_unicode(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob = self._create_blob()

        # Act
        headers = blob.stage_block('1', u'啊齄丂狛狜')
        assert 'content_crc64' in headers

        # Assert

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_block_with_md5(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob = self._create_blob()

        # Act
        blob.stage_block(1, b'block', validate_content=True)

        # Assert

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_block_list(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.stage_block('1', b'AAA')
        blob.stage_block('2', b'BBB')
        blob.stage_block('3', b'CCC')

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        put_block_list_resp = blob.commit_block_list(block_list)

        # Assert
        content = blob.download_blob()
        assert content.readall() == b'AAABBBCCC'
        assert content.properties.etag == put_block_list_resp.get('etag')
        assert content.properties.last_modified == put_block_list_resp.get('last_modified')

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_block_with_immutability_policy(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")
        storage_resource_group_name = kwargs.pop("storage_resource_group_name")
        variables = kwargs.pop("variables", {})

        self._setup(versioned_storage_account_name, versioned_storage_account_key)
        container_name = self.get_resource_name('vlwcontainer')

        if self.is_live:
            token_credential = self.generate_oauth_token()
            subscription_id = self.get_settings_value("SUBSCRIPTION_ID")

            mgmt_client = StorageManagementClient(token_credential, subscription_id, '2021-04-01')
            property = mgmt_client.models().BlobContainer(
                immutable_storage_with_versioning=mgmt_client.models().ImmutableStorageWithVersioning(enabled=True))
            mgmt_client.blob_containers.create(storage_resource_group_name, versioned_storage_account_name, container_name, blob_container=property)

        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(container_name, blob_name)
        blob.stage_block('1', b'AAA')
        blob.stage_block('2', b'BBB')
        blob.stage_block('3', b'CCC')

        # Act
        expiry_time = self.get_datetime_variable(variables, "expiry_time", datetime.utcnow() + timedelta(seconds=5))
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        immutability_policy = ImmutabilityPolicy(expiry_time=expiry_time,
                                                 policy_mode=BlobImmutabilityPolicyMode.Unlocked)
        put_block_list_resp = blob.commit_block_list(block_list,
                                                     immutability_policy=immutability_policy,
                                                     legal_hold=True,
                                                     )

        # Assert
        download_resp = blob.download_blob()
        assert download_resp.readall() == b'AAABBBCCC'
        assert download_resp.properties.etag == put_block_list_resp.get('etag')
        assert download_resp.properties.last_modified == put_block_list_resp.get('last_modified')
        assert download_resp.properties['has_legal_hold']
        assert download_resp.properties['immutability_policy']['expiry_time'] is not None
        assert download_resp.properties['immutability_policy']['policy_mode'] is not None

        if self.is_live:
            blob.delete_immutability_policy()
            blob.set_legal_hold(False)
            blob.delete_blob()
            mgmt_client.blob_containers.delete(storage_resource_group_name, versioned_storage_account_name, container_name)

        return variables

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_block_list_invalid_block_id(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.stage_block('1', b'AAA')
        blob.stage_block('2', b'BBB')
        blob.stage_block('3', b'CCC')

        # Act
        try:
            block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='4')]
            blob.commit_block_list(block_list)
            self.fail()
        except HttpResponseError as e:
            assert str(e).find('specified block list is invalid') >= 0

        # Assert

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_block_list_with_md5(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.stage_block('1', b'AAA')
        blob.stage_block('2', b'BBB')
        blob.stage_block('3', b'CCC')

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        blob.commit_block_list(block_list, validate_content=True)

        # Assert

    @BlobPreparer()
    @recorded_by_proxy
    def test_put_block_list_with_blob_tier_specified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")


        # Arrange
        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
        blob_client.stage_block('1', b'AAA')
        blob_client.stage_block('2', b'BBB')
        blob_client.stage_block('3', b'CCC')
        blob_tier = StandardBlobTier.Cool

        # Act
        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        blob_client.commit_block_list(block_list,
                                      standard_blob_tier=blob_tier)

        # Assert
        blob_properties = blob_client.get_blob_properties()
        assert blob_properties.blob_tier == blob_tier

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_block_list_no_blocks(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        tags = {"tag1": "firsttag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob = self._create_blob(tags=tags)

        # Act
        with pytest.raises(ResourceModifiedError):
            blob.get_block_list('all', if_tags_match_condition="\"condition tag\"='wrong tag'")
        block_list = blob.get_block_list('all', if_tags_match_condition="\"tag1\"='firsttag'")

        # Assert
        assert block_list is not None
        assert len(block_list[1]) == 0
        assert len(block_list[0]) == 0

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_block_list_uncommitted_blocks(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.stage_block('1', b'AAA')
        blob.stage_block('2', b'BBB')
        blob.stage_block('3', b'CCC')

        # Act
        block_list = blob.get_block_list('uncommitted')

        # Assert
        assert block_list is not None
        assert len(block_list) == 2
        assert len(block_list[1]) == 3
        assert len(block_list[0]) == 0
        assert block_list[1][0].id == '1'
        assert block_list[1][0].size == 3
        assert block_list[1][1].id == '2'
        assert block_list[1][1].size == 3
        assert block_list[1][2].id == '3'
        assert block_list[1][2].size == 3

    @BlobPreparer()
    @recorded_by_proxy
    def test_get_block_list_committed_blocks(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob.stage_block('1', b'AAA')
        blob.stage_block('2', b'BBB')
        blob.stage_block('3', b'CCC')

        block_list = [BlobBlock(block_id='1'), BlobBlock(block_id='2'), BlobBlock(block_id='3')]
        blob.commit_block_list(block_list)

        # Act
        block_list = blob.get_block_list('committed')

        # Assert
        assert block_list is not None
        assert len(block_list) == 2
        assert len(block_list[1]) == 0
        assert len(block_list[0]) == 3
        assert block_list[0][0].id == '1'
        assert block_list[0][0].size == 3
        assert block_list[0][1].id == '2'
        assert block_list[0][1].size == 3
        assert block_list[0][2].id == '3'
        assert block_list[0][2].size == 3

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_small_block_blob_with_no_overwrite(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data1 = b'hello world'
        data2 = b'hello second world'

        # Act
        create_resp = blob.upload_blob(data1, overwrite=True)

        with pytest.raises(ResourceExistsError):
            blob.upload_blob(data2, overwrite=False)

        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data1)
        assert props.etag == create_resp.get('etag')
        assert props.last_modified == create_resp.get('last_modified')
        assert props.blob_type == BlobType.BlockBlob

    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_blob_content_md5(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob1_name = self._get_blob_reference(prefix="blob1")
        blob2_name = self._get_blob_reference(prefix="blob2")
        blob1 = self.bsc.get_blob_client(self.container_name, blob1_name)
        blob2 = self.bsc.get_blob_client(self.container_name, blob2_name)
        data1 = b'hello world'
        data2 = b'hello world this wont work'

        # Act
        blob1.upload_blob(data1, overwrite=True)
        blob1_md5 = blob1.get_blob_properties().content_settings.content_md5
        blob2_content_settings = ContentSettings(content_md5=blob1_md5)

        # Passing data that does not match the md5
        with pytest.raises(HttpResponseError):
            blob2.upload_blob(data2, content_settings=blob2_content_settings)
        # Correct data and corresponding md5
        blob2.upload_blob(data1, content_settings=blob2_content_settings)
        blob2_md5 = blob2.get_blob_properties().content_settings.content_md5
        assert blob1_md5 == blob2_md5

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_small_block_blob_with_overwrite(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data1 = b'hello world'
        data2 = b'hello second world'

        # Act
        create_resp = blob.upload_blob(data1, overwrite=True)
        update_resp = blob.upload_blob(data2, overwrite=True)

        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data2)
        assert props.etag == update_resp.get('etag')
        assert props.last_modified == update_resp.get('last_modified')
        assert props.blob_type == BlobType.BlockBlob

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_large_block_blob_with_no_overwrite(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data1 = self.get_random_bytes(LARGE_BLOB_SIZE)
        data2 = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        create_resp = blob.upload_blob(data1, overwrite=True, metadata={'blobdata': 'data1'})

        with pytest.raises(ResourceExistsError):
            blob.upload_blob(data2, overwrite=False, metadata={'blobdata': 'data2'})

        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data1)
        assert props.etag == create_resp.get('etag')
        assert props.last_modified == create_resp.get('last_modified')
        assert props.blob_type == BlobType.BlockBlob
        assert props.metadata == {'blobdata': 'data1'}
        assert props.size == LARGE_BLOB_SIZE

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_large_block_blob_with_overwrite(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data1 = self.get_random_bytes(LARGE_BLOB_SIZE)
        data2 = self.get_random_bytes(LARGE_BLOB_SIZE + 512)

        # Act
        create_resp = blob.upload_blob(data1, overwrite=True, metadata={'blobdata': 'data1'})
        update_resp = blob.upload_blob(data2, overwrite=True, metadata={'blobdata': 'data2'})

        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data2)
        assert props.etag == update_resp.get('etag')
        assert props.last_modified == update_resp.get('last_modified')
        assert props.blob_type == BlobType.BlockBlob
        assert props.metadata == {'blobdata': 'data2'}
        assert props.size == LARGE_BLOB_SIZE + 512

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_from_bytes_single_put(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = b'hello world'

        # Act
        create_resp = blob.upload_blob(data)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        assert props.etag == create_resp.get('etag')
        assert props.last_modified == create_resp.get('last_modified')

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_from_0_bytes(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = b''

        # Act
        create_resp = blob.upload_blob(data)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        assert props.etag == create_resp.get('etag')
        assert props.last_modified == create_resp.get('last_modified')

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_from_bytes_blob_unicode(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = u'hello world'

        # Act
        create_resp = blob.upload_blob(data)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        assert props.etag == create_resp.get('etag')
        assert props.last_modified == create_resp.get('last_modified')

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_from_bytes_blob_unicode(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        data = u'hello world'
        create_resp = blob.upload_blob(data)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data.encode('utf-8'))
        assert props.etag == create_resp.get('etag')
        assert props.last_modified == create_resp.get('last_modified')

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_from_bytes_blob_with_lease_id(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob = self._create_blob()
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        lease = blob.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # Act
        create_resp = blob.upload_blob(data, lease=lease)

        # Assert
        output = blob.download_blob(lease=lease)
        assert output.readall() == data
        assert output.properties.etag == create_resp.get('etag')
        assert output.properties.last_modified == create_resp.get('last_modified')

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_from_bytes_with_metadata(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        blob.upload_blob(data, metadata=metadata)

        # Assert
        md = blob.get_blob_properties().metadata
        assert md == metadata

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_from_bytes_with_properties(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        content_settings=ContentSettings(
                content_type='image/png',
                content_language='spanish')
        blob.upload_blob(data, content_settings=content_settings)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        properties = blob.get_blob_properties()
        assert properties.content_settings.content_type == content_settings.content_type
        assert properties.content_settings.content_language == content_settings.content_language

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_from_bytes_with_progress(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        progress = []
        def callback(response):
            current = response.context['upload_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        create_resp = blob.upload_blob(data, raw_response_hook=callback)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assert_upload_progress(len(data), self.config.max_block_size, progress)
        assert props.etag == create_resp.get('etag')
        assert props.last_modified == create_resp.get('last_modified')

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_from_bytes_with_index(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        blob.upload_blob(data[3:])

        # Assert
        assert data[3:] == blob.download_blob().readall()

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_from_bytes_with_index_and_count(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        blob.upload_blob(data[3:], length=5)

        # Assert
        assert data[3:8] == blob.download_blob().readall()

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_from_bytes_with_index_and_count_and_properties(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        content_settings=ContentSettings(
                content_type='image/png',
                content_language='spanish')
        blob.upload_blob(data[3:], length=5, content_settings=content_settings)

        # Assert
        assert data[3:8] == blob.download_blob().readall()
        properties = blob.get_blob_properties()
        assert properties.content_settings.content_type == content_settings.content_type
        assert properties.content_settings.content_language == content_settings.content_language

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_from_bytes_non_parallel(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        blob.upload_blob(data, length=LARGE_BLOB_SIZE, max_concurrency=1)

        # Assert
        self.assertBlobEqual(self.container_name, blob.blob_name, data)

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_from_bytes_with_blob_tier_specified(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
        data = b'hello world'
        blob_tier = StandardBlobTier.Cool

        # Act
        blob_client.upload_blob(data, standard_blob_tier=blob_tier)
        blob_properties = blob_client.get_blob_properties()

        # Assert
        assert blob_properties.blob_tier == blob_tier

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_from_path(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'create_blob_from_input.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            create_resp = blob.upload_blob(stream)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        assert props.etag == create_resp.get('etag')
        assert props.last_modified == create_resp.get('last_modified')
        self._teardown(FILE_PATH)

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_from_path_non_parallel(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(100)
        FILE_PATH = 'create_blob_from_path_non_par.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            create_resp = blob.upload_blob(stream, length=100, max_concurrency=1)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        assert props.etag == create_resp.get('etag')
        assert props.last_modified == create_resp.get('last_modified')
        self._teardown(FILE_PATH)

    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_blob_from_path_non_parallel_with_standard_blob_tier(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(100)
        FILE_PATH = '_path_non_parallel_with_standard_blob.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)
        blob_tier = StandardBlobTier.Cool
        # Act
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, length=100, max_concurrency=1, standard_blob_tier=blob_tier)
        props = blob.get_blob_properties()

        # Assert
        assert props.blob_tier == blob_tier
        self._teardown(FILE_PATH)

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_from_path_with_progress(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'create_blob_from_path_with_progr.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []
        def callback(response):
            current = response.context['upload_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, raw_response_hook=callback)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assert_upload_progress(len(data), self.config.max_block_size, progress)
        self._teardown(FILE_PATH)

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_from_path_with_properties(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'blob_from_path_with_properties.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        content_settings=ContentSettings(
            content_type='image/png',
            content_language='spanish')
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, content_settings=content_settings)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        properties = blob.get_blob_properties()
        assert properties.content_settings.content_type == content_settings.content_type
        assert properties.content_settings.content_language == content_settings.content_language
        self._teardown(FILE_PATH)

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_from_stream_chunked_upload(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'blob_from_stream_chunked_up.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            create_resp = blob.upload_blob(stream)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        assert props.etag == create_resp.get('etag')
        assert props.last_modified == create_resp.get('last_modified')
        self._teardown(FILE_PATH)

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_from_stream_nonseek_chunk_upload_known_size(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        blob_size = len(data) - 66
        FILE_PATH = 'stream_nonseek_chunk_upld_knwn_size.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            non_seekable_file = NonSeekableStream(stream)
            blob.upload_blob(non_seekable_file, length=blob_size, max_concurrency=1)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])
        self._teardown(FILE_PATH)

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_from_stream_nonseek_chunk_upld_unkwn_size(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'stream_nonseek_chunk_upld.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        with open(FILE_PATH, 'rb') as stream:
            non_seekable_file = NonSeekableStream(stream)
            blob.upload_blob(non_seekable_file, max_concurrency=1)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self._teardown(FILE_PATH)

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_from_stream_with_progress_chunked_upload(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'stream_with_progress_chunked.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        progress = []
        def callback(response):
            current = response.context['upload_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, raw_response_hook=callback)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assert_upload_progress(len(data), self.config.max_block_size, progress)
        self._teardown(FILE_PATH)

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_from_stream_chunked_upload_with_count(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'chunked_upload_with_count.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        blob_size = len(data) - 301
        with open(FILE_PATH, 'rb') as stream:
            resp = blob.upload_blob(stream, length=blob_size)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])
        self._teardown(FILE_PATH)

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_from_stream_chunk_upload_with_cntandrops(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'from_stream_chunk_upload_with_cntandrops.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        content_settings=ContentSettings(
            content_type='image/png',
            content_language='spanish')
        blob_size = len(data) - 301
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, length=blob_size, content_settings=content_settings)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data[:blob_size])
        properties = blob.get_blob_properties()
        assert properties.content_settings.content_type == content_settings.content_type
        assert properties.content_settings.content_language == content_settings.content_language
        self._teardown(FILE_PATH)

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_from_stream_chunked_upload_with_properties(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'stream_chunked_upload_with_properties.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)

        # Act
        content_settings=ContentSettings(
            content_type='image/png',
            content_language='spanish')
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, content_settings=content_settings)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        properties = blob.get_blob_properties()
        assert properties.content_settings.content_type == content_settings.content_type
        assert properties.content_settings.content_language == content_settings.content_language
        self._teardown(FILE_PATH)

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_create_blob_from_stream_chunked_upload_with_properties_parallel(self, **kwargs):
        # parallel tests introduce random order of requests, can only run live
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)
        FILE_PATH = 'stream_chunked_upload_with_properties.temp.{}.dat'.format(str(uuid.uuid4()))
        with open(FILE_PATH, 'wb') as stream:
            stream.write(data)
        blob_tier = StandardBlobTier.Cool

        # Act
        content_settings = ContentSettings(
            content_type='image/png',
            content_language='spanish')
        with open(FILE_PATH, 'rb') as stream:
            blob.upload_blob(stream, content_settings=content_settings, max_concurrency=2, standard_blob_tier=blob_tier)

        properties = blob.get_blob_properties()

        # Assert
        assert properties.blob_tier == blob_tier
        self._teardown(FILE_PATH)

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_from_text(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-8')

        # Act
        create_resp = blob.upload_blob(text)
        props = blob.get_blob_properties()

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        assert props.etag == create_resp.get('etag')
        assert props.last_modified == create_resp.get('last_modified')

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_from_text_with_encoding(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')

        # Act
        blob.upload_blob(text, encoding='utf-16')

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_from_text_with_encoding_and_progress(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')

        # Act
        progress = []
        def callback(response):
            current = response.context['upload_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        blob.upload_blob(text, encoding='utf-16', raw_response_hook=callback)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, data)
        self.assert_upload_progress(len(data), self.config.max_block_size, progress)

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_from_text_chunked_upload(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_text_data(LARGE_BLOB_SIZE)
        encoded_data = data.encode('utf-8')

        # Act
        blob.upload_blob(data)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, encoded_data)

        # Assert
        self.assertBlobEqual(self.container_name, blob_name, encoded_data)

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_with_md5(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = b'hello world'

        # Act
        blob.upload_blob(data, validate_content=True)

        # Assert

    @BlobPreparer()
    @recorded_by_proxy
    def test_create_blob_with_md5_chunked(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = self.get_random_bytes(LARGE_BLOB_SIZE)

        # Act
        blob.upload_blob(data, validate_content=True)

        # Assert

    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_progress_single_put(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        data = b'a' * 5 * 1024

        progress = ProgressTracker(len(data), len(data))

        # Act
        blob_client = BlobClient(
            self.account_url(storage_account_name, 'blob'),
            self.container_name, blob_name,
            credential=storage_account_key)

        blob_client.upload_blob(
            data,
            blob_type=BlobType.BlockBlob,
            overwrite=True,
            max_concurrency=1,
            progress_hook=progress.assert_progress)

        # Assert
        progress.assert_complete()

    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_progress_chunked_non_parallel(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        data = b'a' * 5 * 1024

        progress = ProgressTracker(len(data), 1024)

        # Act
        blob_client = BlobClient(
            self.account_url(storage_account_name, 'blob'),
            self.container_name, blob_name,
            credential=storage_account_key,
            max_single_put_size=1024, max_block_size=1024)

        blob_client.upload_blob(
            data,
            blob_type=BlobType.BlockBlob,
            overwrite=True,
            max_concurrency=1,
            progress_hook=progress.assert_progress)

        # Assert
        progress.assert_complete()

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_upload_progress_chunked_parallel(self, **kwargs):
        # parallel tests introduce random order of requests, can only run live
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        data = b'a' * 5 * 1024

        progress = ProgressTracker(len(data), 1024)

        # Act
        blob_client = BlobClient(
            self.account_url(storage_account_name, 'blob'),
            self.container_name, blob_name,
            credential=storage_account_key,
            max_single_put_size=1024, max_block_size=1024)

        blob_client.upload_blob(
            data,
            blob_type=BlobType.BlockBlob,
            overwrite=True,
            max_concurrency=3,
            progress_hook=progress.assert_progress)

        # Assert
        progress.assert_complete()

    @pytest.mark.live_test_only
    @BlobPreparer()
    def test_upload_progress_unknown_size(self, **kwargs):
        # parallel tests introduce random order of requests, can only run live
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        data = b'a' * 5 * 1024

        progress = ProgressTracker(len(data), 1024)
        stream = NonSeekableStream(BytesIO(data))

        # Act
        blob_client = BlobClient(
            self.account_url(storage_account_name, 'blob'),
            self.container_name, blob_name,
            credential=storage_account_key,
            max_single_put_size=1024, max_block_size=1024)

        blob_client.upload_blob(
            data=stream,
            blob_type=BlobType.BlockBlob,
            overwrite=True,
            max_concurrency=3,
            progress_hook=progress.assert_progress)

        # Assert
        progress.assert_complete()

#------------------------------------------------------------------------------
