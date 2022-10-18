# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

class DictMixin:
    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.keys())

    def __delitem__(self, key):
        self.__dict__[key] = None

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __contains__(self, key):
        return key in self.__dict__

    def __str__(self):
        return str({k: v for k, v in self.__dict__.items() if not k.startswith("_")})

    def has_key(self, k):
        return k in self.__dict__

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        return [k for k in self.__dict__ if not k.startswith("_")]

    def values(self):
        return [v for k, v in self.__dict__.items() if not k.startswith("_")]

    def items(self):
        return [(k, v) for k, v in self.__dict__.items() if not k.startswith("_")]

    def get(self, key, default=None):
        if key in self.__dict__:
            return self.__dict__[key]
        return default
