# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from ._receipt_verification import verify_receipt
from ._claims_digest_computation import compute_claims_digest

__all__ = ["verify_receipt", "compute_claims_digest"]
