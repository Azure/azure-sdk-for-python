# hi

# Pre-requisite

- You need to have Python installed
- We recommend at least version 3.11 to have access to more tools by default
- You may optionally use the ["uv"](https://docs.astral.sh/uv/) tool, which is fast and handles Python version and venv creation automatically.

# Initial setup

- Go to the folder of the package you're working on, for instance `sdk/contoso/azure-contoso`

## Setup with uv

`uv venv`

`uv pip install -r dev_requirements.txt`

## Setup with pip/python

`python -m venv .venv`

```
# for WSL
source .venv/bin/activate 

# for Windows
.venv\Scripts\activate 
```

`- pip install -r dev_requirements.txt`

# Using the CLI

## With uv

```
# uv loads the venv for you when you prefix the command with uvx
uvx azpysdk <tool_name>
```

## With venv

```
# You can call the command directly if you activated the venv
azpysdk <tool_name>
```

# List of available tools

- mypy
- pylint
- sphinx

# Advanced scenario

## Using different Python version

If you want to locally test different Python versions to check compatibility with all the required Python versions, do that.

Note that this is optional, and you can rely onn CI to test python versions.

## With uv
You can specify a Python version upon venv creation:

`uvx --python=3.11 azpysdk mypy`

## With Python

You need to install [pyenv](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation), which lets you easily switch between multiple versions of Python.

To switch Python versions:
```
pyenv install 3.10
pyenv global 3.10
```