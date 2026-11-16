# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Structural gate for migrated Rust copies of the original tests.

The migration workflow copies each in-scope v4 test into a
``tests/<op>/<surface>/`` folder, retaining a ``# Source:`` reference and
selecting ``_backend="rust"``. The Rust column
of every parity audit comes from running those copies. Two ways that can
rot silently:

* A copy loses its backend pin. The "rust" column then runs core-python,
  and the audit reports parity against the wrong backend.
* A copy's ``# Source:`` lineage breaks when the original is renamed or
  deleted. Nobody notices until someone tries to re-derive the copy by
  hand and can't find what it came from.

These checks parse the copies and their cited sources, then perform an
isolated collection-only run. They do not execute service tests or fixtures.
They check seven invariants:

1. Every migrated surface folder is an importable package (has ``__init__.py``).
2. Every ``test_*`` method carries a ``# Source:`` comment naming the
   original it was copied from.
3. Every ``# Source:`` reference resolves to its original or an explicitly
   approved retained replacement, unless marked ``(new)`` for a test with
   no v4 ancestor.
4. Every migrated test file pins the Rust backend with the literal
   ``_backend="rust"``.
5. No migrated test is skipped without a structured reason, so
   every skip names a category a reviewer can act on.
6. Every copied test keeps the original's ``cosmos*`` lane markers (module,
   class and method combined), so it runs in the same pipeline lanes. A
   live-only or multi-region original is not made emulator-only by copying.
   Four reviewed non-split session-token copies use the emulator lane instead
   of inheriting split markers from their original shared class.
7. Every test definition in a source-linked file ends in ``_rust``, including
   copied unit tests outside the surface folders and regressions marked ``(new)``.

Every copy must also collect without shared conftest hooks.

