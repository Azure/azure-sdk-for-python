import os
from setuptools import setup, find_packages

# This is a "fake" package, meaning it's not supposed to be released but used
# locally with "pip install -e"

setup(
    name = "azure-sdk-tools",
    version = "0.0.0",
    author='Microsoft Corporation',
    author_email='azpysdkhelp@microsoft.com',
    url='https://github.com/Azure/azure-sdk-for-python',
    packages=find_packages(),
    long_description="Specific tools for Azure SDK for Python testing"
)
