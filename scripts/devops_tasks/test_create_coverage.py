#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from subprocess import CalledProcessError
from unittest import mock

from coverage import CoverageData

import create_coverage


def test_find_coverage_files_reads_package_data_files(tmp_path, monkeypatch):
    sdk_dir = tmp_path / "sdk"
    first_coverage = sdk_dir / "alpha" / "azure-alpha" / ".coverage"
    second_coverage = sdk_dir / "beta" / "azure-beta" / ".coverage"
    parallel_coverage = sdk_dir / "beta" / "azure-beta" / ".coverage.worker"
    ignored_outside_sdk = tmp_path / "eng" / ".coverage"

    for coverage_file in (
        first_coverage,
        second_coverage,
        parallel_coverage,
        ignored_outside_sdk,
    ):
        coverage_file.parent.mkdir(parents=True, exist_ok=True)
        coverage_file.touch()

    monkeypatch.setattr(create_coverage, "sdk_dir", os.fspath(sdk_dir))

    assert create_coverage.find_coverage_files() == sorted(
        [
            os.fspath(first_coverage),
            os.fspath(second_coverage),
            os.fspath(parallel_coverage),
        ]
    )


def test_collect_coverage_files_relocates_duplicate_package_names(
    tmp_path, monkeypatch
):
    sdk_dir = tmp_path / "sdk"
    first_coverage = (
        sdk_dir / "textanalytics" / "azure-ai-textanalytics" / ".coverage.whl"
    )
    second_coverage = (
        sdk_dir / "cognitivelanguage" / "azure-ai-textanalytics" / ".coverage.whl"
    )
    # Both packages share an identically named isolate path, so the recorded string is
    # the same for each; only the originating data file disambiguates them.
    shared_isolate_path = (
        ".venv/azure-ai-textanalytics/.venv_whl/lib/python3.11/"
        "site-packages/azure/ai/textanalytics/_client.py"
    )

    for coverage_file in (first_coverage, second_coverage):
        coverage_file.parent.mkdir(parents=True, exist_ok=True)
        coverage_data = CoverageData(basename=os.fspath(coverage_file))
        coverage_data.add_lines({shared_isolate_path: {1}})
        coverage_data.write()

    monkeypatch.setattr(create_coverage, "root_dir", os.fspath(tmp_path))
    monkeypatch.setattr(create_coverage, "sdk_dir", os.fspath(sdk_dir))
    monkeypatch.setattr(
        create_coverage, "coverage_data_file", os.fspath(tmp_path / ".coverage")
    )

    assert create_coverage.collect_coverage_files()

    combined_coverage = CoverageData(basename=os.fspath(tmp_path / ".coverage"))
    combined_coverage.read()
    assert set(combined_coverage.measured_files()) == {
        "sdk/textanalytics/azure-ai-textanalytics/azure/ai/textanalytics/_client.py",
        "sdk/cognitivelanguage/azure-ai-textanalytics/azure/ai/textanalytics/_client.py",
    }


def test_collect_coverage_files_creates_combined_data_file(tmp_path, monkeypatch):
    sdk_dir = tmp_path / "sdk"
    first_coverage = sdk_dir / "alpha" / ".coverage"
    second_coverage = sdk_dir / "beta" / ".coverage"
    first_source = sdk_dir / "alpha" / "alpha.py"
    second_source = sdk_dir / "beta" / "beta.py"

    for coverage_file, source_file in (
        (first_coverage, first_source),
        (second_coverage, second_source),
    ):
        coverage_file.parent.mkdir(parents=True, exist_ok=True)
        coverage_data = CoverageData(basename=os.fspath(coverage_file))
        coverage_data.add_lines({os.fspath(source_file): {1}})
        coverage_data.write()

    monkeypatch.setattr(create_coverage, "root_dir", os.fspath(tmp_path))
    monkeypatch.setattr(create_coverage, "sdk_dir", os.fspath(sdk_dir))
    monkeypatch.setattr(
        create_coverage, "coverage_data_file", os.fspath(tmp_path / ".coverage")
    )

    assert create_coverage.collect_coverage_files()

    combined_coverage = CoverageData(basename=os.fspath(tmp_path / ".coverage"))
    combined_coverage.read()
    assert set(combined_coverage.measured_files()) == {
        os.fspath(first_source),
        os.fspath(second_source),
    }
    assert first_coverage.exists()
    assert second_coverage.exists()


def test_collect_coverage_files_returns_false_when_no_data_exists(
    tmp_path, monkeypatch
):
    run = mock.Mock()

    monkeypatch.setattr(create_coverage, "root_dir", os.fspath(tmp_path))
    monkeypatch.setattr(create_coverage, "sdk_dir", os.fspath(tmp_path / "sdk"))
    monkeypatch.setattr(create_coverage, "find_coverage_files", lambda: [])
    monkeypatch.setattr(create_coverage, "run", run)

    assert not create_coverage.collect_coverage_files()
    assert run.call_count == 1


