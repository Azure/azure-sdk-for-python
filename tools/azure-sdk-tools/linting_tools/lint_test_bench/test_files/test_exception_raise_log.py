# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging

# This code violates do-not-log-raised-errors

try:
    a = "this is doing something here"
    a.get("this")
except TypeError as e:
    logging.debug(
        "This is a TypeError: %s",
        e,
    )
    raise e

