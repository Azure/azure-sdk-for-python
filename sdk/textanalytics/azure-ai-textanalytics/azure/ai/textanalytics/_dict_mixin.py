# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Any, Tuple, Optional, Iterable


class DictMixin:
    def __setitem__(self, key: str, item: Any) -> None:
        self.__dict__[key] = item

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]

    def __repr__(self) -> str:
        return str(self)

    def __len__(self) -> int:
        return len(self.keys())  # type: ignore

    def __delitem__(self, key: str) -> None:
        self.__dict__[key] = None

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __contains__(self, key: str) -> bool:
        return key in self.__dict__

    def __str__(self) -> str:
        return str({k: v for k, v in self.__dict__.items() if not k.startswith("_")})

    def has_key(self, k: str) -> bool:
        return k in self.__dict__

    def update(self, *args: Any, **kwargs: Any) -> None:
        self.__dict__.update(*args, **kwargs)

    def keys(self) -> Iterable[str]:
        return [k for k in self.__dict__ if not k.startswith("_")]

    def values(self) -> Iterable[Any]:
        return [v for k, v in self.__dict__.items() if not k.startswith("_")]

    def items(self) -> Iterable[Tuple[str, Any]]:
        return [(k, v) for k, v in self.__dict__.items() if not k.startswith("_")]

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        if key in self.__dict__:
            return self.__dict__[key]
        return default
