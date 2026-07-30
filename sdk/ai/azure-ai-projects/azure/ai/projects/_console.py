# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""Handwritten console helpers used by SDK customization code."""

from __future__ import annotations

from typing import IO


def console_print(
    *values: object,
    sep: str | None = " ",
    end: str | None = "\n",
    file: IO[str] | None = None,
    flush: bool = False,
) -> None:
    """Mirror ``print`` behind a named helper for SDK console capture.

    The SDK patch modules alias this helper to ``print`` so contributors can
    keep writing plain ``print(...)`` calls while tests still patch one module-
    local symbol to distinguish SDK console output from sample-authored prints.
    Keeping this helper in a handwritten module avoids placing custom behavior
    in generated files that may be overwritten by the next emit.
    """
    print(*values, sep=sep, end=end, file=file, flush=flush)
