# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


from azure.storage.fileshare import _models


class TestDictMixin:

    def test_contains(self):
        model = _models.DictMixin()
        key = "name"
        value = "steve"
        model.__setitem__(key, value)
        assert model.__contains__(key)
        assert key in model
