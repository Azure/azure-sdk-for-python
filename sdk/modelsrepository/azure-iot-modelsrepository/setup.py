# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import re
from setuptools import setup, find_packages

# azure v0.x is not compatible with this package
# azure v0.x used to have a __version__ attribute (newer versions don't)
try:
    import azure

    try:
        ver = azure.__version__
        raise Exception(
            "This package is incompatible with azure=={}. ".format(ver)
            + 'Uninstall it with "pip uninstall azure".'
        )
    except AttributeError:
        pass
except ImportError:
    pass


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
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    install_requires=[
        "azure-core<2.0.0,>=1.2.2",
        "six>=1.11.0",
        "aiohttp"
    ],
    extras_require={":python_version<'3.0'": ["azure-iot-nspkg"]},
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3*, !=3.4.*",
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
    zip_safe=False,
)
