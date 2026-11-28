# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Prepare Python wrapper requests and turn backend responses into customer results.

When a customer app reads order "order-42", the public container method passes
its arguments to ItemHelper. On the Rust path, the flow is:

    customer app -> Python wrapper builds PreparedRequest
    -> BindingAdapter calls the binding -> Rust driver uses the service backend
    -> Python wrapper parses BackendResponse -> customer app receives the result

Request builders and parsers do not perform network I/O. Operation helpers
also invoke the selected Python backend; a synchronous invocation can wait for
service I/O. The asynchronous helpers reuse preparation and parsing, then await
their own execution calls.

For feeds, the customer app receives a pager. Its page iterator builds prepared
page requests and consumes backend pages. Retained paging also keeps a feed
cursor; stateless paging does not, although continuation tokens and shared
driver resources can still be used.

Some migration helpers still use the legacy connection. LegacyItemHelper is
selected explicitly for migration comparisons. Unsupported Rust requests fail
before execution. Preflight, execution, parsing, and callback failures never
authorize legacy replay.
"""
