import os
import argparse
import shutil
import pathlib
from checkout_eng import prep_directory, invoke_command, cleanup_directory
root = pathlib.Path(__file__).resolve().parent.parent.parent.parent


def get_release_tag(
    assembly_area: str,
    target_package: str,
    service_directory: str,
    target_version: str,
) -> None:
    clone_folder = prep_directory(os.path.join(assembly_area, "python-sdk"))
    checkout_path = os.path.join("sdk", service_directory, target_package)
    invoke_command(
        f"git clone --no-checkout --filter=tree:0 https://github.com/Azure/azure-sdk-for-python .", clone_folder
    )
    invoke_command(f"git config gc.auto 0", clone_folder)
    invoke_command(f"git sparse-checkout init", clone_folder)
    invoke_command(f'git sparse-checkout add "{checkout_path}"', clone_folder)
    invoke_command(f"git -c advice.detachedHead=false checkout {target_package}_{target_version}", clone_folder)

    cleanup_directory(os.path.join(root, "sdk", service_directory, target_package))
    shutil.move(
        os.path.join(assembly_area, "python-sdk", "sdk", service_directory, target_package),
        os.path.join(root, "sdk", service_directory)
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--package"
    )

    parser.add_argument(
        "--service",
    )

    parser.add_argument(
        "--version"
    )

    args = parser.parse_args()

    get_release_tag(
        assembly_area=os.getcwd(),
        target_package=args.package,
        service_directory=args.service,
        target_version=args.version
    )
