#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from setuptools import setup
import sys


message = """

Starting with v0.4.0, this package cannot be installed anymore, please use [azure-mgmt-monitor](https://pypi.org/project/azure-mgmt-monitor/) instead.
"""

if "sdist" in sys.argv:
    setup(
        name='azure-monitor',
        version='0.4.0',
        description='Microsoft Azure Monitor library for Python',
        long_description=open('README.md', 'r').read(),
        long_description_content_type='text/markdown',
        license='MIT License',
        author='Microsoft Corporation',
        author_email='azpysdkhelp@microsoft.com',
        url='https://github.com/Azure/azure-sdk-for-python',
        classifiers=[
            'Development Status :: 7 - Inactive',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'License :: OSI Approved :: MIT License',
        ],
        zip_safe=False,
    )
else:
    raise RuntimeError(message)
