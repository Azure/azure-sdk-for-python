# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Construct original generated contracts on demand, without substitute model types."""

from threading import RLock
from typing import Any, Callable, MutableMapping

_LOCK = RLock()


def load_model(
    name: str, namespace: MutableMapping[str, Any], factories: dict[str, Callable[[], Any]], module_name: str
) -> Any:
    if name not in factories:
        raise AttributeError(f"module '{module_name}' has no attribute '{name}'")
    with _LOCK:
        if name not in namespace:
            namespace[name] = factories[name]()
        return namespace[name]
