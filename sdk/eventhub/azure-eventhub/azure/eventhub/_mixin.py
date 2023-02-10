# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import (
    List
)

class DictMixin(object):
    def __setitem__(self, key, item) -> None:
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self) -> str:
        return str(self)

    def __len__(self) -> int:
        return len(self.keys())

    def __delitem__(self, key) -> None:
        self.__dict__[key] = None

    def __eq__(self, other) -> bool:
        """Compare objects by comparing all attributes."""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other) -> bool:
        """Compare objects by comparing all attributes."""
        return not self.__eq__(other)

    def __contains__(self, key) -> bool:
        return key in self.__dict__

    def __str__(self) -> str:
        return str({k: v for k, v in self.__dict__.items() if not k.startswith("_")})

    def has_key(self, k) -> bool:
        return k in self.__dict__

    def update(self, *args, **kwargs) -> None:
        return self.__dict__.update(*args, **kwargs)

    def keys(self) -> List:
        return [k for k in self.__dict__ if not k.startswith("_")]

    def values(self) -> List:
        return [v for k, v in self.__dict__.items() if not k.startswith("_")]

    def items(self) -> List:
        return [(k, v) for k, v in self.__dict__.items() if not k.startswith("_")]

    def get(self, key, default=None):
        if key in self.__dict__:
            return self.__dict__[key]
        return default
