"""PEP 517 wrapper that adds QueryPlanInterop native files to platform wheels.

Background: a cross-partition query needs a *query plan* first -- the list of
partitions to contact and the work to do on the results afterwards. The Rust
driver can build that plan on the customer's own machine using a separate
compiled library called QueryPlanInterop, which is not part of the Rust
extension and has to travel in the wheel as its own file.

``pip`` does not run this module; it runs whatever ``pyproject.toml`` names as
the build backend. That used to be Maturin directly. Maturin compiles the Rust
extension but knows nothing about QueryPlanInterop, so this module sits in
front of it: for a wheel build it copies the QueryPlanInterop files into
``azure/cosmos/.libs`` first, lets Maturin build and package as usual, then
removes them again so the source tree is left as it was found.

Without this module the wheel would ship the Rust extension and nothing else.
Queries would still return correct results -- the driver asks the Cosmos DB
gateway for the plan when the local library is missing -- but every
cross-partition query would pay one extra network round trip before its first
page, and the local-planning work would be compiled in and permanently unused.

Only wheels get the files. Source distributions and editable installs
deliberately do not, so a developer's checkout never accumulates release
binaries.
"""

from __future__ import annotations

import errno
import hashlib
import json
import os
import shutil
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Mapping, Optional

import maturin

if os.name == "nt":
    import msvcrt
else:
    import fcntl  # pylint: disable=import-error

_SOURCE_DIRECTORY_ENV = "AZURE_COSMOS_QUERYPLANINTEROP_SOURCE_DIR"
_STAGING_ACTIVE_ENV = "AZURE_COSMOS_QUERYPLANINTEROP_STAGING_ACTIVE"
_PACKAGE_LIBS_DIRECTORY = Path(__file__).parent / "azure" / "cosmos" / ".libs"
_PROJECT_LOCK_KEY = hashlib.sha256(
    str(Path(__file__).resolve().parent).casefold().encode("utf-8")
).hexdigest()[:16]
_STAGING_LOCK_FILE = (
    Path(tempfile.gettempdir()) / f"azure-cosmos-queryplan-{_PROJECT_LOCK_KEY}.lock"
)
_STAGING_LOCK_TIMEOUT_SECONDS = 600
_STAGING_MANIFEST_FILE = (
    Path(tempfile.gettempdir())
    / f"azure-cosmos-queryplan-{_PROJECT_LOCK_KEY}-staging.json"
)
_STAGING_MANIFEST_TEMP_FILE = _STAGING_MANIFEST_FILE.with_suffix(".json.tmp")
_PRIMARY_LIBRARY_NAMES = {
    "Cosmos.QueryPlanInterop.dll",
    "libqueryplaninterop.so",
    "libqueryplaninterop.dylib",
}


def _is_native_library(path: Path, primary_library: str) -> bool:
    name = path.name
    if primary_library.endswith(".dll"):
        return name.lower().endswith(".dll")
    if primary_library.endswith(".so"):
        return name.endswith(".so") or ".so." in name
    return name.endswith(".dylib")


@contextmanager
def _staging_lock() -> Iterator[None]:
    lock_file = _STAGING_LOCK_FILE.open("a+b")
    locked = False
    try:
        if os.name == "nt":
            if os.fstat(lock_file.fileno()).st_size == 0:
                lock_file.seek(0)
                lock_file.write(b"\0")
                lock_file.flush()
        deadline = time.monotonic() + _STAGING_LOCK_TIMEOUT_SECONDS
        while True:
            lock_file.seek(0)
            try:
                if os.name == "nt":
                    msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                locked = True
                break
            except OSError as error:
                if error.errno not in (errno.EACCES, errno.EAGAIN, errno.EDEADLK):
                    raise
                if time.monotonic() >= deadline:
                    raise RuntimeError(
                        "timed out waiting for another QueryPlanInterop wheel build "
                        f"to release {_STAGING_LOCK_FILE}"
                    ) from error
                time.sleep(0.1)
        yield
    finally:
        if locked:
            if os.name == "nt":
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        lock_file.close()


def _prepare_package_directory() -> bool:
    if _PACKAGE_LIBS_DIRECTORY.exists():
        if not _PACKAGE_LIBS_DIRECTORY.is_dir() or any(
            _PACKAGE_LIBS_DIRECTORY.iterdir()
        ):
            raise RuntimeError(
                f"{_PACKAGE_LIBS_DIRECTORY} must be an empty directory "
                "before wheel staging"
            )
        return False
    _PACKAGE_LIBS_DIRECTORY.mkdir(parents=True)
    return True


