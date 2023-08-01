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
    # black,
    "pytoml",
    "json-delta>=2.0",
    # Tests
    "pytest-cov",
    "pytest>=3.5.1",
    "readme_renderer",
    "pyopenssl",
    "python-dotenv",
    "PyYAML",
    "urllib3<2",
    "tomli"
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
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "generate_package=packaging_tools.generate_package:generate_main",
            "generate_sdk=packaging_tools.generate_sdk:generate_main",
            "sdk_generator=packaging_tools.sdk_generator:generate_main",
            "sdk_package=packaging_tools.sdk_package:generate_main",
            "sdk_build=ci_tools.build:build",
            "sdk_set_dev_version=ci_tools.versioning.version_set_dev:version_set_dev_main",
            "sdk_set_version=ci_tools.versioning.version_set:version_set_main",
            "sdk_increment_version=ci_tools.versioning.version_increment:version_increment_main",
            "sdk_analyze_deps=ci_tools.dependency_analysis:analyze_dependencies",
            "sdk_find_invalid_versions=ci_tools.versioning.find_invalid_versions:find_invalid_versions_main",
            "multiapi_combiner=packaging_tools.multiapi_combiner:combine",
        ],
    },
    extras_require={
        ":python_version>='3.5'": ["pytest-asyncio>=0.9.0"],
        "build": ["six", "setuptools", "pyparsing", "certifi"],
    },
)
