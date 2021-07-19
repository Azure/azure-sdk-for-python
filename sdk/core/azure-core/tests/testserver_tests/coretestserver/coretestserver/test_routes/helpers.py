# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

def assert_with_message(param_name, expected_value, actual_value):
    assert expected_value == actual_value, "Expected '{}' to be '{}', got '{}'".format(
        param_name, expected_value, actual_value
    )

__all__ = ["assert_with_message"]
