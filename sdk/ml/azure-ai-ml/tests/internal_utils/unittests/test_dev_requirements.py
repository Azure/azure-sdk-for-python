import sys
import subprocess
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

    @pytest.mark.skipif(sys.version_info < (3, 13), reason="Skipping because Python version is below 3.13")
    def test_package_not_installed_in_python_3_13(self):
        """Ensure azureml-dataprep-rslex is NOT installed in Python 3.13+."""
        assert not is_package_installed(PACKAGE_NAME), f"{PACKAGE_NAME} should not be installed in Python 3.13+"

    @pytest.mark.skipif(sys.version_info >= (3, 13), reason="Skipping because Python version is 3.13 or above")
    def test_package_installed_below_python_3_13(self):
        """Ensure azureml-dataprep-rslex IS installed in Python < 3.13."""
        assert is_package_installed(PACKAGE_NAME), f"{PACKAGE_NAME} should be installed in Python < 3.13"
