#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

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

setup(
    name='azure-cognitiveservices-nspkg',
    version='3.0.0',
    description='Microsoft Azure Cognitive Services Namespace Package [Internal]',
    long_description=open('README.rst', 'r').read(),
    license='MIT License',
    author='Microsoft Corporation',
    author_email='azpysdkhelp@microsoft.com',
    url='https://github.com/Azure/azure-sdk-for-python',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: MIT License',
    ],
    zip_safe=False,
    packages=[
        'azure.cognitiveservices',
    ],
    python_requires='<3',
    install_requires=[
        'azure-nspkg>=3.0.0',
    ]
)
