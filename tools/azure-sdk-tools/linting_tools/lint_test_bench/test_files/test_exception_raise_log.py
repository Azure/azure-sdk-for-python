# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import logging

# This code violates do-not-log-raised-errors

def add(a, b):
    """
    Add two numbers together.
    :param a: The first number.
    :type a: int or float
    :param b: The second number.
    :type b: int or float
    :return: The sum of the two numbers.
    """
    logging.debug("Adding %s and %s", a, b)
    try:
        return a + b
    except TypeError as e:
        logging.debug(
            "This is a TypeError: %s",
            e,
        )
        raise e
