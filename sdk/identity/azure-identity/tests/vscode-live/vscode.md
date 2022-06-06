# Testing visual studio code credential

## Test matrix

- Python 3.7, 3.9
- Windows, Ubuntu 18.04, Redhat Enterprise Linux 8.1, Debian 10, Mac OS

## Test steps

- Install Visual Studio Code from https://code.visualstudio.com/

- Launch Visual Studio Code and go to Extension tab.

- Search and install Azure Storage extension

- Go to Azure tab and log in with your credential

- Open a terminal, install latest azure-identity by running 
```python
pip install azure-identity -i https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python%40Local/pypi/simple/
```

- Run run-test.py

Expect: an access token is printed out.
