import logging
from packaging.version import InvalidVersion, Version, parse
import sys
import pdb
from urllib3 import Retry, PoolManager
import json
import os
from typing import List


def get_pypi_xmlrpc_client():
    """This is actually deprecated client."""
    import xmlrpc.client

    return xmlrpc.client.ServerProxy("https://pypi.python.org/pypi", use_datetime=True)


class PyPIClient:
    def __init__(self, host="https://pypi.org"):
        self._host = host
        self._http = PoolManager(
            retries=Retry(total=3, raise_on_status=True), ca_certs=os.getenv("REQUESTS_CA_BUNDLE", None)
        )

    def project(self, package_name):
        response = self._http.request(
            "get", "{host}/pypi/{project_name}/json".format(host=self._host, project_name=package_name)
        )
        return json.loads(response.data.decode("utf-8"))

    def project_release(self, package_name, version):
        response = self._http.request(
            "get",
            "{host}/pypi/{project_name}/{version}/json".format(
                host=self._host, project_name=package_name, version=version
            ),
        )
        return json.loads(response.data.decode("utf-8"))

    def filter_packages_for_compatibility(self, package_name, version_set):
        # only need the packaging.specifiers import if we're actually executing this filter.
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
        project = self.project(package_name)

        versions: List[Version] = []
        for package_version in project["releases"].keys():
            try:
                versions.append(parse(package_version))
            except InvalidVersion as e:
                logging.warn(f"Invalid version {package_version} for package {package_name}")
                continue
        versions.sort()

        if filter_by_compatibility:
            return self.filter_packages_for_compatibility(package_name, versions)

        return versions

    def get_relevant_versions(self, package_name):
        """Return a tuple: (latest release, latest stable)
        If there are different, it means the latest is not a stable
        """
        versions = self.get_ordered_versions(package_name)
        stable_releases = [version for version in versions if not version.is_prerelease]
        return (versions[-1], stable_releases[-1])
