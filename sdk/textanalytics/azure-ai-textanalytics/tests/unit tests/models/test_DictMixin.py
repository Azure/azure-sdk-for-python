# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest

from azure.ai.textanalytics._models import DictMixin


class TestDictMixin:

    def test_contains(self):
        dict_mixin = DictMixin()
        key = "name"
        value = "steve"
        dict_mixin.__setitem__(key, value)
        assert dict_mixin.__contains__(key)