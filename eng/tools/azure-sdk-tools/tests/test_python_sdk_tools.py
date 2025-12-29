from subprocess import CalledProcessError
import tempfile

import pytest


@pytest.mark.skip(reason="test for SDK team that should be manually activated")
def test_build_package_from_pr_number(github_token):
    from pathlib import Path
    from packaging_tools.drop_tools import build_package_from_pr_number

    # Should build package azure-mgmt-advisor 1.0.1
    with tempfile.TemporaryDirectory() as temp_dir:
        build_package_from_pr_number(github_token, "Azure/azure-sdk-for-python", 2417, temp_dir)
        temp_dir_path = Path(temp_dir)
        files = set(file.relative_to(temp_dir) for file in temp_dir_path.iterdir())
        assert files == {
            Path("azure_mgmt_iothubprovisioningservices-0.2.0-py2.py3-none-any.whl"),
            Path("azure-mgmt-iothubprovisioningservices-0.2.0.zip"),
        }

    # This PR is broken and can't be built: 2040
    with tempfile.TemporaryDirectory() as temp_dir, pytest.raises(CalledProcessError):
        build_package_from_pr_number(github_token, "Azure/azure-sdk-for-python", 2040, temp_dir)
