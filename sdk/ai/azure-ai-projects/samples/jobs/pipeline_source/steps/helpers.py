# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Shared functions and resources used by the pipeline components."""

from pathlib import Path


def greeting(text: str) -> str:
    prefix = Path(__file__).with_name("greeting.txt").read_text(encoding="utf-8").strip()
    return f"{prefix} {text}"
