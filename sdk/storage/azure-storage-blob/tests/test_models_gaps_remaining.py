# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from types import SimpleNamespace
from unittest import mock

import pytest
from azure.core.exceptions import HttpResponseError
from azure.storage.blob._models import ContainerEncryptionScope, PageRangePaged


def test_pagerangepaged_get_next_cb_when_process_storage_error_returns_value_returns_processed_value():
    def command(**kwargs):
        raise HttpResponseError(message="boom")

    pager = PageRangePaged(command)
    sentinel = object()

    # Tests defensive branch — requires mock.
    with mock.patch("azure.storage.blob._models.process_storage_error", return_value=sentinel) as patched:
        result = pager._get_next_cb(None)

    assert result is None
    assert patched.call_count == 1
    assert patched.call_args[0][0].args[0] == "boom"



def test_pagerangepaged_build_page_when_response_is_none_raises_stop_iteration():
    pager = PageRangePaged(lambda **kwargs: None)

    with pytest.raises(StopIteration):
        pager._extract_data_cb(("primary", None))

    assert pager.location_mode == "primary"
    assert pager._response is None



def test_containerencryptionscope_from_generated_when_default_scope_missing_returns_none():
    generated = SimpleNamespace(
        properties=SimpleNamespace(
            default_encryption_scope=None,
            prevent_encryption_scope_override=True,
        )
    )

    scope = ContainerEncryptionScope._from_generated(generated)

    assert scope is None
