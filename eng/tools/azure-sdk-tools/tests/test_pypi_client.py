from pypi_tools.pypi import PyPIClient, retrieve_versions_from_pypi
from pypi_tools.azdo import AzureArtifactsClient, AzureArtifactsFeedConfig
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


class TestGetLatestDownloadUri:
    """Covers latest sdist URL resolution without relying on live package indexes."""

    def test_pypi_backend_uses_latest_stable_by_default(self):
        project_data = {
            "info": {"version": "2.0.0b1"},
            "releases": {
                "1.0.0": [
                    {
                        "packagetype": "sdist",
                        "url": "https://example.test/pkg-1.0.0.tar.gz",
                    }
                ],
                "2.0.0b1": [
                    {
                        "packagetype": "sdist",
                        "url": "https://example.test/pkg-2.0.0b1.tar.gz",
                    }
                ],
            },
        }
        client = _make_client(PYPI_HOST)

        with patch.object(PyPIClient, "project", return_value=project_data):
            version, url = client.get_latest_download_uri("example-pkg")

        assert version == "1.0.0"
        assert url == "https://example.test/pkg-1.0.0.tar.gz"

    def test_pypi_backend_can_return_latest_prerelease(self):
        project_data = {
            "info": {"version": "2.0.0b1"},
            "releases": {
                "1.0.0": [
                    {
                        "packagetype": "sdist",
                        "url": "https://example.test/pkg-1.0.0.tar.gz",
                    }
                ],
                "2.0.0b1": [
                    {
                        "packagetype": "sdist",
                        "url": "https://example.test/pkg-2.0.0b1.tar.gz",
                    }
                ],
            },
        }
        client = _make_client(PYPI_HOST)

        with patch.object(PyPIClient, "project", return_value=project_data):
            version, url = client.get_latest_download_uri("example-pkg", allow_prerelease=True)

        assert version == "2.0.0b1"
        assert url == "https://example.test/pkg-2.0.0b1.tar.gz"

    def test_pypi_backend_returns_none_when_latest_has_no_sdist(self):
        project_data = {
            "info": {"version": "1.0.0"},
            "releases": {
                "1.0.0": [
                    {
                        "packagetype": "bdist_wheel",
                        "url": "https://example.test/pkg-1.0.0.whl",
                    }
                ],
            },
        }
        client = _make_client(PYPI_HOST)

        with patch.object(PyPIClient, "project", return_value=project_data):
            version, url = client.get_latest_download_uri("example-pkg")

        assert version == "1.0.0"
        assert url is None

    def test_azdo_backend_uses_latest_stable_by_default(self):
        client = AzureArtifactsClient(AzureArtifactsFeedConfig("org", "project", "feed"))

        with patch.object(
            client,
            "get_ordered_versions",
            return_value=[Version("1.0.0"), Version("2.0.0b1")],
        ), patch.object(
            client,
            "get_download_uri",
            return_value="https://example.test/pkg-1.0.0.tar.gz",
        ) as get_download_uri:
            version, url = client.get_latest_download_uri("example-pkg")

        assert version == "1.0.0"
        assert url == "https://example.test/pkg-1.0.0.tar.gz"
        get_download_uri.assert_called_once_with("example-pkg", "1.0.0")

    def test_azdo_backend_can_return_latest_prerelease(self):
        client = AzureArtifactsClient(AzureArtifactsFeedConfig("org", "project", "feed"))

        with patch.object(
            client,
            "get_ordered_versions",
            return_value=[Version("1.0.0"), Version("2.0.0b1")],
        ), patch.object(
            client,
            "get_download_uri",
            return_value="https://example.test/pkg-2.0.0b1.tar.gz",
        ) as get_download_uri:
            version, url = client.get_latest_download_uri("example-pkg", allow_prerelease=True)

        assert version == "2.0.0b1"
        assert url == "https://example.test/pkg-2.0.0b1.tar.gz"
        get_download_uri.assert_called_once_with("example-pkg", "2.0.0b1")

    def test_azdo_download_uri_probes_normalized_sdist_names(self):
        client = AzureArtifactsClient(
            AzureArtifactsFeedConfig("org", "project", "feed"),
            pkgs_base_url="https://pkgs.example.test",
        )

        with patch.object(
            client,
            "_head_ok",
            side_effect=lambda url: url.endswith("/azure_core-1.2.3.tar.gz"),
        ):
            url = client.get_download_uri("azure-core", "1.2.3")

        assert (
            url
            == "https://pkgs.example.test/org/project/_packaging/feed/pypi/download/azure-core/1.2.3/azure_core-1.2.3.tar.gz"
        )

    def test_azdo_download_uri_returns_none_when_no_candidate_resolves(self):
        client = AzureArtifactsClient(AzureArtifactsFeedConfig("org", "project", "feed"))

        with patch.object(client, "_head_ok", return_value=False):
            assert client.get_download_uri("example-pkg", "1.0.0") is None


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
