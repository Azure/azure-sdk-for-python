import logging
from packaging.version import InvalidVersion, Version, parse
import sys
from urllib3 import Retry, PoolManager
import json
import os
from typing import List


def get_pypi_xmlrpc_client():
    """This is actually deprecated client."""
    import xmlrpc.client

    return xmlrpc.client.ServerProxy("https://pypi.python.org/pypi", use_datetime=True)


class PyPIClient:
    """Unified package-index client.

    By default, reads ``PIP_INDEX_URL`` to decide the backend:
    * If the URL contains ``pkgs.dev.azure.com`` → Azure Artifacts REST API.
    * Otherwise → PyPI JSON API (``https://pypi.org``).
    """

    def __init__(self, host="https://pypi.org"):
        index_url = os.environ.get("PIP_INDEX_URL", "")

        # Lazy import to avoid circular deps at module level.
        from pypi_tools.azdo import parse_pip_index_url, AzureArtifactsClient

        azdo_cfg = parse_pip_index_url(index_url) if index_url else None

        if azdo_cfg is not None:
            self._backend = "azdo"
            self._azdo = AzureArtifactsClient(azdo_cfg)
        else:
            self._backend = "pypi"
            self._host = host
            self._http = PoolManager(
                retries=Retry(total=3, raise_on_status=True),
                ca_certs=os.getenv("REQUESTS_CA_BUNDLE", None),
            )

    def _pypi_http(self):
        """Lazy PoolManager for pypi.org fallback when on AzDO backend."""
        if not hasattr(self, "_pypi_http_pool"):
            self._pypi_http_pool = PoolManager(
                retries=Retry(total=3, raise_on_status=True),
                ca_certs=os.getenv("REQUESTS_CA_BUNDLE", None),
            )
        return self._pypi_http_pool

    def _pypi_json_request(self, path):
        """GET from pypi.org JSON API, using the active backend's http pool if on pypi, else fallback."""
        if self._backend == "pypi":
            url = "{host}{path}".format(host=self._host, path=path)
            response = self._http.request("get", url)
        else:
            url = "https://pypi.org{path}".format(path=path)
            response = self._pypi_http().request("get", url)
        return json.loads(response.data.decode("utf-8"))

    # ------------------------------------------------------------------
    # PyPI JSON endpoints (fall back to pypi.org when on AzDO backend)
    # ------------------------------------------------------------------

    def project(self, package_name):
        if self._backend != "pypi":
            raise NotImplementedError("project() is only available against pypi.org")
        return self._pypi_json_request("/pypi/{}/json".format(package_name))

    def project_release(self, package_name, version):
        return self._pypi_json_request("/pypi/{}/{}/json".format(package_name, version))

    # ------------------------------------------------------------------
    # Shared interface
    # ------------------------------------------------------------------

    def filter_packages_for_compatibility(self, package_name, version_set):
        if self._backend != "pypi":
            raise NotImplementedError(
                "filter_packages_for_compatibility() requires pypi.org (needs requires_python metadata)"
            )
        from packaging.specifiers import InvalidSpecifier, SpecifierSet

        results: List[Version] = []
        for version in version_set:
            requires_python = self.project_release(package_name, version)["info"]["requires_python"]
            if requires_python:
                try:
                    if parse(".".join(map(str, sys.version_info[:3]))) in SpecifierSet(requires_python):
                        results.append(version)
                except InvalidSpecifier:
                    logging.warn(f"Invalid python_requires {requires_python!r} for package {package_name}=={version}")
                    continue
            else:
                results.append(version)
        return results

    def get_ordered_versions(self, package_name, filter_by_compatibility=False) -> List[Version]:
        if self._backend == "azdo":
            versions = self._azdo.get_ordered_versions(package_name)
            if filter_by_compatibility:
                logging.warning(
                    "filter_by_compatibility is not supported against Azure Artifacts; returning unfiltered versions"
                )
            return versions

        project = self.project(package_name)
        versions: List[Version] = []
        for package_version, files in project["releases"].items():
            try:
                if not files or all(f.get("yanked", False) for f in files):
                    continue
                versions.append(parse(package_version))
            except InvalidVersion:
                logging.warn(f"Invalid version {package_version} for package {package_name}")
                continue
        versions.sort()

        if filter_by_compatibility:
            return self.filter_packages_for_compatibility(package_name, versions)

        return versions

    def get_relevant_versions(self, package_name):
        """Return a tuple: (latest release, latest stable)"""
        versions = self.get_ordered_versions(package_name)
        stable_releases = [version for version in versions if not version.is_prerelease]
        return (versions[-1], stable_releases[-1])


def retrieve_versions_from_pypi(package_name: str) -> List[str]:
    """
    Retrieve all published versions for the package from the active index.

    :param str package_name: The name of the package.
    :rtype: List[str]
    :return: List of all version strings (sorted ascending).
    """
    try:
        client = PyPIClient()
        all_versions = client.get_ordered_versions(package_name)
        return [str(v) for v in all_versions]
    except Exception as ex:
        logging.warning("Failed to retrieve package data for %s: %s", package_name, ex)
        return []
