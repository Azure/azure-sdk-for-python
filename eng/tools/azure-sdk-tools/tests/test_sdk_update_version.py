import tempfile
import shutil
import time
from pathlib import Path

from packaging_tools.sdk_update_version import main as update_version_main


def test_preview_to_stable_version_update():
    temp_dir = tempfile.mkdtemp()
    try:
        package_path = Path(temp_dir)

        # seed version file
        version_file = package_path / "_version.py"
        version_file.write_text('VERSION = "1.0.0b2"\n')

        # seed changelog
        changelog = package_path / "CHANGELOG.md"
        changelog.write_text("## 1.0.0b2 (Unreleased)\n\n### Features\n\n- Something\n")

        package_result = {
            "version": "1.0.0b2",
            "tagIsStable": True,
            "changelog": {"content": "### Features"},
        }

        update_version_main(package_path, package_result=package_result)

        # version file updated to stable
        assert 'VERSION = "1.0.0"' in version_file.read_text()

        # changelog first line updated
        first_line = changelog.read_text().splitlines()[0]
        assert first_line.startswith("## 1.0.0 (")
    finally:
        shutil.rmtree(temp_dir)


def test_initial_version_generated():
    temp_dir = tempfile.mkdtemp()
    try:
        pkg = Path(temp_dir)
        (pkg / "_version.py").write_text('VERSION = "0.0.0"\n')
        (pkg / "CHANGELOG.md").write_text("## 0.0.0 (Unreleased)\n\n### Features\n")
        package_result = {"version": "", "tagIsStable": False, "changelog": {"content": "### Features"}}
        update_version_main(pkg, package_result=package_result)
        assert 'VERSION = "1.0.0b1"' in (pkg / "_version.py").read_text()
        assert (pkg / "CHANGELOG.md").read_text().splitlines()[0].startswith("## 1.0.0b1 (")
    finally:
        shutil.rmtree(temp_dir)


def test_bugfix_increments_patch_beta():
    temp_dir = tempfile.mkdtemp()
    try:
        pkg = Path(temp_dir)
        (pkg / "_version.py").write_text('VERSION = "1.0.0"\n')
        (pkg / "CHANGELOG.md").write_text("## 1.0.0 (Unreleased)\n\n### Bugs Fixed\n- Fix\n")
        package_result = {"version": "1.0.0", "tagIsStable": False, "changelog": {"content": "### Bugs Fixed"}}
        update_version_main(pkg, package_result=package_result)
        assert 'VERSION = "1.0.1b1"' in (pkg / "_version.py").read_text()
        assert (pkg / "CHANGELOG.md").read_text().splitlines()[0].startswith("## 1.0.1b1 (")
    finally:
        shutil.rmtree(temp_dir)


def test_preview_increments_beta_counter():
    temp_dir = tempfile.mkdtemp()
    try:
        pkg = Path(temp_dir)
        (pkg / "_version.py").write_text('VERSION = "1.2.0b3"\n')
        (pkg / "CHANGELOG.md").write_text("## 1.2.0b3 (Unreleased)\n\n### Features\n")
        package_result = {"version": "1.2.0b3", "tagIsStable": False, "changelog": {"content": "### Features"}}
        update_version_main(pkg, package_result=package_result)
        assert 'VERSION = "1.2.0b4"' in (pkg / "_version.py").read_text()
        assert (pkg / "CHANGELOG.md").read_text().splitlines()[0].startswith("## 1.2.0b4 (")
    finally:
        shutil.rmtree(temp_dir)


def test_breaking_change_increments_major_beta():
    temp_dir = tempfile.mkdtemp()
    try:
        pkg = Path(temp_dir)
        (pkg / "_version.py").write_text('VERSION = "1.4.2"\n')
        (pkg / "CHANGELOG.md").write_text("## 1.4.2 (Unreleased)\n\n### Breaking Changes\n- Remove X\n")
        package_result = {"version": "1.4.2", "tagIsStable": False, "changelog": {"content": "### Breaking Changes"}}
        update_version_main(pkg, package_result=package_result)
        assert 'VERSION = "2.0.0b1"' in (pkg / "_version.py").read_text()
        assert (pkg / "CHANGELOG.md").read_text().splitlines()[0].startswith("## 2.0.0b1 (")
    finally:
        shutil.rmtree(temp_dir)


