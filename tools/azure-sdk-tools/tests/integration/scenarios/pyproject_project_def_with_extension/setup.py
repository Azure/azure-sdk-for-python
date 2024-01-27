import os
from setuptools import Extension, setup

PACKAGE_NAME = "azure-keyvault-keys"
package_folder_path = PACKAGE_NAME.replace('-', '/')

setup(
    ext_package='azure.keyvault.keys',
    ext_modules=[
        Extension(
            'crc64',
            [os.path.join(package_folder_path, "crc64", "crc64module.c")],
            py_limited_api=True
        ),
    ],
)