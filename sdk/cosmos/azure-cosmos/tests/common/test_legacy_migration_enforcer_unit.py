# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Structural gate for the legacy-folder parity copies.

The legacy-folder parity workflow copies each in-scope v4 test into a
``tests/<op>/<surface>/legacy/`` folder and changes exactly one thing:
the copy constructs its client with ``_backend="rust"``. The rust column
of every parity audit comes from running those copies. Two ways that can
rot silently:

* A copy loses its backend pin. The "rust" column then runs core-python,
  and the audit reports parity against the wrong backend.
* A copy's ``# Source:`` lineage breaks when the original is renamed or
  deleted. Nobody notices until someone tries to re-derive the copy by
  hand and can't find what it came from.

This test makes both loud. It does no network I/O and never constructs a
``CosmosClient`` -- it parses the legacy files (and the sources they cite)
with ``ast`` and checks five invariants:

1. Every ``legacy/`` folder is an importable package (has ``__init__.py``).
2. Every ``test_*`` method carries a ``# Source:`` comment naming the
   original it was copied from.
3. Every ``# Source:`` reference resolves -- the cited file, class, and
   method still exist -- unless the source is marked ``(new)`` for a test
   with no v4 ancestor.
4. Every legacy test file pins the rust backend with the literal
   ``_backend="rust"``.
5. No test in a legacy folder is skipped without a structured reason, so
   every skip names a category a reviewer can act on.

Runs in milliseconds as a normal unit test.
"""
from __future__ import annotations

import ast
import pathlib
import unittest


# tests/common/<this file> -> parents[1] is .../azure-cosmos/tests
_TESTS_DIR = pathlib.Path(__file__).resolve().parents[1]
# .../azure-cosmos -- the root the ``# Source: tests/...`` paths are relative to.
_PKG_ROOT = _TESTS_DIR.parent

#: The backend pin, in both quote styles a copy might use.
_PIN_LITERALS = ('_backend="rust"', "_backend='rust'")

#: A test in a legacy folder may only be skipped if its reason string
#: starts with one of these category tags, so every skip says which kind
#: of gap parked it. Extend this list when a new category is needed.
_STRUCTURED_SKIP_TAGS = (
    "internals-only",   # the v4 test pokes at SDK internals (not a customer contract)
    "driver-gap",       # blocked on a known rust driver / binding gap
    "sync-only",        # the operation's async surface has no equivalent test
    "async-only",       # the operation's sync surface has no equivalent test
)

#: Decorator names that mean "skip this test".
_SKIP_NAMES = frozenset({"skip", "skipif", "skipIf", "skipUnless"})


def _legacy_dirs():
    """Every directory named ``legacy`` anywhere under ``tests/``."""
    return sorted(p for p in _TESTS_DIR.rglob("legacy") if p.is_dir())


def _legacy_test_files():
    """Every ``test_*.py`` file inside a legacy folder."""
    files = []
    for directory in _legacy_dirs():
        files.extend(sorted(directory.glob("test_*.py")))
    return files


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
    """Parses the legacy/ copies with ``ast`` and enforces their shape."""

    def test_legacy_folders_discovered(self):
        """Sanity: the walk finds legacy folders, so the checks below
        can't pass vacuously on a misconfigured path."""
        dirs = _legacy_dirs()
        self.assertTrue(
            dirs,
            "No tests/<op>/<surface>/legacy/ folders found under {}.".format(_rel(_TESTS_DIR)),
        )

    def test_every_legacy_folder_is_a_package(self):
        """Invariant 1: each legacy/ folder has __init__.py."""
        missing = [_rel(d) for d in _legacy_dirs() if not (d / "__init__.py").is_file()]
        self.assertEqual(
            missing, [],
            "legacy/ folders missing __init__.py:\n  - " + "\n  - ".join(missing),
        )

    def test_every_test_method_has_a_source_comment(self):
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
            "test methods in legacy/ without a `# Source:` comment:\n  - "
            + "\n  - ".join(violations),
        )

    def test_every_source_reference_resolves(self):
        """Invariant 3: each `# Source:` file::Class.method still exists."""
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
                path_part, qualified = ref.split("::", 1)
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
            "legacy/ tests whose `# Source:` lineage no longer resolves:\n  - "
            + "\n  - ".join(violations),
        )

    def test_every_legacy_file_pins_rust_backend(self):
        """Invariant 4: each legacy file carries the literal _backend pin."""
        violations = []
        for path in _legacy_test_files():
            text = path.read_text(encoding="utf-8")
            if not any(pin in text for pin in _PIN_LITERALS):
                violations.append(_rel(path))
        self.assertEqual(
            violations, [],
            'legacy/ files missing the literal _backend="rust" pin (without it '
            "the rust column silently runs core-python):\n  - " + "\n  - ".join(violations),
        )

    def test_no_unstructured_skips(self):
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
            "legacy/ skips whose reason does not start with a structured tag "
            "({}):\n  - ".format(", ".join(_STRUCTURED_SKIP_TAGS)) + "\n  - ".join(violations),
        )


if __name__ == "__main__":
    unittest.main()

