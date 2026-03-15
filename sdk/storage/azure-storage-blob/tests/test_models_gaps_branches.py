# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from types import SimpleNamespace
from unittest import mock

import pytest
from azure.core.exceptions import HttpResponseError

from azure.storage.blob._models import BlobBlock, BlockState, ContainerPropertiesPaged, PageRangePaged

from devtools_testutils.storage import StorageRecordedTestCase


class TestModelsGaps(StorageRecordedTestCase):

    def test_containerpropertiespaged_get_next_cb_when_command_raises_http_response_error_returns_processed_value(self):
        # Tests defensive branch — requires mock.
        error = HttpResponseError(message="container failure")

        def command(**kwargs):
            raise error

        paged = ContainerPropertiesPaged(command, prefix="pref", results_per_page=2)

        with mock.patch("azure.storage.blob._models.process_storage_error", return_value="container handled") as process_storage_error:
            result = paged._get_next_cb("token")

        assert result is None
        process_storage_error.assert_called_once_with(error)

    def test_containerpropertiespaged_get_next_cb_when_process_storage_error_raises_converted_error(self):
        # Tests defensive branch — requires mock.
        error = HttpResponseError(message="container failure")

        def command(**kwargs):
            raise error

        paged = ContainerPropertiesPaged(command, results_per_page=1)

        with mock.patch("azure.storage.blob._models.process_storage_error", side_effect=ValueError("converted container error")):
            with pytest.raises(ValueError) as exc:
                paged._get_next_cb(None)

        assert str(exc.value) == "converted container error"

    def test_blobblock_from_generated_when_decoded_bytes_are_not_utf8_uses_original_name(self):
        generated = SimpleNamespace(name="/w==", size=3)

        block = BlobBlock._from_generated(generated)

        assert block.id == "/w=="

    def test_blobblock_from_generated_when_decoded_bytes_are_not_utf8_preserves_size_and_latest_state(self):
        generated = SimpleNamespace(name="/w==", size=8)

        block = BlobBlock._from_generated(generated)

        assert block.size == 8
        assert block.state == BlockState.LATEST

    def test_pagerangepaged_get_next_cb_when_command_raises_http_response_error_raises_processed_error(self):
        # Tests defensive branch — requires mock.
        error = HttpResponseError(message="page failure")

        def command(**kwargs):
            raise error

        paged = PageRangePaged(command, results_per_page=4)

        with mock.patch("azure.storage.blob._models.process_storage_error", side_effect=RuntimeError("converted page error")):
            with pytest.raises(RuntimeError) as exc:
                paged._get_next_cb("next")

        assert str(exc.value) == "converted page error"
