#!/usr/bin/env python

from distutils.core import setup
import setuptools

setup(name='pydocumentdb',
      version='2.2.1-SNAPSHOT',
      description='Azure DocumentDB Python SDK',
      author="Microsoft",
      author_email="askdocdb@microsoft.com",
      maintainer="Microsoft",
      maintainer_email="askdocdb@microsoft.com",
      url="https://github.com/Azure/azure-documentdb-python",
      license='MIT',
      install_requires=['six >=1.6', 'requests>=2.10.0'],
      classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules'
      ],
      packages=setuptools.find_packages(exclude=['test', 'test.*']))
