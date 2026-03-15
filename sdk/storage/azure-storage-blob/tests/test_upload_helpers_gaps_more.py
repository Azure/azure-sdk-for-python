# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from io import BytesIO
from types import SimpleNamespace
from unittest import mock

import pytest
from azure.core.exceptions import HttpResponseError, ResourceModifiedError
from azure.storage.blob._encryption import _ENCRYPTION_PROTOCOL_V1
from azure.storage.blob._generated.models import ModifiedAccessConditions
from azure.storage.blob._upload_helpers import upload_append_blob, upload_page_blob


def _blob_settings():
    return SimpleNamespace(max_page_size=512, max_block_size=4)


def _http_error(status_code, message="boom"):
    response = SimpleNamespace(
        status_code=status_code,
        reason=message,
        headers={},
        request=SimpleNamespace(url="https://example.com/blob")
    )
    return HttpResponseError(message=message, response=response)


def test_upload_page_blob_when_premium_tier_has_no_value_attribute_passes_object_to_create():
    client = mock.Mock()
    premium_tier = object()
    create_response = {"etag": "etag-0"}
    client.create.return_value = create_response

    result = upload_page_blob(
        client=client,
        overwrite=True,
        encryption_options={},
        blob_settings=_blob_settings(),
        headers={},
        stream=BytesIO(b""),
        length=0,
        validate_content=False,
        max_concurrency=1,
        modified_access_conditions=ModifiedAccessConditions(),
        premium_page_blob_tier=premium_tier,
    )

    assert result == {"etag": "etag-0"}
    assert client.create.call_args.kwargs["tier"] is premium_tier
    assert client.create.call_args.kwargs["blob_content_length"] == 0



def test_upload_page_blob_when_v1_encryption_enabled_sets_encryptor_and_if_match():
    client = mock.Mock()
    client.create.return_value = {"etag": "etag-1"}
    headers = {}
    encryptor = object()
    padder = object()
    upload_response = {"chunk_upload": "complete"}

    with mock.patch(
        "azure.storage.blob._upload_helpers.generate_blob_encryption_data",
        return_value=(b"cek", b"iv", "encrypted-metadata"),
    ), mock.patch(
        "azure.storage.blob._upload_helpers.get_blob_encryptor_and_padder",
        return_value=(encryptor, padder),
    ), mock.patch(
        "azure.storage.blob._upload_helpers.upload_data_chunks",
        return_value=upload_response,
    ) as upload_data_chunks_mock:
        result = upload_page_blob(
            client=client,
            overwrite=True,
            encryption_options={"key": object(), "version": _ENCRYPTION_PROTOCOL_V1},
            blob_settings=_blob_settings(),
            headers=headers,
            stream=BytesIO(b"a" * 512),
            length=512,
            validate_content=False,
            max_concurrency=1,
            modified_access_conditions=ModifiedAccessConditions(),
        )

    modified_access_conditions = upload_data_chunks_mock.call_args.kwargs["modified_access_conditions"]

    assert result == {"chunk_upload": "complete"}
    assert headers["x-ms-meta-encryptiondata"] == "encrypted-metadata"
    assert upload_data_chunks_mock.call_args.kwargs["encryptor"] is encryptor
    assert upload_data_chunks_mock.call_args.kwargs["padder"] is padder
    assert isinstance(modified_access_conditions, ModifiedAccessConditions)
    assert modified_access_conditions.if_match == "etag-1"



def test_upload_page_blob_when_overwrite_true_and_modified_error_raises_original_error():
    client = mock.Mock()
    client.create.side_effect = _http_error(412, "condition not met")
    mod_error = ResourceModifiedError(message="original modified error", response=client.create.side_effect.response)

    with mock.patch(
        "azure.storage.blob._upload_helpers.process_storage_error",
        side_effect=mod_error,
    ) as process_storage_error_mock, mock.patch(
        "azure.storage.blob._upload_helpers._convert_mod_error"
    ) as convert_mod_error_mock:
        with pytest.raises(ResourceModifiedError) as exc:
            upload_page_blob(
                client=client,
                overwrite=True,
                encryption_options={},
                blob_settings=_blob_settings(),
                headers={},
                stream=BytesIO(b""),
                length=0,
                validate_content=False,
                max_concurrency=1,
                modified_access_conditions=ModifiedAccessConditions(),
            )

    assert exc.value is mod_error
    assert process_storage_error_mock.call_count == 1
    convert_mod_error_mock.assert_not_called()



def test_upload_append_blob_when_first_append_gets_404_rewinds_stream_and_retries():
    client = mock.Mock()
    client.create.return_value = {"etag": "created"}
    stream = BytesIO(b"abcdef")
    not_found_error = _http_error(404, "missing append blob")
    stream_positions = []

    def upload_side_effect(**kwargs):
        stream_positions.append(kwargs["stream"].tell())
        if len(stream_positions) == 1:
            kwargs["stream"].read(2)
            raise not_found_error
        return {"etag": "retried"}

    with mock.patch(
        "azure.storage.blob._upload_helpers.upload_data_chunks",
        side_effect=upload_side_effect,
    ) as upload_data_chunks_mock:
        result = upload_append_blob(
            client=client,
            overwrite=False,
            encryption_options={},
            blob_settings=_blob_settings(),
            headers={},
            stream=stream,
            length=6,
            validate_content=False,
            max_concurrency=1,
        )

    assert result == {"etag": "retried"}
    assert stream_positions == [0, 0]
    assert client.create.call_count == 1
    assert client.create.call_args.kwargs["content_length"] == 0
    assert upload_data_chunks_mock.call_count == 2
