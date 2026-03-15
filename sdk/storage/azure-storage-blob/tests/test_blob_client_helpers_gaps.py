# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from unittest import mock

import pytest
from azure.storage.blob import BlobClient
from azure.storage.blob.aio import BlobClient as AsyncBlobClient
from azure.storage.blob._shared.uploads_async import AsyncIterStreamer

from devtools_testutils.storage import StorageRecordedTestCase
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from settings.testcase import BlobPreparer
from test_helpers_async import MockLegacyTransport


class TestStorageBlobClientHelperGaps(StorageRecordedTestCase):

    def test_blob_client_when_account_url_is_none_raises_value_error(self):
        with pytest.raises(ValueError) as error:
            BlobClient(None, container_name='foo', blob_name='bar')

        assert str(error.value) == 'Account URL must be a string.'

    def test_blob_client_when_account_url_is_not_string_preserves_attribute_error_cause(self):
        with pytest.raises(ValueError) as error:
            BlobClient(123, container_name='foo', blob_name='bar')

        assert str(error.value.__cause__) == "'int' object has no attribute 'lower'"

    def test_blob_client_when_account_url_is_missing_host_raises_invalid_url(self):
        with pytest.raises(ValueError) as error:
            BlobClient('', container_name='foo', blob_name='bar')

        assert str(error.value) == 'Invalid URL: https://'

    @BlobPreparer()
    def test_blob_client_when_container_name_is_str_encodes_container_in_url(self, **kwargs):
        storage_account_name = kwargs.pop('storage_account_name')
        storage_account_key = kwargs.pop('storage_account_key')

        blob = BlobClient(
            self.account_url(storage_account_name, 'blob'),
            container_name='cont áiner',
            blob_name='blob',
            credential=storage_account_key.secret,
        )

        assert blob.url == 'https://{}.blob.core.windows.net/cont%20%C3%A1iner/blob'.format(storage_account_name)


class _AsyncIterableData:
    def __init__(self, chunks):
        self.chunks = chunks

    def __aiter__(self):
        async def iterator():
            for chunk in self.chunks:
                yield chunk
        return iterator()


class TestStorageBlobClientHelperAsyncGaps(AsyncStorageRecordedTestCase):

    @BlobPreparer()
    async def test_upload_blob_when_data_is_async_iterable_uses_async_iter_streamer(self, **kwargs):
        storage_account_name = kwargs.pop('storage_account_name')
        storage_account_key = kwargs.pop('storage_account_key')

        transport = MockLegacyTransport()
        blob_client = AsyncBlobClient(
            self.account_url(storage_account_name, 'blob'),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret,
            transport=transport,
            retry_total=0,
        )

        try:
            data = _AsyncIterableData([b'Hello ', b'World'])
            with mock.patch('azure.storage.blob._blob_client_helpers.AsyncIterStreamer', wraps=AsyncIterStreamer) as patched:
                await blob_client.upload_blob(data, length=11, overwrite=True)

            assert patched.call_count == 1
            assert patched.call_args.kwargs['encoding'] == 'UTF-8'

            downloaded = await (await blob_client.download_blob()).read()
            assert downloaded == b'Hello Async World!'
        finally:
            await blob_client.close()

from azure.storage.blob import CustomerProvidedEncryptionKey
from azure.storage.blob._models import DelimitedTextDialect, QuickQueryDialect

from fake_credentials import CPK_KEY_HASH, CPK_KEY_VALUE


