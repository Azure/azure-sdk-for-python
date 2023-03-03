import os
import sys
from pathlib import Path
from subprocess import check_call


def main(sdk_folder: str):
    # install package.json
    script = Path("eng/common/scripts/Cadl-Project-Sync.ps1")
    check_call(f"pwsh {script} {Path(sdk_folder)}", shell=True)

    # generate SDK
    cmd = Path("eng/common/scripts/Cadl-Project-Generate.ps1")
    check_call(f"pwsh {cmd} {Path(sdk_folder)}", shell=True)

if __name__ == '__main__':
    if len(sys.argv[1:]) != 1:
        print("Please input sdk folder like: sdk/datadog/azure-mgmt-datadog")
    else:
        main(sys.argv[1])
