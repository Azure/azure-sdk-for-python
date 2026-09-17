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
still being moved and still reach for the older Python connection, some for
nearly everything they do, some only to find the backend hanging off it.
Expect to see both styles side by side for now.

The legacy item helper is a separate thing again. It uses the older
connection on purpose and serves callers who ask for that path by name. It
is not a safety net: a request that fails on the normal path is never
re-sent through it.

The mixture is temporary. As each group finishes moving, its reach into the
older connection goes away, and once every group is done the legacy helper
and the older connection are deleted outright. The single-item helper shows
where the rest are headed: public class, helper, backend, driver, and
nothing else in the chain. New work should follow that shape rather than
copying the older one.
"""
