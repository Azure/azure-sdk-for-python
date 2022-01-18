#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import sys
from setuptools import setup


PACKAGES = []
# Do an empty package on Python 3 and not python_requires, since not everybody is ready
# https://github.com/Azure/azure-sdk-for-python/issues/3447
# https://github.com/Azure/azure-sdk-for-python/issues/3481
if sys.version_info[0] < 3:
    PACKAGES = ['azure.mgmt.datalake']

setup(
    name='azure-mgmt-datalake-nspkg',
    version='3.0.1',
    description='Microsoft Azure Data Lake Management Namespace Package [Internal]',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    license='MIT License',
    author='Microsoft Corporation',
    author_email='azpysdkhelp@microsoft.com',
    url='https://github.com/Azure/azure-sdk-for-python',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
    ],
    zip_safe=False,
    packages=PACKAGES,
    install_requires=[
        'azure-mgmt-nspkg>=3.0.0',
    ],
)
