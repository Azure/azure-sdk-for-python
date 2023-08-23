# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# -------------------------------------------------------------------------

from os.path import isdir

_PREVIEW_ENTRY_POINT_WARNING = "OpenTelemetry Autoinstrumentation is in preview."


def _is_attach_enabled():
    return isdir("/agents/python/")
