# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Internal Helper functions in the Azure Cosmos database change_feed service.
"""

import warnings
from datetime import datetime
from typing import Any, Dict, Tuple

# pylint: disable=docstring-keyword-should-match-keyword-only

CHANGE_FEED_MODES = ["LatestVersion", "AllVersionsAndDeletes"]

def add_args_to_kwargs(
        args: Tuple[Any, ...],
        kwargs: Dict[str, Any]
    ) -> None:
    """Add positional arguments(args) to keyword argument dictionary(kwargs).
    Since 'query_items_change_feed' method only allows the following 4 positional arguments in the exact order
    and types, if the order and types don't match, errors will be raised.
    If the positional arguments are in the correct orders and types, the arguments will be added to keyword arguments.

    4 positional arguments:
        - str 'partition_key_range_id': [Deprecated] ChangeFeed requests can be executed against specific partition
            key ranges. This is used to process the change feed in parallel across multiple consumers.
        - bool 'is_start_from_beginning': [Deprecated] Get whether change feed should start from
            beginning (true) or from current (false). By default, it's start from current (false).
        - str 'continuation': e_tag value to be used as continuation for reading change feed.
        - int 'max_item_count': Max number of items to be returned in the enumeration operation.

    :param args: Positional arguments. Arguments must be in the following order:
        1. partition_key_range_id
        2. is_start_from_beginning
        3. continuation
        4. max_item_count
    :type args: Tuple[Any, ...]
    :param kwargs: Keyword arguments
    :type kwargs: dict[str, Any]
    """
    if len(args) > 4:
        raise TypeError(f"'query_items_change_feed()' takes 4 positional arguments but {len(args)} were given.")

    if len(args) > 0:
        keys = [
            'partition_key_range_id',
            'is_start_from_beginning',
            'continuation',
            'max_item_count',
        ]
        for i, value in enumerate(args):
            key = keys[i]

            if key in kwargs:
                raise TypeError(f"'query_items_change_feed()' got multiple values for argument '{key}'.")

            kwargs[key] = value

def validate_kwargs(
        keyword_arguments: Dict[str, Any]
    ) -> None:
    """Validate keyword arguments for change_feed API.
    The values of keyword arguments must match the expected type and conditions. If the conditions do not match,
    errors will be raised with the proper error messages and possible ways to correct the errors.

    :param dict[str, Any] keyword_arguments: Keyword arguments to verify for query_items_change_feed API
        - Literal["LatestVersion", "AllVersionsAndDeletes"] mode: Must be one of the values in the Enum,
            'ChangeFeedMode'. If the value is 'ALL_VERSIONS_AND_DELETES', the following keywords must be in the right
            conditions:
                - 'partition_key_range_id': Cannot be used at any time
                - 'is_start_from_beginning': Must be 'False'
                - 'start_time': Must be "Now"
        - str partition_key_range_id: Deprecated Warning.
        - bool is_start_from_beginning: Deprecated Warning. Cannot be used with 'start_time'.
        - Union[~datetime.datetime, Literal["Now", "Beginning"]] start_time: Must be in supported types.
    """
    # Filter items with value None
    keyword_arguments = {key: value for key, value in keyword_arguments.items() if value is not None}

    # Validate the keyword arguments
    if "mode" in keyword_arguments:
        mode = keyword_arguments["mode"]
        if mode not in CHANGE_FEED_MODES:
            raise ValueError(
                f"Invalid mode was used: '{keyword_arguments['mode']}'."
                f" Supported modes are {CHANGE_FEED_MODES}.")

        if mode == 'AllVersionsAndDeletes':
            if "partition_key_range_id" in keyword_arguments:
                raise ValueError(
                    "'AllVersionsAndDeletes' mode is not supported if 'partition_key_range_id'"
                    " was used. Please use 'feed_range' instead.")
            if ("is_start_from_beginning" in keyword_arguments
                    and keyword_arguments["is_start_from_beginning"] is not False):
                raise ValueError(
                    "'AllVersionsAndDeletes' mode is only supported if 'is_start_from_beginning'"
                    " is 'False'. Please use 'is_start_from_beginning=False' or 'continuation' instead.")
            if "start_time" in keyword_arguments and keyword_arguments["start_time"] != "Now":
                raise ValueError(
                    "'AllVersionsAndDeletes' mode is only supported if 'start_time' is 'Now'."
                    " Please use 'start_time=\"Now\"' or 'continuation' instead.")

    if "partition_key_range_id" in keyword_arguments:
        warnings.warn(
            "'partition_key_range_id' is deprecated. Please pass in 'feed_range' instead.",
            DeprecationWarning
        )

    if "is_start_from_beginning" in keyword_arguments:
        warnings.warn(
            "'is_start_from_beginning' is deprecated. Please pass in 'start_time' instead.",
            DeprecationWarning
        )

        if not isinstance(keyword_arguments["is_start_from_beginning"], bool):
            raise TypeError(
                f"'is_start_from_beginning' must be 'bool' type,"
                f" but given '{type(keyword_arguments['is_start_from_beginning']).__name__}'.")

        if keyword_arguments["is_start_from_beginning"] is True and "start_time" in keyword_arguments:
            raise ValueError("'is_start_from_beginning' and 'start_time' are exclusive, please only set one of them.")

    if "start_time" in keyword_arguments:
        if not isinstance(keyword_arguments['start_time'], datetime):
            if keyword_arguments['start_time'].lower() not in ["now", "beginning"]:
                raise ValueError(
                    f"'start_time' must be either 'Now' or 'Beginning', but given '{keyword_arguments['start_time']}'.")
