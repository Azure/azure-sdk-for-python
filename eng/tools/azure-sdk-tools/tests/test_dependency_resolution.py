import subprocess
from unittest.mock import patch

import pytest
from packaging.version import Version

from ci_tools.scenario.dependency_resolution import install_packages, process_requirement


def test_minimum_selects_oldest_compatible_index_version():
    with patch(
        "ci_tools.scenario.dependency_resolution.PyPIClient.get_ordered_versions",
        return_value=[Version("1.0.0"), Version("1.1.0"), Version("2.0.0")],
    ) as get_versions:
        result = process_requirement("example-dependency>=1.1.0", "Minimum", "example-package")

    assert result == "example-dependency==1.1.0"
    get_versions.assert_called_once_with("example-dependency", True)


def test_latest_selects_newest_compatible_index_version():
    with patch(
        "ci_tools.scenario.dependency_resolution.PyPIClient.get_ordered_versions",
        return_value=[Version("1.0.0"), Version("1.1.0"), Version("2.0.0")],
    ):
        result = process_requirement("example-dependency>=1.1.0", "Latest", "example-package")

    assert result == "example-dependency==2.0.0"


def test_prerelease_is_excluded_unless_requirement_allows_it():
    versions = [Version("1.0.0"), Version("2.0.0b1")]
    with patch(
        "ci_tools.scenario.dependency_resolution.PyPIClient.get_ordered_versions",
        return_value=versions,
    ):
        stable_result = process_requirement("example-dependency>=1.0.0", "Latest", "example-package")
        preview_result = process_requirement("example-dependency>=1.0.0b1", "Latest", "example-package")

    assert stable_result == "example-dependency==1.0.0"
    assert preview_result == "example-dependency==2.0.0b1"


def test_install_passes_exact_pins_and_requirement_file_in_one_uv_command():
    with patch(
        "ci_tools.scenario.dependency_resolution.get_pip_command",
        return_value=["uv", "pip"],
    ), patch("ci_tools.scenario.dependency_resolution.subprocess.check_call") as check_call:
        install_packages(
            ["azure-core==1.30.0"],
            "/tmp/new_dev_requirements.txt",
            "/tmp/python",
            cwd="/repo/package",
        )

    check_call.assert_called_once_with(
        [
            "uv",
            "pip",
            "install",
            "--python",
            "/tmp/python",
            "azure-core==1.30.0",
            "-r",
            "/tmp/new_dev_requirements.txt",
        ],
        cwd="/repo/package",
    )


def test_unsatisfiable_install_propagates_resolver_failure():
    failure = subprocess.CalledProcessError(1, ["uv", "pip", "install"])
    with patch(
        "ci_tools.scenario.dependency_resolution.get_pip_command",
        return_value=["uv", "pip"],
    ), patch(
        "ci_tools.scenario.dependency_resolution.subprocess.check_call",
        side_effect=failure,
    ):
        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            install_packages(
                ["azure-core==1.30.0"],
                "/tmp/new_dev_requirements.txt",
                "/tmp/python",
            )

    assert exc_info.value is failure