def test_generate_coverage_xml_uses_combined_data_file(tmp_path, monkeypatch):
    coverage_data_file = tmp_path / ".coverage"
    coverage_data_file.touch()
    run_check_call = mock.Mock(return_value=None)

    monkeypatch.setattr(create_coverage, "root_dir", os.fspath(tmp_path))
    monkeypatch.setattr(
        create_coverage, "coverage_data_file", os.fspath(coverage_data_file)
    )
    monkeypatch.setattr(
        create_coverage, "coveragerc", os.fspath(tmp_path / ".coveragerc")
    )
    monkeypatch.setattr(create_coverage, "run_check_call", run_check_call)

    assert create_coverage.generate_coverage_xml()
    run_check_call.assert_called_once_with(
        ["coverage", "xml", "-i", "--rcfile", os.fspath(tmp_path / ".coveragerc")],
        os.fspath(tmp_path),
        always_exit=False,
    )


def test_generate_coverage_xml_returns_false_without_combined_data(
    tmp_path, monkeypatch
):
    run_check_call = mock.Mock()

    monkeypatch.setattr(
        create_coverage, "coverage_data_file", os.fspath(tmp_path / ".coverage")
    )
    monkeypatch.setattr(create_coverage, "run_check_call", run_check_call)

    assert not create_coverage.generate_coverage_xml()
    run_check_call.assert_not_called()


def test_generate_coverage_xml_returns_false_without_exiting_on_command_failure(
    tmp_path, monkeypatch
):
    coverage_data_file = tmp_path / ".coverage"
    coverage_data_file.touch()
    run_check_call = mock.Mock(
        return_value=CalledProcessError(returncode=1, cmd=["coverage", "xml"])
    )

    monkeypatch.setattr(create_coverage, "root_dir", os.fspath(tmp_path))
    monkeypatch.setattr(
        create_coverage, "coverage_data_file", os.fspath(coverage_data_file)
    )
    monkeypatch.setattr(create_coverage, "run_check_call", run_check_call)

    assert not create_coverage.generate_coverage_xml()
    run_check_call.assert_called_once_with(
        ["coverage", "xml", "-i", "--rcfile", create_coverage.coveragerc],
        os.fspath(tmp_path),
        always_exit=False,
    )


def test_fix_coverage_xml_normalizes_venv_paths_like_tox(tmp_path, monkeypatch):
    sdk_dir = tmp_path / "sdk"
    package_dir = sdk_dir / "core" / "azure-core"
    package_dir.mkdir(parents=True)
    coverage_xml = tmp_path / "coverage.xml"
    coverage_xml.write_text(
        """
        <class filename=".venv/azure-core/.venv_whl/lib/python3.11/site-packages/azure/core/_base.py" />
        <package name=".venv.azure-core..venv_whl.lib.python3.11.site-packages.azure.core" />
        <class filename="sdk/core/azure-core/.tox/whl/lib/python3.11/site-packages/azure/core/_base.py" />
        <package name="sdk.core.azure-core.tox.whl.lib.python3.11.site-packages.azure.core" />
        """,
        encoding="utf-8",
    )

    monkeypatch.setattr(create_coverage, "root_dir", os.fspath(tmp_path))
    monkeypatch.setattr(create_coverage, "sdk_dir", os.fspath(sdk_dir))

    create_coverage.fix_coverage_xml(os.fspath(coverage_xml))

    normalized_xml = coverage_xml.read_text(encoding="utf-8")
    assert (
        normalized_xml.count('filename="sdk/core/azure-core/azure/core/_base.py"') == 2
    )
    assert normalized_xml.count('name="sdk.core.azure-core.azure.core"') == 2


def test_normalize_venv_paths_supports_versioned_and_windows_environments(
    tmp_path, monkeypatch
):
    sdk_dir = tmp_path / "sdk"
    package_dir = sdk_dir / "storage" / "azure-storage-blob"
    package_dir.mkdir(parents=True)

    monkeypatch.setattr(create_coverage, "root_dir", os.fspath(tmp_path))
    monkeypatch.setattr(create_coverage, "sdk_dir", os.fspath(sdk_dir))

    coverage_xml = (
        '<class filename=".venv/azure-storage-blob/.venv_whl_py310/'
        'Lib/site-packages/azure/storage/blob/_blob_client.py" />'
    )

    assert create_coverage.normalize_venv_paths(coverage_xml) == (
        '<class filename="sdk/storage/azure-storage-blob/'
        'azure/storage/blob/_blob_client.py" />'
    )


def test_normalize_venv_paths_leaves_unknown_packages_unchanged(tmp_path, monkeypatch):
    monkeypatch.setattr(create_coverage, "root_dir", os.fspath(tmp_path))
    monkeypatch.setattr(create_coverage, "sdk_dir", os.fspath(tmp_path / "sdk"))
    (tmp_path / "sdk").mkdir()
    coverage_xml = (
        '<class filename=".venv/unknown/.venv_whl/lib/python3.11/'
        'site-packages/unknown/__init__.py" />'
    )

    assert create_coverage.normalize_venv_paths(coverage_xml) == coverage_xml
