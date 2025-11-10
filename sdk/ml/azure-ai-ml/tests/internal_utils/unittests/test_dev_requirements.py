import platform
import subprocess
import sys

import pytest

PACKAGE_NAME = "azureml-dataprep-rslex"


def is_package_installed(package_name):
    """Check if a package is installed in the current environment."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "show", package_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    return result.returncode == 0


@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestPackageInstallation:
    """Test class to validate package installation across Python versions."""

    @pytest.mark.skipif(
        sys.version_info < (3, 13) and platform.python_implementation() != "PyPy",
        reason="Skipping because Python version is below 3.13 and environment is not PyPy",
    )
    def test_package_not_installed_in_unsupported_environment(self):
        """Ensure azureml-dataprep-rslex is NOT installed in Python 3.13+ or PyPy environment."""
        assert not is_package_installed(
            PACKAGE_NAME
        ), f"{PACKAGE_NAME} should not be installed in Python 3.13+ or PyPy environment."

    @pytest.mark.skipif(
        sys.version_info >= (3, 13) or platform.python_implementation() == "PyPy",
        reason="Skipping because Python version is 3.13 or above or environment is PyPy",
    )
    def test_package_installed_in_supported_environment(self):
        """Ensure azureml-dataprep-rslex IS installed in Python < 3.13 and not PyPy environment."""
        assert is_package_installed(
            PACKAGE_NAME
        ), f"{PACKAGE_NAME} should be installed in Python < 3.13 and not PyPy environment."
