# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Prepare requests and await execution for the asynchronous Python wrapper.

For a customer app reading "order-42", AsyncItemHelper uses the shared Python
request builder, awaits AsyncRustBackend.execute, and parses its BackendResponse.
AsyncRustBackend calls the binding; the Rust driver performs the operation
against the service backend. The helper does not call the Rust driver directly.

Request builders, parsers, and paging state records come from azure.cosmos._helpers
where their rules are shared. These async helpers add the awaits and the
operation-specific handling of deadlines and cancellation. Response hooks are
ordinary Python calls here, not awaited calls.

Feed methods return a pager. Its async page iterator fetches backend pages and
keeps its own progress. Retained paging also keeps a feed cursor; stateless
paging uses continuation tokens without keeping a feed cursor. Constructing
the pager does not fetch its first page.

AsyncItemHelper retains the Python backend, client defaults, and response-header
state. Some other migration helpers also retain the legacy connection.
AsyncLegacyItemHelper is selected explicitly, not after a failed Rust operation.
Other permitted fallback decisions happen before execution.

Use docs/V5/VOCABULARY.md for terminology. The matching synchronous helper
explains shared preparation; each async helper explains differences that matter
for waiting, callbacks, or cancellation.
"""
