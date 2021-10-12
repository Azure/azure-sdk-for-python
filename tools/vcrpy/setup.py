#!/usr/bin/env python

import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

long_description = open("README.rst", "r").read()


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(self.test_args)
        sys.exit(errno)


install_requires = [
    "PyYAML",
    "wrapt<=1.12.1",
    "six>=1.5",
    'contextlib2; python_version=="2.7"',
    'mock; python_version=="2.7"',
    'yarl; python_version>="3.6"',
    'yarl<1.4; python_version=="3.5"',
]

excluded_packages = ["tests*"]
if sys.version_info[0] == 2:
    excluded_packages.append("vcr.stubs.aiohttp_stubs")

setup(
    name="vcrpy",
    version="3.0.1",
    description=("Automatically mock your HTTP interactions to simplify and " "speed up testing"),
    long_description=long_description,
    author="Kevin McCarthy",
    author_email="me@kevinmccarthy.org",
    url="https://github.com/kevin1024/vcrpy",
    packages=find_packages(exclude=excluded_packages),
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    install_requires=install_requires,
    license="MIT",
    tests_require=["pytest", "mock", "pytest-httpbin"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Testing",
        "Topic :: Internet :: WWW/HTTP",
        "License :: OSI Approved :: MIT License",
    ],
)
