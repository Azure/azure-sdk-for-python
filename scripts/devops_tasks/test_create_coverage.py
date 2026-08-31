#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from unittest import mock

from coverage import CoverageData

import create_coverage


def test_find_coverage_files_reads_package_data_files(tmp_path, monkeypatch):
    sdk_dir = tmp_path / "sdk"
    first_coverage = sdk_dir / "alpha" / "azure-alpha" / ".coverage"
    second_coverage = sdk_dir / "beta" / "azure-beta" / ".coverage"
    ignored_parallel_file = sdk_dir / "beta" / "azure-beta" / ".coverage.worker"
    ignored_outside_sdk = tmp_path / "eng" / ".coverage"

    for coverage_file in (
        first_coverage,
        second_coverage,
        ignored_parallel_file,
        ignored_outside_sdk,
    ):
        coverage_file.parent.mkdir(parents=True, exist_ok=True)
        coverage_file.touch()

    monkeypatch.setattr(create_coverage, "sdk_dir", os.fspath(sdk_dir))

    assert create_coverage.find_coverage_files() == sorted(
        [os.fspath(first_coverage), os.fspath(second_coverage)]
    )


def test_collect_coverage_files_combines_package_data_files(tmp_path, monkeypatch):
    first_coverage = tmp_path / "sdk" / "alpha" / ".coverage"
    second_coverage = tmp_path / "sdk" / "beta" / ".coverage"
    run = mock.Mock()

    monkeypatch.setattr(create_coverage, "root_dir", os.fspath(tmp_path))
    monkeypatch.setattr(
        create_coverage,
        "find_coverage_files",
        lambda: [os.fspath(first_coverage), os.fspath(second_coverage)],
    )
    monkeypatch.setattr(create_coverage, "run", run)

    assert create_coverage.collect_coverage_files()
    assert run.call_args_list[1] == mock.call(
        [
            create_coverage.sys.executable,
            "-m",
            "coverage",
            "combine",
            "--keep",
            os.fspath(first_coverage),
            os.fspath(second_coverage),
        ],
        cwd=os.fspath(tmp_path),
        check=True,
    )


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
    run_check_call = mock.Mock()

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
