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

from packaging import tags as packaging_tags
from packaging.utils import parse_wheel_filename

# Suffixes for files this script will actually try to import as Python extension modules.
# Deliberately excludes .dylib: on macOS, compiled Python extensions are always packaged with a
# `.so` suffix (CPython's import machinery never resolves `.dylib` as an extension-module
# suffix), while `.dylib` is used for *shared libraries* a wheel vendors as a dependency of its
# real extension (e.g. delocate/auditwheel repair output). Those vendored libraries are still
# signed like any other native binary, but importing them directly is neither meaningful nor
# expected to work, and doing so would fail this smoke test on an otherwise correctly signed
# wheel. See extract_sign_inputs.py's SIGNABLE_SUFFIXES for what actually gets sent through ESRP.
IMPORTABLE_EXTENSION_SUFFIXES = (".pyd", ".so")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install a signed wheel and import its compiled extension module(s) as a smoke test."
    )
    parser.add_argument(
        "--wheel-dir",
        required=True,
        help=(
            "Directory containing signed wheels. cibuildwheel can legitimately "
            "produce more than one wheel per platform for the same package/version (e.g. "
            "separate CPython and PyPy builds, or multiple Windows/macOS architectures); this "
            "script selects one representative wheel that is installable on the invoking "
            "interpreter."
        ),
    )
    return parser.parse_args()


def interpreter_compatible_tags() -> List[str]:
    """The set of platform/interpreter/ABI tags pip considers installable on this interpreter."""
    return [str(t) for t in packaging_tags.sys_tags()]


def find_representative_wheel(wheel_dir: str) -> str:
    """Return one wheel from *wheel_dir* that is installable on the invoking interpreter.

    A signed-binary package's platform artifact directory can contain wheels for multiple
    Python implementations or architectures. This is representative coverage of the signed
    repackaging boundary, not an exhaustive compatibility test, so prefer the first wheel
    matching pip's ordered compatibility tags and use the filename as a stable tie-breaker.
    """
    candidates = sorted(glob.glob(os.path.join(wheel_dir, "*.whl")))
    if not candidates:
        raise FileNotFoundError(f"No wheel found in {wheel_dir}.")

    wheel_tags = {
        candidate: {str(tag) for tag in parse_wheel_filename(os.path.basename(candidate))[3]}
        for candidate in candidates
    }
    for compatible_tag in interpreter_compatible_tags():
        for candidate in candidates:
            if compatible_tag in wheel_tags[candidate]:
                return candidate

    raise RuntimeError(
        f"None of the wheels in {wheel_dir} are installable on this interpreter, so the smoke "
        f"test cannot validate a representative wheel: {candidates}"
    )


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
        if not any(suffix.endswith(ext) for ext in IMPORTABLE_EXTENSION_SUFFIXES):
            continue

        # Strip the platform/abi tag portion of the filename (e.g. "native.cp310-win_amd64.pyd"
        # -> "native"), then convert the file's path into a dotted module name.
        path = Path(relative_path)
        stem = path.name
        for ext in IMPORTABLE_EXTENSION_SUFFIXES:
            idx = stem.lower().find(ext)
            if idx != -1:
                stem = stem[:idx]
                break
        stem = stem.split(".")[0]

        parent_parts = path.parent.parts

        # Not every .so is an importable module. auditwheel vendors a package's native
        # dependencies under `<dist>.libs/*.so`; that's signable but isn't a Python module and
        # doesn't sit on a valid dotted import path. A directory or filename that isn't a valid
        # identifier can't be part of one, so skip it instead of handing import_module() a bogus
        # name like "pkg.libs.libfoo".
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


def smoke_test_wheel(wheel_path: str) -> int:
    """Install *wheel_path* and import every compiled module it ships. Returns the count imported."""
    print(f"Smoke-testing signed wheel: {wheel_path}")

    install_wheel(wheel_path)

    dist_name = distribution_name_from_wheel(wheel_path)
    compiled_modules = find_compiled_modules(dist_name)

    if not compiled_modules:
        raise RuntimeError(
            f"No importable compiled extension modules (.pyd/.so) found for {dist_name}; expected at "
            "least one for a signed-binary package. The smoke test would not have exercised anything."
        )

    for module_name in compiled_modules:
        print(f"Importing {module_name}...")
        importlib.import_module(module_name)
        print(f"OK: {module_name} imported successfully.")

    return len(compiled_modules)


def main() -> None:
    args = parse_args()
    wheel_path = find_representative_wheel(args.wheel_dir)
    total_modules = smoke_test_wheel(wheel_path)

    print(f"Smoke test passed: {total_modules} compiled module(s) imported successfully.")


if __name__ == "__main__":
    try:
        main()
    except (CalledProcessError, RuntimeError, FileNotFoundError, ImportError) as error:
        print(f"Smoke test failed: {error}", file=sys.stderr)
        sys.exit(1)