The collection check runs pytest in a subprocess without shared conftest files.
"""

from __future__ import annotations

import ast
import os
import pathlib
import subprocess
import sys
import unittest
from unittest.mock import patch

from common._retired_test_sources import RETIRED_QUERY_SOURCE_MARKERS, RETIRED_TEST_SOURCES


# tests/common/<this file> -> parents[1] is .../azure-cosmos/tests
_TESTS_DIR = pathlib.Path(__file__).resolve().parents[1]
# .../azure-cosmos -- the root the ``# Source: tests/...`` paths are relative to.
_PKG_ROOT = _TESTS_DIR.parent

#: The backend pin, in both quote styles a copy might use.
_PIN_LITERALS = ('_backend="rust"', "_backend='rust'")

# These cases do not split partitions; their originals inherit split markers
# from a class shared with a real-split test.
_LANE_MARKER_OVERRIDES = {
    (
        "tests/get_latest_session_token/sync/test_latest_session_token.py"
        "::TestLatestSessionToken.test_latest_session_token_hpk_rust"
    ): frozenset({"cosmosEmulator"}),
    (
        "tests/get_latest_session_token/sync/test_latest_session_token.py"
        "::TestLatestSessionToken.test_latest_session_token_logical_hpk_rust"
    ): frozenset({"cosmosEmulator"}),
    (
        "tests/get_latest_session_token/aio/test_latest_session_token_async.py"
        "::TestLatestSessionTokenAsync.test_latest_session_token_hpk_rust"
    ): frozenset({"cosmosEmulator"}),
    (
        "tests/get_latest_session_token/aio/test_latest_session_token_async.py"
        "::TestLatestSessionTokenAsync.test_latest_session_token_logical_hpk_rust"
    ): frozenset({"cosmosEmulator"}),
}

#: A migrated test may only be skipped if its reason string
#: starts with one of these category tags, so every skip says which kind
#: of gap parked it. Extend this list when a new category is needed.
_STRUCTURED_SKIP_TAGS = (
    "internals-only",   # the v4 test pokes at SDK internals (not a customer contract)
    "driver-gap",       # blocked on a known Rust driver / binding gap
    "environment-gap",  # the target service/emulator lacks the required capability
    "sync-only",        # the operation's async surface has no equivalent test
    "async-only",       # the operation's sync surface has no equivalent test
    "accepted-vnext-change",  # an explicitly documented major-version contract change
)

#: Decorator names that mean "skip this test".
_SKIP_NAMES = frozenset({"skip", "skipif", "skipIf", "skipUnless"})


def _source_linked_test_files():
    """Find copied service and unit files without neighboring unlinked tests."""
    return sorted(
        path
        for path in _TESTS_DIR.rglob("test_*.py")
        if any(line.lstrip().startswith("# Source:") for line in path.read_text(encoding="utf-8").splitlines())
    )


def _legacy_test_files():
    """Find service copies governed by the backend and pipeline-lane checks."""
    return [path for path in _source_linked_test_files() if path.parent.name in ("sync", "aio")]


def _legacy_dirs():
    """Surface packages containing migrated tests."""
    return sorted({path.parent for path in _legacy_test_files()})


def _rel(path):
    """Path relative to the package root, for readable failure messages."""
    try:
        return str(path.relative_to(_PKG_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def _iter_test_functions(tree):
    """Yield ``(class_name_or_None, func_node)`` for every ``test_*`` def."""
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)) and sub.name.startswith("test_"):
                    yield node.name, sub
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
            yield None, node


def _label(path, class_name, func_name):
    """Return a readable file and test name for failure messages."""
    qualified = (class_name + "." if class_name else "") + func_name
    return "{}::{}".format(_rel(path), qualified)


def _source_ref(func, lines):
    """Return the text after ``# Source:`` inside the function, or None.

    Scans the whole function (signature through last body line) so the
    comment is found whether it is the first body line or sits just under
    a docstring.
    """
    start = func.lineno - 1
    end = getattr(func, "end_lineno", func.lineno)
    for line in lines[start:end]:
        stripped = line.strip()
        if stripped.startswith("# Source:"):
            return stripped[len("# Source:"):].strip()
    return None


def _decorator_name(dec):
    """Final attribute/name of a decorator expression (e.g. ``skip``)."""
    target = dec.func if isinstance(dec, ast.Call) else dec
    if isinstance(target, ast.Attribute):
        return target.attr
    if isinstance(target, ast.Name):
        return target.id
    return None


def _skip_reason(dec):
    """Return ``(is_skip, reason_or_None)`` for one decorator.

    Handles ``@pytest.mark.skip(reason=...)``,
    ``@pytest.mark.skipif(cond, reason=...)``, ``@unittest.skip("...")``,
    ``@unittest.skipIf(cond, "...")`` and the bare ``@pytest.mark.skip``
    (no reason) form.
    """
    if _decorator_name(dec) not in _SKIP_NAMES:
        return False, None
    if not isinstance(dec, ast.Call):
        return True, None  # bare ``@pytest.mark.skip`` -- no reason given
    for kw in dec.keywords:
        if kw.arg == "reason" and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
            return True, kw.value.value
    for arg in dec.args:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            return True, arg.value
    return True, None


def _lane_markers_from(decorators):
    """``cosmos*`` names from ``@pytest.mark.<name>`` expressions."""
    names = set()
    for dec in decorators:
        target = dec.func if isinstance(dec, ast.Call) else dec
        if (isinstance(target, ast.Attribute) and target.attr.startswith("cosmos")
                and isinstance(target.value, ast.Attribute) and target.value.attr == "mark"):
            names.add(target.attr)
    return names


def _effective_lane_markers(tree, class_name, method_name):
    """Lane markers that apply to one test (module ``pytestmark`` + class + method).

    Returns None when the test is not defined in ``tree``.
    """
    markers = set()
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "pytestmark" for t in node.targets):
            value = node.value
            markers |= _lane_markers_from(value.elts if isinstance(value, (ast.List, ast.Tuple)) else [value])
    scopes = [(None, tree.body)]
    if class_name is not None:
        scopes = [(n, n.body) for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name]
    for cls, body in scopes:
        for func in body:
            if isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)) and func.name == method_name:
                if cls is not None:
                    markers |= _lane_markers_from(cls.decorator_list)
                return markers | _lane_markers_from(func.decorator_list)
    return None


def _class_method_exists(src_tree, class_name, method_name):
    """True if ``class_name.method_name`` (or a module function when
    ``class_name`` is None) is defined in the parsed source tree."""
    if class_name is None:
        return any(
            isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == method_name
            for n in src_tree.body
        )
    for node in src_tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return any(
                isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == method_name
                for n in node.body
            )
    return False


class LegacyMigrationEnforcerTests(unittest.TestCase):
    """Check the copies' source structure and marker-based collection."""

    def test_migrated_folders_discovered_rust(self):
        """Sanity: the walk finds migrated copies, so the checks below
        can't pass vacuously on a misconfigured path."""
        dirs = _legacy_dirs()
        self.assertTrue(
            dirs,
            "No source-linked tests/<op>/<surface>/ copies found under {}.".format(_rel(_TESTS_DIR)),
        )

    def test_every_migrated_folder_is_a_package_rust(self):
        """Invariant 1: each surface and operation has __init__.py."""
        packages = {package for surface in _legacy_dirs() for package in (surface, surface.parent)}
        missing = sorted(_rel(d) for d in packages if not (d / "__init__.py").is_file())
        self.assertEqual(
            missing, [],
            "Migrated-test packages missing __init__.py:\n  - " + "\n  - ".join(missing),
        )

    def test_every_test_method_has_a_source_comment_rust(self):
        """Invariant 2: every test_* method names where it was copied from."""
        violations = []
        for path in _legacy_test_files():
            text = path.read_text(encoding="utf-8")
            lines = text.splitlines()
            tree = ast.parse(text, filename=str(path))
            for class_name, func in _iter_test_functions(tree):
                if _source_ref(func, lines) is None:
                    violations.append(_label(path, class_name, func.name))
        self.assertEqual(
            violations, [],
            "migrated test methods without a `# Source:` comment:\n  - "
            + "\n  - ".join(violations),
        )

    def test_every_test_method_has_rust_suffix_rust(self):
        """Every test in a migrated file has an explicit Rust-path name."""
        violations = []
        for path in _source_linked_test_files():
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for class_name, func in _iter_test_functions(tree):
                if not func.name.endswith("_rust"):
                    violations.append(_label(path, class_name, func.name))
        self.assertEqual(
            violations,
            [],
            "migrated test definitions without the _rust suffix:\n  - " + "\n  - ".join(violations),
        )

    def test_every_source_reference_resolves_rust(self):
        """Invariant 3: each source has a live original or approved replacement."""
        violations = []
        src_cache = {}
        for path in _legacy_test_files():
            text = path.read_text(encoding="utf-8")
            lines = text.splitlines()
            tree = ast.parse(text, filename=str(path))
            for class_name, func in _iter_test_functions(tree):
                ref = _source_ref(func, lines)
                if ref is None or ref.startswith("(new)"):
                    continue
                where = _label(path, class_name, func.name)
                if "::" not in ref:
                    violations.append("{} -> malformed Source {!r}".format(where, ref))
                    continue
                path_part, qualified = RETIRED_TEST_SOURCES.get(ref, ref).split("::", 1)
                src_path = _PKG_ROOT / path_part
                if not src_path.is_file():
                    violations.append("{} -> source file not found: {}".format(where, path_part))
                    continue
                if "." in qualified:
                    src_class, src_method = qualified.rsplit(".", 1)
                else:
                    src_class, src_method = None, qualified
                if src_path not in src_cache:
                    src_cache[src_path] = ast.parse(src_path.read_text(encoding="utf-8"), filename=str(src_path))
                if not _class_method_exists(src_cache[src_path], src_class, src_method):
                    violations.append("{} -> {} not found in {}".format(where, qualified, path_part))
        self.assertEqual(
            violations, [],
            "migrated tests whose `# Source:` lineage no longer resolves:\n  - "
            + "\n  - ".join(violations),
        )

    def test_every_migrated_file_pins_rust_backend_rust(self):
        """Invariant 4: each legacy file carries the literal _backend pin."""
        violations = []
        for path in _legacy_test_files():
            text = path.read_text(encoding="utf-8")
            if not any(pin in text for pin in _PIN_LITERALS):
                violations.append(_rel(path))
        self.assertEqual(
            violations, [],
            'migrated files missing the literal _backend="rust" pin (without it '
            "the rust column silently runs core-python):\n  - " + "\n  - ".join(violations),
        )

    def test_no_unstructured_skips_rust(self):
        """Invariant 5: every skip in a legacy file has a structured reason."""
        violations = []
        for path in _legacy_test_files():
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            targets = []
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    targets.append((node.name, node))
                    for sub in node.body:
                        if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)) and sub.name.startswith("test_"):
                            targets.append((node.name + "." + sub.name, sub))
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
                    targets.append((node.name, node))
            for label, node in targets:
                for dec in node.decorator_list:
                    is_skip, reason = _skip_reason(dec)
                    if not is_skip:
                        continue
                    if reason is None:
                        violations.append("{}::{} -> skip with no reason string".format(_rel(path), label))
                    elif not any(reason.startswith(tag) for tag in _STRUCTURED_SKIP_TAGS):
                        violations.append("{}::{} -> skip reason not structured: {!r}".format(_rel(path), label, reason))
        self.assertEqual(
            violations, [],
            "migrated-test skips whose reason does not start with a structured tag "
            "({}):\n  - ".format(", ".join(_STRUCTURED_SKIP_TAGS)) + "\n  - ".join(violations),
        )

    def test_every_copy_keeps_original_lane_markers_rust(self):
        """Invariant 6: retain original lanes or the exact approved replacement."""
        violations = []
        src_cache = {}
        for path in _legacy_test_files():
            text = path.read_text(encoding="utf-8")
            lines = text.splitlines()
            tree = ast.parse(text, filename=str(path))
            for class_name, func in _iter_test_functions(tree):
                ref = _source_ref(func, lines)
                if ref is None or ref.startswith("(new)") or "::" not in ref:
                    continue
                if ref in RETIRED_QUERY_SOURCE_MARKERS:
                    original = RETIRED_QUERY_SOURCE_MARKERS[ref]
                else:
                    path_part, qualified = RETIRED_TEST_SOURCES.get(ref, ref).split("::", 1)
                    src_path = _PKG_ROOT / path_part
                    if not src_path.is_file():
                        continue  # reported by invariant 3
                    src_class, src_method = qualified.rsplit(".", 1) if "." in qualified else (None, qualified)
                    if src_path not in src_cache:
                        src_cache[src_path] = ast.parse(src_path.read_text(encoding="utf-8"), filename=str(src_path))
                    original = _effective_lane_markers(src_cache[src_path], src_class, src_method)
                if original is None:
                    continue  # reported by invariant 3
                original = _LANE_MARKER_OVERRIDES.get(_label(path, class_name, func.name), original)
                copy = _effective_lane_markers(tree, class_name, func.name)
                if copy != original:
                    violations.append(
                        "{} -> missing {}, extra {} (source {})".format(
                            _label(path, class_name, func.name), sorted(original - copy), sorted(copy - original), ref
                        )
                    )
        self.assertEqual(
            violations,
            [],
            "migrated tests whose cosmos* lane markers differ from the original:\n  - " + "\n  - ".join(violations),
        )

    def test_every_migrated_test_collects_without_conftest_rust(self):
        """Every copied test definition collects without shared conftest hooks."""
        files = _legacy_test_files()
        expected = set()
        for path in files:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for class_name, method in _iter_test_functions(tree):
                parts = [_rel(path), method.name]
                if class_name is not None:
                    parts.insert(1, class_name)
                expected.add("::".join(parts))
        self.assertTrue(expected, "No legacy-copy test definitions found.")

        env = dict(os.environ)
        env["PYTHONPATH"] = str(_PKG_ROOT / "tests") + os.pathsep + env.get("PYTHONPATH", "")
        env.pop("PYTEST_ADDOPTS", None)

        def collect(extra_args):
            collected = set()
            # Batches keep each command line under the Windows length limit (WinError 206).
            for start in range(0, len(files), 40):
                batch = [os.path.relpath(path, _PKG_ROOT) for path in files[start:start + 40]]
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", "--noconftest", "--import-mode=importlib",
                     "--collect-only", "-q", *extra_args, *batch],
                    cwd=_PKG_ROOT, env=env, capture_output=True, text=True, timeout=60, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                collected |= {
                    line.replace("\\", "/") for line in result.stdout.splitlines()
                    if line.replace("\\", "/").startswith("tests/") and "::test_" in line
                }
            return collected

        unfiltered = collect([])
        self.assertSetEqual(
            {nodeid.split("[", 1)[0] for nodeid in unfiltered}, expected,
            "Unfiltered collection must include all legacy-copy test definitions.",
        )


