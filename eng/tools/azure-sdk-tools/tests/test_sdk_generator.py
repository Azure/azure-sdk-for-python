import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch


MODULE = "packaging_tools.sdk_generator"


@pytest.fixture
def io_paths():
    """Create temp input/output JSON files and clean up after test."""
    tmp_dir = tempfile.mkdtemp()
    input_path = str(Path(tmp_dir) / "input.json")
    output_path = str(Path(tmp_dir) / "output.json")
    yield input_path, output_path
    shutil.rmtree(tmp_dir)


def _write_input(path, data):
    with open(path, "w") as f:
        json.dump(data, f)


def _read_output(path):
    with open(path, "r") as f:
        return json.load(f)


# ── helpers for the heavy mocking needed by main() ──────────────────────


def _common_patches():
    """Return a dict of patch targets used by most tests."""
    return {
        "gen_typespec": patch(f"{MODULE}.gen_typespec", return_value=None),
        "gen_dpg": patch(f"{MODULE}.gen_dpg", return_value=None),
        "generate": patch(f"{MODULE}.generate", return_value=None),
        "get_package_names": patch(f"{MODULE}.get_package_names"),
        "judge_tag_preview": patch(f"{MODULE}.judge_tag_preview"),
        "format_samples_and_tests": patch(f"{MODULE}.format_samples_and_tests"),
        "check_call": patch(f"{MODULE}.check_call"),
        "sdk_changelog_generate": patch(f"{MODULE}.sdk_changelog_generate"),
        "sdk_update_version": patch(f"{MODULE}.sdk_update_version"),
        "sdk_update_metadata": patch(f"{MODULE}.sdk_update_metadata"),
        "create_package": patch(f"{MODULE}.create_package"),
        "check_file": patch(f"{MODULE}.check_file"),
        "del_outdated_generated_files": patch(f"{MODULE}.del_outdated_generated_files"),
        "del_outdated_files": patch(f"{MODULE}.del_outdated_files"),
    }


