# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Explicit SDK opt-ins for features that are still under development."""

from dataclasses import dataclass

__all__ = ["ExperimentalSettings"]


@dataclass(frozen=True, kw_only=True)
class ExperimentalSettings:
    """:meta private:"""

    enable_score_centering: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.enable_score_centering, bool):
            raise TypeError("enable_score_centering must be a bool")
