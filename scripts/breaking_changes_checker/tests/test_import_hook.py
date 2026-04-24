#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Tests for the PEP 563 import hook used by ``build_library_report``.

These tests cover the scenario described in the issue report where a generated
Azure SDK module contains a method named ``list`` followed by another method
whose return annotation uses ``list[...]`` as a generic alias (e.g.
``LROPoller[ItemPaged[list[str]]]``). Without the import hook the class body
raises ``TypeError: 'function' object is not subscriptable`` at import time
because the method definition shadows the builtin in the class-body namespace.
"""

import importlib
import os
import sys
import tempfile
import textwrap

import pytest

PACKAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.dirname(PACKAGE_DIR)

for path in (SCRIPTS_DIR, PACKAGE_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)


_SOURCE_WITH_LIST_SHADOW = textwrap.dedent(
    """
    class Client:
        def list(self):
            return []

        def other(self) -> list[int]:
            return [1]

        def nested(self) -> dict[str, list[str]]:
            return {}
    """
)


def _make_fake_package(tmpdir, pkg_name="fakepkg_list_shadow"):
    pkg_dir = os.path.join(tmpdir, pkg_name)
    os.makedirs(pkg_dir)
    with open(os.path.join(pkg_dir, "__init__.py"), "w") as f:
        f.write("from ._client import Client\n")
    with open(os.path.join(pkg_dir, "_client.py"), "w") as f:
        f.write(_SOURCE_WITH_LIST_SHADOW)
    return pkg_dir


def _cleanup(pkg_name):
    for mod in list(sys.modules):
        if mod == pkg_name or mod.startswith(pkg_name + "."):
            del sys.modules[mod]
    # Remove any PEP 563 finders we installed for this prefix so tests don't
    # leak state between cases.
    from breaking_changes_checker.detect_breaking_changes import _PEP563MetaPathFinder

    sys.meta_path[:] = [
        finder
        for finder in sys.meta_path
        if not (isinstance(finder, _PEP563MetaPathFinder) and finder.target_prefix == pkg_name)
    ]


def test_vanilla_import_reproduces_crash():
    """Baseline: without the hook, the shadowing bug raises TypeError."""
    pkg_name = "fakepkg_list_shadow_vanilla"
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_fake_package(tmpdir, pkg_name)
        sys.path.insert(0, tmpdir)
        try:
            with pytest.raises(TypeError, match="'function' object is not subscriptable"):
                importlib.import_module(pkg_name)
        finally:
            sys.path.remove(tmpdir)
            _cleanup(pkg_name)


def test_build_library_report_handles_list_name_shadowing():
    """``build_library_report`` must import a package that shadows ``list``
    in a class body without crashing and must still capture the class.
    """
    from breaking_changes_checker.detect_breaking_changes import build_library_report

    pkg_name = "fakepkg_list_shadow_hooked"
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_fake_package(tmpdir, pkg_name)
        sys.path.insert(0, tmpdir)
        try:
            report = build_library_report(pkg_name)
        finally:
            sys.path.remove(tmpdir)
            _cleanup(pkg_name)

    assert pkg_name in report
    # The root package re-exports ``Client`` from its ``__init__``.
    assert "Client" in report[pkg_name]["class_nodes"]
    methods = report[pkg_name]["class_nodes"]["Client"]["methods"]
    # Both the shadowing ``list`` method and the annotated ``other`` method
    # must be captured.
    assert "list" in methods
    assert "other" in methods
    assert "nested" in methods


def test_build_library_report_recovers_after_failed_vanilla_import():
    """Even if a prior vanilla ``import`` populated ``__pycache__`` with
    bytecode compiled without the annotations flag, ``build_library_report``
    must still succeed because the hook bypasses the stale ``.pyc`` cache.
    """
    from breaking_changes_checker.detect_breaking_changes import build_library_report

    pkg_name = "fakepkg_list_shadow_after_failure"
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_fake_package(tmpdir, pkg_name)
        sys.path.insert(0, tmpdir)
        try:
            with pytest.raises(TypeError):
                importlib.import_module(pkg_name)
            # Clear the broken partial import but leave any written .pyc on disk.
            _cleanup(pkg_name)
            report = build_library_report(pkg_name)
        finally:
            sys.path.remove(tmpdir)
            _cleanup(pkg_name)

    assert pkg_name in report
    assert "Client" in report[pkg_name]["class_nodes"]
