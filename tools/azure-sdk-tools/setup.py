import os
from setuptools import setup, find_packages

# This is a "fake" package, meaning it's not supposed to be released but used
# locally with "pip install -e"

DEPENDENCIES = [
    # Packaging
    "packaging",
    "wheel",
    "Jinja2",
    "pytoml",
    "json-delta>=2.0",
    # Tests
    "pytest-cov",
    "pytest>=3.5.1",
    "readme_renderer",
    "azure-storage-common<1.4.1",
    "pyopenssl",
    "azure-mgmt-resource",
    "azure-mgmt-storage",
    "azure-mgmt-keyvault",
    "python-dotenv",
]

setup(
    name="azure-sdk-tools",
    version="0.0.0",
    author="Microsoft Corporation",
    author_email="azpysdkhelp@microsoft.com",
    url="https://github.com/Azure/azure-sdk-for-python",
    packages=find_packages(),
    long_description="Build and test tooling for the Azure SDK for Python",
    install_requires=DEPENDENCIES,
    entry_points={
        "console_scripts": [
            "generate_package=packaging_tools.generate_package:generate_main",
            "generate_sdk=packaging_tools.generate_sdk:generate_main",
            "auto_codegen=packaging_tools.auto_codegen:generate_main",
            "auto_package=packaging_tools.auto_package:generate_main",
            "sdk_generator=packaging_tools.sdk_generator:generate_main",
            "sdk_package=packaging_tools.sdk_package:generate_main",
            "sdk_build=ci_tools.build:build",
            # "sdk_set_dev_version=ci_tools:",
            # "sdk_increment_version=ci_tools:",
        ],
    },
    extras_require={
        ":python_version>='3.5'": ["pytest-asyncio>=0.9.0"],
        "build": ["six", "setuptools", "packaging", "pyparsing"],
    },
)
