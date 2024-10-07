#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from _models import RegexSuppression

def test_regex_suppressions():
    regex_suppression = RegexSuppression(".*")
    assert regex_suppression.match("some_string") == True
    assert regex_suppression.match("another_string") == True

    regex_suppression = RegexSuppression(".*ListResult$")
    assert regex_suppression.match("FooListResult") == True
