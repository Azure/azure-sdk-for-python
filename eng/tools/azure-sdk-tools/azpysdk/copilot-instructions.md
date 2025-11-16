# copilot check migration instructions

This document provides instructions on how to migrate existing Copilot check configurations to the new format used by the Azure SDK Tools.

1. identify a check from `tox.ini`.
2. Given that `tox.ini`, read the `tox.ini` config for that environment from `eng/tox/tox.ini`
3. Copy the relevant configuration options from `tox.ini` to a new check configuration file located at `eng/tools/azure-sdk-tools/azpysdk/<check_name>.py`.
4. Ensure that within the new file, a class inheriting from `Check` is created, and the flow of said check looks similar to any of the existing checks in this directory: `next_mpy.py`, `import_all.py`.
5. Import and register the new check within `main.py` located in this directory.
6. Make a decision for any of the custom commands in the `tox.ini` file to either pull the rference iimpoement over here, or to remove them if they are no longer necessary.
7. Test the new check by running it with `azpysdk whl --isolate azure-template`
8. Ensure that environment variables are set if they are in the original tox.ini file. migrate the requirements that would get installed in the tox.ini file to calls to Check.install_into_venv to ensure that the check has the necessary dependencies.

