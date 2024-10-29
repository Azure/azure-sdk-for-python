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

from azure.cosmos._change_feed.change_feed_state import ChangeFeedMode

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
        raise ValueError(f"Too many arguments. Expected: less than 4, but given: {len(args)}")

    if len(args) > 0:
        key_and_types = [
            ('partition_key_range_id', str),
            ('is_start_from_beginning', bool),
            ('continuation', str),
            ('max_item_count', int),
        ]
        for i, value in enumerate(args):
            key, expected_type = key_and_types[i]

            if key in kwargs:
                raise ValueError(f"'{key}' is in both positional and keyword argument list. Please remove one of them.")

            if not isinstance(value, expected_type):
                raise TypeError(f"'{value}' is not of type '{expected_type.__name__}'")
            kwargs[key] = value

def validate_kwargs(
        kwargs: Dict[str, Any]
    ) -> None:
    """Validate keyword arguments(kwargs).
    The values of keyword arguments must match the expect type and conditions. If the conditions do not match,
    errors will be raised with the error messages and possible ways to correct the errors.

    :param kwargs: Keyword arguments to verify for query_items_change_feed API
    :keyword change_feed_mode: Must be one of the values in the Enum, 'ChangeFeedMode'.
        If the value is 'ALL_VERSIONS_AND_DELETES', the following keywords must be in the right condition:
            - 'partition_key_range_id': Cannot be used at any time
            - 'is_start_from_beginning': Must be 'False'
            - 'start_time': Must be "Now"
    :type change_feed_mode: ChangeFeedMode
    :keyword partition_key_range_id: Deprecated Warning.
    :type partition_key_range_id: str
    :keyword is_start_from_beginning: Deprecated Warning. Cannot be used with 'start_time'.
    :type is_start_from_beginning: bool
    :keyword start_time: Must be in supported types.
    :type start_time: Union[~datetime.datetime, Literal["Now", "Beginning"]]
    :type kwargs: dict[str, Any]
    """
    # Filter items with value None
    kwargs = {key: value for key, value in kwargs.items() if value is not None}

    # Validate the keyword arguments
    if "change_feed_mode" in kwargs:
        change_feed_mode = kwargs["change_feed_mode"]
        if change_feed_mode not in ChangeFeedMode:
            raise ValueError(
                f"Invalid change_feed_mode was used: '{kwargs['change_feed_mode']}'."
                f" Supported 'change_feed_modes' are {ChangeFeedMode.to_string()}.")

        if change_feed_mode == ChangeFeedMode.ALL_VERSIONS_AND_DELETES:
            if "partition_key_range_id" in kwargs:
                raise ValueError(
                    f"'{ChangeFeedMode.ALL_VERSIONS_AND_DELETES}' mode is not supported if 'partition_key_range_id'"
                    f" was used. Please use 'feed_range' instead.")
            if "is_start_from_beginning" in kwargs and kwargs["is_start_from_beginning"] != False:
                raise ValueError(
                    f"'{ChangeFeedMode.ALL_VERSIONS_AND_DELETES}' mode is only supported if 'is_start_from_beginning'"
                    f" is 'False'. Please use 'is_start_from_beginning=False' or 'continuation' instead.")
            if "start_time" in kwargs and kwargs["start_time"] != "Now":
                raise ValueError(
                    f"'{ChangeFeedMode.ALL_VERSIONS_AND_DELETES}' mode is only supports if 'start_time' is 'Now'."
                    f" Please use 'start_time=\"Now\"' or 'continuation' instead.")

    if "partition_key_range_id" in kwargs:
        warnings.warn(
            "'partition_key_range_id' is deprecated. Please pass in 'feed_range' instead.",
            DeprecationWarning
        )

    if "is_start_from_beginning" in kwargs:
        warnings.warn(
            "'is_start_from_beginning' is deprecated. Please pass in 'start_time' instead.",
            DeprecationWarning
        )

        if "start_time" in kwargs:
            raise ValueError("'is_start_from_beginning' and 'start_time' are exclusive, please only set one of them.")

        if not isinstance(kwargs["is_start_from_beginning"], bool):
            raise TypeError(
                f"'is_start_from_beginning' must be 'bool' type,"
                f" but given '{type(kwargs["is_start_from_beginning"]).__name__}'.")

    elif "start_time" in kwargs:
        start_time = kwargs['start_time']
        if not isinstance(start_time, datetime) and not isinstance(start_time, str):
            raise TypeError(
                f"'start_time' must be either a 'datetime' or 'str' type, but given '{type(start_time).__name__}'.")

        if isinstance(start_time, str) and start_time not in ["Now", "Beginning"]:
            raise ValueError(f"'start_time' must be either 'Now' or 'Beginning', but given '{start_time}'.")
