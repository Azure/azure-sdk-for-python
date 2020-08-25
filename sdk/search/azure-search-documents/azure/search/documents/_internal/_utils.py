# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
def is_retryable_status_code(status_code):
    # type: (int) -> bool
    return status_code in [422, 409, 503]
