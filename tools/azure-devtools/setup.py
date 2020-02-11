#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import io
from setuptools import setup


VERSION = "1.2.1"


CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'License :: OSI Approved :: MIT License',
]


DEPENDENCIES = [
    'ConfigArgParse>=0.12.0',
    'six>=1.10.0',
    'vcrpy>=1.11.0,<2.1.0',
]

with io.open('README.rst', 'r', encoding='utf-8') as f:
    README = f.read()

setup(
    name='azure-devtools',
    version=VERSION,
    description='Microsoft Azure Development Tools for SDK',
    long_description=README,
    license='MIT',
    author='Microsoft Corporation',
    author_email='ptvshelp@microsoft.com',
    url='https://github.com/Azure/azure-python-devtools',
    zip_safe=False,
    classifiers=CLASSIFIERS,
    packages=[
        'azure_devtools',
        'azure_devtools.scenario_tests',
        'azure_devtools.ci_tools',
    ],
    extras_require={
        'ci_tools':[
            "PyGithub>=1.40", # Can Merge PR after 1.36, "requests" and tests after 1.40
            "GitPython",
            "requests>=2.0"
        ]
    },
    package_dir={'': 'src'},
    install_requires=DEPENDENCIES,
)
