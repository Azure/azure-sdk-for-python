from setuptools import setup, find_packages
import os
from io import open
import re

# example setup.py Feel free to copy the entire "azure-template" folder into a package folder named 
# with "azure-<yourpackagename>". Ensure that the below arguments to setup() are updated to reflect 
# your package.

# this setup.py is set up in a specific way to keep the azure* and azure-mgmt-* namespaces WORKING all the way 
# up from python 2.7. Reference here: https://github.com/Azure/azure-sdk-for-python/wiki/Azure-packaging

PACKAGE_NAME = "azure-template"
PACKAGE_PPRINT_NAME = "Template Package"

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

    # ensure that these are updated to reflect the package owners' information
    long_description=long_description,
    url='https://github.com/Azure/azure-sdk-for-python',
    author='Microsoft Corporation',
    author_email='azuresdkengsysadmins@microsoft.com',

    license='MIT License',
    # ensure that the development status reflects the status of your package
    classifiers=[
        "Development Status :: 5 - Production/Stable",

        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
    ],
    packages=find_packages(exclude=[
        'tests',
        # Exclude packages that will be covered by PEP420 or nspkg
        'azure'
    ]),
    install_requires=[
        #'msrest>=0.5.0',
        #'msrestazure>=0.4.32,<2.0.0',
        #'azure-common~=1.1',
    ],
    extras_require={
        ":python_version<'3.0'": ['azure-nspkg'],
    },
    project_urls={
        'Bug Reports': 'https://github.com/Azure/azure-sdk-for-python/issues',
        'Source': 'https://github.com/Azure/azure-sdk-python',
    }
)
