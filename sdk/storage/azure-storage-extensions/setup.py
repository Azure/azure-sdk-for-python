# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import glob
from setuptools import setup, Extension

PACKAGE_NAME = "azure-storage-extensions"
PACKAGE_PPRINT_NAME = "Azure Storage Extensions"

package_folder_path = PACKAGE_NAME.replace('-', '/')

setup(
    name=PACKAGE_NAME,
    version="1.0.0b1",
    include_package_data=True,
    description=PACKAGE_PPRINT_NAME,
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    license='MIT License',
    author='Microsoft Corporation',
    author_email='ascl@microsoft.com',
    url='https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-extensions',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
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
    python_requires=">=3.7",
    ext_package='azure.storage.extensions',
    ext_modules=[
        Extension('crc64', glob.glob(os.path.join(package_folder_path, 'crc64', '*.c')))
    ],
)
