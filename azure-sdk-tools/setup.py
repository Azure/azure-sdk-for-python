import os
from setuptools import setup, find_packages

# This is a "fake" package, meaning it's not supposed to be released but used
# locally with "pip install -e"

DEPENDENCIES = [
    # Packaging
    'packaging',
    'wheel',
    'Jinja2',
    'pytoml',
    'json-delta>=2.0',
    'azure-devtools[ci_tools]>=1.1.0',
    # Tests
    'pytest-cov',
    'pytest>=3.5.1',
    # 'azure-devtools>=0.4.1' override by packaging needs
    'readme_renderer',

    # Should not be here, but split per package once they have test dependencies
    'azure-storage-blob', # azure-servicemanagement-legacy azure-keyvault
    'azure-storage-file', # azure-mgmt-batchai
    'azure-storage-common', # azure-keyvault
    'pyopenssl' # azure-servicemanagement-legacy
]

setup(
    name = "azure-sdk-tools",
    version = "0.0.0",
    author='Microsoft Corporation',
    author_email='azpysdkhelp@microsoft.com',
    url='https://github.com/Azure/azure-sdk-for-python',
    packages=find_packages(),
    long_description="Specific tools for Azure SDK for Python testing",
    install_requires=DEPENDENCIES,
    entry_points = {
        'console_scripts': [
            'generate_package=packaging_tools.generate_package:generate_main',
        ],
    }
)
