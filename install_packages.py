#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
#
# This script supports discovery and installation of Azure SDK packages
# from both traditional setup.py and modern pyproject.toml configurations.
#
# Package Discovery:
# - Finds packages with setup.py at root or in sdk/*/ directories
# - Finds packages with pyproject.toml at root or in sdk/*/ directories
#
# Installation Logic:
# - Packages with pyproject.toml containing [project] section:
#   Installed using pip (PEP 621 compliant)
# - Packages with setup.py:
#   Installed using traditional setuptools via runpy
# - Packages with both setup.py and pyproject.toml (without [project]):
#   Prefer setup.py for backward compatibility
#--------------------------------------------------------------------------

import os.path
import glob
import copy
import sys
import runpy
import subprocess

def main():
    root_folder = os.path.abspath(os.path.dirname(__file__))

    # pull in any packages that exist in the root directory
    # Support both setup.py and pyproject.toml packages
    packages = {('.', os.path.dirname(p)) for p in glob.glob('azure*/setup.py')}
    packages.update({('.', os.path.dirname(p)) for p in glob.glob('azure*/pyproject.toml')})
    # Handle the SDK folder as well
    packages.update({tuple(os.path.dirname(f).rsplit(os.sep, 1)) for f in glob.glob('sdk/*/azure*/setup.py')})
    packages.update({tuple(os.path.dirname(f).rsplit(os.sep, 1)) for f in glob.glob('sdk/*/azure*/pyproject.toml')})
    # [(base_folder, package_name), ...] to {package_name: base_folder, ...}
    packages = {package_name: base_folder for (base_folder, package_name) in packages}

    # Extract nspkg and sort nspkg by number of "-"
    nspkg_packages = [p for p in packages.keys() if "nspkg" in p]
    nspkg_packages.sort(key = lambda x: len([c for c in x if c == '-']))

    # Meta-packages to ignore
    meta_package = ['azure-keyvault', 'azure-mgmt', 'azure', 'azure-storage']

    # content packages are packages that are not meta nor nspkg
    content_package = sorted([p for p in packages.keys() if p not in meta_package+nspkg_packages])

    # Move azure-common at the beginning, it's important this goes first
    if "azure-common" in content_package:
        content_package.remove("azure-common")
        content_package.insert(0, "azure-common")

    # Package final:
    if "install" in sys.argv:
        packages_for_installation = content_package
    else:
        packages_for_installation = nspkg_packages + content_package

    for pkg_name in packages_for_installation:
        pkg_setup_folder = os.path.join(root_folder, packages[pkg_name], pkg_name)
        pkg_setup_path = os.path.join(pkg_setup_folder, 'setup.py')
        pkg_pyproject_path = os.path.join(pkg_setup_folder, 'pyproject.toml')

        try:
            saved_dir = os.getcwd()
            saved_syspath = sys.path

            os.chdir(pkg_setup_folder)
            sys.path = [pkg_setup_folder] + copy.copy(saved_syspath)

            # Determine which file to use: pyproject.toml with [project] or setup.py
            use_pyproject = False
            if os.path.exists(pkg_pyproject_path):
                # Check if pyproject.toml has [project] section using TOML parser
                try:
                    # Use tomllib for Python 3.11+, fallback to tomli for older versions
                    try:
                        import tomllib as toml
                    except ImportError:
                        import tomli as toml
                    
                    with open(pkg_pyproject_path, 'rb') as f:
                        pyproject_data = toml.load(f)
                        if 'project' in pyproject_data:
                            use_pyproject = True
                except Exception:
                    # If parsing fails, fallback to setup.py if available
                    pass
            
            if use_pyproject:
                # Use pip to install pyproject.toml-based packages
                # Map setup.py commands to pip commands
                if "install" in sys.argv:
                    print("Start ", pkg_pyproject_path)
                    cmd = [sys.executable, '-m', 'pip', 'install', '.']
                elif "develop" in sys.argv or any(arg in sys.argv for arg in ['-e', '--editable']):
                    print("Start ", pkg_pyproject_path)
                    cmd = [sys.executable, '-m', 'pip', 'install', '-e', '.']
                else:
                    # For other commands like --version, --help, etc., skip pyproject.toml packages
                    # These commands are meant for the root setup.py, not individual packages
                    continue
                
                result = subprocess.run(cmd, cwd=pkg_setup_folder, capture_output=False)
                if result.returncode != 0:
                    print(f"Warning: Package {pkg_name} installation returned non-zero exit code", file=sys.stderr)
            elif os.path.exists(pkg_setup_path):
                # Use the traditional setup.py approach
                print("Start ", pkg_setup_path)
                result = runpy.run_path(pkg_setup_path)
            else:
                print(f"Warning: No setup.py or pyproject.toml found for {pkg_name}", file=sys.stderr)
        except Exception as e:
            print(e, file=sys.stderr)
        finally:
            os.chdir(saved_dir)
            sys.path = saved_syspath

if __name__ == '__main__':
    main()
