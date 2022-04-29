# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import MutableMapping


def _validate_value(value):
    primitive = (int,
                 float,
                 str,
                 bool)
    return isinstance(value, primitive)


class LabelCollection(MutableMapping):
    def __init__(self, *args, **kwargs):
        self.store = {}
        self.update(*args, **kwargs)

    def __setitem__(self, key, value):
        if isinstance(key, str):
            if _validate_value(value):
                self.store[key] = value
            else:
                raise ValueError("Unsupported value type " + str(type(value)))
        else:
            raise ValueError("Unsupported key type " + str(type(key)))

    def __delitem__(self, key):
        del self.store[key]

    def __getitem__(self, item):
        return self.store[item]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __repr__(self):
        return repr(self.store)
