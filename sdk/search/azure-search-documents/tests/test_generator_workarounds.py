# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for package-owned post-generation workarounds."""

from pathlib import Path
import importlib.util
import subprocess
import sys

import pytest


@pytest.fixture(scope="module")
def workarounds():
    package_root = Path(__file__).resolve().parents[1]
    script = package_root / ".github/skills/azure-search-documents/scripts/apply_generator_workarounds.py"
    spec = importlib.util.spec_from_file_location("_search_generator_workarounds", script)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_sphinx_type_section_excludes_only_wire_keys_and_preserves_aliases(workarounds):
    source = """
Plain = TypedDict("Plain", {"name": str}, total=False)
Wire = TypedDict("Wire", {"name": str, "@odata.type": str, "@odata.etag": str}, total=False)
WireAlias = Union[Wire]
"""

    section = workarounds.build_sphinx_type_section("azure.search.documents.types", source)

    assert section.startswith(".. automodule:: azure.search.documents.types\n")
    assert "   :exclude-members: Wire\n" in section
    assert ".. autoclass:: azure.search.documents.types.Wire\n" in section
    assert "   :exclude-members: @odata.etag, @odata.type\n" in section
    assert section.count("   :undoc-members:\n") == 2
    assert ".. autoclass:: azure.search.documents.types.Plain" not in section
    assert ".. autoclass:: azure.search.documents.types.WireAlias" not in section


def test_sphinx_type_section_keeps_normal_input_types_automatic(workarounds):
    source = 'Plain = TypedDict("Plain", {"name": str, "value": int}, total=False)'

    section = workarounds.build_sphinx_type_section("azure.search.documents.types", source)

    assert section == (
        ".. automodule:: azure.search.documents.types\n"
        "   :inherited-members:\n"
        "   :members:\n"
        "   :show-inheritance:\n"
        "   :undoc-members:\n"
    )


def test_package_source_distribution_includes_documentation():
    package_root = Path(__file__).resolve().parents[1]

    assert "recursive-include doc *.rst" in (package_root / "MANIFEST.in").read_text().splitlines()


def test_generator_workarounds_restore_documentation_packaging(workarounds, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(workarounds, "PACKAGE_ROOT", tmp_path)
    monkeypatch.setattr(workarounds, "REPLACEMENTS", ())
    manifest = tmp_path / "MANIFEST.in"
    original_manifest = "include *.md\ninclude LICENSE\n"
    manifest.write_text(original_manifest)
    doc_dir = tmp_path / "doc"
    doc_dir.mkdir()
    for namespace in ("azure.search.documents", "azure.search.documents.indexes"):
        source = 'Plain = TypedDict("Plain", {"name": str}, total=False)'
        type_path = tmp_path.joinpath(*namespace.split("."), "types.py")
        type_path.parent.mkdir(parents=True, exist_ok=True)
        type_path.write_text(source)
        (doc_dir / f"{namespace}.rst").write_text(workarounds.build_sphinx_type_section(f"{namespace}.types", source))

    assert workarounds.update_sources(check=True) == 1
    assert "include package-local Sphinx documentation in the source distribution" in capsys.readouterr().out
    assert manifest.read_text() == original_manifest

    assert workarounds.update_sources(check=False) == 0
    assert manifest.read_text() == original_manifest + "recursive-include doc *.rst\n"
    assert workarounds.update_sources(check=True) == 0
    assert workarounds.update_sources(check=False) == 0
    assert manifest.read_text().count("recursive-include doc *.rst") == 1


def test_generator_workarounds_are_applied():
    package_root = Path(__file__).resolve().parents[1]
    script = package_root / ".github/skills/azure-search-documents/scripts/apply_generator_workarounds.py"

    result = subprocess.run(
        [sys.executable, str(script), "--check"],
        cwd=package_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
