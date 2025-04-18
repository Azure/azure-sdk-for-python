# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging

# This code violates do-not-log-exceptions-if-not-debug

try:
    a = "this is doing something here"
except TypeError as e:
    logging.info(
        "This is a TypeError: %s",
        e,
    )


