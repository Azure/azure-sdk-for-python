from packaging.version import parse as Version
import sys

import requests

def get_pypi_xmlrpc_client():
    """This is actually deprecated client.
    """
    import xmlrpc.client
    return xmlrpc.client.ServerProxy("https://pypi.python.org/pypi", use_datetime=True)

class PyPIClient:
    def __init__(self, host="https://pypi.org"):
        self._host = host
        self._session = requests.Session()

    def project(self, package_name):
        response = self._session.get(
            "{host}/pypi/{project_name}/json".format(
                host=self._host,
                project_name=package_name
            )
        )
        response.raise_for_status()
        return response.json()

    def project_release(self, package_name, version):
        response = self._session.get(
            "{host}/pypi/{project_name}/{version}/json".format(
                host=self._host,
                project_name=package_name,
                version=version
            )
        )
        response.raise_for_status()
        return response.json()

    def filter_packages_for_compatibility(self, package_name, version_set):
        # only need the packaging.specifiers import if we're actually executing this filter.
        from packaging.specifiers import SpecifierSet

        results = []

        for version in version_set:
            requires_python = self.project_release(package_name, version)["info"]["requires_python"]
            if requires_python:
                if Version('.'.join(map(str, sys.version_info[:3]))) in SpecifierSet(requires_python):
                    results.append(version)
            else:
                results.append(version)

        return results

    def get_ordered_versions(self, package_name, filter_by_compatibility = False):
        project = self.project(package_name)

        versions = [
            Version(package_version)
            for package_version
            in project["releases"].keys()
        ]
        versions.sort()

        if filter_by_compatibility:
            return self.filter_packages_for_compatibility(package_name, versions)

        return versions

    def get_relevant_versions(self, package_name):
        """Return a tuple: (latest release, latest stable)
        If there are different, it means the latest is not a stable
        """
        versions = self.get_ordered_versions(package_name)
        pre_releases = [version for version in versions if not version.is_prerelease]
        return (
            versions[-1],
            pre_releases[-1]
        )