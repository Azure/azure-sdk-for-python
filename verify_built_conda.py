import os
import glob
import pprint

import subprocess
import yaml
import re

from typing import List

repo_root = os.path.dirname(__file__)

conda_recipe_folder = os.path.join(repo_root, "conda", "conda-recipes")
recipe_glob = os.path.join(conda_recipe_folder, "*", "meta.yaml")

conda_channel = "C:/repo/scratch/verify-conda-builds"
conda_env_name = "verify_artifacts"

def get_imports_from_recipe(recipe_file: str) -> List[str]:
    imports = []
    with open(recipe_file, "r") as f:
        content = f.readlines()

    store_lines = False
    for line in content:
        if store_lines == True and not line.strip() or "requires" in line:
            store_lines = False

        if "imports" in line:
            store_lines = True
            continue

        if store_lines:
            imports.append(line.strip())
            continue


    return [i.replace("- ", "import ").strip() for i in imports]


def create_conda_env() -> str:
    print(f"Re-creating the conda environment {conda_env_name}")
    subprocess.run(["conda", "create", "--name", conda_env_name, "python=3.11", "-y"], check=False, capture_output=True)

    results = subprocess.run(["conda", "env", "list"], check=True, capture_output=True)
    lines = results.stdout.decode("utf-8").split(os.linesep)

    for line in lines:
        if conda_env_name in line:
            return re.split(r"\s+", line)[1].strip()

    return ""


if __name__ == "__main__":
    recipes = glob.glob(recipe_glob)

    env_location = create_conda_env()
    if not env_location:
        print("Failed to create conda environment")
        exit(1)

    install_results = {}
    test_results = {}

    recipes = [recipe for recipe in recipes if "uamqp" not in recipe]

    for recipe_file in recipes:
        recipe_dir = os.path.dirname(recipe_file)
        recipe_name = os.path.basename(recipe_dir)
        print(f"Processing package {recipe_name} from output channel into conda env {conda_env_name}")

        imports = get_imports_from_recipe(recipe_file)

        install_result = subprocess.run(["conda", "install", "-n", conda_env_name, "-c", "conda-forge", "-c", conda_channel, recipe_name, "-y"], check=False, capture_output=True)
        if install_result.returncode != 0:
            print(f"Failed to install package {recipe_name}")
            print(install_result.stdout.decode("utf-8"))
            print(install_result.stderr.decode("utf-8"))
            install_results[recipe_name] = False
            continue
        install_results[recipe_name] = True

        if imports:
            test_results[recipe_name] = install_results[recipe_name]
            for import_line in imports:
                result = subprocess.run([f"{env_location}/python.exe", "-c", f"{import_line}"], check=False)

                if result.returncode != 0:
                    test_results[recipe_name] = False

    for package, result in install_results.items():
        print(f"Package {package} installed: {result}")

        if package in test_results:
            print(f"Package {package} tested: {test_results[package]}")
        else:
            print("We didn't run tests for {package}, we crashed on build.")