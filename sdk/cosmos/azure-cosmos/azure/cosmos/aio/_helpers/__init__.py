# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async siblings of the helpers in ``azure/cosmos/_helpers``.

The pure-data helpers (`_options`, `_pk_wire`, `_body_wire`,
`_auto_id`, `_container_rid`, `_request_prep`) hold no I/O, so they
do not need async variants and the async code reaches into the sync
package directly. Only ``ItemHelper`` lives twice â—” once here for the
async path, once in the sync sibling â—” because its ``create_item``
method awaits the async ``client_connection.CreateItem`` and the
async cache-refresh.
"""
