# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import re
from setuptools import setup, find_packages

# Fetch description
with open("README.md", "r") as fh:
    _long_description = fh.read()


# Fetch version
with open("azure/iot/modelsrepository/_version.py", "r") as fh:
    VERSION = re.search(r"^VERSION\s=\s*[\"']([^\"']*)", fh.read(), re.MULTILINE).group(1)
if not VERSION:
    raise RuntimeError("Cannot find version information")


setup(
    name="azure-iot-modelsrepository",
    version=VERSION,
    description="Microsoft Azure IoT Models Repository Library",
    license="MIT License",
    author="Microsoft Corporation",
    author_email="azpysdkhelp@microsoft.com",
    url="https://github.com/Azure/azure-sdk-for-python",
    project_urls={
        "Bug Tracker": "https://github.com/Azure/azure-sdk-for-python/issues",
        "Source": "https://github.com/Azure/azure-sdk-for-python",
    },
    long_description=_long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    install_requires=[
        "azure-core<2.0.0,>=1.2.2",
        "six>=1.11.0",
    ],
    python_requires=">=3.6",
    packages=find_packages(
        exclude=[
            "tests",
            "tests.*",
            "samples",
            "samples.*",
            # Exclude packages that will be covered by PEP420 or nspkg
            "azure",
            "azure.iot",
        ]
    ),
    include_package_data=True,
    package_data={
        'pytyped': ['py.typed'],
    },
    zip_safe=False,
)