class TestTagIsStableForTypeSpec:
    """Tests for the tagIsStable logic change: TypeSpec projects use sdkReleaseType,
    while Swagger projects still use judge_tag_preview."""

    def _run_main(self, input_path, output_path, input_data, package_names, judge_return=False):
        """Helper that wires up all the mocks and calls main()."""
        _write_input(input_path, input_data)

        patches = _common_patches()
        mocks = {name: p.start() for name, p in patches.items()}

        # get_package_names returns our controlled list
        mocks["get_package_names"].return_value = package_names
        mocks["judge_tag_preview"].return_value = judge_return

        # create_package needs a dist folder with a .whl
        def fake_create_package(folder, pkg):
            # Use a temporary base directory to avoid polluting the repo workspace
            base_dir = Path(tempfile.mkdtemp())
            dist = base_dir / folder / pkg / "dist"
            dist.mkdir(parents=True, exist_ok=True)
            (dist / f"{pkg}-0.0.0-py3-none-any.whl").touch()

        mocks["create_package"].side_effect = fake_create_package

        try:
            from packaging_tools.sdk_generator import main

            main(input_path, output_path)
        finally:
            for p in patches.values():
                p.stop()

        return _read_output(output_path)

    # ── TypeSpec: sdkReleaseType == "stable" → tagIsStable = True ────

    def test_typespec_stable_release_type(self, io_paths):
        input_path, output_path = io_paths
        input_data = {
            "specFolder": "spec",
            "headSha": "abc123",
            "repoHttpsUrl": "https://github.com/test/repo",
            "relatedTypeSpecProjectFolder": ["Microsoft.Test/stable"],
            "sdkReleaseType": "stable",
        }
        result = self._run_main(
            input_path,
            output_path,
            input_data,
            package_names=[("sdk/test", "azure-mgmt-test")],
        )
        pkg = result["packages"][0]
        assert pkg["tagIsStable"] is True

    # ── TypeSpec: sdkReleaseType == "preview" → tagIsStable = False ──

    def test_typespec_preview_release_type(self, io_paths):
        input_path, output_path = io_paths
        input_data = {
            "specFolder": "spec",
            "headSha": "abc123",
            "repoHttpsUrl": "https://github.com/test/repo",
            "relatedTypeSpecProjectFolder": ["Microsoft.Test/preview"],
            "sdkReleaseType": "preview",
        }
        result = self._run_main(
            input_path,
            output_path,
            input_data,
            package_names=[("sdk/test", "azure-mgmt-test")],
        )
        pkg = result["packages"][0]
        assert pkg["tagIsStable"] is False

    # ── TypeSpec: sdkReleaseType missing → tagIsStable = False ───────

    def test_typespec_no_release_type(self, io_paths):
        input_path, output_path = io_paths
        input_data = {
            "specFolder": "spec",
            "headSha": "abc123",
            "repoHttpsUrl": "https://github.com/test/repo",
            "relatedTypeSpecProjectFolder": ["Microsoft.Test/preview"],
            # no sdkReleaseType key
        }
        result = self._run_main(
            input_path,
            output_path,
            input_data,
            package_names=[("sdk/test", "azure-mgmt-test")],
        )
        pkg = result["packages"][0]
        assert pkg["tagIsStable"] is False

    # ── Swagger: tagIsStable delegates to judge_tag_preview ──────────

    def test_swagger_stable_by_judge(self, io_paths):
        """When judge_tag_preview returns False (not preview), tagIsStable should be True."""
        input_path, output_path = io_paths
        input_data = {
            "specFolder": "spec",
            "relatedReadmeMdFiles": ["specification/test/resource-manager/readme.md"],
            "sdkReleaseType": "stable",
        }
        result = self._run_main(
            input_path,
            output_path,
            input_data,
            package_names=[("sdk/test", "azure-mgmt-test")],
            judge_return=False,  # not preview → tagIsStable = True
        )
        pkg = result["packages"][0]
        assert pkg["tagIsStable"] is True

    def test_swagger_preview_by_judge(self, io_paths):
        """When judge_tag_preview returns True (preview), tagIsStable should be False,
        regardless of sdkReleaseType."""
        input_path, output_path = io_paths
        input_data = {
            "specFolder": "spec",
            "relatedReadmeMdFiles": ["specification/test/resource-manager/readme.md"],
            "sdkReleaseType": "stable",  # even though release type says "stable"
        }
        result = self._run_main(
            input_path,
            output_path,
            input_data,
            package_names=[("sdk/test", "azure-mgmt-test")],
            judge_return=True,  # preview → tagIsStable = False
        )
        pkg = result["packages"][0]
        assert pkg["tagIsStable"] is False


class TestExtractSdkFolder:
    def test_extracts_folder(self):
        from packaging_tools.sdk_generator import extract_sdk_folder

        lines = [
            "``` yaml $(python)\n",
            "  output-folder: $(python-sdks-folder)/network/azure-mgmt-network\n",
            "```\n",
        ]
        assert extract_sdk_folder(lines) == "network/azure-mgmt-network"

    def test_returns_empty_when_no_match(self):
        from packaging_tools.sdk_generator import extract_sdk_folder

        lines = ["some random line\n"]
        assert extract_sdk_folder(lines) == ""


class TestGetReadmePythonContent:
    def test_returns_content_when_file_exists(self, tmp_path):
        from packaging_tools.sdk_generator import get_readme_python_content

        readme = tmp_path / "readme.md"
        readme.touch()
        python_readme = tmp_path / "readme.python.md"
        python_readme.write_text("line1\nline2\n")

        result = get_readme_python_content(str(readme))
        assert len(result) == 2
        assert "line1\n" in result

    def test_returns_empty_when_no_python_readme(self, tmp_path):
        from packaging_tools.sdk_generator import get_readme_python_content

        readme = tmp_path / "readme.md"
        readme.touch()

        result = get_readme_python_content(str(readme))
        assert result == []
