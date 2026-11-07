# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


def template_main() -> bool:
    print("Package code.")
    return True


# Added as part of an authorized MSRC bug-bounty reachability check (APIView review-generation
# pipeline). Trivial public-API addition only, to give this revision a detectable API surface change.
# See the accompanying PR description. Safe to revert/ignore.
def xcheck_marker() -> str:
    return "MSRC-XCHECK-2026-11-07"
