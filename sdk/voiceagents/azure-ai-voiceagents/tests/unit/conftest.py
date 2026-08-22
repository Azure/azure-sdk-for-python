# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Test configuration for the unit test package.

Ensures the unit test directory is importable so tests can share the local
``_mock_transport`` helper module regardless of the pytest invocation directory.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
