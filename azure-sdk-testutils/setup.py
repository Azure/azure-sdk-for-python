import os
from setuptools import setup, find_packages

# This is a "fake" package, meaning it's not supposed to be released but used
# locally with "pip install -e"

setup(
    name = "azure-sdk-testutils",
    version = "0.0.0",
    packages=find_packages(),
)
