import ast
import sys

def fetch_dependencies_from_setup(file_path):
    with open(file_path, "r") as file:
        tree = ast.parse(file.read(), filename=file_path)

    dependencies = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "setup":
            for keyword in node.keywords:
                if keyword.arg == "install_requires":
                    dependencies = [elt.s for elt in keyword.value.elts]
                    break

    return dependencies


# Path to the setup.py file of azure-ai-ml
setup_file_path = "C:/Projects/azure-sdk-for-python/sdk/ml/azure-ai-ml/setup.py"

# Fetch dependencies
deps_list = fetch_dependencies_from_setup(setup_file_path)

print("Dependencies of azure-sdk-for-python repo from setup.py of azure-ai-ml:")
print(deps_list)

from packaging.requirements import Requirement

deps = [
    Requirement(line) for line in deps_list if line.strip() and not line.startswith("#")
]
import requests


def list_versions(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    data = response.json()
    versions = data["releases"].keys()
    version_array = []
    for version in versions:
        version_array.append(version.split(".")[0])
    return sorted(version_array, key=int, reverse=True)


from packaging.version import Version


def is_major_update(previous, latest):
    return Version(latest).major > Version(previous).major



def check_for_major_updates():
    major_updates = []
    for dep in deps:
        all_version = list_versions(dep.name)
        if len(all_version) > 1 and is_major_update(all_version[1], all_version[0]):
            major_updates.append(
                f"Current config of `{dep}` and major version updated from {dep.name}: {all_version[1]} → {all_version[0]}"
            )
    if major_updates:
        # body = "\n".join(major_updates) # Uncomment this line if you want to send an email or notification
        print("Major Dependency Updates Found:")
        print(major_updates)
        sys.exit(1)
    else:
        print("No major updates found.")


check_for_major_updates()
