# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Internal helpers shared between the core-python and rust backends.

Modules in this package contain pure-function building blocks that
turn user-facing kwargs into the exact bytes that go on the wire.
Both backends consume them, which is how the SDK guarantees byte-for-
byte parity between the two paths.

Nothing in this package depends on a specific backend, the
``CosmosClientConnection``, or the azure-core pipeline. That isolation
is what lets the helpers be unit-tested without a network or an
emulator and reused unchanged once the rust path lands.
"""
