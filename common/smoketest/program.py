# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
logging.basicConfig()

from smoke_test import execute_smoke_tests
execute_smoke_tests()


try:
    from smoke_test_async import execute_async_smoke_tests
    execute_async_smoke_tests()
except SyntaxError:
    print("\n===================")
    print(" Async not suported")
    print("====================\n")
