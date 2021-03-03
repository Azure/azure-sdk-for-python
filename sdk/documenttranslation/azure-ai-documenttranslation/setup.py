from setuptools import setup, find_packages
import os
from io import open
import re

PACKAGE_NAME = "azure-ai-documenttranslation"
PACKAGE_PPRINT_NAME = "Document Translation Package"

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
        "Development Status :: 4 - Beta",

        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
    ],
    packages=find_packages(exclude=[
        'tests',
        # Exclude packages that will be covered by PEP420 or nspkg
        'azure',
        'azure.ai',
    ]),
    install_requires=[
        "azure-core<2.0.0,>=1.8.2",
        "msrest>=0.6.21",
        'six>=1.11.0',
        'azure-common~=1.1',
    ],
    extras_require={
        ":python_version<'3.0'": ['azure-ai-nspkg'],
        ":python_version<'3.5'": ['typing'],
    },
    project_urls={
        'Bug Reports': 'https://github.com/Azure/azure-sdk-for-python/issues',
        'Source': 'https://github.com/Azure/azure-sdk-python',
    }
)
