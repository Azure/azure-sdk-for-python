from setuptools import setup, find_packages
import os
from io import open
import re


PACKAGE_NAME = "azure-eventhub-checkpointstoretable"
PACKAGE_PPRINT_NAME = "Event Hubs checkpointer implementation with Azure Table Storage"

package_folder_path = "azure/eventhub/extensions/checkpointstoretable"

namespace_name = "azure.eventhub.extensions.checkpointstoretable"

# Version extraction inspired from 'requests'
with open(os.path.join(package_folder_path, "_version.py"), "r") as fd:
    version = re.search(r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)
if not version:
    raise RuntimeError("Cannot find version information")

with open('README.md') as f:
    readme = f.read()
with open('CHANGELOG.md') as f:
    changelog = f.read()

setup(
    name=PACKAGE_NAME,
    version=version,
    description="Microsoft Azure {} Client Library for Python".format(PACKAGE_PPRINT_NAME),
    # ensure that these are updated to reflect the package owners' information
    long_description=readme + '\n\n' + changelog,
    long_description_content_type="text/markdown",
    url="https://github.com/Azure/azure-sdk-for-python",
    author="Microsoft Corporation",
    author_email="azuresdkengsysadmins@microsoft.com",
    license="MIT License",
    # ensure that the development status reflects the status of your package
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
    ],
    packages=find_packages(
        exclude=[
            "tests",
            "samples",
            # Exclude packages that will be covered by PEP420 or nspkg
            # This means any folder structure that only consists of a __init__.py.
            # For example, for storage, this would mean adding 'azure.storage'
            # in addition to the default 'azure' that is seen here.
            "azure",
            "azure.eventhub",
            "azure.eventhub.extensions",
        ]
    ),
    install_requires=[
        # dependencies for the vendored storage tables
        "azure-core<2.0.0,>=1.14.0",
        "msrest>=0.6.19",
        # end of dependencies for the vendored storage tables
        'azure-eventhub<6.0.0,>=5.0.0',
    ],
    extras_require={
        ":python_version<'3.0'": ['futures', 'azure-data-nspkg<2.0.0,>=1.0.0'],
        ":python_version<'3.4'": ['enum34>=1.0.4'],
        ":python_version<'3.5'": ["typing"],
    },
    project_urls={
        "Bug Reports": "https://github.com/Azure/azure-sdk-for-python/issues",
        "Source": "https://github.com/Azure/azure-sdk-python",
    },
)
