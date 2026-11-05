# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Compatibility imports for retained local comparison tests."""

from config.provisioning import (
    _create_or_reconcile as _create_or_reconcile,
    _verify_database_throughput as _verify_database_throughput,
    create_owned_container as create_owned_container,
    create_owned_database as create_owned_database,
    time as time,
)
