import os
import re
import shutil

def find_inactive_packages(base_dir, plane="sdk"):
    inactive_packages = []
    if plane == "mgmt":
        for root, dirs, files in os.walk(base_dir):
            if "setup.py" in files:
                setup_path = os.path.join(root, "setup.py")
                with open(setup_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if re.search(r"Development Status :: 7 - Inactive", content) and ("azure-mgmt" in root or "management" in root):
                        inactive_packages.append(root)
    elif plane == "sdk":
        for root, dirs, files in os.walk(base_dir):
            if "setup.py" in files:
                setup_path = os.path.join(root, "setup.py")
                with open(setup_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if re.search(r"Development Status :: 7 - Inactive", content) and "azure-mgmt" not in root:
                        inactive_packages.append(root)
    return inactive_packages

def get_latest_version_from_changelog(package_path):
    changelog_path = os.path.join(package_path, "CHANGELOG.md")
    if os.path.exists(changelog_path):
        with open(changelog_path, "r", encoding="utf-8") as f:
            for line in f:
                match = re.match(r"##\s+([\d\.]+(?:b\d+)?(?:\.post\d+)?)", line)
                if match:
                    return match.group(1)
    return None

pkgs_w_no_latest_version = []
def execute_step_5(package_path):
    # Step 1: Update README.md
    latest_version = get_latest_version_from_changelog(package_path)
    if not latest_version:
        pkgs_w_no_latest_version.append(package_path)
        latest_version = "PLACEHOLDER"
        print(f"Warning: Could not determine the latest version for {package_path}. Skipping README update.")

    readme_path = os.path.join(package_path, "README.md")
    with open(readme_path, "a", encoding="utf-8") as f:
        package_name = os.path.basename(package_path)
        with open(readme_path, "r", encoding="utf-8") as readme_file:
            existing_content = readme_file.read()
        
        relative_path = os.path.relpath(package_path, base_directory)
        pypi_url = f"https://pypi.org/project/{package_name}/"
        new_content = (
            f"\n\nPackage source code and samples have been removed from the `main` branch and can be found under the release tag for the latest version. "
            f"See [{package_name}_{latest_version}](https://github.com/Azure/azure-sdk-for-python/tree/{package_name}_{latest_version}/sdk/{relative_path}). "
            f"The latest release can be found on [PyPI]({pypi_url}).\n\nIf you have any questions, please open a [GitHub Issue](https://github.com/Azure/azure-sdk-for-python/issues) "
            f"or email `azpysdkhelp@microsoft.com`."
        )
        
        with open(readme_path, "w", encoding="utf-8") as readme_file:
            readme_file.write(existing_content + new_content)

    # Step 2: Remove all files except README.md
    for root, _, files in os.walk(package_path):
        for file in files:
            if file != "README.md" or root != package_path:
                os.remove(os.path.join(root, file))

    # Remove all folders in the package path
    for root, dirs, _ in os.walk(package_path, topdown=False):
        for dir in dirs:
            shutil.rmtree(os.path.join(root, dir))

    # Check and remove specific files in the parent folder if conditions are met
    parent_folder = os.path.dirname(package_path)
    ci_yml_path = os.path.join(parent_folder, "ci.yml")
    if os.path.exists(ci_yml_path):
        with open(ci_yml_path, "r", encoding="utf-8") as ci_file:
            ci_content = ci_file.read()
            if "Artifacts" not in ci_content or (ci_content.count("Artifacts") == 1 and ci_content.count("name") == 1 and ci_content.count("safeName") == 1 and f"name: {os.path.basename(package_path)}" in ci_content):
                # Remove all files in the parent folder, but keep subfolders intact
                for file_name in os.listdir(parent_folder):
                    file_path = os.path.join(parent_folder, file_name)
                    if os.path.isfile(file_path):
                        os.remove(file_path)

if __name__ == "__main__":
    base_directory = "/home/swathip/repos/azure-sdk-for-python/sdk"
    #inactive_packages = find_inactive_packages(base_directory)
    inactive_packages = find_inactive_packages(base_directory, "mgmt")
    exceptions = ["eventhub/azure-eventhub-checkpointstoretable"]
    inactive_packages = [pkg for pkg in inactive_packages if pkg.split("sdk/")[1] not in exceptions]
    if inactive_packages:
        print("Executing Step 5 for inactive packages:")
        for package in inactive_packages:
            print(f"- Processing {package}")
            execute_step_5(package)
        print("Step 5 completed for all inactive packages.")
        print("Packages with no latest version found:")
        for package in pkgs_w_no_latest_version:
            print(f"- {package}")
    else:
        print("No inactive packages found.")
    #if pkgs_samples_readme:
    #    print("Packages with samples and README.md:")
    #    for package in pkgs_samples_readme:
    #        print(f"- {package}")
