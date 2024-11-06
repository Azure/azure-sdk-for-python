import os
from setuptools import setup, find_packages

# This is a "fake" package, meaning it's not supposed to be released but used
# locally with "pip install -e"

DEPENDENCIES = [
    # Packaging
    "packaging",
    "wheel",
    "Jinja2",
    "json-delta>=2.0",
    # Tests
    "pytest-cov",
    "pytest>=3.5.1",
    "python-dotenv",
    "PyYAML",
    "urllib3",
    "tomli-w==1.0.0",
    "azure-core",
    # Perf/Build
    "ConfigArgParse>=0.12.0",
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
            "generate_client=packaging_tools.generate_client:generate_main",
            "multiapi_combiner=packaging_tools.multiapi_combiner:combine",
            "perfstress=devtools_testutils.perfstress_tests:run_perfstress_cmd",
            "perfstressdebug=devtools_testutils.perfstress_tests:run_perfstress_debug_cmd",
            "sdk_generator=packaging_tools.sdk_generator:generate_main",
            "sdk_package=packaging_tools.sdk_package:generate_main",
            "sdk_build=ci_tools.build:build",
            "sdk_build_conda=ci_tools.conda:entrypoint",
            "sdk_set_dev_version=ci_tools.versioning.version_set_dev:version_set_dev_main",
            "sdk_set_version=ci_tools.versioning.version_set:version_set_main",
            "sdk_increment_version=ci_tools.versioning.version_increment:version_increment_main",
            "sdk_analyze_deps=ci_tools.dependency_analysis:analyze_dependencies",
            "sdk_find_invalid_versions=ci_tools.versioning.find_invalid_versions:find_invalid_versions_main",
            "sdk_verify_keywords=ci_tools.keywords_verify:entrypoint",
            "systemperf=devtools_testutils.perfstress_tests:run_system_perfstress_tests_cmd",
        ],
    },
    extras_require={
        ":python_version>='3.5'": ["pytest-asyncio>=0.9.0"],
        ":python_version<'3.11'": ["tomli==2.0.1"],
        "build": ["six", "setuptools", "pyparsing", "certifi", "cibuildwheel", "pkginfo", "build"],
        "conda": ["beautifulsoup4"],
        "systemperf": ["aiohttp>=3.0", "requests>=2.0", "tornado==6.0.3", "httpx>=0.21", "azure-core"],
        "ghtools": ["GitPython", "PyGithub>=1.59.0", "requests>=2.0"],
    },
)