class RustSuffixEnforcerTests(unittest.TestCase):
    """Exercise the naming guard without importing or executing service tests."""

    def test_source_linked_unit_files_are_included_rust(self):
        service = _PKG_ROOT / "tests" / "query_items" / "sync" / "test_example.py"
        unit = _PKG_ROOT / "tests" / "query_items" / "test_example_unit.py"
        unlinked = _PKG_ROOT / "tests" / "common" / "test_unlinked_unit.py"
        contents = {
            service: "# Source: tests/test_original.py::test_example",
            unit: "# Source: tests/test_original.py::test_example",
            unlinked: "def test_example(): pass",
        }
        with patch.object(pathlib.Path, "rglob", return_value=list(contents)):
            with patch.object(pathlib.Path, "read_text", autospec=True, side_effect=lambda path, **_: contents[path]):
                self.assertEqual(_source_linked_test_files(), sorted([service, unit]))
                self.assertEqual(_legacy_test_files(), [service])

    def test_missing_suffix_is_rejected_rust(self):
        path = _PKG_ROOT / "tests" / "query_items" / "sync" / "test_example.py"
        for source in (
            "def test_example(): pass",
            "async def test_example(): pass",
            "class Example:\n    def test_example(self): pass",
            "class Example:\n    async def test_example(self): pass",
            "def test_example_rust_extra(): pass",
        ):
            with self.subTest(source=source):
                with patch(__name__ + "._source_linked_test_files", return_value=[path]):
                    with patch.object(pathlib.Path, "read_text", return_value=source):
                        check = LegacyMigrationEnforcerTests("test_every_test_method_has_rust_suffix_rust")
                        with self.assertRaisesRegex(AssertionError, "without the _rust suffix"):
                            check.test_every_test_method_has_rust_suffix_rust()

    def test_valid_suffixes_are_accepted_rust(self):
        path = _PKG_ROOT / "tests" / "query_items" / "aio" / "test_example.py"
        source = (
            "def test_example_rust(): pass\n"
            "async def test_example_async_rust(): pass\n"
            "class Example:\n"
            "    def helper(self): pass\n"
            "    def test_example_rust(self): pass\n"
            "    async def test_example_async_rust(self): pass\n"
        )
        with patch(__name__ + "._source_linked_test_files", return_value=[path]):
            with patch.object(pathlib.Path, "read_text", return_value=source):
                check = LegacyMigrationEnforcerTests("test_every_test_method_has_rust_suffix_rust")
                check.test_every_test_method_has_rust_suffix_rust()


if __name__ == "__main__":
    unittest.main()
