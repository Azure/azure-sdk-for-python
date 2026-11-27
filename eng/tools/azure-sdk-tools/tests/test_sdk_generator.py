import pytest
import json
import tempfile
import shutil
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import call, patch


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
        "update_api_versions_in_changelog": patch(f"{MODULE}.update_api_versions_in_changelog"),
        "create_package": patch(f"{MODULE}.create_package"),
        "check_file": patch(f"{MODULE}.check_file"),
        "del_outdated_generated_files": patch(f"{MODULE}.del_outdated_generated_files"),
        "del_outdated_files": patch(f"{MODULE}.del_outdated_files"),
    }


def _run_main(
    input_path,
    output_path,
    input_data,
    package_names,
    judge_return=False,
    expected_create_package_calls=None,
    changelog_side_effect=None,
):
    """Helper that wires up all the mocks and calls main()."""
    _write_input(input_path, input_data)

    patches = _common_patches()
    mocks = {name: p.start() for name, p in patches.items()}

    # get_package_names returns our controlled list
    mocks["get_package_names"].return_value = package_names
    mocks["judge_tag_preview"].return_value = judge_return
    mocks["sdk_changelog_generate"].side_effect = changelog_side_effect

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
        if expected_create_package_calls is not None:
            mocks["create_package"].assert_has_calls(expected_create_package_calls, any_order=True)
    finally:
        for p in patches.values():
            p.stop()

    return _read_output(output_path)


@pytest.mark.parametrize("enable_changelog", [True, False])
def test_api_version_disclosure_uses_final_metadata_before_build(tmp_path, io_paths, enable_changelog):
    from packaging_tools.sdk_changelog import update_api_versions_in_changelog
    from packaging_tools.sdk_generator import main

    input_path, output_path = io_paths
    package_path = tmp_path / "azure-mgmt-test"
    package_path.mkdir()
    changelog = package_path / "CHANGELOG.md"
    metadata = package_path / "_metadata.json"
    dist = package_path / "dist"
    dist.mkdir()
    (dist / "test.whl").touch()
    events = []
    diff = "### Bugs Fixed\n\n- Fixed a bug.\n"

    def generate_changelog(path, *, package_result, **kwargs):
        events.append("changelog")
        assert kwargs["enable_changelog"] is enable_changelog
        changelog.write_text("# Release History\n\n## 0.0.0 (Unreleased)\n\n" + diff)
        package_result["changelog"] = {"content": diff, "hasBreakingChange": False, "breakingChangeItems": []}
        package_result["version"] = "1.0.0"

    def update_version(path, *, package_result):
        events.append("version")
        assert package_result["changelog"]["content"] == diff
        assert "Package API versions:" not in changelog.read_text()
        package_result["version"] = "1.0.1"
        changelog.write_text(changelog.read_text().replace("0.0.0", "1.0.1"))

    def update_metadata(*args, **kwargs):
        events.append("metadata")
        metadata.write_text(json.dumps({"apiVersions": {"Test": "2025-01-01"}}))

    def post_emitter(*args):
        events.append("post-emitter")
        metadata.write_text(json.dumps({"apiVersions": {"Test": "2026-01-01"}}))

    def build(*args):
        events.append("build")
        assert "### Features Added\n\n- Package API versions: Test: `2026-01-01`.\n" in changelog.read_text()
        assert "2025-01-01" not in changelog.read_text()

    _write_input(
        input_path,
        {
            "relatedTypeSpecProjectFolder": ["Microsoft.Test/Test.Management"],
            "headSha": "abc123",
            "repoHttpsUrl": "https://github.com/Azure/azure-rest-api-specs",
            "enableChangelog": enable_changelog,
        },
    )
    with ExitStack() as stack:
        mocks = {name: stack.enter_context(patch_context) for name, patch_context in _common_patches().items()}
        mocks["get_package_names"].return_value = [(str(tmp_path), package_path.name)]
        mocks["sdk_changelog_generate"].side_effect = generate_changelog
        mocks["sdk_update_version"].side_effect = update_version
        mocks["sdk_update_metadata"].side_effect = update_metadata
        mocks["update_api_versions_in_changelog"].side_effect = update_api_versions_in_changelog
        mocks["create_package"].side_effect = build
        stack.enter_context(patch(f"{MODULE}.run_post_emitter_script", side_effect=post_emitter))

        main(input_path, output_path)

    package = _read_output(output_path)["packages"][0]
    assert events == ["changelog", "version", "metadata", "post-emitter", "build"]
    assert package["version"] == "1.0.1"
    assert package["changelog"]["content"] == diff


