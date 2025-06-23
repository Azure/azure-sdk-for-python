import ast
import requests
from packaging.requirements import Requirement
from packaging.version import Version

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

def list_versions(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    data = response.json()
    versions = data["releases"].keys()
    return sorted(versions, key=Version, reverse=True)

def is_major_update(previous, latest):
    return Version(latest).major > Version(previous).major

def check_for_major_updates():
    setup_file_path = "sdk/ml/azure-ai-ml/setup.py"
    deps_list = fetch_dependencies_from_setup(setup_file_path)
    deps = [Requirement(line) for line in deps_list if line.strip() and not line.strip().startswith("#")]

    with open("updates.txt", "w") as f:
        for dep in deps:
            all_versions = list_versions(dep.name)
            if len(all_versions) > 1 and is_major_update(all_versions[1], all_versions[0]):
                f.write(f"{dep.name} {all_versions[0]}\n")

check_for_major_updates()
