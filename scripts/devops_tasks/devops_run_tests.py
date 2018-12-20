#!/usr/bin/env python

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Assumptions when running this script:
#  You are running in the root directory of azure-sdk-for-python repo clone

def devops_run_tests(globString, python_console_name):
    individual_globs = globString.split(',')


