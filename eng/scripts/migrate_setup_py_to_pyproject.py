#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
Migrate packages from setup.py to pyproject.toml.

Usage:
    # Migrate a single package
    python migrate_setup_py_to_pyproject.py --package-path sdk/tables/azure-data-tables

    # Migrate all packages in the sdk directory
    python migrate_setup_py_to_pyproject.py --all

    # Dry run (don't write files)
    python migrate_setup_py_to_pyproject.py --all --dry-run

    # Migrate a single package without deleting setup.py
    python migrate_setup_py_to_pyproject.py --package-path sdk/tables/azure-data-tables --keep-setup-py
"""

import argparse
import ast
import logging
import os
import re
import sys
import textwrap
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import tomllib as toml
except ImportError:
    import tomli as toml  # type: ignore

import tomli_w as tomlw

logging.basicConfig(
    stream=sys.stdout,
    format="[%(levelname)s] %(message)s",
)
_LOGGER = logging.getLogger(__name__)

# Directories to skip during migration
_SKIP_DIRS = {"tests", "test", "testserver_tests", "generated_tests", "coretestserver", "modeltypes"}

# Standard build system config
_BUILD_SYSTEM = {
    "requires": ["setuptools>=77.0.3", "wheel"],
    "build-backend": "setuptools.build_meta",
}

VERSION_REGEX = r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]'


def _is_excluded_package(package_path: Path) -> bool:
    """Return True if the package should be skipped (test packages, etc.)."""
    parts = set(package_path.parts)
    return bool(parts & _SKIP_DIRS)


def _get_version_attr(package_dir: Path) -> Optional[str]:
    """Find the version file and return the setuptools dynamic attr string."""
    exclude_dirs = {"tests", "test", "samples", "generated_samples", "generated_tests", "doc", ".tox", "venv"}

    for root, dirs, files in os.walk(str(package_dir)):
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith(".")]
        for version_file in ("_version.py", "version.py"):
            if version_file in files:
                version_path = Path(root) / version_file
                rel = version_path.relative_to(package_dir)
                # Convert path to module notation e.g. azure/data/tables/_version.py -> azure.data.tables._version
                module = str(rel).replace(os.sep, ".")[: -len(".py")]
                return f"{module}.VERSION"

    return None


def _extract_setup_kwargs(setup_py_path: str) -> Dict[str, Any]:
    """Execute setup.py and capture kwargs passed to setup()."""
    mock_setup = textwrap.dedent(
        """\
    def setup(*args, **kwargs):
        __setup_calls__.append((args, kwargs))
    """
    )
    with open(setup_py_path, "r", encoding="utf-8-sig") as f:
        content = f.read()

    parsed_mock = ast.parse(mock_setup, filename=setup_py_path)
    parsed = ast.parse(content, filename=setup_py_path)

    for idx, node in enumerate(parsed.body[:]):
        if (
            not isinstance(node, ast.Expr)
            or not isinstance(node.value, ast.Call)
            or not hasattr(node.value.func, "id")
            or node.value.func.id != "setup"
        ):
            continue
        parsed.body[idx:idx] = parsed_mock.body
        break

    fixed = ast.fix_missing_locations(parsed)
    code = compile(fixed, setup_py_path, "exec")
    global_vars: Dict[str, Any] = {"__setup_calls__": []}
    local_vars: Dict[str, Any] = {}

    orig_dir = os.getcwd()
    os.chdir(os.path.dirname(setup_py_path))
    try:
        exec(code, global_vars, local_vars)  # nosec
    finally:
        os.chdir(orig_dir)

    if not global_vars["__setup_calls__"]:
        return {}
    _, kwargs = global_vars["__setup_calls__"][0]
    return kwargs


def _extract_find_packages_exclude(setup_py_path: str) -> Optional[List[str]]:
    """Parse AST of setup.py to extract the exclude list from find_packages()."""
    with open(setup_py_path, "r", encoding="utf-8-sig") as f:
        content = f.read()

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return None

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func_name = ""
        if hasattr(node.func, "id"):
            func_name = node.func.id
        elif hasattr(node.func, "attr"):
            func_name = node.func.attr
        if func_name != "find_packages":
            continue
        for kw in node.keywords:
            if kw.arg == "exclude" and isinstance(kw.value, ast.List):
                items = [elt.value for elt in kw.value.elts if isinstance(elt, ast.Constant)]
                # Deduplicate while preserving order
                seen: set = set()
                deduped = []
                for item in items:
                    if item not in seen:
                        seen.add(item)
                        deduped.append(item)
                return deduped
    return None


def _extract_readme_files(setup_py_path: str) -> List[str]:
    """Detect which readme files are referenced in setup.py."""
    with open(setup_py_path, "r", encoding="utf-8-sig") as f:
        content = f.read()

    files = []
    if "README.md" in content:
        files.append("README.md")
    if "CHANGELOG.md" in content:
        files.append("CHANGELOG.md")
    return files or ["README.md"]


def _normalize_license(license_str: str) -> str:
    """Normalize license string to PEP 621 format."""
    mapping = {
        "MIT License": "MIT",
        "MIT": "MIT",
        "Apache Software License": "Apache-2.0",
        "Apache 2.0": "Apache-2.0",
        "Apache-2.0": "Apache-2.0",
    }
    return mapping.get(license_str, license_str)


def _filter_classifiers(classifiers: List[str]) -> List[str]:
    """Remove License classifiers since license is now a dedicated field."""
    return [c for c in classifiers if not c.startswith("License ::")]


def _normalize_keywords(keywords: Any) -> List[str]:
    """Normalize keywords to a list."""
    if isinstance(keywords, str):
        # Split on comma-separated values, preserving multi-word entries like "azure sdk"
        parts = [k.strip() for k in keywords.split(",") if k.strip()]
        return parts
    if isinstance(keywords, list):
        return keywords
    return ["azure", "azure sdk"]


def _build_project_section(
    kwargs: Dict[str, Any],
    package_dir: Path,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Build the [project] and [project.urls] sections from setup() kwargs.
    Returns (project_dict, project_urls_dict).
    """
    name = kwargs.get("name", "")
    description = kwargs.get("description", "")
    author = kwargs.get("author", "Microsoft Corporation")
    author_email = kwargs.get("author_email", "azpysdkhelp@microsoft.com")
    url = kwargs.get("url", "https://github.com/Azure/azure-sdk-for-python")
    license_val = kwargs.get("license", "MIT License")
    classifiers = kwargs.get("classifiers", [])
    keywords = kwargs.get("keywords", "azure, azure sdk")
    python_requires = kwargs.get("python_requires", ">=3.9")
    install_requires = kwargs.get("install_requires", [])

    project: Dict[str, Any] = {}
    project["name"] = name
    project["authors"] = [{"name": author, "email": author_email}]
    project["description"] = description
    project["license"] = _normalize_license(license_val)
    filtered_classifiers = _filter_classifiers(classifiers)
    if filtered_classifiers:
        project["classifiers"] = filtered_classifiers
    project["requires-python"] = python_requires
    project["keywords"] = _normalize_keywords(keywords)
    project["dependencies"] = install_requires

    # extras_require → optional-dependencies
    extras = kwargs.get("extras_require", {})
    if extras:
        project["optional-dependencies"] = extras

    # Dynamic fields
    project["dynamic"] = ["version", "readme"]

    # URL
    urls: Dict[str, str] = {}
    if url:
        urls["repository"] = url

    return project, urls


