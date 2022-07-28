from setuptools import setup, find_packages
import os
from io import open
import re

PACKAGE_NAME = "azure-ai-language-questionanswering"
PACKAGE_PPRINT_NAME = "Question Answering"

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
    long_description_content_type='text/markdown',
    url='https://github.com/Azure/azure-sdk-for-python',
    author='Microsoft Corporation',
    author_email='azuresdkengsysadmins@microsoft.com',

    license='MIT License',
    # ensure that the development status reflects the status of your package
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
    zip_safe=False,
    packages=find_packages(exclude=[
        'tests',
        # Exclude packages that will be covered by PEP420 or nspkg
        # This means any folder structure that only consists of a __init__.py.
        # For example, for storage, this would mean adding 'azure.storage'
        # in addition to the default 'azure' that is seen here.
        'azure',
        'azure.ai',
        'azure.ai.language',
    ]),
    include_package_data=True,
    package_data={
        'pytyped': ['py.typed'],
    },
    install_requires=[
        "azure-core<2.0.0,>=1.24.0",
        'msrest>=0.6.21',
    ],
    project_urls={
        'Bug Reports': 'https://github.com/Azure/azure-sdk-for-python/issues',
        'Source': 'https://github.com/Azure/azure-sdk-python',
    }
)
