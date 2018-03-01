# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import sys

# Ignore collection of async tests for Python 2
collect_ignore = []
if sys.version_info < (3,6):
    collect_ignore.append("test_mgmt_storage_async.py")
