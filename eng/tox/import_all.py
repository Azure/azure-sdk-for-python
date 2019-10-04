#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is used to verify package dependency by importing all modules
import os

#get current package name
current_dir = os.path.basename(os.getcwd())
package_name = current_dir.replace('-','.')

#import all modules from current package
import_script_all = 'from {0} import *'.format(package_name)

exec(import_script_all)