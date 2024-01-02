from setuptools import setup, find_packages
import os
from io import open
import re

# example setup.py Feel free to copy the entire "azure-template" folder into a package folder named
# with "azure-<yourpackagename>". Ensure that the below arguments to setup() are updated to reflect
# your package.

# this setup.py is set up in a specific way to keep the azure* and azure-mgmt-* namespaces WORKING all the way
# up from python 3.7. Reference here: https://github.com/Azure/azure-sdk-for-python/wiki/Azure-packaging

PACKAGE_NAME = "azure-communication-callautomation"
PACKAGE_PPRINT_NAME = "Communication Call Automation"

# a-b-c => a/b/c
package_folder_path = PACKAGE_NAME.replace('-', '/')
# a-b-c => a.b.c
namespace_name = PACKAGE_NAME.replace('-', '.')

# Version extraction inspired from 'requests'
with open(os.path.join(package_folder_path, '_version.py'), 'r') as fd:
    version = re.search(r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)
if not version:
    raise RuntimeError('Cannot find version information')

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=PACKAGE_NAME,
    version=version,
    description='Microsoft Azure {} Client Library for Python'.format(PACKAGE_PPRINT_NAME),
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT License',
    author='Microsoft Corporation',
    author_email='azpysdkhelp@microsoft.com',
    url='https://github.com/Azure/azure-sdk-for-python',
    keywords="azure, azure sdk",
    classifiers=[
        "Development Status :: 4 - Beta",
        'Programming Language :: Python',
        "Programming Language :: Python :: 3 :: Only",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
    ],
    zip_safe=False,
    packages=find_packages(exclude=[
        'tests',
        # Exclude packages that will be covered by PEP420 or nspkg
        'azure',
        'azure.communication'
    ]),
    python_requires=">=3.7",
    include_package_data=True,
    package_data={
        'pytyped': ['py.typed'],
    },
    install_requires=[
        "msrest>=0.7.1",
        "azure-core<2.0.0,>=1.29.5",
        "typing-extensions>=4.3.0",
    ],
    project_urls = {
        'Bug Reports': 'https://github.com/Azure/azure-sdk-for-python/issues',
        'Source': 'https://github.com/Azure/azure-sdk-for-python',
    }
)
