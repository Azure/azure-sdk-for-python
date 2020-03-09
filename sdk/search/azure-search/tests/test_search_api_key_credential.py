# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest

from azure.search import SearchApiKeyCredential

BAD_KEYS = (10, 10.2, None, dict(), set(), list())


class TestSearchApiKeyCredential(object):
    def test_init(self):
        credential = SearchApiKeyCredential("some_key")
        assert credential.api_key == "some_key"

    @pytest.mark.parametrize("bad_key", BAD_KEYS, ids=repr)
    def test_bad_init(self, bad_key):
        with pytest.raises(TypeError) as e:
            SearchApiKeyCredential(bad_key)
            assert str(e) == "api_key must be a string."

    def test_update_key(self):
        credential = SearchApiKeyCredential("some_key")
        assert credential.api_key == "some_key"
        credential.update_key("new_key")
        assert credential.api_key == "new_key"
