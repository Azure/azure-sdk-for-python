# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Import-safe component definitions; the pipeline submission lives elsewhere."""

from pathlib import Path

from azure.ai.projects.dsl import Input, Output, component

from .helpers import greeting


def normalize(text: str) -> str:
    return text.strip()


@component(code="..")
def produce(text: str, message: Output(type="uri_file")) -> None:  # type: ignore[valid-type]
    Path(message).write_text(greeting(normalize(text)), encoding="utf-8")


@component(code="..")
def consume(message: Input(type="uri_file"), receipt: Output(type="uri_file")) -> None:  # type: ignore[valid-type]
    Path(receipt).write_text(Path(message).read_text(encoding="utf-8").upper(), encoding="utf-8")
