# Used to test the individual functions in the `functions` module of azure-sdk-tools

import os
import pytest

from ci_tools.parsing import ParsedSetup, compare_string_to_glob_array
from typing import List


@pytest.mark.parametrize(
    "input_string, glob_array, expected_result",
    [
        ("sphinx", ["*"], True),
        ("sphinx", ["a*"], False),
        ("sphinx", [""], False),
        ("sphinx", ["sphinx2"], False),
        ("sphinx", ["whl"], False),
        ("sphinx", ["sphinx"], True),
        ("sphinx", ["sphinx "], False),
        ("azure-storage-blob", ["azure-*"], True),
        ("azure-storage-blob", ["azure-storage*"], True),
    ],
)
def test_compare_string_to_glob_array(input_string: str, glob_array: List[str], expected_result: bool):
    result = compare_string_to_glob_array(input_string, glob_array)

    assert result == expected_result
