# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from importlib.machinery import EXTENSION_SUFFIXES
from importlib.metadata import version

import pytest

from azure.template.three import __version__, _rust


def test_is_true_returns_true():
    assert _rust.is_true() is True


def test_is_true_takes_no_arguments():
    with pytest.raises(TypeError):
        _rust.is_true(1)


def test_extension_is_native():
    assert any(_rust.__file__.endswith(suffix) for suffix in EXTENSION_SUFFIXES)


def test_runtime_version_matches_distribution():
    assert __version__ == version("azure-template-three")
