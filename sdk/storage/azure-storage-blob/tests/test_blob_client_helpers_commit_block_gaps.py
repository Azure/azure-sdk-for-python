# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

from azure.storage.blob import BlobBlock, ContentSettings
from azure.storage.blob._blob_client_helpers import (
    _commit_block_list_options,
    _stage_block_from_url_options,
    _stage_block_options,
)
from azure.storage.blob._shared import encode_base64


class _BlockState:
    def __init__(self, value):
        self.value = value


class TestBlobClientHelperCommitBlockBranches:

    def test_stage_block_when_data_is_bytes_and_length_is_shorter_commits_truncated_bytes(self):
        # Act
        options = _stage_block_options(block_id='1', data=b'abcde', length=3)

        # Assert
        assert options['block_id'] == encode_base64('1')
        assert options['content_length'] == 3
        assert options['body'] == b'abc'

    def test_stage_block_from_url_when_source_length_is_set_without_source_offset_raises_value_error(self):
        with pytest.raises(ValueError) as error:
            _stage_block_from_url_options(
                block_id='1',
                source_url='https://sourceaccount.blob.core.windows.net/sourcecontainer/sourceblob',
                source_length=4,
            )

        assert str(error.value) == 'Source offset value must not be None if length is set.'

    def test_commit_block_list_when_blob_block_state_is_uncommitted_commits_uncommitted_block(self):
        block = BlobBlock(block_id='block1', state='uncommitted')
        block.state = _BlockState(block.state)

        # Act
        options = _commit_block_list_options([block])
        blocks = options['blocks']

        # Assert
        assert blocks.committed == []
        assert blocks.uncommitted == [encode_base64('block1')]
        assert blocks.latest == []

    def test_commit_block_list_when_blob_block_uses_default_latest_state_commits_latest_block(self):
        block = BlobBlock(block_id='block1')
        block.state = _BlockState(block.state)

        # Act
        options = _commit_block_list_options([block])
        blocks = options['blocks']

        # Assert
        assert blocks.committed == []
        assert blocks.uncommitted == []
        assert blocks.latest == [encode_base64('block1')]

    def test_commit_block_list_when_content_settings_are_provided_applies_blob_http_headers(self):
        content_settings = ContentSettings(content_type='text/plain', cache_control='no-cache')

        # Act
        options = _commit_block_list_options(['block1'], content_settings=content_settings)
        blocks = options['blocks']
        headers = options['blob_http_headers']

        # Assert
        assert blocks.latest == [encode_base64('block1')]
        assert headers.blob_content_type == 'text/plain'
        assert headers.blob_cache_control == 'no-cache'
