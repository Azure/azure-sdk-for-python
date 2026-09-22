# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Prepare partition-key inputs in the Python wrapper for the Python/Rust binding.

For example, ``components`` carries supplied values, ``extract`` asks the
binding to read the key from the item, and ``cross_partition`` does not select
one partition key. Keep these cases distinct even when they carry no values.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from types import EllipsisType
from typing import Literal, Union

# Ellipsis marks an undefined partition-key component for the binding. It is
# distinct from None, which represents a JSON null value.
UNDEFINED_PARTITION_KEY = Ellipsis
PartitionKeyComponent = Union[str, bool, int, float, None, EllipsisType]
PartitionKeyKind = Literal[
    "components", "extract", "cross_partition", "empty_sentinel", "empty_sequence"
]


@dataclass(frozen=True, eq=False)
class BindingPartitionKey:
    kind: PartitionKeyKind
    values: tuple[PartitionKeyComponent, ...] = ()

    def __post_init__(self) -> None:
        if type(self.kind) is not str or self.kind not in (
            "components",
            "extract",
            "cross_partition",
            "empty_sentinel",
            "empty_sequence",
        ):
            raise ValueError("Unknown partition-key input kind")
        if not isinstance(self.values, tuple):
            raise TypeError("Partition-key values must be an immutable tuple")
        if self.kind != "components":
            if self.values:
                raise ValueError("Only component partition keys may carry values")
            return
        if not 1 <= len(self.values) <= 3:
            raise ValueError("Partition keys require one to three components")
        for value in self.values:
            if (
                value is None
                or value is UNDEFINED_PARTITION_KEY
                or type(value) in (str, bool)
            ):
                continue
            if type(value) in (int, float):
                try:
                    finite = math.isfinite(float(value))
                except OverflowError:
                    finite = False
                if not finite:
                    raise ValueError(
                        "Partition-key numbers must be representable as finite f64 values"
                    )
                continue
            raise TypeError("Unsupported partition-key component type")

    def _identity(self) -> tuple:
        # A saved query must distinguish True from 1, and 0.0 from -0.0.
        return self.kind, tuple(
            (type(value), value.hex() if type(value) is float else value)
            for value in self.values
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BindingPartitionKey):
            return NotImplemented
        return self._identity() == other._identity()

    def __hash__(self) -> int:
        return hash(self._identity())
