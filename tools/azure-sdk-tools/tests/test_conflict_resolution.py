import pytest

from unittest.mock import patch
from tempfile import TemporaryDirectory
from ci_tools.functions import resolve_compatible_package, is_package_compatible
from typing import Optional, List
from packaging.version import Version
from pkg_resources import Requirement


@pytest.mark.parametrize(
    "fake_package_input_requirements, immutable_requirements, expected_result",
    [([Requirement("sphinx==1.0.0")], [Requirement("sphinx>=1.0.0")], True),
     ([Requirement("sphinx==1.0.0")], [Requirement("sphinx>=1.1.0")], False)],
)
def test_incompatible_specifier(fake_package_input_requirements, immutable_requirements, expected_result):
    result = is_package_compatible("fake-package", fake_package_input_requirements, immutable_requirements)
    assert result == expected_result


def test_identity_resolution():
    result = resolve_compatible_package(
        "azure-identity",
        [Requirement("azure-core>=1.28.0"), Requirement("isodate>=0.6.1"), Requirement("typing-extensions>=4.0.1")],
    )
    assert result == "azure-identity==1.16.0"


def test_resolution_no_requirement():
    result = resolve_compatible_package(
        "azure-identity",
        [Requirement("azure-core")],
    )
    assert result == "azure-identity==1.19.0"
