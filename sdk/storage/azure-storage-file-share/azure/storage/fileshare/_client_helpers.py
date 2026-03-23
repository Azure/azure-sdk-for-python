# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Helpers for the Azure File Share convenience layer clients."""


class _NoOpCredential:
    """No-op credential for the generated client when auth is handled by the convenience layer pipeline."""

    def get_token(self, *args, **kwargs):
        raise RuntimeError("This credential should not be used to get tokens directly.")


def _strip_snapshot_from_url(url):
    """Strip sharesnapshot and snapshot query params from URL.

    The generated client should receive a base URL without snapshot params,
    since snapshots are passed per-operation.
    """
    if "?" not in url:
        return url
    base, qs = url.split("?", 1)
    filtered = "&".join(
        part for part in qs.split("&") if not part.startswith("sharesnapshot=") and not part.startswith("snapshot=")
    )
    return f"{base}?{filtered}" if filtered else base
