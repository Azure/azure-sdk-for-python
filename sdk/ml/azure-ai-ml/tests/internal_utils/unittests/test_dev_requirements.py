import platform
import subprocess
import sys

import pytest

PACKAGE_NAME = "azureml-dataprep-rslex"
IS_CPYTHON = platform.python_implementation() == "CPython"
IS_PYPY = platform.python_implementation() == "PyPy"


def is_package_installed(package_name):
    """Check if a package is installed in the current environment."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "show", package_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    return result.returncode == 0


@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestPackageInstallation:
    """Test class to validate package installation across Python versions and environments."""

    @pytest.mark.skipif(
        not (IS_CPYTHON and sys.version_info >= (3, 13)),
        reason="Skipping because environment is not >= cpython 3.13",
    )
    def test_package_not_installed_in_cpython_3_13(self):
        assert not is_package_installed(
            PACKAGE_NAME
        ), f"{PACKAGE_NAME} should not be installed in CPython 3.13 or above environment."

    @pytest.mark.skipif(
        not (IS_CPYTHON and sys.version_info < (3, 13)),
        reason="Skipping because environment is not below cpython 3.13",
    )
    def test_package_installed_below_cpython_3_13(self):
        assert is_package_installed(PACKAGE_NAME), f"{PACKAGE_NAME} should be installed in CPython < 3.13."

    @pytest.mark.skipif(
        not (IS_PYPY and sys.version_info >= (3, 10)),
        reason="Skipping because environment is not >= pypy 3.10",
    )
    def test_package_not_installed_in_pypy_3_10(self):
        assert not is_package_installed(
            PACKAGE_NAME
        ), f"{PACKAGE_NAME} should not be installed in PyPy 3.10 or above environment."

    @pytest.mark.skipif(
        not (IS_PYPY and sys.version_info < (3, 10)),
        reason="Skipping because environment is not below pypy 3.10",
    )
    def test_package_installed_below_pypy_3_10(self):
        assert is_package_installed(PACKAGE_NAME), f"{PACKAGE_NAME} should be installed in PyPy < 3.10 environment."
