#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Used to 
# 


import argparse
import sys
import os

from common_tasks import process_glob_string, run_check_call, str_to_bool, parse_setup
from subprocess import check_call

NAMESPACE_EXTENSION_TEMPLATE = """__path__ = __import__('pkgutil').extend_path(__path__, __name__)  # type: str
"""

CONDA_PKG_SETUP_TEMPLATE = """from setuptools import find_packages, setup

setup(
    name={conda_package_name},
    version={version},
    description='Microsoft Azure SDK For Python {service} Combined Conda Library',
    license='MIT License',
    author='Microsoft Corporation',
    author_email='azpysdkhelp@microsoft.com',
    url='https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/{service}/',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
    ],
    zip_safe=False,
    packages=find_packages(exclude=[ {package_excludes} ]),
    install_requires=[]
)
"""

def create_package(pkg_directory, output_directory):
    check_call([sys.executable, 'setup.py', "sdist", "--format", "zip", '-d', output_directory], cwd=pkg_directory)

def create_sdist_skeleton(build_directory, artifact_name, common_root):
    # clean

    # create existing

    # given the common root, create a folder for each level, populating with a __init__ that has content from 
    # NAMESPACE_EXTENSION_TEMPLATE
    pass

def create_sdist_setup(build_directory, artifact_name, service):
    # populate a setup.py in the root of the build_directory/artifact_name
    # resolve to 0.0.0
    pass

def resolve_common_namespaces(build_directory, artifact_name, common_root):
    pass

def create_combined_sdist(output_directory, build_directory, artifact_name, common_root):
    
    create_sdist_skeleton(build_directory, artifact_name, common_root)
    resolve_common_namespaces(build_directory, artifact_name, common_root)
    create_sdist_setup(build_directory, artifact_name, service)

    print('{}/{}/{}.zip'.format(output_directory, artifact_name, artifact_name))
    return '{}/{}/{}.zip'.format(output_directory, artifact_name, artifact_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build a Conda Package, given a properly formatted build directory, and input configuration. This script assumes that the build directory has been set up w/ the necessary sdists in each location."
    )

    parser.add_argument(
        "-d",
        "--distribution-directory",
        dest="distribution_directory",
        help="The output conda sdist will be dropped into this directory under a folder named the same as argument artifact_name.",
        required=True,
    )

    parser.add_argument(
        "-b",
        "--build-directory",
        dest="build_directory",
        help="The 'working' directory. This top level path will contain all the necessary sdist code from the appropriate historical tag. EG: <build-directory>/azure-storage-blob, <build-directory/azure-storage-queue",
        required=True,
    )

    parser.add_argument(
        "-m",
        "--meta-yml",
        dest="meta_yml",
        help="The path to the meta yaml that will be used to generate this conda distribution.",
        required=True,
    )

    parser.add_argument(
        "-r",
        "--common_root",
        dest="common_root",
        help="The common root namespace. For instance, when outputting the artifact 'azure-storage', the common root will be azure/storage.",
        required=False,
    )

    parser.add_argument(
        "-n",
        "--artifact_name",
        dest="artifact_name",
        help="The name of the output conda package.",
        required=True,
    )

    parser.add_argument(
        "-o",
        "--output_var",
        dest="output_var",
        help="The name of the environment variable that will be set in azure devops. The contents will be the final location of the output artifact. Local users will need to grab this value and set their env manually.",
        required=False,
    )

    args = parser.parse_args()
    output_source_location = create_combined_sdist(output_directory, args.build_directory, args.artifact_name, args.common_root)

    if args.output_var:
        print("##vso[task.setvariable variable={}]{}".format(args.output_var, output_source_location))