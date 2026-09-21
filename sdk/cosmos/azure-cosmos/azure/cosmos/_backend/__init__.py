# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Connect Python SDK operations to Rust or the existing Python implementation.

The customer app calls the SDK's public methods. The SDK prepares the inputs,
then uses a backend object selected when the client was constructed. The Rust
backend calls a binding: the compiled extension that lets Python call the Rust
driver. The driver handles connections and sends requests to the service backend.

Rust calls return a status, available headers, body bytes, and diagnostics.
The SDK's response helpers turn these into customer results or exceptions.
These are not necessarily the original HTTP headers: the driver and binding
may omit headers or build values from the information they retained.

Queries return batches of results called pages. Some fetch each page using a
continuation token, a bookmark for the next request. Others also keep a cursor,
a Rust object that stores query progress between fetches.

The existing Python implementation remains for migration work. Its backend
runs a supplied Python function rather than a prepared Rust request. Only
operations allowed by capabilities.py may switch from Rust to that function,
and only before execution. An execution, parsing, or callback failure is
reported, not retried through the other implementation.

Prepared requests include timeout settings. An absolute deadline, measured
with a clock unaffected by wall-clock changes, is passed separately. The
binding call receives the time remaining before that deadline.

Driver creation waits until the first operation. Closing a client releases
its reference; other clients or active operations can keep that driver alive.
Keep the legacy selection and fallback code separate so they can be removed
without changing the Rust request and response handling.
Do not add new operations to the legacy backend.
"""
