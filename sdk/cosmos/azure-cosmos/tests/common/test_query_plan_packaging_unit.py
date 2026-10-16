# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Tests for QueryPlanInterop wheel staging (no network, no real wheel build).

QueryPlanInterop is a compiled library the Rust driver uses to work out a
cross-partition query's plan locally instead of asking the Gateway for it. It is
built elsewhere, so the wheel build has to copy it into ``azure/cosmos/.libs``
just before packaging and take it out again afterwards.

That copy step writes into the source tree, which is why these tests exist. A
build that crashes partway, or two builds running at once on the same machine,
could otherwise leave files behind that end up in the next wheel or delete files
that were never the build's to delete. Both mistakes are invisible until a
customer installs the result.

The staging code guards against that with a lock file that only one build can
hold, and a manifest that records exactly which files this build created so
cleanup never touches anything else. These tests drive that code directly with
fake files in a temporary directory.
"""
# pylint: disable=protected-access

import json
import os
import threading

import pytest

import azure_cosmos_build_backend as build_backend


def _configure_test_paths(monkeypatch, tmp_path):
    """Create isolated native-library source and package paths."""
    package_directory = tmp_path / "package"
    package_directory.mkdir()
    libs_directory = package_directory / ".libs"
    lock_file = package_directory / ".queryplaninterop-wheel.lock"
    manifest_file = package_directory / ".queryplaninterop-staging.json"
    manifest_temp_file = package_directory / ".queryplaninterop-staging.json.tmp"
    source_directory = tmp_path / "source"
    source_directory.mkdir()
    (source_directory / "Cosmos.QueryPlanInterop.dll").write_bytes(b"primary")
    (source_directory / "dependency.dll").write_bytes(b"dependency")
    (source_directory / "ignored.txt").write_text("ignored", encoding="utf-8")
    monkeypatch.setattr(
        build_backend, "_PACKAGE_LIBS_DIRECTORY", libs_directory
    )
    monkeypatch.setattr(build_backend, "_STAGING_LOCK_FILE", lock_file)
    monkeypatch.setattr(build_backend, "_STAGING_MANIFEST_FILE", manifest_file)
    monkeypatch.setattr(
        build_backend, "_STAGING_MANIFEST_TEMP_FILE", manifest_temp_file
    )
    monkeypatch.setenv(
        "AZURE_COSMOS_QUERYPLANINTEROP_SOURCE_DIR", str(source_directory)
    )
    return libs_directory, lock_file, manifest_file


def test_sidecars_are_staged_and_cleaned(monkeypatch, tmp_path):
    """The build stages only native files and removes its temporary state.

    The source directory can hold other files next to the libraries. Copying
    those in would put unrelated content inside every wheel, so only ``.dll``
    style files are taken. The lock file is deliberately left behind: it holds no
    state, and deleting it would race with the next build trying to take it.
    """
    libs_directory, lock_file, manifest_file = _configure_test_paths(
        monkeypatch, tmp_path
    )

    with build_backend._staged_query_plan_interop():
        assert (libs_directory / "Cosmos.QueryPlanInterop.dll").is_file()
        assert (libs_directory / "dependency.dll").is_file()
        assert not (libs_directory / "ignored.txt").exists()
        assert manifest_file.is_file()
        assert lock_file.is_file()

    assert not libs_directory.exists()
    assert not manifest_file.exists()
    assert lock_file.exists()


def test_preexisting_package_files_are_preserved(monkeypatch, tmp_path):
    """An unexpected package file fails staging without deleting that file.

    If ``.libs`` already has something in it, the build cannot tell whether that
    is leftover junk or someone's work. Guessing wrong in one direction ships a
    stray file to customers; guessing wrong in the other destroys a file the
    build did not create. So it stops and says so.
    """
    libs_directory, lock_file, _ = _configure_test_paths(monkeypatch, tmp_path)
    libs_directory.mkdir()
    unrelated_file = libs_directory / "unrelated.dll"
    unrelated_file.write_bytes(b"keep")

    with pytest.raises(RuntimeError, match="must be an empty directory"):
        with build_backend._staged_query_plan_interop():
            pass

    assert unrelated_file.read_bytes() == b"keep"
    assert lock_file.exists()


def test_stale_lock_file_does_not_block_staging(monkeypatch, tmp_path):
    """A lock file left by a dead process does not block a later build.

    The lock is held by the operating system, not by the file's existence, so a
    build killed mid-run releases it automatically. Treating a leftover file as
    "someone is building" would wedge that machine until a person deleted it by
    hand.
    """
    libs_directory, lock_file, _ = _configure_test_paths(monkeypatch, tmp_path)
    lock_file.write_text("another process", encoding="ascii")

    with build_backend._staged_query_plan_interop():
        assert (libs_directory / "Cosmos.QueryPlanInterop.dll").is_file()

    assert lock_file.read_text(encoding="ascii") == "another process"


def test_staging_lock_serializes_parallel_builds(monkeypatch, tmp_path):
    """A second build waits until the first build releases its OS-backed lock.

    Release pipelines build several wheels on one machine at the same time, and
    they all stage into the same directory in the same checkout. Without the
    lock, one build's cleanup would delete the files another build was about to
    package, producing a wheel with no QueryPlanInterop in it and no error.
    """
    _, lock_file, _ = _configure_test_paths(monkeypatch, tmp_path)
    first_acquired = threading.Event()
    release_first = threading.Event()
    second_acquired = threading.Event()

    def hold_first_lock():
        with build_backend._staging_lock():
            first_acquired.set()
            assert release_first.wait(timeout=5)

    def wait_for_second_lock():
        assert first_acquired.wait(timeout=5)
        with build_backend._staging_lock():
            second_acquired.set()

    first_thread = threading.Thread(target=hold_first_lock)
    second_thread = threading.Thread(target=wait_for_second_lock)
    first_thread.start()
    assert first_acquired.wait(timeout=5)
    second_thread.start()
    assert not second_acquired.wait(timeout=0.2)

    release_first.set()
    first_thread.join(timeout=5)
    second_thread.join(timeout=5)

    assert not first_thread.is_alive()
    assert not second_thread.is_alive()
    assert second_acquired.is_set()
    assert lock_file.exists()


def test_partial_copy_failure_releases_staging_lock(monkeypatch, tmp_path):
    """A failed copy removes its partial output and releases the staging lock.

    A half-copied library is worse than a missing one: it is the right size and
    name but will not load, so the wheel looks complete. The partial file is
    removed, and the lock is released so the next build on the machine is not
    stuck behind a build that already gave up.
    """
    libs_directory, lock_file, manifest_file = _configure_test_paths(
        monkeypatch, tmp_path
    )

    def fail_after_partial_copy(_source, destination):
        destination.write_bytes(b"partial")
        raise OSError("copy failed")

    monkeypatch.setattr(build_backend.shutil, "copy2", fail_after_partial_copy)

    with pytest.raises(OSError, match="copy failed"):
        with build_backend._staged_query_plan_interop():
            pass

    assert not libs_directory.exists()
    assert not manifest_file.exists()
    assert lock_file.exists()


def test_abandoned_staging_is_recovered_without_deleting_unrelated_files(
    monkeypatch, tmp_path
):
    """A crashed build's manifest allows the next build to remove only owned files.

    A build that is killed outright cannot clean up after itself, so it writes
    down the file names it is about to create before it creates them. The next
    build reads that list and removes exactly those, which is why a stale file
    from a dead build cannot end up inside a released wheel.
    """
    libs_directory, _, manifest_file = _configure_test_paths(monkeypatch, tmp_path)
    libs_directory.mkdir()
    abandoned_file = libs_directory / "old-dependency.dll"
    abandoned_file.write_bytes(b"abandoned")
    manifest_file.write_text(
        json.dumps(
            {
                "created_directory": True,
                "files": [abandoned_file.name],
            }
        ),
        encoding="utf-8",
    )

    with build_backend._staged_query_plan_interop():
        assert not abandoned_file.exists()
        assert (libs_directory / "Cosmos.QueryPlanInterop.dll").is_file()

    assert not libs_directory.exists()


def test_abandoned_staging_preserves_unowned_files(monkeypatch, tmp_path):
    """Recovery fails rather than deleting files absent from the ownership manifest.

    Cleanup is only allowed to remove names the crashed build wrote down. Anything
    else in the directory belongs to someone else, and a build has no business
    deleting files from a developer's checkout.
    """
    libs_directory, _, manifest_file = _configure_test_paths(monkeypatch, tmp_path)
    libs_directory.mkdir()
    owned_file = libs_directory / "old-dependency.dll"
    owned_file.write_bytes(b"abandoned")
    unowned_file = libs_directory / "unrelated.dll"
    unowned_file.write_bytes(b"keep")
    manifest_file.write_text(
        json.dumps(
            {
                "created_directory": True,
                "files": [owned_file.name],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="files not owned"):
        with build_backend._staged_query_plan_interop():
            pass

    assert unowned_file.read_bytes() == b"keep"


def test_editable_build_ignores_release_sidecar_source(monkeypatch, tmp_path):
    """Editable builds do not trigger release-only Cargo sidecar validation.

    ``pip install -e`` is what a developer runs while working on the SDK. There is
    no wheel to package, so staging is skipped and the source-directory setting is
    hidden from the build script. Otherwise everyday local installs would fail on
    a check that only matters when producing a release artifact.
    """
    source_directory = tmp_path / "source"
    monkeypatch.setenv(
        "AZURE_COSMOS_QUERYPLANINTEROP_SOURCE_DIR", str(source_directory)
    )

    def fake_build_editable(*_args, **_kwargs):
        assert "AZURE_COSMOS_QUERYPLANINTEROP_SOURCE_DIR" not in os.environ
        return "editable.whl"

    monkeypatch.setattr(build_backend.maturin, "build_editable", fake_build_editable)

    assert build_backend.build_editable(str(tmp_path)) == "editable.whl"
    assert os.environ["AZURE_COSMOS_QUERYPLANINTEROP_SOURCE_DIR"] == str(
        source_directory
    )
