# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Prepare customer app requests in Python and pass them to the binding.

The customer app calls CosmosClient and its database/container objects.
The Python wrapper, including this package, validates values and prepares
requests. RustBackend is the Python execution component that calls the
binding through azure.cosmos._rust.

The binding calls the Rust driver library.
The Rust driver manages connections and sends requests to the service backend,
the remote Cosmos DB service.

The binding returns status, available headers, body bytes, and diagnostics.
The Python wrapper converts them into customer results or exceptions.

Feed results arrive in pages; a feed can also finish in one page. The customer
app uses a pager, such as ItemPaged, whose page iterator fetches those pages.

Capabilities.py limits which requests may use the legacy path
before execution. Execution, parsing, and callback failures must not cause
a request to be repeated through the legacy path.

The Python wrapper passes the time remaining before an operation's deadline
to the binding. On first use, RustBackend acquires a driver handle identifying
a retained CosmosDriver object. Closing a client releases its acquisition;
other clients or operations can keep that CosmosDriver alive.


"""
