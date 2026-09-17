# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async helpers that build Cosmos requests and read the replies back.

The public async container and database classes do very little themselves.
They hand the work to a helper in this package. The helper collects the
caller's arguments, turns them into a request, asks a backend to send it,
and turns the reply into the value the caller gets back.

There is one helper per group of operations: single items, containers,
databases, queries, reading every item in a container, and the change feed.
Each has a matching version in the sync helper package. The two versions
make the same decisions; only the waiting differs.

Work that just rearranges data is not copied here. Building a request,
pulling a partition key out of a document, and reading a reply involve no
waiting, so the async helpers call the sync versions directly. That keeps
the rules for what a request looks like in one place.

These helpers are not all at the same stage, and the difference is worth
knowing before reading them. Single items have finished moving: that
helper holds a backend and nothing else. Containers and databases are
still being moved and still reach for the older Python connection
alongside the backend. Expect to see both styles side by side for now.

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
