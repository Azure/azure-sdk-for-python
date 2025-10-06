from pypi_tools.pypi import PyPIClient
from unittest.mock import patch
import os
import pytest
import pdb


class TestPyPiClient:
    @pytest.mark.skipif(
        os.environ.get("TF_BUILD", "None") == True,
        reason=f"This test isn't worth recording and could be flaky. Skipping in CI.",
    )
    def test_package_retrieve(self):
        client = PyPIClient()
        result = client.project("azure-core")

        # we won't _exhaustively_ check this, but we can sanity check a few proxy values to ensure we haven't broken anything
        assert result["info"]["name"] == "azure-core"
        assert len(result["releases"].keys()) > 47
        assert "1.25.1" in result["releases"]
        assert "1.10.0" in result["releases"]

    @pytest.mark.skipif(
        os.environ.get("TF_BUILD", "None") == True,
        reason=f"This test isn't worth recording and could be flaky. Skipping in CI.",
    )
    def test_package_version_retrieve(self):
        client = PyPIClient()
        result = client.project_release("azure-core", "1.8.0")

        assert result["info"]["name"] == "azure-core"
        assert result["info"]["release_url"] == "https://pypi.org/project/azure-core/1.8.0/"

    @patch("pypi_tools.pypi.sys")
    def test_package_filter_for_compatibility(self, mock_sys):
        mock_sys.version_info = (2, 7, 0)
        client = PyPIClient()
        result = client.get_ordered_versions("azure-core", True)
        unfiltered_results = client.get_ordered_versions("azure-core", False)

        assert len(result) < len(unfiltered_results)
