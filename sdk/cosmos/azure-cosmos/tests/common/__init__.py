# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Shared migration-test support.

Test functions and methods under tests/<folder>/ use the suffix ``_rust``,
except workloads. Root legacy tests keep their original names.

The suffix labels the migration suite, not its execution backend: these
folders also contain mixed-backend comparisons and Python-only unit tests.
Inspect backend parameters to identify which backend a failing case used.
"""
