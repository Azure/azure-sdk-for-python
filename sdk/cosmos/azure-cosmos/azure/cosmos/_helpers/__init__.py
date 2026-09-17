# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Helpers that build Cosmos requests and read the replies back.

The public client, database, and container classes do very little
themselves. They hand the work to a helper here. The helper collects the
caller's arguments, turns them into a request, asks a backend to send it,
and turns the reply into the value the caller gets back.

Most of this package is small, single-purpose pieces: working out a
resource path, sorting out request options and headers, filling in an item
id the caller left out, turning a document into the bytes that go on the
wire, pulling a partition key out of a document, and reading a reply. None
of them wait on anything, so the async package reuses them as they are
instead of keeping a second copy.

On top of those sit the per-operation helpers, one for each group of work:
single items, containers, databases, queries, reading every item in a
container, the change feed, throughput, and feed ranges.

These are not all at the same stage, and the difference is worth knowing
before reading them. Single items have finished moving: that helper holds
a backend and a little client state, and nothing else. The other groups are
still being moved and still reach for the legacy Python connection, some for
nearly everything they do, some only to find the backend hanging off it.
Expect to see both styles side by side for now.

The legacy item helper is a separate thing again. It uses the legacy
connection on purpose and serves callers who ask for that path by name. It
is not a safety net: a request that fails on the normal path is never
re-sent through it.

The mixture is temporary. As each group finishes moving, its reach into the
legacy connection goes away, and once every group is done the legacy helper
and the legacy connection are deleted outright. The single-item helper shows
where the rest are headed: public class, helper, backend, driver, and
nothing else in the chain. New work should follow that shape rather than
copying the legacy one.

Words used throughout this package, each meaning one thing:

legacy
    The Python implementation that predates the Rust driver. It is being
    removed.
helper
    The code that builds a request, hands it to a backend, and turns the
    reply into what the caller asked for.
point operation
    An operation on a single item, found by its id and partition key: read,
    create, replace, upsert, patch, delete. As opposed to a query or a feed,
    which return many results.
page
    One batch of results from an operation that returns many.
pager
    The object that walks through those pages one at a time. A pager is
    used by one caller at a time, and a failed pager is not replayed; the
    caller starts a new one from the last bookmark it saved.
bookmark
    The marker a caller saves after finishing a page, used to start a new
    pager where the previous one left off.
stateless
    A paged operation where each page is fetched on its own, with nothing
    carried between them.
retained
    A paged operation where a cursor is kept alive between pages. The
    opposite of stateless. It is not related to legacy.
"""
