# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
logging.basicConfig()

import smoke_test


try:
    import smoke_test_async
except SyntaxError:
    print("\n===================")
    print(" Async not suported")
    print("====================\n")
