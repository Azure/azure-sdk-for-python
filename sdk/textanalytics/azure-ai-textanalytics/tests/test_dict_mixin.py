# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
from azure.ai.textanalytics import _models


class TestDictMixin:

    def test_contains(self):
        model = _models.DictMixin()
        key = "name"
        value = "steve"
        model.__setitem__(key, value)
        assert model.__contains__(key)
