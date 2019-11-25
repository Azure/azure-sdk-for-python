from typing import Optional

from packaging.version import parse as Version, InvalidVersion

import requests

def get_pypi_xmlrpc_client():
    """This is actually deprecated client.
    """
    import xmlrpc.client
    return xmlrpc.client.ServerProxy("https://pypi.python.org/pypi", use_datetime=True)

class PyPIClient:
    def __init__(self, host: str = "https://pypi.org"):
        self._host = host
        self._session = requests.Session()

    def project(self, package_name: str):
        response = self._session.get(
            "{host}/pypi/{project_name}/json".format(
                host=self._host,
                project_name=package_name
            )
        )
        response.raise_for_status()
        return response.json()

    def project_release(self, package_name: str, version: str):
        response = self._session.get(
            "{host}/pypi/{project_name}/{version}/json".format(
                host=self._host,
                project_name=package_name,
                version=version
            )
        )
        response.raise_for_status()
        return response.json()

    def get_ordered_versions(self, package_name: str):
        project = self.project(package_name)
        versions = [
            Version(package_version)
            for package_version
            in project["releases"].keys()
        ]
        versions.sort()
        return versions

    def get_relevant_versions(self, package_name: str):
        """Return a tuple: (latest release, latest stable)
        If there are different, it means the latest is not a stable
        """
        versions = self.get_ordered_versions(package_name)
        pre_releases = [version for version in versions if not version.is_prerelease]
        return (
            versions[-1],
            pre_releases[-1]
        )