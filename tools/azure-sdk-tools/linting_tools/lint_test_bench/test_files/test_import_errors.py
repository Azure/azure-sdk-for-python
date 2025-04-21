# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.core.exceptions import raise_with_traceback
# This code violates no-raise-with-traceback


async def main():
    l = {}
    try:
        l["a"].append(1)
    except TypeError:
        print("An error occurred")
        raise_with_traceback(ValueError("This is a test error"))
