# Testing visual studio code credential

## Test matrix

- Python 2.7, 3.5.3, 3.8
- Windows, Ubuntu 18.04, Redhat Enterprise Linux 8.1, Debian 10, Mac OS

## Test steps

- Install Visual Studio Code from https://code.visualstudio.com/

- Launch Visual Studio Code and go to Extension tab.

- Search and install Azure Storage extension

- Go to Azure tab and log in with your credential

- Open a terminal, install azure-core & azure-identity

- Run run-test.py

Expect: a valid access token is printed out.