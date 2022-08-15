#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import sys
from setuptools import setup

# azure v0.x is not compatible with this package
# azure v0.x used to have a __version__ attribute (newer versions don't)
try:
    import azure
    try:
        ver = azure.__version__
        raise Exception(
            'This package is incompatible with azure=={}. '.format(ver) +
            'Uninstall it with "pip uninstall azure".'
        )
    except AttributeError:
        pass
except ImportError:
    pass

PACKAGES = []
# Do an empty package on Python 3 and not python_requires, since not everybody is ready
# https://github.com/Azure/azure-sdk-for-python/issues/3447
# https://github.com/Azure/azure-sdk-for-python/issues/3481
if sys.version_info[0] < 3:
    PACKAGES = ['azure.ai.language']

setup(
    name='azure-ai-language-nspkg',
    version='1.1.0b1',
    description='Microsoft Azure ai-language Namespace Package [Internal]',
    long_description=open('README.md', 'r').read(),
    license='MIT License',
    author='Microsoft Corporation',
    author_email='azpysdkhelp@microsoft.com',
    url='https://github.com/Azure/azure-sdk-for-python',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
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
    zip_safe=False,
    packages=PACKAGES,
    install_requires=[
        'azure-ai-nspkg>=1.0.0'
    ]
)