def test_feature_change_increments_minor_beta():
    temp_dir = tempfile.mkdtemp()
    try:
        pkg = Path(temp_dir)
        (pkg / "_version.py").write_text('VERSION = "1.4.2"\n')
        (pkg / "CHANGELOG.md").write_text("## 1.4.2 (Unreleased)\n\n### Features\n- Add Y\n")
        package_result = {"version": "1.4.2", "tagIsStable": False, "changelog": {"content": "### Features"}}
        update_version_main(pkg, package_result=package_result)
        assert 'VERSION = "1.5.0b1"' in (pkg / "_version.py").read_text()
        assert (pkg / "CHANGELOG.md").read_text().splitlines()[0].startswith("## 1.5.0b1 (")
    finally:
        shutil.rmtree(temp_dir)


def test_initial_version_generated_without_package_result():
    # Ensure code path works when package_result is None (falsy)
    temp_dir = tempfile.mkdtemp()
    try:
        pkg = Path(temp_dir)
        (pkg / "_version.py").write_text('VERSION = "0.0.0"\n')
        (pkg / "CHANGELOG.md").write_text("## 0.0.0 (Unreleased)\n\n### Features\n")
        # Call without a package_result dict to exercise else branch logic
        update_version_main(pkg)  # type: ignore[arg-type]
        # Should compute first preview version
        assert 'VERSION = "1.0.0b1"' in (pkg / "_version.py").read_text()
        assert (pkg / "CHANGELOG.md").read_text().splitlines()[0].startswith("## 1.0.0b1 (")
    finally:
        shutil.rmtree(temp_dir)


def test_explicit_version_and_release_date_used():
    temp_dir = tempfile.mkdtemp()
    try:
        pkg = Path(temp_dir)
        (pkg / "_version.py").write_text('VERSION = "0.0.0"\n')
        (pkg / "CHANGELOG.md").write_text("## 0.0.0 (Unreleased)\n\n### Features\n")
        desired_version = "2.3.4b5"
        desired_date = "2025-02-15"
        update_version_main(pkg, version=desired_version, release_date=desired_date, release_type="beta")
        assert f'VERSION = "{desired_version}"' in (pkg / "_version.py").read_text()
        first_line = (pkg / "CHANGELOG.md").read_text().splitlines()[0]
        assert first_line == f"## {desired_version} ({desired_date})"  # exact match
    finally:
        shutil.rmtree(temp_dir)


def test_invalid_version_format_fallbacks_to_calculated():
    temp_dir = tempfile.mkdtemp()
    try:
        pkg = Path(temp_dir)
        (pkg / "_version.py").write_text('VERSION = "0.0.0"\n')
        (pkg / "CHANGELOG.md").write_text("## 0.0.0 (Unreleased)\n\n### Features\n")
        # Provide invalid version string; should be ignored and computed as 1.0.0b1
        update_version_main(pkg, version="v1.0.0", release_type="beta")
        assert 'VERSION = "1.0.0b1"' in (pkg / "_version.py").read_text()
        first_line = (pkg / "CHANGELOG.md").read_text().splitlines()[0]
        assert first_line.startswith("## 1.0.0b1 (")
    finally:
        shutil.rmtree(temp_dir)


def test_invalid_release_type_defaults_to_beta_flow():
    temp_dir = tempfile.mkdtemp()
    try:
        pkg = Path(temp_dir)
        (pkg / "_version.py").write_text('VERSION = "0.0.0"\n')
        (pkg / "CHANGELOG.md").write_text("## 0.0.0 (Unreleased)\n\n### Features\n")
        # release_type invalid; treated as beta; initial version should be computed preview
        update_version_main(pkg, release_type="foo")
        assert 'VERSION = "1.0.0b1"' in (pkg / "_version.py").read_text()
        first_line = (pkg / "CHANGELOG.md").read_text().splitlines()[0]
        assert first_line.startswith("## 1.0.0b1 (")
    finally:
        shutil.rmtree(temp_dir)


def test_invalid_release_date_uses_current_date():
    temp_dir = tempfile.mkdtemp()
    try:
        pkg = Path(temp_dir)
        (pkg / "_version.py").write_text('VERSION = "0.0.0"\n')
        (pkg / "CHANGELOG.md").write_text("## 0.0.0 (Unreleased)\n\n### Features\n")
        today = time.strftime("%Y-%m-%d", time.localtime())
        # Provide invalid release_date; should fall back to today's date
        update_version_main(pkg, release_date="13-2025-11")
        first_line = (pkg / "CHANGELOG.md").read_text().splitlines()[0]
        assert first_line.startswith("## 1.0.0b1 ("), "Expected computed version line"
        assert today in first_line, f"Expected fallback date {today} in changelog line"
    finally:
        shutil.rmtree(temp_dir)

