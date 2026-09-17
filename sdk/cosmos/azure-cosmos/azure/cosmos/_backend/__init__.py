# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Backends that send Cosmos requests and hand back the raw reply.

A backend is the layer that actually talks to the service. There are two
here: one that calls the Rust driver, and one that uses the legacy Python
code. A factory picks between them once, when the client is built, and
nothing above this package has to know which one it got.

Callers pass in a request that is already finished and get back what came
off the wire. Replies come in two shapes: a single reply, or a series of
pages. Backends do not build requests and do not interpret replies; the
helper package does both.

Operations that have finished moving to Rust go straight to the driver.
Operations still being moved go through a wrapper that first works out
which path to use. There are three possible answers: the Rust path can
handle the request, so it does; the Rust path cannot, but the legacy Python
path is allowed to step in for this kind of request, so it does; or neither
can, and the call fails right away with a message naming the option to
remove. That choice is made before anything is sent.

Falling back is a decision, never a recovery. Once a request has been sent,
its outcome stands: a failure while sending, while reading the reply, or
inside the caller's own callback is reported as a failure. It is never
quietly retried against the other path.

A request holds the data to send but not the caller's time limit. The time
limit travels separately, so a request can be built once and still be
subject to how much time is actually left.

Two kinds of cleanup are tracked apart. Closing one client releases that
client's own registration, while a Rust driver shared with other clients
stays alive until the last of them is done with it.

Having two backends is a stage, not the destination. The legacy Python
backend exists only until every operation works on Rust. When that lands,
it is deleted, and so is the wrapper that chooses between paths, because
there will be nothing left to choose between. What remains is the shape
the item path already has: public class, helper, one backend, driver.

So treat anything legacy in here as code with an expiry date. Do not build
on it, do not add operations to it, and do not design around the
possibility of falling back to it.

Words used throughout this package, each meaning one thing:

legacy
    The Python implementation that predates the Rust driver. It is being
    removed.
driver
    The Rust driver. It owns connection pooling, request signing, and
    choosing which region to talk to.
binding
    The layer that lets Python call into the Rust driver.
backend
    The object chosen when the client is built, which sends requests.
dispatch
    Looking up which binding method to call for a given operation. The
    tables that do this live in operations.py.
point operation
    An operation on a single item, found by its id and partition key: read,
    create, replace, upsert, patch, delete. As opposed to a query or a feed,
    which return many results.
page
    One batch of results from an operation that returns many.
stateless
    A paged operation where each page is fetched on its own, with nothing
    carried between them.
retained
    A paged operation where a cursor is kept alive between pages. The
    opposite of stateless. It is not related to legacy.
cursor
    The position the driver keeps while a retained operation is being
    paged through.
"""
