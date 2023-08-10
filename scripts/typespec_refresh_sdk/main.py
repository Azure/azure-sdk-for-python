import os
import sys
from pathlib import Path
from subprocess import check_call


def call(cmd: str):
    print(f"Calling: {cmd}")
    return check_call(cmd, shell=True)


def main(sdk_folder: str):
    repoRoot = Path(os.path.dirname(os.path.abspath(__file__))) / "../.."
    npmrcPath = repoRoot / ".npmrc"
    npmrcPathArg = f"-NpmrcPath {npmrcPath}" if npmrcPath.exists() else ""

    # install package.json
    call(f"pwsh eng/common/scripts/TypeSpec-Project-Sync.ps1 {Path(sdk_folder)}")

    # generate SDK
    call(
        f"pwsh eng/common/scripts/TypeSpec-Project-Generate.ps1 {Path(sdk_folder)} {npmrcPathArg}"
    )


if __name__ == "__main__":
    if len(sys.argv[1:]) != 1:
        print("Please input sdk folder like: sdk/datadog/azure-mgmt-datadog")
    else:
        main(sys.argv[1])
