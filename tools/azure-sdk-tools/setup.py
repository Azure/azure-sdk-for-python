import os
from setuptools import setup, find_packages

# This is a "fake" package, meaning it's not supposed to be released but used
# locally with "pip install -e"

DEPENDENCIES = [
    # Packaging
    "packaging",
    "wheel",
    "Jinja2",
    "MarkupSafe==2.0.1",
    "pytoml",
    "json-delta>=2.0",
    # Tests
    "pytest-cov",
    "pytest>=3.5.1",
    # 'azure-devtools>=0.4.1' override by packaging needs
    "readme_renderer",
    # 'azure-storage-file<2.0',
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
    long_description="Specific tools for Azure SDK for Python testing",
    install_requires=DEPENDENCIES,
    entry_points={
        "console_scripts": [
            "generate_package=packaging_tools.generate_package:generate_main",
            "generate_sdk=packaging_tools.generate_sdk:generate_main",
            "auto_codegen=packaging_tools.auto_codegen:generate_main",
            "auto_package=packaging_tools.auto_package:generate_main",
            "sdk_generator=packaging_tools.sdk_generator:generate_main",
            "sdk_package=packaging_tools.sdk_package:generate_main",
        ],
    },
    extras_require={":python_version>='3.5'": ["pytest-asyncio>=0.9.0"]},
)
