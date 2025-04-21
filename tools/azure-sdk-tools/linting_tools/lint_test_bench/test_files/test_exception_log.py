# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging

# This code violates do-not-log-exceptions-if-not-debug

def add(a, b):
    """
    Add two numbers together.
    :param a: The first number.
    :param b: The second number.
    :return: The sum of the two numbers.
    """
    logging.debug("Adding %s and %s", a, b)
    try:
        return a + b
    except TypeError as e:
        logging.info(
            "This is a TypeError: %s",
            e,
        )


