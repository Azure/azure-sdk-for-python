from pypi_tools.pypi import PyPIClient, retrieve_versions_from_pypi
from unittest.mock import patch
import os
import pytest
from packaging.version import Version


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SKIP_IN_CI = pytest.mark.skipif(
    os.environ.get("TF_BUILD", "None") == True,
    reason="Live network test — skipped in CI.",
)

PYPI_HOST = "https://pypi.org"
AZDO_FEED_URL = "https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple/"

WELL_KNOWN_PACKAGE = "azure-core"
WELL_KNOWN_VERSION = "1.8.0"  # old enough to always exist everywhere
MINIMUM_EXPECTED_VERSIONS = 47  # azure-core has *far* more than this


def _make_client(index_url: str) -> PyPIClient:
    """Create a PyPIClient whose backend is driven by *index_url*.

    Temporarily sets PIP_INDEX_URL so the constructor picks the right backend.
    """
    old = os.environ.get("PIP_INDEX_URL")
    try:
        if index_url:
            os.environ["PIP_INDEX_URL"] = index_url
        elif "PIP_INDEX_URL" in os.environ:
            del os.environ["PIP_INDEX_URL"]
        return PyPIClient()
    finally:
        if old is not None:
            os.environ["PIP_INDEX_URL"] = old
        elif "PIP_INDEX_URL" in os.environ:
            del os.environ["PIP_INDEX_URL"]


# ---------------------------------------------------------------------------
# Tests parametrized across backends
# ---------------------------------------------------------------------------


@pytest.fixture(params=[PYPI_HOST, AZDO_FEED_URL], ids=["pypi", "azdo"])
def client(request):
    return _make_client(request.param)


class TestGetOrderedVersions:
    """Covers the dominant call pattern: ~10 call-sites do get_ordered_versions()."""

    @SKIP_IN_CI
    def test_returns_sorted_version_objects(self, client):
        versions = client.get_ordered_versions(WELL_KNOWN_PACKAGE)
        assert len(versions) >= MINIMUM_EXPECTED_VERSIONS
        assert all(isinstance(v, Version) for v in versions)
        assert versions == sorted(versions)

    @SKIP_IN_CI
    def test_known_version_present(self, client):
        versions = client.get_ordered_versions(WELL_KNOWN_PACKAGE)
        version_strs = [str(v) for v in versions]
        assert WELL_KNOWN_VERSION in version_strs


class TestGetRelevantVersions:
    """Covers detect_breaking_changes.py usage of get_relevant_versions()."""

    @SKIP_IN_CI
    def test_returns_latest_and_latest_stable(self, client):
        latest, latest_stable = client.get_relevant_versions(WELL_KNOWN_PACKAGE)
        assert isinstance(latest, Version)
        assert isinstance(latest_stable, Version)
        assert not latest_stable.is_prerelease
        assert latest_stable <= latest


class TestRetrieveVersions:
    """Covers the convenience wrapper used by verify_sdist.py / verify_whl.py."""

    @SKIP_IN_CI
    @pytest.mark.parametrize("index_url", [PYPI_HOST, AZDO_FEED_URL], ids=["pypi", "azdo"])
    def test_retrieve_versions_returns_strings(self, index_url):
        old = os.environ.get("PIP_INDEX_URL")
        try:
            if index_url:
                os.environ["PIP_INDEX_URL"] = index_url
            versions = retrieve_versions_from_pypi(WELL_KNOWN_PACKAGE)
        finally:
            if old is not None:
                os.environ["PIP_INDEX_URL"] = old
            elif "PIP_INDEX_URL" in os.environ:
                del os.environ["PIP_INDEX_URL"]

        assert len(versions) >= MINIMUM_EXPECTED_VERSIONS
        assert all(isinstance(v, str) for v in versions)
        assert WELL_KNOWN_VERSION in versions


# ---------------------------------------------------------------------------
# project_release — works on both backends (AzDO falls back to pypi.org)
# ---------------------------------------------------------------------------


class TestProjectRelease:
    """Covers functions.py:888 usage of project_release() for requires_dist."""

    @SKIP_IN_CI
    def test_project_release_returns_version_info(self, client):
        result = client.project_release(WELL_KNOWN_PACKAGE, WELL_KNOWN_VERSION)

        assert result["info"]["name"] == WELL_KNOWN_PACKAGE
        assert result["info"]["release_url"] == f"https://pypi.org/project/{WELL_KNOWN_PACKAGE}/{WELL_KNOWN_VERSION}/"
        # requires_dist is what the mindep resolver reads
        assert "requires_dist" in result["info"]


# ---------------------------------------------------------------------------
# PyPI-only tests (project / filter_packages_for_compatibility)
# ---------------------------------------------------------------------------


class TestPyPIOnlyMethods:
    """Methods that only work against pypi.org JSON API.

    Callers: discover_unpublished_packages.py, output_old_packages.py.
    """

    @SKIP_IN_CI
    def test_project_returns_info_and_releases(self):
        client = _make_client(PYPI_HOST)
        result = client.project(WELL_KNOWN_PACKAGE)

        assert result["info"]["name"] == WELL_KNOWN_PACKAGE
        assert len(result["releases"]) > MINIMUM_EXPECTED_VERSIONS
        assert "1.25.1" in result["releases"]
        assert WELL_KNOWN_VERSION in result["releases"]

    @SKIP_IN_CI
    @patch("pypi_tools.pypi.sys")
    def test_filter_packages_for_compatibility(self, mock_sys):
        mock_sys.version_info = (2, 7, 0)
        client = _make_client(PYPI_HOST)
        filtered = client.get_ordered_versions(WELL_KNOWN_PACKAGE, True)
        unfiltered = client.get_ordered_versions(WELL_KNOWN_PACKAGE, False)
        assert len(filtered) < len(unfiltered)
