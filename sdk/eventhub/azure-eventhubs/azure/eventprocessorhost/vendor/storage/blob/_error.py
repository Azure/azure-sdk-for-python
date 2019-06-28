# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

_ERROR_PAGE_BLOB_SIZE_ALIGNMENT = \
    'Invalid page blob size: {0}. ' + \
    'The size must be aligned to a 512-byte boundary.'

_ERROR_PAGE_BLOB_START_ALIGNMENT = \
    'start_range must align with 512 page size'

_ERROR_PAGE_BLOB_END_ALIGNMENT = \
    'end_range must align with 512 page size'

_ERROR_INVALID_BLOCK_ID = \
    'All blocks in block list need to have valid block ids.'

_ERROR_INVALID_LEASE_DURATION = \
    "lease_duration param needs to be between 15 and 60 or -1."

_ERROR_INVALID_LEASE_BREAK_PERIOD = \
    "lease_break_period param needs to be between 0 and 60."

_ERROR_NO_SINGLE_THREAD_CHUNKING = \
    'To use blob chunk downloader more than 1 thread must be ' + \
    'used since get_blob_to_bytes should be called for single threaded ' + \
    'blob downloads.'
