import os
import re
import argparse

from ci_tools.functions import discover_targeted_packages
from ci_tools.parsing import ParsedSetup

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def replace_samples_in(directory: str) -> None:
    # Define the strings to search and replace
    old_string = "DefaultAzureCredential()"
    new_string = "DefaultAzureCredential(exclude_managed_identity_credential=True)"

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):  # Only process Python files
                file_path = os.path.join(root, file)

                # Read the file contents
                with open(file_path, "r", encoding="utf-8") as f:
                    file_content = f.read()

                # Replace the old string with the new string
                updated_content = re.sub(re.escape(old_string), new_string, file_content)

                if updated_content != file_content:
                    print(f"Updating {file_path}")

                    # Write the updated content back to the file
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(updated_content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="DefaultAzureCredential tries credentials in a specific order. "
        "This script is intended to walk all the samples of a service and update them to exclude a configuration that is unsupported by Azure Devops."
        "This is necessary because we do not want customers copying part of a sample that is only the way it is BECAUSE of restrictions of our infrastructure."
    )
    parser.add_argument("target_service", help="The target service to process.")

    args = parser.parse_args()
    target_discovery_directory = os.path.join(root_dir, "sdk", args.target_service)

    discovered_packages = discover_targeted_packages("*", target_discovery_directory)

    for package_directory in discovered_packages:
        print(f"scanning {package_directory}")
        if os.path.exists(os.path.join(package_directory, "samples")):
            replace_samples_in(os.path.join(package_directory, "samples"))

        if os.path.exists(os.path.join(package_directory, "sample")):
            replace_samples_in(os.path.join(package_directory, "sample"))