# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Request preparation, Rust coordinators, and explicit migration adapters.

Rust item preparation uses transport-independent option, path, partition-key,
and serialization utilities. Its coordinator receives a backend and narrow
client state, never a legacy connection. Public compatibility utilities may be
shared with legacy, with dependency direction from legacy into those utilities.

The separate legacy item adapter and still-migrating families retain Python
connection/pipeline dependencies. They are not fallback ports for Rust items.
"""
