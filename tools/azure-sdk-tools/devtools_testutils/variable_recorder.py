# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING

import pytest

from .proxy_testcase import recorded_test

if TYPE_CHECKING:
    from typing import Any, Dict


class VariableRecorder():
    def __init__(self, variables: "Dict[str, str]") -> None:
        self.variables = variables

    def get_or_record(self, variable: str, default: str) -> str:
        """Returns the recorded value of `variable`, or records and returns `default` as the value for `variable`.

        In recording mode, `get_or_record("a", "b")` will record "b" for the value of the variable `a` and return "b".
        In playback, it will return the recorded value of `a`. This is an analogue of a Python dictionary's `setdefault`
        method: https://docs.python.org/library/stdtypes.html#dict.setdefault.

        :param str variable: The name of the variable to search the value of, or record a value for.
        :param str default: The variable value to record.

        :returns: str
        """
        if not isinstance(default, str):
            raise ValueError('"default" must be a string. The test proxy cannot record non-string variable values.')
        return self.variables.setdefault(variable, default)


@pytest.fixture
def variable_recorder(recorded_test: "Dict[str, Any]") -> "Dict[str, str]":
    """Fixture that invokes the `recorded_test` fixture and returns a dictionary of recorded test variables.

    :param recorded_test: The fixture responsible for redirecting network traffic to target the test proxy.
        This should return a dictionary containing information about the current test -- in particular, the variables
        that were recorded with the test.
    :type recorded_test: Dict[str, Any]

    :returns: A dictionary that maps test variables to string values. If no variable dictionary was stored when the test
        was recorded, this returns an empty dictionary.
    """
    return recorded_test["variables"]
