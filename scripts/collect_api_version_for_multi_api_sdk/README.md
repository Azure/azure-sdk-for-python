# Overview
This folder contains collecting the multi API versions in use from:
- https://github.com/Azure/azure-cli/blob/dev/src/azure-cli-core/azure/cli/core/profiles/_shared.py
- https://github.com/Azure/azure-rest-api-specs/tree/main/profiles/definitions
- https://github.com/Azure/azure-rest-api-specs/tree/main/profile

## `main.py`
the script could help to collect all the Api Versions used by Azure CLI and Azure Stack.

### Usage
```
pip install -r requirement.txt
python main.py
```

### Tip
if you don't want to upload result to github, you could comment out the `upload_to_github` function in `main.py` before running it.
