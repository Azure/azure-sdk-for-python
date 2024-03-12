# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from setuptools import setup, Extension
from wheel.bdist_wheel import bdist_wheel


class bdist_wheel_abi3(bdist_wheel):
    """Override bdist_wheel tag behavior to add abi3 tag."""
    def get_tag(self):
        python, abi, plat = super().get_tag()

        if python.startswith("cp"):
            return python, "abi3", plat
        return python, abi, plat


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
    keywords="azure, azure sdk",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        "Programming Language :: Python :: 3 :: Only",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
    ],
    zip_safe=False,
    python_requires=">=3.8",
    ext_package='azure.storage.extensions',
    ext_modules=[
        Extension(
            'crc64',
            [os.path.join(package_folder_path, "crc64", "crc64module.c")],
            define_macros=[("Py_LIMITED_API", "3")],
            py_limited_api=True
        ),
    ],
    cmdclass={"bdist_wheel": bdist_wheel_abi3},
)