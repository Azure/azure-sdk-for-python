# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# This code violates docstring-admonition-needs-newline
class DeadClient():
    def get_function(self, x: int) -> int:
        """
        :param x: This is a parameter
        :type x: int
        :return: int y
        :rtype: int

        docstring
        
        .. admonition:: Example:
        
            This is Example content.
            Should support multi-line.
            Can also include file:
            .. literalinclude:: ../samples/sample_detect_language.py
        """
        y = x + 1
        return y
