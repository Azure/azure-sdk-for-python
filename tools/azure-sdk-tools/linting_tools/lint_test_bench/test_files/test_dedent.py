# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------

# This code violates do-not-hardcode-dedent

def function_foo1(x, y, z):
    """docstring

    :param x: x
    :type x: int
    :param y: y
    :type y: int
    :param z: z
    :type z: int
    :return: int sum
    :rtype: int
    .. admonition:: Example:
        This is Example content.
        Should support multi-line.
        Can also include file:

        .. literalinclude:: ../samples/sample_authentication.py 
                 :start-after: [START auth_from_connection_string] 
                 :end-before: [END auth_from_connection_string] 
                 :language: python 
                 :dedent: 8 
    """
    return x + y + z
