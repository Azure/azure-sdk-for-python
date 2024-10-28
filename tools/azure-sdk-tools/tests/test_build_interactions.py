import os, tempfile, shutil

from ci_tools.build import discover_targeted_packages, build_packages, build

repo_root = os.path.join(os.path.dirname(__file__), "..", "..", "..")
integration_folder = os.path.join(os.path.dirname(__file__), "integration")
pyproject_folder = os.path.join(integration_folder, "scenarios", "pyproject_build_config")
pyproject_file = os.path.join(integration_folder, "scenarios", "pyproject_build_config", "pyproject.toml")

def test_build_core():
    pass

def test_discover_targeted_packages():
    pass

def test_build_packages():
    pass