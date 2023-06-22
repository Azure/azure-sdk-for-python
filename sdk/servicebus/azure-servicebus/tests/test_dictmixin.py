# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


from azure.servicebus.management import _models
from azure.servicebus.amqp import _amqp_message

class TestDictMixin:

    def test_contains(self):
        model = _models.DictMixin()
        key = "name"
        value = "steve"
        model.__setitem__(key, value)
        assert model.__contains__(key)
        assert key in model

class TestDictMixinAmqp:

    def test_contains(self):
        model = _amqp_message.DictMixin()
        key = "name"
        value = "steve"
        model.__setitem__(key, value)
        assert model.__contains__(key)
        assert key in model
