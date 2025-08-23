# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import sys
import unittest


class ExtendedTestCase(unittest.TestCase):
    """Extended tests method for Azure SDK"""

    def assertNamedItemInContainer(self, container, item_name, msg=None):
        for item in container:
            if item.name == item_name:
                return

        standardMsg = "{0} not found in {1}".format(repr(item_name), repr(container))
        self.fail(self._formatMessage(msg, standardMsg))

    def assertNamedItemNotInContainer(self, container, item_name, msg=None):
        for item in container:
            if item.name == item_name:
                standardMsg = "{0} unexpectedly found in {1}".format(repr(item_name), repr(container))
                self.fail(self._formatMessage(msg, standardMsg))
