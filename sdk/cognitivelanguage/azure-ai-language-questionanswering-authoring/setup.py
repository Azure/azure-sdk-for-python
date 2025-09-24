from setuptools import setup, find_packages
import os
import re
from io import open

PACKAGE_NAME = "azure-ai-language-questionanswering-authoring"
PACKAGE_PPRINT_NAME = "Question Answering Authoring"

package_folder_path = PACKAGE_NAME.replace('-', '/')
namespace_name = PACKAGE_NAME.replace('-', '.')

version_file = os.path.join(package_folder_path, "_version.py")
with open(version_file, 'r', encoding='utf-8') as fd:
    version = re.search(r'^VERSION\\s*=\\s*[\'\"]([^\'\"]*)[\'\"]', fd.read(), re.MULTILINE).group(1)
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
    url='https://github.com/Azure/azure-sdk-for-python',
    keywords=["azure", "cognitive services", "language", "question answering", "authoring"],
    author='Microsoft Corporation',
    author_email='azuresdkengsysadmins@microsoft.com',
    license='MIT License',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.9",
    zip_safe=False,
    packages=find_packages(exclude=[
        'tests',
        'azure',
        'azure.ai',
        'azure.ai.language',
        'azure.ai.language.questionanswering',
    ]),
    include_package_data=True,
    package_data={
        'azure.ai.language.questionanswering.authoring': ['py.typed'],
    },
    install_requires=[
        "azure-core>=1.28.0",
        "isodate>=0.6.1",
        "typing-extensions>=4.0.1; python_version<'3.11'",
    ],
    project_urls={
        'Bug Reports': 'https://github.com/Azure/azure-sdk-for-python/issues',
        'Source': 'https://github.com/Azure/azure-sdk-for-python',
    }
)
