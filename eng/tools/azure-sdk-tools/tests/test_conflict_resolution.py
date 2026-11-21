from types import SimpleNamespace
from unittest.mock import patch
from tempfile import TemporaryDirectory

import pytest
from packaging.requirements import Requirement
from packaging.version import Version

from ci_tools.functions import handle_incompatible_minimum_dev_reqs, is_package_compatible


@pytest.mark.parametrize(
    "fake_package_input_requirements, immutable_requirements, expected_result",
    [
        ([Requirement("sphinx==1.0.0")], [Requirement("sphinx>=1.0.0")], True),
        ([Requirement("sphinx==1.0.0")], [Requirement("sphinx>=1.1.0")], False),
    ],
)
def test_incompatible_specifier(fake_package_input_requirements, immutable_requirements, expected_result):
    result = is_package_compatible("fake-package", fake_package_input_requirements, immutable_requirements)
    assert result == expected_result


@pytest.fixture
def incompatible_local_package():
    return SimpleNamespace(
        name="azure-identity",
        version="1.26.0",
        requires=["azure-core>=1.31.0"],
    )


def test_compatible_relative_requirement_stays_relative():
    local_package = SimpleNamespace(name="azure-identity", version="1.26.0", requires=["azure-core>=1.30.0"])
    with patch("ci_tools.functions.ParsedSetup.from_path", return_value=local_package):
        result = handle_incompatible_minimum_dev_reqs(
            "/repo/package",
            ["../identity/azure-identity\n"],
            [Requirement("azure-core==1.30.0")],
        )

    assert result == ["../identity/azure-identity"]


def test_incompatible_relative_requirement_uses_configured_index(incompatible_local_package):
    with patch("ci_tools.functions.ParsedSetup.from_path", return_value=incompatible_local_package), patch(
        "ci_tools.functions.PyPIClient.get_ordered_versions",
        return_value=[Version("1.17.1")],
    ) as get_versions:
        result = handle_incompatible_minimum_dev_reqs(
            "/repo/package",
            ["../identity/azure-identity\n"],
            [Requirement("azure-core==1.30.0")],
        )

    assert result == ["azure-identity"]
    get_versions.assert_called_once_with("azure-identity", True)


def test_incompatible_unpublished_relative_requirement_stays_relative(incompatible_local_package):
    with patch("ci_tools.functions.ParsedSetup.from_path", return_value=incompatible_local_package), patch(
        "ci_tools.functions.PyPIClient.get_ordered_versions",
        return_value=[],
    ):
        result = handle_incompatible_minimum_dev_reqs(
            "/repo/package",
            ["../identity/azure-identity\n"],
            [Requirement("azure-core==1.30.0")],
        )

    assert result == ["../identity/azure-identity"]


def test_incompatible_local_wheel_uses_configured_index(tmp_path):
    wheel_path = tmp_path / "azure_identity-1.26.0-py3-none-any.whl"
    wheel_path.touch()
    metadata = SimpleNamespace(
        name="azure-identity",
        version="1.26.0",
        requires_dist=["azure-core>=1.31.0"],
    )
    with patch("pkginfo.get_metadata", return_value=metadata), patch(
        "ci_tools.functions.PyPIClient.get_ordered_versions",
        return_value=[Version("1.17.1")],
    ):
        result = handle_incompatible_minimum_dev_reqs(
            "/repo/package",
            [str(wheel_path)],
            [Requirement("azure-core==1.30.0")],
        )

    assert result == ["azure-identity"]


def test_standard_requirement_is_unchanged():
    result = handle_incompatible_minimum_dev_reqs(
        "/repo/package",
        ["pytest>=8\n"],
        [Requirement("azure-core==1.30.0")],
    )

    assert result == ["pytest>=8\n"]
