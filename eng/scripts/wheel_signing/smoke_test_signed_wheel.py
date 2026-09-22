# Post-signing smoke test: install a signed wheel on its real target OS and import every
# compiled extension module it ships, proving the actual released artifact still loads.
#
# Nothing else in the signing pipeline verifies this. repackage_signed_wheels.py runs
# entirely on a Linux agent and never executes the mac/Windows binary it just repackaged, so
# a binary corrupted by signing (or a repackaging bug that swaps in the wrong file) would
# otherwise only surface after release, when a customer tries to import the package.
#
# This intentionally does not run the package's own test suite: that already runs against
# the *unsigned* wheel on the same OS during the Build_<platform> job and would be redundant
# here. This only checks the one thing that is unique to the signed artifact: can the signed
# binary still be loaded.

import argparse
import glob
import importlib
import os
import sys
from importlib import metadata
from pathlib import Path
from subprocess import CalledProcessError, check_call
from typing import List

COMPILED_EXTENSION_SUFFIXES = (".pyd", ".so", ".dylib")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install a signed wheel and import its compiled extension module(s) as a smoke test."
    )
    parser.add_argument("--wheel-dir", required=True, help="Directory containing exactly one signed wheel to test.")
    return parser.parse_args()


def find_wheel(wheel_dir: str) -> str:
    candidates = sorted(glob.glob(os.path.join(wheel_dir, "*.whl")))
    if not candidates:
        raise FileNotFoundError(f"No wheel found in {wheel_dir}.")
    if len(candidates) > 1:
        raise RuntimeError(f"Expected exactly one wheel in {wheel_dir}, found {len(candidates)}: {candidates}")
    return candidates[0]


def install_wheel(wheel_path: str) -> None:
    check_call([sys.executable, "-m", "pip", "install", "--no-deps", "--force-reinstall", wheel_path])


def distribution_name_from_wheel(wheel_path: str) -> str:
    # Wheel filename format: {distribution}-{version}(-{build tag})?-{python tag}-{abi tag}-{platform tag}.whl
    return Path(wheel_path).name.split("-")[0]


def find_compiled_modules(dist_name: str) -> List[str]:
    """Return the dotted module path for every compiled extension file the distribution installed."""
    dist = metadata.distribution(dist_name)
    files = dist.files or []

    modules = []
    for file in files:
        # `file` is a PackagePath; str(file) is the full relative path from the dist-info root
        # (POSIX-separated), while file.name is only the basename. We need the full path to
        # reconstruct the dotted module path.
        relative_path = str(file)
        suffix = "".join(Path(relative_path).suffixes).lower()
        if not any(suffix.endswith(ext) for ext in COMPILED_EXTENSION_SUFFIXES):
            continue

        # Strip the platform/abi tag portion of the filename (e.g. "native.cp310-win_amd64.pyd"
        # -> "native"), then convert the file's path into a dotted module name.
        path = Path(relative_path)
        stem = path.name
        for ext in COMPILED_EXTENSION_SUFFIXES:
            idx = stem.lower().find(ext)
            if idx != -1:
                stem = stem[:idx]
                break
        stem = stem.split(".")[0]

        parent_parts = path.parent.parts

        # Not every compiled file under COMPILED_EXTENSION_SUFFIXES is an importable module.
        # Repair tools that vendor a package's native dependencies alongside its real
        # extensions (delocate's `<pkg>/.dylibs/*.dylib`, auditwheel's `<dist>.libs/*.so`) are
        # signable, but they aren't Python modules and don't sit on a valid dotted import
        # path. A directory or filename that isn't a valid identifier can't be part of one, so
        # skip it instead of handing import_module() a bogus name like "pkg.dylibs.libfoo".
        if not stem.isidentifier() or not all(part.isidentifier() for part in parent_parts):
            continue

        # A compiled package initializer (e.g. "pkg/__init__.cpython-310-x86_64-linux-gnu.so")
        # *is* the package; the importable name is the parent package, not "pkg.__init__".
        if stem == "__init__":
            if not parent_parts:
                continue
            module_path = ".".join(parent_parts)
        else:
            module_path = ".".join([*parent_parts, stem]) if parent_parts else stem

        modules.append(module_path)

    return sorted(set(modules))


def main() -> None:
    args = parse_args()
    wheel_path = find_wheel(args.wheel_dir)
    print(f"Smoke-testing signed wheel: {wheel_path}")

    install_wheel(wheel_path)

    dist_name = distribution_name_from_wheel(wheel_path)
    compiled_modules = find_compiled_modules(dist_name)

    if not compiled_modules:
        raise RuntimeError(
            f"No compiled extension modules (.pyd/.so/.dylib) found for {dist_name}; expected at "
            "least one for a signed-binary package. The smoke test would not have exercised anything."
        )

    for module_name in compiled_modules:
        print(f"Importing {module_name}...")
        importlib.import_module(module_name)
        print(f"OK: {module_name} imported successfully.")

    print(f"Smoke test passed: {len(compiled_modules)} compiled module(s) imported successfully.")


if __name__ == "__main__":
    try:
        main()
    except (CalledProcessError, RuntimeError, FileNotFoundError, ImportError) as error:
        print(f"Smoke test failed: {error}", file=sys.stderr)
        sys.exit(1)