def _recover_stale_staging() -> None:
    _STAGING_MANIFEST_TEMP_FILE.unlink(missing_ok=True)
    if not _STAGING_MANIFEST_FILE.is_file():
        return
    try:
        manifest = json.loads(_STAGING_MANIFEST_FILE.read_text(encoding="utf-8"))
        file_names = manifest["files"]
        created_directory = manifest["created_directory"]
        if (
            not isinstance(file_names, list)
            or not isinstance(created_directory, bool)
            or any(
                not isinstance(name, str) or Path(name).name != name
                for name in file_names
            )
        ):
            raise ValueError("invalid staging manifest fields")
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise RuntimeError(
            "cannot safely recover invalid QueryPlanInterop staging manifest "
            f"{_STAGING_MANIFEST_FILE}"
        ) from error

    if _PACKAGE_LIBS_DIRECTORY.is_dir():
        for file_name in file_names:
            (_PACKAGE_LIBS_DIRECTORY / file_name).unlink(missing_ok=True)
        if any(_PACKAGE_LIBS_DIRECTORY.iterdir()):
            raise RuntimeError(
                f"{_PACKAGE_LIBS_DIRECTORY} contains files not owned by the abandoned "
                "QueryPlanInterop build"
            )
        if created_directory:
            _PACKAGE_LIBS_DIRECTORY.rmdir()
    _STAGING_MANIFEST_FILE.unlink()


def _write_staging_manifest(created_directory: bool, file_names: list[str]) -> Path:
    _STAGING_MANIFEST_TEMP_FILE.write_text(
        json.dumps(
            {
                "created_directory": created_directory,
                "files": file_names,
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    os.replace(_STAGING_MANIFEST_TEMP_FILE, _STAGING_MANIFEST_FILE)
    return _STAGING_MANIFEST_FILE


@contextmanager
def _staged_query_plan_interop() -> Iterator[None]:
    source_value = os.environ.get(_SOURCE_DIRECTORY_ENV)
    if not source_value:
        yield
        return

    source_directory = Path(source_value).resolve()
    if not source_directory.is_dir():
        raise RuntimeError(
            f"{_SOURCE_DIRECTORY_ENV} is not a directory: {source_directory}"
        )
    primary_libraries = [
        name for name in _PRIMARY_LIBRARY_NAMES if (source_directory / name).is_file()
    ]
    if len(primary_libraries) != 1:
        raise RuntimeError(
            f"{_SOURCE_DIRECTORY_ENV} must contain exactly one target-platform "
            f"QueryPlanInterop primary library; found {primary_libraries}"
        )

    primary_library = primary_libraries[0]
    native_files = [
        path
        for path in source_directory.iterdir()
        if path.is_file() and _is_native_library(path, primary_library)
    ]
    with _staging_lock():
        previous_staging_value = os.environ.get(_STAGING_ACTIVE_ENV)
        copied_files = []
        created_directory = False
        manifest_path = None
        try:
            _recover_stale_staging()
            created_directory = _prepare_package_directory()
            manifest_path = _write_staging_manifest(
                created_directory,
                [path.name for path in native_files],
            )
            os.environ[_STAGING_ACTIVE_ENV] = "1"
            for source in native_files:
                destination = _PACKAGE_LIBS_DIRECTORY / source.name
                copied_files.append(destination)
                shutil.copy2(source, destination)
            yield
        finally:
            if previous_staging_value is None:
                os.environ.pop(_STAGING_ACTIVE_ENV, None)
            else:
                os.environ[_STAGING_ACTIVE_ENV] = previous_staging_value
            for copied_file in copied_files:
                copied_file.unlink(missing_ok=True)
            _STAGING_MANIFEST_TEMP_FILE.unlink(missing_ok=True)
            if manifest_path is not None:
                manifest_path.unlink(missing_ok=True)
            if created_directory:
                _PACKAGE_LIBS_DIRECTORY.rmdir()


@contextmanager
def _without_packaging_source() -> Iterator[None]:
    source_value = os.environ.pop(_SOURCE_DIRECTORY_ENV, None)
    try:
        yield
    finally:
        if source_value is not None:
            os.environ[_SOURCE_DIRECTORY_ENV] = source_value


def build_wheel(
    wheel_directory: str,
    config_settings: Optional[Mapping[str, Any]] = None,
    metadata_directory: Optional[str] = None,
) -> str:
    """Build a wheel after temporarily staging configured native sidecars."""
    with _staged_query_plan_interop():
        return maturin.build_wheel(
            wheel_directory,
            config_settings=config_settings,
            metadata_directory=metadata_directory,
        )


def build_sdist(
    sdist_directory: str,
    config_settings: Optional[Mapping[str, Any]] = None,
) -> str:
    """Build a source distribution without native sidecars."""
    return maturin.build_sdist(sdist_directory, config_settings=config_settings)


def build_editable(
    wheel_directory: str,
    config_settings: Optional[Mapping[str, Any]] = None,
    metadata_directory: Optional[str] = None,
) -> str:
    """Delegate editable builds without copying release sidecars into the source tree."""
    with _without_packaging_source():
        return maturin.build_editable(
            wheel_directory,
            config_settings=config_settings,
            metadata_directory=metadata_directory,
        )


def prepare_metadata_for_build_wheel(
    metadata_directory: str,
    config_settings: Optional[Mapping[str, Any]] = None,
) -> str:
    """Prepare wheel metadata through Maturin."""
    return maturin.prepare_metadata_for_build_wheel(
        metadata_directory,
        config_settings=config_settings,
    )


def prepare_metadata_for_build_editable(
    metadata_directory: str,
    config_settings: Optional[Mapping[str, Any]] = None,
) -> str:
    """Prepare editable-build metadata through Maturin."""
    return maturin.prepare_metadata_for_build_editable(
        metadata_directory,
        config_settings=config_settings,
    )
