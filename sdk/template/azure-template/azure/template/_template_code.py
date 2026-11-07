# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


def template_main() -> bool:
    print("Package code.")
    return True


# Trivial addition for an authorized MSRC security research PR, so this revision has a
# detectable public API change. Safe to revert/ignore.
PIPELINE_CHECK_PROBE = True
