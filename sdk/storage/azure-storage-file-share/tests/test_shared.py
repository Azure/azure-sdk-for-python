# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import asyncio
from io import BytesIO
from types import SimpleNamespace

from azure.storage.fileshare._models import DictMixin
from azure.storage.fileshare._shared.request_handlers import (
    validate_and_format_range_headers,
)
from azure.storage.fileshare._shared.uploads import (
    BlockBlobChunkUploader,
    _remove_parallel_access_conditions,
    _update_append_position,
    _update_etag,
)
from azure.storage.fileshare._shared.uploads_async import (
    BlockBlobChunkUploader as AsyncBlockBlobChunkUploader,
)


class _KeywordOnlyBlockService:
    def __init__(self):
        self.blocks = []

    def stage_block(self, *, block_id, content_length, body, **kwargs):
        self.blocks.append((block_id, content_length, body, kwargs))


class _AsyncKeywordOnlyBlockService:
    def __init__(self):
        self.blocks = []

    async def stage_block(self, *, block_id, content_length, body, **kwargs):
        self.blocks.append((block_id, content_length, body, kwargs))


def _create_uploader(uploader_class, service):
    return uploader_class(
        service=service,
        total_size=1,
        chunk_size=1,
        stream=BytesIO(b"x"),
        parallel=False,
    )


def test_range_validation_uses_boolean():
    assert validate_and_format_range_headers(0, 1, check_content_md5=True) == (
        "bytes=0-1",
        True,
    )


def test_dict_mixin_update_returns_none():
    model = DictMixin()
    assert model.update({"key": "value"}) is None
    assert model["key"] == "value"


def test_parallel_upload_removes_both_access_condition_representations():
    options = {
        "etag": "etag",
        "match_condition": "IfNotModified",
        "if_modified_since": "modified",
        "if_unmodified_since": "unmodified",
        "if_tags": "tag",
        "modified_access_conditions": SimpleNamespace(if_match="etag"),
        "lease": "lease",
    }

    _remove_parallel_access_conditions(options)

    assert options == {"modified_access_conditions": None, "lease": "lease"}


def test_sequential_upload_updates_both_access_condition_representations():
    flattened_options = {"etag": "old", "append_position": 0}
    _update_etag(flattened_options, "new")
    _update_append_position(flattened_options, 4)
    assert flattened_options == {"etag": "new", "append_position": 4}

    modified_conditions = SimpleNamespace(if_match="old")
    append_conditions = SimpleNamespace(append_position=0)
    legacy_options = {
        "modified_access_conditions": modified_conditions,
        "append_position_access_conditions": append_conditions,
    }
    _update_etag(legacy_options, "new")
    _update_append_position(legacy_options, 4)
    assert modified_conditions.if_match == "new"
    assert append_conditions.append_position == 4
    assert "etag" not in legacy_options
    assert "append_position" not in legacy_options

    default_options = {}
    _update_append_position(default_options, 4)
    assert default_options == {"append_position": 4}


def test_block_upload_uses_generated_keyword_only_signature():
    service = _KeywordOnlyBlockService()
    uploader = _create_uploader(BlockBlobChunkUploader, service)

    uploader.process_chunk((0, b"x"))

    assert service.blocks[0][1:3] == (1, b"x")


def test_async_block_upload_uses_generated_keyword_only_signature():
    service = _AsyncKeywordOnlyBlockService()
    uploader = _create_uploader(AsyncBlockBlobChunkUploader, service)

    asyncio.run(uploader.process_chunk((0, b"x")))

    assert service.blocks[0][1:3] == (1, b"x")
