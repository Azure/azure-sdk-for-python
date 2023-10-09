# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


from azure.storage.blob._models import DictMixin


class TestDictMixin:

    def test_contains_haskey(self):
        model = DictMixin()
        key = "testkey"
        value = "testval"
        model.__setitem__(key, value)
        assert key in model  # calls __contains__
        assert model.has_key(key)

    def test_getitem_get(self):
        model = DictMixin()
        key = "testkey"
        value = "testval"
        model.__setitem__(key, value)
        assert model.__getitem__(key) == "testval"
        assert model.get(key) == "testval"

    def test_repr_str(self):
        model = DictMixin()
        key = "testkey"
        value = "testval"
        model.__setitem__(key, value)
        assert model.__repr__() == "{'testkey': 'testval'}"

    def test_len_delitem(self):
        model = DictMixin()
        key = "testkey"
        value = "testval"
        model.__setitem__(key, value)
        assert model.__len__() == 1
        model.__delitem__(key)
        assert model[key] is None

    def test_eq_ne(self):
        model = DictMixin()
        model2 = DictMixin()
        key = "testkey"
        value = "testval"
        value2 = "testval2"
        model.__setitem__(key, value)
        model2.__setitem__(key, value2)
        assert model.__ne__(model2) is True

    def test_update(self):
        model = DictMixin()
        key = "testkey"
        value = "testval"
        updatedval = "updatedval"
        model.__setitem__(key, value)
        updated = {key: updatedval}
        model.update(updated)
        assert model[key] == updatedval
    
    def test_values_items(self):
        model = DictMixin()
        key = "testkey"
        value = "testval"
        key2 = "testkey2"
        value2 = "testval2"
        model.__setitem__(key, value)
        model.__setitem__(key2, value2)
        vals = model.values()
        for item in model.items():
            assert item[1] in vals
