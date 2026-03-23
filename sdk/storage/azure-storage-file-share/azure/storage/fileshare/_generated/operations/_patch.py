# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import functools

from . import _operations


__all__: list[str] = []  # Add all objects you want publicly available to users at this package level


# ---------------------------------------------------------------------------
# Emitter bug fixes applied via patch_sdk()
#
# 1. Trailing slash: The emitter generates _url = "/" for @route("") which
#    creates a trailing slash when combined with the base URL. Fix: change
#    _url from "/" to "" in the affected build_*_request functions.
#
# 2. Missing Accept header: Operations using StorageOperationNoBody (no
#    response body) don't get an Accept header generated, even though error
#    responses are XML. Fix: set Accept: application/xml as the default.
# ---------------------------------------------------------------------------

# Build functions that generate _url = "/" (trailing slash bug)
_TRAILING_SLASH_FUNCTIONS = [
    "build_file_create_request",
    "build_file_download_request",
    "build_file_get_properties_request",
    "build_file_delete_request",
    "build_file_start_copy_request",
]

# Build functions missing Accept header
_MISSING_ACCEPT_FUNCTIONS = [
    "build_service_set_properties_request",
    "build_share_create_request",
    "build_share_get_properties_request",
    "build_share_delete_request",
    "build_share_acquire_lease_request",
    "build_share_release_lease_request",
    "build_share_change_lease_request",
    "build_share_renew_lease_request",
    "build_share_break_lease_request",
    "build_share_create_snapshot_request",
    "build_share_create_permission_request",
    "build_share_set_properties_request",
    "build_share_set_metadata_request",
    "build_share_set_access_policy_request",
    "build_share_restore_request",
    "build_directory_create_request",
    "build_directory_get_properties_request",
    "build_directory_delete_request",
    "build_directory_set_properties_request",
    "build_directory_set_metadata_request",
    "build_directory_force_close_handles_request",
    "build_directory_rename_request",
    "build_file_create_request",
    "build_file_get_properties_request",
    "build_file_delete_request",
    "build_file_set_http_headers_request",
    "build_file_set_metadata_request",
    "build_file_acquire_lease_request",
    "build_file_release_lease_request",
    "build_file_change_lease_request",
    "build_file_break_lease_request",
    "build_file_upload_range_request",
    "build_file_upload_range_from_url_request",
    "build_file_start_copy_request",
    "build_file_abort_copy_request",
    "build_file_force_close_handles_request",
    "build_file_rename_request",
    "build_file_create_symbolic_link_request",
    "build_file_get_symbolic_link_request",
    "build_file_create_hard_link_request",
]


def _fix_trailing_slash(build_fn):
    """Wrap a build_*_request function to strip the trailing slash from _url = "/"."""

    @functools.wraps(build_fn)
    def wrapper(*args, **kwargs):
        request = build_fn(*args, **kwargs)
        url = request.url
        if url == "/" or url.startswith("/?"):
            request.url = url[1:]  # Strip leading "/"
        return request

    return wrapper


def _fix_accept_header(build_fn):
    """Wrap a build_*_request function to add Accept: application/xml if missing."""

    @functools.wraps(build_fn)
    def wrapper(*args, **kwargs):
        request = build_fn(*args, **kwargs)
        if "Accept" not in request.headers:
            request.headers["Accept"] = "application/xml"
        return request

    return wrapper


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
    for fn_name in _TRAILING_SLASH_FUNCTIONS:
        original = getattr(_operations, fn_name)
        setattr(_operations, fn_name, _fix_trailing_slash(original))

    for fn_name in _MISSING_ACCEPT_FUNCTIONS:
        original = getattr(_operations, fn_name)
        setattr(_operations, fn_name, _fix_accept_header(original))
