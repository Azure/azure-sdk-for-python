# Overview
This folder contains collecting the multi API versions in use from:
https://github.com/Azure/azure-cli/blob/dev/src/azure-cli-core/azure/cli/core/profiles/_shared.py
https://github.com/Azure/azure-rest-api-specs/tree/main/profiles/definitions
https://github.com/Azure/azure-rest-api-specs/tree/main/profile

## `main.py`
the script could help to collect Multi Api quickly.

### Usage
```
pip install -r requirement.txt
python main.py
```

### Tip
if you don't want to load result to github,you could comment out the `upload_to_github` function in Line 200 from main.py.