class TestBlobClientHelpersGaps(StorageRecordedTestCase):

    def _get_blob_client(self, storage_account_name, storage_account_key):
        return BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret,
        )

    @BlobPreparer()
    def test_upload_blob_when_blob_type_is_unsupported_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = self._get_blob_client(storage_account_name, storage_account_key)

        with pytest.raises(ValueError) as exc:
            blob_client.upload_blob(b"hello world", blob_type="UnsupportedBlob")

        assert str(exc.value) == "Unsupported BlobType: UnsupportedBlob"

    @BlobPreparer()
    def test_download_blob_when_length_is_set_without_offset_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = self._get_blob_client(storage_account_name, storage_account_key)

        with pytest.raises(ValueError) as exc:
            blob_client.download_blob(length=3)

        assert str(exc.value) == "Offset value must not be None if length is set."

    @BlobPreparer()
    def test_query_blob_when_blob_format_is_delimited_json_enum_uses_json_serialization(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = self._get_blob_client(storage_account_name, storage_account_key)
        captured = {}

        def fake_query(**options):
            captured.update(options)
            return {"etag": "etag"}, iter(())

        # Tests defensive branch — requires mock.
        with mock.patch.object(blob_client._client.blob, "query", side_effect=fake_query), \
                mock.patch("azure.storage.blob._blob_client.BlobQueryReader", side_effect=lambda **reader_kwargs: reader_kwargs):
            reader = blob_client.query_blob(
                "SELECT * from BlobStorage",
                blob_format=QuickQueryDialect.DelimitedJson,
                output_format=DelimitedTextDialect(lineterminator='|')
            )

        assert captured["query_request"].input_serialization.format.type == "json"
        assert captured["query_request"].output_serialization.format.type == "delimited"
        assert reader["record_delimiter"] == "|"

    @BlobPreparer()
    def test_query_blob_when_output_format_is_delimited_json_enum_uses_json_serialization(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = self._get_blob_client(storage_account_name, storage_account_key)
        captured = {}

        def fake_query(**options):
            captured.update(options)
            return {"etag": "etag"}, iter(())

        # Tests defensive branch — requires mock.
        with mock.patch.object(blob_client._client.blob, "query", side_effect=fake_query), \
                mock.patch("azure.storage.blob._blob_client.BlobQueryReader", side_effect=lambda **reader_kwargs: reader_kwargs):
            reader = blob_client.query_blob(
                "SELECT * from BlobStorage",
                blob_format=DelimitedTextDialect(lineterminator='|'),
                output_format=QuickQueryDialect.DelimitedJson
            )

        assert captured["query_request"].input_serialization.format.type == "delimited"
        assert captured["query_request"].output_serialization.format.type == "json"
        assert reader["record_delimiter"] == "\n"

    @BlobPreparer()
    def test_query_blob_when_cpk_is_provided_populates_cpk_info(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = self._get_blob_client(storage_account_name, storage_account_key)
        captured = {}

        def fake_query(**options):
            captured.update(options)
            return {"etag": "etag"}, iter(())

        # Tests defensive branch — requires mock.
        with mock.patch.object(blob_client._client.blob, "query", side_effect=fake_query), \
                mock.patch("azure.storage.blob._blob_client.BlobQueryReader", side_effect=lambda **reader_kwargs: reader_kwargs):
            reader = blob_client.query_blob(
                "SELECT * from BlobStorage",
                blob_format=DelimitedTextDialect(),
                cpk=CustomerProvidedEncryptionKey(CPK_KEY_VALUE, CPK_KEY_HASH)
            )

        assert captured["cpk_info"].encryption_key == CPK_KEY_VALUE
        assert captured["cpk_info"].encryption_key_sha256 == CPK_KEY_HASH
        assert captured["cpk_info"].encryption_algorithm == "AES256"
        assert reader["record_delimiter"] == "\n"

from azure.storage.blob import ContentSettings
from azure.storage.blob._blob_client_helpers import (
    _create_append_blob_options,
    _create_page_blob_options,
    _set_http_headers_options,
)
from azure.storage.blob._shared.response_handlers import return_response_headers


def test_set_http_headers_options_when_content_settings_provided_populates_blob_http_headers():
    content_settings = ContentSettings(
        content_type='text/plain',
        content_encoding='utf-8',
        content_language='en-US',
        content_disposition='inline',
        cache_control='no-cache',
        content_md5=b'1234'
    )

    options = _set_http_headers_options(content_settings=content_settings, timeout=15)

    assert options['timeout'] == 15
    assert options['cls'] is return_response_headers
    assert options['blob_http_headers'].blob_cache_control == 'no-cache'
    assert options['blob_http_headers'].blob_content_type == 'text/plain'
    assert options['blob_http_headers'].blob_content_md5 == b'1234'
    assert options['blob_http_headers'].blob_content_encoding == 'utf-8'
    assert options['blob_http_headers'].blob_content_language == 'en-US'
    assert options['blob_http_headers'].blob_content_disposition == 'inline'



def test_create_page_blob_options_when_content_settings_provided_populates_blob_http_headers():
    content_settings = ContentSettings(
        content_type='application/octet-stream',
        content_encoding='gzip',
        content_language='fr-FR',
        content_disposition='attachment',
        cache_control='max-age=60',
        content_md5=b'abcd'
    )

    options = _create_page_blob_options(size=512, content_settings=content_settings)

    assert options['content_length'] == 0
    assert options['blob_content_length'] == 512
    assert options['cls'] is return_response_headers
    assert options['blob_http_headers'].blob_cache_control == 'max-age=60'
    assert options['blob_http_headers'].blob_content_type == 'application/octet-stream'
    assert options['blob_http_headers'].blob_content_md5 == b'abcd'
    assert options['blob_http_headers'].blob_content_encoding == 'gzip'
    assert options['blob_http_headers'].blob_content_language == 'fr-FR'
    assert options['blob_http_headers'].blob_content_disposition == 'attachment'



def test_create_page_blob_options_when_premium_tier_is_string_uses_fallback_value_directly():
    options = _create_page_blob_options(size=1024, premium_page_blob_tier='P4')

    assert options['content_length'] == 0
    assert options['blob_content_length'] == 1024
    assert options['tier'] == 'P4'



def test_create_page_blob_options_when_premium_tier_has_no_value_attribute_preserves_original_object():
    class CustomTier(object):
        pass

    custom_tier = CustomTier()

    options = _create_page_blob_options(size=2048, premium_page_blob_tier=custom_tier)

    assert options['content_length'] == 0
    assert options['blob_content_length'] == 2048
    assert options['tier'] is custom_tier



def test_create_append_blob_options_when_content_settings_provided_populates_blob_http_headers():
    content_settings = ContentSettings(
        content_type='text/csv',
        content_encoding='ascii',
        content_language='de-DE',
        content_disposition='filename="data.csv"',
        cache_control='public',
        content_md5=b'wxyz'
    )

    options = _create_append_blob_options(content_settings=content_settings)

    assert options['content_length'] == 0
    assert options['cls'] is return_response_headers
    assert options['blob_http_headers'].blob_cache_control == 'public'
    assert options['blob_http_headers'].blob_content_type == 'text/csv'
    assert options['blob_http_headers'].blob_content_md5 == b'wxyz'
    assert options['blob_http_headers'].blob_content_encoding == 'ascii'
    assert options['blob_http_headers'].blob_content_language == 'de-DE'
    assert options['blob_http_headers'].blob_content_disposition == 'filename="data.csv"'

from azure.storage.blob import BlobLeaseClient


class _LeaseWithId(object):
    def __init__(self, lease_id):
        self.id = lease_id


class TestBlobClientStartCopyFromUrlSourceLeaseGaps(StorageRecordedTestCase):

    def _get_blob_client(self, storage_account_name, storage_account_key):
        return BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='container',
            blob_name=self.get_resource_name('blob'),
            credential=storage_account_key.secret,
        )

    @BlobPreparer()
    def test_start_copy_from_url_when_source_lease_is_provided_forwards_source_lease_header(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = self._get_blob_client(storage_account_name, storage_account_key)
        captured = {}

        def fake_start_copy_from_url(*args, **options):
            captured.update(options)
            return {'copy_id': 'copy-id-1', 'copy_status': 'success'}

        with mock.patch.object(blob_client._client.blob, 'start_copy_from_url', side_effect=fake_start_copy_from_url):
            response = blob_client.start_copy_from_url(
                'https://example.com/source/sourceblob',
                source_lease=_LeaseWithId('lease-id-1')
            )

        assert response['copy_id'] == 'copy-id-1'
        assert captured['headers']['x-ms-source-lease-id'] == 'lease-id-1'

    @BlobPreparer()
    def test_start_copy_from_url_when_source_lease_has_id_attribute_uses_try_path(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = self._get_blob_client(storage_account_name, storage_account_key)
        captured = {}
        source_lease = _LeaseWithId('lease-id-2')

        def fake_start_copy_from_url(*args, **options):
            captured.update(options)
            return {'copy_id': 'copy-id-2', 'copy_status': 'success'}

        with mock.patch.object(blob_client._client.blob, 'start_copy_from_url', side_effect=fake_start_copy_from_url):
            response = blob_client.start_copy_from_url(
                'https://example.com/source/sourceblob',
                source_lease=source_lease
            )

        assert response['copy_status'] == 'success'
        assert captured['headers']['x-ms-source-lease-id'] == source_lease.id

    @BlobPreparer()
    def test_start_copy_from_url_when_source_lease_is_blob_lease_client_sets_header_from_id(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = self._get_blob_client(storage_account_name, storage_account_key)
        source_lease = BlobLeaseClient(blob_client, lease_id='lease-id-3')
        captured = {}

        def fake_start_copy_from_url(*args, **options):
            captured.update(options)
            return {'copy_id': 'copy-id-3', 'copy_status': 'success'}

        with mock.patch.object(blob_client._client.blob, 'start_copy_from_url', side_effect=fake_start_copy_from_url):
            response = blob_client.start_copy_from_url(
                'https://example.com/source/sourceblob',
                source_lease=source_lease
            )

        assert response['copy_id'] == 'copy-id-3'
        assert captured['headers']['x-ms-source-lease-id'] == 'lease-id-3'

    @BlobPreparer()
    def test_start_copy_from_url_when_source_lease_is_string_uses_attribute_error_fallback(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = self._get_blob_client(storage_account_name, storage_account_key)

        def fake_start_copy_from_url(*args, **options):
            return {'copy_id': 'copy-id-4', 'copy_status': 'success'}

        with mock.patch.object(blob_client._client.blob, 'start_copy_from_url', side_effect=fake_start_copy_from_url):
            response = blob_client.start_copy_from_url(
                'https://example.com/source/sourceblob',
                source_lease='lease-id-4'
            )

        assert response['copy_id'] == 'copy-id-4'
        assert response['copy_status'] == 'success'

    @BlobPreparer()
    def test_start_copy_from_url_when_source_lease_is_string_sets_header_to_raw_value(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = self._get_blob_client(storage_account_name, storage_account_key)
        captured = {}

        def fake_start_copy_from_url(*args, **options):
            captured.update(options)
            return {'copy_id': 'copy-id-5', 'copy_status': 'success'}

        with mock.patch.object(blob_client._client.blob, 'start_copy_from_url', side_effect=fake_start_copy_from_url):
            response = blob_client.start_copy_from_url(
                'https://example.com/source/sourceblob',
                source_lease='lease-id-5'
            )

        assert response['copy_status'] == 'success'
        assert captured['headers']['x-ms-source-lease-id'] == 'lease-id-5'
