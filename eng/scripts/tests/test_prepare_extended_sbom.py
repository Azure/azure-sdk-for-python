from pathlib import Path
import sys
from zipfile import ZipFile

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from prepare_extended_sbom import main, prepare_discovery_inputs


def make_project(repo, relative_path, name, version="1.0.0"):
    directory = repo / relative_path
    directory.mkdir(parents=True)
    (directory / "pyproject.toml").write_text(
        f'[project]\nname = "{name}"\nversion = "{version}"\ndependencies = []\n', encoding="utf-8"
    )
    return directory


def make_wheel(artifacts, name, version="1.0.0", tag="py3-none-any"):
    artifacts.mkdir(parents=True, exist_ok=True)
    normalized = name.replace("-", "_")
    wheel = artifacts / f"{normalized}-{version}-{tag}.whl"
    with ZipFile(wheel, "w") as archive:
        archive.writestr(
            f"{normalized}-{version}.dist-info/METADATA",
            f"Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n",
        )
    return wheel


def test_selects_artifact_projects_across_services_and_tools(tmp_path):
    repo = tmp_path / "repository with spaces"
    artifacts = tmp_path / "artifacts"
    output = tmp_path / "scan"
    projects = [
        ("sdk/keyvault/azure-keyvault-keys", "azure-keyvault-keys"),
        ("sdk/resources/azure-mgmt-resource", "azure-mgmt-resource"),
        ("sdk/monitor/azure-monitor-query", "azure-monitor-query"),
        ("sdk/core/azure-core", "azure-core"),
        ("sdk/identity/azure-identity", "azure-identity"),
        ("eng/tools/azure-sdk-tools", "azure-sdk-tools"),
    ]
    expected = []
    for path, name in projects:
        directory = make_project(repo, path, name)
        make_wheel(artifacts / name, name)
        expected.append(directory.as_uri())
    make_project(repo, "sdk/ml/azure-ai-ml", "azure-ai-ml")
    make_project(repo, "sdk/core/azure-core/tests/fixture", "fixture")
    prepare_discovery_inputs(repo, artifacts, output)
    assert set((output / "requirements.txt").read_text().splitlines()) == set(expected)
    assert list(output.iterdir()) == [output / "requirements.txt"]


def test_deduplicates_native_wheels_and_accepts_normalized_names(tmp_path):
    repo = tmp_path / "repo"
    artifacts = tmp_path / "artifacts"
    output = tmp_path / "scan"
    source = make_project(repo, "sdk/service/azure-native", "azure-native", "1.0.0a20261026001")
    make_wheel(artifacts, "azure_native", "1.0.0a20261026001", "cp310-abi3-win_amd64")
    make_wheel(artifacts, "azure-native", "1.0.0a20261026001", "cp310-abi3-manylinux2014_x86_64")
    prepare_discovery_inputs(repo, artifacts, output)
    assert (output / "requirements.txt").read_text().splitlines() == [source.as_uri()]


@pytest.mark.parametrize("failure", ["missing", "version", "name", "duplicate"])
def test_rejects_missing_mismatched_or_ambiguous_sources(tmp_path, failure):
    repo = tmp_path / "repo"
    artifacts = tmp_path / "artifacts"
    output = tmp_path / "scan"
    make_wheel(artifacts, "azure-example")
    if failure != "missing":
        make_project(
            repo,
            "sdk/example/azure-example",
            "azure-other" if failure == "name" else "azure-example",
            "2.0.0" if failure == "version" else "1.0.0",
        )
    if failure == "duplicate":
        make_project(repo, "sdk/other/azure-example", "azure-example")
    with pytest.raises(ValueError, match="Expected one matching source project|do not match artifact wheels"):
        prepare_discovery_inputs(repo, artifacts, output)
    assert not output.exists()


def test_rejects_multiple_versions_of_one_distribution(tmp_path):
    artifacts = tmp_path / "artifacts"
    make_wheel(artifacts, "azure-example", "1.0.0")
    make_wheel(artifacts, "azure-example", "2.0.0")
    with pytest.raises(ValueError, match="Multiple versions"):
        prepare_discovery_inputs(tmp_path / "repo", artifacts, tmp_path / "scan")


