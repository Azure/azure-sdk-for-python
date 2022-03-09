# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# Fixture
from testcase import load_registry

def pytest_configure(config):
    config.addinivalue_line("usefixtures", "load_registry")
