import sys
from pathlib import Path

import yaml

CONDA_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CONDA_DIR))

import update_conda_files as update  # pylint: disable=wrong-import-position


def _write_conda_client(path: Path, checkout: list[dict[str, str]]) -> None:
    content = {
        "parameters": [],
        "extends": {
            "parameters": {
                "stages": [
                    {
                        "jobs": [
                            {
                                "steps": [
                                    {
                                        "parameters": {
                                            "CondaArtifacts": [
                                                {
                                                    "name": "test",
                                                    "checkout": checkout,
                                                },
                                                {
                                                    "name": "azure-mgmt",
                                                    "checkout": [],
                                                },
                                            ]
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        },
    }
    path.write_text(yaml.safe_dump(content, sort_keys=False), encoding="utf-8")


def test_reconciles_outdated_versions_in_conda_client_yml(
    tmp_path: Path, monkeypatch
) -> None:
    conda_client_path = tmp_path / "conda-sdk-client.yml"
    _write_conda_client(
        conda_client_path,
        [{"package": "azure-example", "version": "1.0.0"}],
    )
    monkeypatch.setattr(update, "CONDA_CLIENT_YAML_PATH", str(conda_client_path))
    monkeypatch.setattr(update, "PACKAGES_WITH_DOWNLOAD_URI", {})

    update.update_conda_sdk_client_yml(
        {"azure-example": {update.VERSION_GA_COL: "2.0.0"}},
        packages_to_update=[],
        new_data_plane_packages=[],
        new_mgmt_plane_packages=[],
    )

    package_versions = update.get_conda_client_package_versions()
    assert package_versions["azure-example"] == "2.0.0"


def test_creates_release_log_for_existing_package(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(update, "CONDA_RELEASE_LOGS_DIR", str(tmp_path))

    result = update.update_data_plane_release_logs(
        {"azure-ai-evaluation": "1.18.3"},
        bundle_map={},
        data_plane_names=["azure-ai-evaluation"],
        release_date="2026.09.01",
    )

    assert result == []
    assert (tmp_path / "azure-ai-evaluation.md").read_text(encoding="utf-8") == (
        "# Azure AI Evaluation client library for Python (conda)\n\n"
        "## 2026.09.01\n\n"
        "### Packages included\n\n"
        "- azure-ai-evaluation-1.18.3"
    )


def test_release_log_uses_reconciled_checkout_version(
    tmp_path: Path, monkeypatch
) -> None:
    release_log = tmp_path / "azure-example.md"
    release_log.write_text(
        "# Azure Example client library for Python (conda)\n\n"
        "## 2026.09.01\n\n"
        "### Packages included\n\n"
        "- azure-example-1.0.0\n\n"
        "## 2026.06.01\n\n"
        "### Packages included\n\n"
        "- azure-example-0.9.0",
        encoding="utf-8",
    )
    monkeypatch.setattr(update, "CONDA_RELEASE_LOGS_DIR", str(tmp_path))

    update.update_data_plane_release_logs(
        {"azure-example": "2.0.0"},
        bundle_map={},
        data_plane_names=["azure-example"],
        release_date="2026.09.01",
    )

    content = release_log.read_text(encoding="utf-8")
    assert content.count("## 2026.09.01") == 1
    assert "- azure-example-2.0.0" in content
    assert "- azure-example-1.0.0" not in content
    assert "## 2026.06.01" in content


def test_filters_package_without_parseable_setup(monkeypatch) -> None:
    packages = [
        {update.PACKAGE_COL: "azure-mgmt-trustedsigning"},
        {update.PACKAGE_COL: "azure-mgmt-example"},
    ]
    monkeypatch.setattr(
        update,
        "get_package_path",
        lambda name: f"/repo/{name}",
    )

    def parse_setup(path: str) -> object:
        if path.endswith("azure-mgmt-trustedsigning"):
            raise FileNotFoundError("setup.py or pyproject.toml not found")
        return object()

    monkeypatch.setattr(update.ParsedSetup, "from_path", parse_setup)

    assert update.filter_packages_with_parseable_setup(packages) == [packages[1]]
