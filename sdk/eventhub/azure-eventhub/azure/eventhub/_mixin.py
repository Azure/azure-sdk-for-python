# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import Any, Optional, List, Tuple


class DictMixin:
    def __setitem__(self, key: str, item: Any) -> None:
        self.__dict__[key] = item

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]

    def __repr__(self) -> str:
        return str(self)

    def __len__(self) -> int:
        return len(self.keys())

    def __delitem__(self, key: str) -> None:
        self.__dict__[key] = None

    def __eq__(self, other: Any) -> bool:
        """Compare objects by comparing all attributes.

        :param any other: Any object
        :return: True if objects are equal, False otherwise.
        :rtype: bool
        """
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other: Any) -> bool:
        """Compare objects by comparing all attributes.

        :param any other: Any object
        :return: True if objects are not equal, False otherwise.
        :rtype: bool
        """
        return not self.__eq__(other)

    def __contains__(self, key: str) -> bool:
        return key in self.__dict__

    def __str__(self) -> str:
        return str({k: v for k, v in self.__dict__.items() if not k.startswith("_")})

    def has_key(self, k: str) -> bool:
        return k in self.__dict__

    def update(self, *args: Any, **kwargs: Any) -> None:
        return self.__dict__.update(*args, **kwargs)

    def keys(self) -> List[str]:
        return [k for k in self.__dict__ if not k.startswith("_")]

    def values(self) -> List[Any]:
        return [v for k, v in self.__dict__.items() if not k.startswith("_")]

    def items(self) -> List[Tuple[str, Any]]:
        return [(k, v) for k, v in self.__dict__.items() if not k.startswith("_")]

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        if key in self.__dict__:
            return self.__dict__[key]
        return default
