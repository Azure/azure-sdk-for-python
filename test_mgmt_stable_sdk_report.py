from pathlib import Path

import mgmt_stable_sdk_report as report


def test_get_candidate_sdk_names_includes_supplemental_candidates(monkeypatch):
    files = {
        "data.txt": "azure-mgmt-domainservices azure-mgmt-existing\n",
        "result.md": "| a | b | c | azure-mgmt-result |\n",
    }

    monkeypatch.setattr(report, "fetch_pr_file", lambda pr_number, file_name: files[file_name])

    names = report.get_candidate_sdk_names("123")

    assert names == [
        "azure-mgmt-result",
        "azure-mgmt-domainservices",
        "azure-mgmt-existing",
        "azure-mgmt-alertprocessingrules",
        "azure-mgmt-prometheusrulegroups",
    ]


def _write_package(root: Path, service: str, name: str, version: str, release_date: str) -> None:
    package_dir = root / "sdk" / service / name
    package_dir.mkdir(parents=True)
    (package_dir / "tsp-location.yaml").write_text("directory: .\n", encoding="utf-8")
    (package_dir / "_metadata.json").write_text('{"apiVersions": ["2025-01-01"]}\n', encoding="utf-8")
    (package_dir / "CHANGELOG.md").write_text(f"## {version} ({release_date})\n", encoding="utf-8")


def test_build_rows_skips_beta_sdk_when_last_release_date_is_before_cutoff(tmp_path, monkeypatch):
    monkeypatch.setattr(report, "ROOT", tmp_path)
    _write_package(tmp_path, "old", "azure-mgmt-old", "1.0.0b1", "2025-12-31")
    _write_package(tmp_path, "current", "azure-mgmt-current", "1.0.0b1", "2026-01-01")

    rows = report.build_rows(["azure-mgmt-old", "azure-mgmt-current"])

    assert [row.name for row in rows] == ["azure-mgmt-current"]


def test_build_rows_skips_stable_sdk_because_stable_release_is_already_done(tmp_path, monkeypatch):
    monkeypatch.setattr(report, "ROOT", tmp_path)
    monkeypatch.setattr(report, "find_refresh_pr", lambda package_dir: "123")
    _write_package(tmp_path, "done", "azure-mgmt-done", "1.0.0", "2026-02-01")
    _write_package(tmp_path, "candidate", "azure-mgmt-candidate", "1.0.0b1", "2026-02-01")

    rows = report.build_rows(["azure-mgmt-done", "azure-mgmt-candidate"])

    assert [row.name for row in rows] == ["azure-mgmt-candidate"]