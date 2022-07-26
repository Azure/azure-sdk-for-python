# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

def get_decorator():
    try:
        import uamqp
    except (ImportError, ModuleNotFoundError):
        return [False]
    return [True, False]
