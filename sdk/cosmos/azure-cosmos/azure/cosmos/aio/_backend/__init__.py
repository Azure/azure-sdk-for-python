# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Execute prepared requests through the asynchronous Python backend.

For a customer app reading "order-42", the Python wrapper builds a
PreparedRequest and calls AsyncRustBackend.execute. AsyncRustBackend calls the
binding and awaits its result; the Rust driver performs the operation against
the service backend. The binding's response tuple is converted to BackendResponse
before a Python response helper parses the body for the customer app.

Page fetches start with PreparedPageRequest. AsyncRustBackend converts it to
PreparedRequest, passes a feed cursor separately when retained paging uses one,
and yields one BackendPage. The page iterator owns subsequent fetches; the
customer-facing pager uses that iterator.

Driver acquisition runs on a worker thread because it can block. The acquired
driver handle identifies a CosmosDriver retained by the binding. Closing the
client releases its acquisition and its use of an async credential bridge,
when present, not another client's resources. An in-flight operation can retain
the CosmosDriver after the last client releases it. There is no separate
Python client-registration table.

An invocation's absolute deadline is passed separately from the prepared
request. Typed request settings can still contain a relative timeout; the
binding call receives the remaining time when a deadline is supplied.

AsyncLegacyBackend and OperationRouting's choice of execution path remain only for
migration. Permitted fallback is chosen before execution, never as a retry of
execution, parsing, or callback failures. The Rust path is the release target.

Terminology follows docs/V5/VOCABULARY.md. See AsyncRustBackend for the separate
rules governing acquisition, cancellation, and the shared close future.
"""