def _build_setuptools_section(
    kwargs: Dict[str, Any],
    package_dir: Path,
    version_attr: Optional[str],
    readme_files: List[str],
    exclude_list: Optional[List[str]],
) -> Dict[str, Any]:
    """Build the tool.setuptools.* section."""
    setuptools: Dict[str, Any] = {}

    # Dynamic version and readme
    dynamic: Dict[str, Any] = {}
    if version_attr:
        dynamic["version"] = {"attr": version_attr}
    dynamic["readme"] = {"file": readme_files, "content-type": "text/markdown"}
    setuptools["dynamic"] = dynamic

    # packages.find
    if exclude_list is not None:
        setuptools["packages"] = {"find": {"exclude": exclude_list}}

    # package-data
    package_data = kwargs.get("package_data", {})
    if package_data:
        setuptools["package-data"] = package_data

    return setuptools


def migrate_package(
    package_dir: Path,
    dry_run: bool = False,
    keep_setup_py: bool = False,
) -> bool:
    """
    Migrate a single package from setup.py to pyproject.toml.

    Returns True if the package was migrated, False if skipped.
    """
    setup_py = package_dir / "setup.py"
    pyproject_toml = package_dir / "pyproject.toml"

    if not setup_py.exists():
        _LOGGER.debug("No setup.py found in %s, skipping", package_dir)
        return False

    # Skip excluded directories
    if _is_excluded_package(package_dir):
        _LOGGER.debug("Skipping excluded directory: %s", package_dir)
        return False

    _LOGGER.info("Migrating %s", package_dir)

    # Parse setup.py
    try:
        kwargs = _extract_setup_kwargs(str(setup_py))
    except Exception as e:
        _LOGGER.warning("Failed to parse setup.py in %s: %s", package_dir, e)
        return False

    if not kwargs:
        _LOGGER.warning("No setup() call found in %s, skipping", package_dir)
        return False

    # Check if it's a namespace package (no _version.py, hardcoded version, special handling needed)
    name = kwargs.get("name", "")
    is_nspkg = "nspkg" in name
    if is_nspkg:
        _LOGGER.info("Skipping namespace package %s (nspkg)", name)
        return False

    # Get version attribute
    version_attr = _get_version_attr(package_dir)
    if not version_attr:
        _LOGGER.warning("Could not find version file in %s, skipping", package_dir)
        return False

    # Get readme files
    readme_files = _extract_readme_files(str(setup_py))
    # Only include CHANGELOG.md if it actually exists
    if "CHANGELOG.md" in readme_files and not (package_dir / "CHANGELOG.md").exists():
        readme_files = ["README.md"]

    # Get packages exclude list
    exclude_list = _extract_find_packages_exclude(str(setup_py))

    # Build project section
    project_section, urls_section = _build_project_section(kwargs, package_dir)

    # Build setuptools section
    setuptools_section = _build_setuptools_section(
        kwargs, package_dir, version_attr, readme_files, exclude_list
    )

    # Load existing pyproject.toml
    existing_toml: Dict[str, Any] = {}
    if pyproject_toml.exists():
        try:
            with open(pyproject_toml, "rb") as f:
                existing_toml = toml.load(f)
        except Exception as e:
            _LOGGER.warning("Failed to parse existing pyproject.toml in %s: %s", package_dir, e)

    # Load sdk_packaging.toml if present (older packages used this file)
    sdk_packaging_toml = package_dir / "sdk_packaging.toml"
    sdk_packaging_content: Dict[str, Any] = {}
    if sdk_packaging_toml.exists():
        try:
            with open(sdk_packaging_toml, "rb") as f:
                sdk_packaging_content = toml.load(f)
        except Exception as e:
            _LOGGER.warning("Failed to parse sdk_packaging.toml in %s: %s", package_dir, e)

    # Build the new toml dict, preserving existing sections
    new_toml: Dict[str, Any] = {}

    # 1. Build system (always add/replace)
    new_toml["build-system"] = _BUILD_SYSTEM.copy()

    # 2. Project section (always add/replace)
    new_toml["project"] = project_section

    # 3. Project URLs
    if urls_section:
        new_toml["project"]["urls"] = urls_section

    # 4. Tool sections - merge existing tool settings, then add setuptools
    new_toml["tool"] = {}

    # Copy existing tool.* sections except setuptools (we rebuild it)
    existing_tool = existing_toml.get("tool", {})
    for key, val in existing_tool.items():
        if key != "setuptools":
            new_toml["tool"][key] = val

    # Add setuptools section
    new_toml["tool"]["setuptools"] = setuptools_section

    # 5. Preserve top-level non-tool sections (like [packaging], etc.)
    for key, val in existing_toml.items():
        if key not in ("build-system", "project", "tool"):
            new_toml[key] = val

    # 6. Merge sdk_packaging.toml content (if any) - it may contain [packaging] section
    for key, val in sdk_packaging_content.items():
        if key not in new_toml:
            new_toml[key] = val
        elif isinstance(new_toml[key], dict) and isinstance(val, dict):
            new_toml[key].update(val)

    if dry_run:
        _LOGGER.info("[DRY RUN] Would write pyproject.toml for %s", package_dir)
        import io

        buf = io.BytesIO()
        tomlw.dump(new_toml, buf)
        print(buf.getvalue().decode("utf-8"))
        return True

    # Write pyproject.toml
    with open(pyproject_toml, "wb") as f:
        tomlw.dump(new_toml, f)
    _LOGGER.info("Updated pyproject.toml for %s", package_dir)

    # Remove setup.py
    if not keep_setup_py:
        setup_py.unlink()
        _LOGGER.info("Removed setup.py from %s", package_dir)

    # Remove sdk_packaging.toml (its content is now in pyproject.toml)
    if sdk_packaging_toml.exists() and not dry_run:
        sdk_packaging_toml.unlink()
        _LOGGER.info("Removed sdk_packaging.toml from %s", package_dir)

    return True


