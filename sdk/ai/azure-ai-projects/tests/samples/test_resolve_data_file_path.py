# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for ``resolve_data_file_path`` with concrete examples.

Example base script path used by tests:
    root/samples/finetuning/sample.py

Example outcomes:
    - env missing + default ``train.jsonl`` -> ``.../finetuning/data/train.jsonl``
    - env absolute ``C:/root/custom/train.jsonl`` -> same absolute path
    - env relative ``custom/train.jsonl`` -> ``.../finetuning/custom/train.jsonl``
    - env filename ``train_override.jsonl`` -> ``.../finetuning/data/train_override.jsonl``
"""

import os
import sys
from pathlib import Path

SAMPLES_FINETUNING_DIR = Path(__file__).resolve().parents[1] / ".." / "samples" / "finetuning"
sys.path.insert(0, str(SAMPLES_FINETUNING_DIR.resolve()))

from fine_tuning_sample_helper import resolve_data_file_path


def test_resolve_data_file_path_defaults_to_data_folder_when_env_missing(monkeypatch):
    """Given env var ``TRAINING_FILE_PATH`` is unset.

    When resolving using:
    - script_file: ``root/samples/finetuning/sample.py``
    - default_filename: ``train.jsonl``

    Then the result is:
    ``<script_dir>/data/train.jsonl``.
    """
    monkeypatch.delenv("TRAINING_FILE_PATH", raising=False)
    script_file = os.path.join("root", "samples", "finetuning", "sample.py")

    actual = resolve_data_file_path(script_file, "TRAINING_FILE_PATH", "train.jsonl")

    expected = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(script_file)), "data", "train.jsonl"))
    assert actual == expected


def test_resolve_data_file_path_returns_absolute_env_path(monkeypatch):
    """Given env var ``TRAINING_FILE_PATH`` is an absolute path.

    Example input value:
    ``<abs>/root/custom/train.jsonl``.

    Then resolver returns that exact absolute path unchanged.
    """
    absolute_path = os.path.abspath(os.path.join("root", "custom", "train.jsonl"))
    monkeypatch.setenv("TRAINING_FILE_PATH", absolute_path)
    script_file = os.path.join("root", "samples", "finetuning", "sample.py")

    actual = resolve_data_file_path(script_file, "TRAINING_FILE_PATH", "train.jsonl")

    assert actual == absolute_path


def test_resolve_data_file_path_resolves_relative_subpath_from_script_dir(monkeypatch):
    """Given env var ``TRAINING_FILE_PATH`` is a relative subpath.

    Example input value:
    ``custom/train.jsonl``.

    Then resolver anchors it at script dir:
    ``<script_dir>/custom/train.jsonl`` (not under ``data``).
    """
    monkeypatch.setenv("TRAINING_FILE_PATH", os.path.join("custom", "train.jsonl"))
    script_file = os.path.join("root", "samples", "finetuning", "sample.py")

    actual = resolve_data_file_path(script_file, "TRAINING_FILE_PATH", "train.jsonl")

    expected = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(script_file)), "custom", "train.jsonl"))
    assert actual == expected


def test_resolve_data_file_path_resolves_filename_from_data_folder(monkeypatch):
    """Given env var ``TRAINING_FILE_PATH`` is filename-only.

    Example input value:
    ``train_override.jsonl``.

    Then resolver places it under the default data directory:
    ``<script_dir>/data/train_override.jsonl``.
    """
    monkeypatch.setenv("TRAINING_FILE_PATH", "train_override.jsonl")
    script_file = os.path.join("root", "samples", "finetuning", "sample.py")

    actual = resolve_data_file_path(script_file, "TRAINING_FILE_PATH", "train.jsonl")

    expected = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(script_file)), "data", "train_override.jsonl")
    )
    assert actual == expected
