---
name: check-azpysdk
description: Automate verification of changes to tools in the azpysdk CLI. Use this skill when the user is working on azpysdk and needs to verify functionality.
---

## Check azpysdk 

Steps to verify changes:

### Basic Verification

1. Ensure your venv is activated and azure-sdk-tools is installed
2. Clarify the azpysdk command to check. Clarify if there are specific expected outputs or behaviors to verify against.
3. For each following package, navigate to the package root. Ensure `.venv_<command>` is removed to start from clean state. Run `azpysdk <command>` and `azpysdk <command> --isolate`, and verify the outputs are as expected:
  - azure-core
  - azure-mgmt-core
  - azure-storage-blob
4. If the command is not working as expected, investigate the issue by checking the code changes, error messages, and relevant documentation.

### Extended Verification

Verify with entrypoint used in CI pipelines.

1. From the repo root, run 
```
python eng/scripts/dispatch_checks.py <pkg to check> --service=<service> --checks=<command> --filter-type=Omit_management 
```
