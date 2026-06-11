import requests

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from packaging.requirements import Requirement
from packaging.version import Version


def fetch_dependencies_from_pyproject(file_path):
    with open(file_path, "rb") as file:
        data = tomllib.load(file)

    return data.get("project", {}).get("dependencies", [])


def list_versions(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    data = response.json()
    versions = data["releases"].keys()
    return sorted(versions, key=Version, reverse=True)


def is_major_update(previous, latest):
    return Version(latest).major > Version(previous).major


def check_for_major_updates():
    pyproject_file_path = "sdk/ml/azure-ai-ml/pyproject.toml"
    deps_list = fetch_dependencies_from_pyproject(pyproject_file_path)
    deps = [Requirement(line) for line in deps_list if line.strip() and not line.strip().startswith("#")]

    with open("updates.txt", "w") as f:
        for dep in deps:
            all_versions = list_versions(dep.name)
            if len(all_versions) > 1 and is_major_update(all_versions[1], all_versions[0]):
                f.write(f"{dep.name} {all_versions[0]}\n")


check_for_major_updates()
