# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


# Block blob uploads
MAX_SINGLE_PUT_SIZE = 64 * 1024 * 1024
MAX_BLOCK_SIZE = 4 * 1024 * 1024
MIN_LARGE_BLOCK_UPLOAD_THRESHOLD = 4 * 1024 * 1024 + 1

# Default credentials for Development Storage Service
DEV_ACCOUNT_NAME = 'devstoreaccount1'
DEV_ACCOUNT_SECONDARY_NAME = 'devstoreaccount1-secondary'
DEV_ACCOUNT_KEY = 'Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw=='
