#!/usr/bin/env python

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


import os
import re

from setuptools import find_packages, setup

# Change the PACKAGE_NAME only to change folder and different name
PACKAGE_NAME = "azure-monitor-opentelemetry"
PACKAGE_PPRINT_NAME = "Azure Monitor Opentelemetry Distro"

# a-b-c => a/b/c
package_folder_path = PACKAGE_NAME.replace("-", "/")


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

# Version extraction inspired from 'requests'
with open(os.path.join(package_folder_path, "_version.py"), "r") as fd:
    version = re.search(
        r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    ).group(1)

if not version:
    raise RuntimeError("Cannot find version information")

setup(
    name=PACKAGE_NAME,
    version=version,
    description="Microsoft {} Client Library for Python".format(
        PACKAGE_PPRINT_NAME
    ),
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    license="MIT License",
    author="Microsoft Corporation",
    author_email="ascl@microsoft.com",
    url="https://github.com/microsoft/ApplicationInsights-Python/tree/main/azure-monitor-opentelemetry",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
    ],
    zip_safe=False,
    packages=find_packages(
        exclude=[
            "tests",
            "samples",
            # Exclude packages that will be covered by PEP420 or nspkg
            "azure",
            "azure.monitor",
        ]
    ),
    include_package_data=True,
    package_data={
        "pytyped": ["py.typed"],
    },
    python_requires=">=3.7",
    install_requires=[
        "azure-core<2.0.0,>=1.24.0",
        "azure-core-tracing-opentelemetry~=1.0.0b10",
        "azure-monitor-opentelemetry-exporter~=1.0.0b15",
        "opentelemetry-api~=1.19.0",
        "opentelemetry-instrumentation-django~=0.40b0",
        "opentelemetry-instrumentation-fastapi~=0.40b0",
        "opentelemetry-instrumentation-flask~=0.40b0",
        "opentelemetry-instrumentation-psycopg2~=0.40b0",
        "opentelemetry-instrumentation-requests~=0.40b0",
        "opentelemetry-instrumentation-urllib~=0.40b0",
        "opentelemetry-instrumentation-urllib3~=0.40b0",
        "opentelemetry-sdk~=1.19.0",
        "wrapt >= 1.14.0, < 2.0.0",
    ],
    entry_points={
        "opentelemetry_distro": [
            "azure_monitor_opentelemetry_distro = azure.monitor.opentelemetry.autoinstrumentation._distro:AzureMonitorDistro"
        ],
        "opentelemetry_configurator": [
            "azure_monitor_opentelemetry_configurator = azure.monitor.opentelemetry.autoinstrumentation._configurator:AzureMonitorConfigurator"
        ],
    },
)