@pytest.mark.parametrize("sdk_release_type", ["preview", "stable"])
@pytest.mark.parametrize(
    "releases, expected_breaking",
    [
        pytest.param({"1.0.0b1": [{}]}, False, id="preview-only"),
        pytest.param({}, False, id="unpublished"),
        pytest.param({"1.0.0": [{}], "2.0.0b1": [{}]}, True, id="prior-ga"),
    ],
)
def test_generation_output_uses_published_ga_history(io_paths, tmp_path, sdk_release_type, releases, expected_breaking):
    from packaging_tools.sdk_changelog import main as changelog_main

    input_path, output_path = io_paths
    package_path = tmp_path / "azure-mgmt-test"
    package_path.mkdir()
    changelog_path = package_path / "CHANGELOG.md"
    changelog_path.write_text("# Release History\n\n")
    md_output = "### Breaking Changes\n\n  - dropped bar\n"

    with (
        patch("packaging_tools.sdk_changelog.get_changelog_content", return_value=(md_output, "1.0.0b1")),
        patch("pypi_tools.pypi.PyPIClient.project", return_value={"releases": releases}),
    ):
        result = _run_main(
            input_path,
            output_path,
            {
                "specFolder": "spec",
                "headSha": "abc123",
                "repoHttpsUrl": "https://github.com/test/repo",
                "relatedTypeSpecProjectFolder": ["Microsoft.Test/Test.Management"],
                "sdkReleaseType": sdk_release_type,
                "runMode": "spec-pull-request",
            },
            package_names=[(str(tmp_path), package_path.name)],
            changelog_side_effect=changelog_main,
        )

    package = result["packages"][0]
    assert package["tagIsStable"] is (sdk_release_type == "stable")
    assert package["changelog"] == {
        "content": md_output,
        "hasBreakingChange": expected_breaking,
        "breakingChangeItems": ["dropped bar"],
    }
    assert md_output in changelog_path.read_text()


class TestTagIsStableForTypeSpec:
    """Tests for the tagIsStable logic change: TypeSpec projects use sdkReleaseType,
    while Swagger projects still use judge_tag_preview."""

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
        result = _run_main(
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
        result = _run_main(
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
        result = _run_main(
            input_path,
            output_path,
            input_data,
            package_names=[("sdk/test", "azure-mgmt-test")],
            judge_return=True,  # preview package → tagIsStable = False
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
        result = _run_main(
            input_path,
            output_path,
            input_data,
            package_names=[("sdk/test", "azure-mgmt-test")],
            judge_return=False,  # not preview → tagIsStable = True
        )
        pkg = result["packages"][0]
        assert pkg["tagIsStable"] is True

    def test_swagger_preview_by_sdk_release_type(self, io_paths):
        input_path, output_path = io_paths
        input_data = {
            "specFolder": "spec",
            "relatedReadmeMdFiles": ["specification/test/resource-manager/readme.md"],
            "sdkReleaseType": "stable",
        }
        result = _run_main(
            input_path,
            output_path,
            input_data,
            package_names=[("sdk/test", "azure-mgmt-test")],
            judge_return=True,  # preview → tagIsStable = False
        )
        pkg = result["packages"][0]
        assert pkg["tagIsStable"] is True


class TestPackagePaths:
    def test_reports_package_source_root(self, io_paths):
        input_path, output_path = io_paths
        result = _run_main(
            input_path,
            output_path,
            {
                "specFolder": "spec",
                "headSha": "abc123",
                "repoHttpsUrl": "https://github.com/test/repo",
                "relatedTypeSpecProjectFolder": ["Microsoft.DevTestLab/DevTestLab.Management"],
            },
            package_names=[("sdk/devtestlabs", "azure-mgmt-devtestlabs")],
            expected_create_package_calls=[call("sdk/devtestlabs", "azure-mgmt-devtestlabs")],
        )

        assert result["packages"][0]["path"] == ["sdk/devtestlabs/azure-mgmt-devtestlabs"]

    def test_reports_distinct_roots_for_packages_in_same_service(self, io_paths):
        input_path, output_path = io_paths
        result = _run_main(
            input_path,
            output_path,
            {
                "specFolder": "spec",
                "headSha": "abc123",
                "repoHttpsUrl": "https://github.com/test/repo",
                "relatedTypeSpecProjectFolder": ["Microsoft.ServiceFabric/ServiceFabric.Management"],
            },
            package_names=[
                ("sdk/servicefabric", "azure-servicefabric"),
                ("sdk/servicefabric", "azure-mgmt-servicefabric"),
            ],
            expected_create_package_calls=[
                call("sdk/servicefabric", "azure-servicefabric"),
                call("sdk/servicefabric", "azure-mgmt-servicefabric"),
            ],
        )

        package_paths = {package["packageName"]: package["path"] for package in result["packages"]}
        assert package_paths == {
            "azure-servicefabric": ["sdk/servicefabric/azure-servicefabric"],
            "azure-mgmt-servicefabric": ["sdk/servicefabric/azure-mgmt-servicefabric"],
        }


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
