# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Prepare customer requests in Python and pass them to the Python/Rust binding.

The customer app calls CosmosClient and its database/container objects.
The Python wrapper, including this package, validates values and prepares
requests. RustBinding is a Python wrapper class, despite its name; it calls
the compiled Python/Rust binding, azure.cosmos._rust.

Our team owns the Python wrapper and Python/Rust binding. The binding calls
the Rust driver, maintained by a separate team. The Rust driver manages
connections and sends requests to the service backend, the remote Cosmos DB
service. "SDK" means the complete installed package, not one of these layers.

The binding returns status, available headers, body bytes, and diagnostics.
The Python wrapper converts them into customer results or exceptions.
Headers omitted by the Rust driver or binding cannot be recovered here.

Large results arrive in groups called pages. The Python result iterator
fetches pages as the customer app loops over results. A continuation token
records where a later request should resume. Some queries also keep an
in-memory object in the binding containing their plan and current progress.
That saved query progress is not the same as a continuation token.

Rust is the only backend for the release. This checkout still contains
legacy Python calls and private migration/test controls, not a second
supported customer backend. capabilities.py limits which unmigrated calls
can use that legacy code before execution. Execution, parsing, and callback
failures must not cause a request to be repeated through legacy Python.

The Python wrapper passes the time remaining before an operation's deadline
to the binding. The binding acquires a Rust driver on first use. Closing a
client releases its reference; other clients or operations can keep that
driver alive. Retained legacy routing is removal work, not an extension point.
"""