def find_packages_with_setup_py(repo_root: Path) -> List[Path]:
    """Find all packages in the sdk directory that have setup.py."""
    sdk_dir = repo_root / "sdk"
    packages = []

    for setup_py in sdk_dir.rglob("setup.py"):
        package_dir = setup_py.parent
        # Skip test packages inside other packages
        parts = set(package_dir.relative_to(sdk_dir).parts)
        if parts & _SKIP_DIRS:
            continue
        # Only include direct package directories (not nested)
        packages.append(package_dir)

    return sorted(packages)


def main():
    parser = argparse.ArgumentParser(
        description="Migrate packages from setup.py to pyproject.toml.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--package-path",
        "-p",
        dest="package_path",
        help="Path to a single package directory (absolute or relative to repo root).",
    )
    group.add_argument(
        "--all",
        "-a",
        dest="all_packages",
        action="store_true",
        help="Migrate all packages in the sdk directory.",
    )

    parser.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        help="Print what would be done without making changes.",
    )
    parser.add_argument(
        "--keep-setup-py",
        dest="keep_setup_py",
        action="store_true",
        help="Keep setup.py after migration (don't delete it).",
    )
    parser.add_argument(
        "--repo-root",
        dest="repo_root",
        default=None,
        help="Path to the repository root. Defaults to auto-detection.",
    )
    parser.add_argument("--debug", dest="debug", action="store_true", help="Enable debug logging.")

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    # Determine repo root
    if args.repo_root:
        repo_root = Path(args.repo_root).resolve()
    else:
        # Auto-detect: walk up from this script's directory
        script_dir = Path(__file__).resolve().parent
        repo_root = script_dir.parent.parent
        if not (repo_root / "sdk").exists():
            _LOGGER.error("Could not find repo root. Please specify --repo-root.")
            sys.exit(1)

    migrated = 0
    skipped = 0

    if args.package_path:
        package_dir = Path(args.package_path)
        if not package_dir.is_absolute():
            package_dir = repo_root / package_dir
        package_dir = package_dir.resolve()

        if migrate_package(package_dir, dry_run=args.dry_run, keep_setup_py=args.keep_setup_py):
            migrated += 1
        else:
            skipped += 1
    else:
        # Migrate all packages
        packages = find_packages_with_setup_py(repo_root)
        _LOGGER.info("Found %d packages with setup.py", len(packages))

        for package_dir in packages:
            try:
                if migrate_package(package_dir, dry_run=args.dry_run, keep_setup_py=args.keep_setup_py):
                    migrated += 1
                else:
                    skipped += 1
            except Exception as e:
                _LOGGER.error("Error migrating %s: %s", package_dir, e)
                skipped += 1

    _LOGGER.info("Migration complete: %d migrated, %d skipped", migrated, skipped)


if __name__ == "__main__":
    main()
