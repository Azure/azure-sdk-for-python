# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Prepare Python wrapper requests and turn backend responses into customer results.

When a customer app reads order "order-42", the public container method passes
its arguments to ItemHelper. On the Rust path, the flow is:

    customer app -> Python wrapper builds PreparedRequest
    -> RustBackend calls the binding -> Rust driver uses the service backend
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
selected explicitly, not after a failed Rust operation. Other migration-path
decisions follow their operation's permitted pre-execution fallback rules.
Execution, parsing, and callback failures do not authorize legacy replay.

Use docs/V5/VOCABULARY.md for terminology rather than maintaining another
glossary in this package.
"""