@pytest.mark.parametrize("targeting_string", ["", "*", "azure-example"])
def test_rejects_empty_artifact(tmp_path, targeting_string):
    with pytest.raises(ValueError, match="No wheels"):
        prepare_discovery_inputs(
            tmp_path / "repo", tmp_path / "artifacts", tmp_path / "scan", targeting_string=targeting_string
        )


def test_accepts_explicitly_empty_selection(tmp_path):
    output = tmp_path / "scan"
    prepare_discovery_inputs(tmp_path / "repo", tmp_path / "artifacts", output, targeting_string="null")
    assert (output / "requirements.txt").read_text() == ""
    assert list(output.iterdir()) == [output / "requirements.txt"]


def test_empty_selection_replaces_stale_requirements(tmp_path):
    output = tmp_path / "scan"
    output.mkdir()
    (output / "requirements.txt").write_text("old-input\n")
    prepare_discovery_inputs(tmp_path / "repo", tmp_path / "artifacts", output, targeting_string="null")
    assert (output / "requirements.txt").read_text() == ""


def test_empty_selection_still_includes_existing_wheels(tmp_path):
    repo = tmp_path / "repo"
    artifacts = tmp_path / "artifacts"
    output = tmp_path / "scan"
    source = make_project(repo, "sdk/example/azure-example", "azure-example")
    make_wheel(artifacts, "azure-example")
    prepare_discovery_inputs(repo, artifacts, output, targeting_string="null")
    assert (output / "requirements.txt").read_text().splitlines() == [source.as_uri()]


def test_cli_accepts_explicitly_empty_selection(tmp_path, monkeypatch):
    output = tmp_path / "scan"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prepare_extended_sbom.py",
            "--repo-root",
            str(tmp_path / "repo"),
            "--artifact-directory",
            str(tmp_path / "artifacts"),
            "--output-directory",
            str(output),
            "--targeting-string",
            "null",
        ],
    )
    main()
    assert (output / "requirements.txt").read_text() == ""


@pytest.mark.parametrize("metadata", ["", "Metadata-Version: 2.1\nName: azure-example\n"])
def test_rejects_missing_wheel_metadata(tmp_path, metadata):
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    with ZipFile(artifacts / "azure_example-1.0.0-py3-none-any.whl", "w") as archive:
        if metadata:
            archive.writestr("azure_example-1.0.0.dist-info/METADATA", metadata)
    with pytest.raises(ValueError, match="metadata|name or version"):
        prepare_discovery_inputs(tmp_path / "repo", artifacts, tmp_path / "scan")


def test_replaces_stale_requirements_on_retry(tmp_path):
    repo = tmp_path / "repo"
    artifacts = tmp_path / "artifacts"
    output = tmp_path / "scan"
    source = make_project(repo, "sdk/example/azure-example", "azure-example")
    make_wheel(artifacts, "azure-example")
    output.mkdir()
    (output / "requirements.txt").write_text("old-input\n")
    prepare_discovery_inputs(repo, artifacts, output)
    assert (output / "requirements.txt").read_text().splitlines() == [source.as_uri()]


def test_failure_removes_stale_requirements(tmp_path):
    output = tmp_path / "scan"
    output.mkdir()
    requirements = output / "requirements.txt"
    requirements.write_text("old-input\n")
    with pytest.raises(ValueError, match="No wheels"):
        prepare_discovery_inputs(tmp_path / "repo", tmp_path / "artifacts", output)
    assert not requirements.exists()


def test_legacy_setup_project(tmp_path):
    repo = tmp_path / "repo"
    source = repo / "sdk/example/azure-example"
    source.mkdir(parents=True)
    (source / "setup.py").write_text(
        "from setuptools import setup\nsetup(name='azure-example', version='1.0.0')\n", encoding="utf-8"
    )
    artifacts = tmp_path / "artifacts"
    make_wheel(artifacts, "azure-example")
    output = tmp_path / "scan"
    prepare_discovery_inputs(repo, artifacts, output)
    assert (output / "requirements.txt").read_text().splitlines() == [source.as_uri()]
