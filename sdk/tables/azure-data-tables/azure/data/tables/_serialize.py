# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from binascii import hexlify
from typing import Dict, Optional, Union
from uuid import UUID
from datetime import datetime

from azure.core import MatchConditions

from ._common_conversion import _to_utc_datetime


def _get_match_condition(etag, match_condition):
    if match_condition == MatchConditions.IfNotModified:
        if not etag:
            raise ValueError("IfNotModified must be specified with etag.")
        return match_condition
    if match_condition == MatchConditions.Unconditionally:
        if etag:
            raise ValueError("Etag is not supported for an Unconditional operation.")
        return MatchConditions.IfPresent
    raise ValueError(f"Unsupported match condition: {match_condition}")


def _parameter_filter_substitution(parameters: Optional[Dict[str, str]], query_filter: str) -> str:
    """Replace user defined parameters in filter.

    :param parameters: User defined parameters
    :type parameters: dict[str, str]
    :param str query_filter: Filter for querying
    :return: A query filter replaced by user defined parameters.
    :rtype: str
    """
    if parameters:
        filter_strings = query_filter.split(" ")
        for index, word in enumerate(filter_strings):
            if word[0] == "@":
                val = parameters[word[1:]]
                if val in [True, False]:
                    filter_strings[index] = str(val).lower()
                elif isinstance(val, (float)):
                    filter_strings[index] = str(val)
                elif isinstance(val, int):
                    if val.bit_length() <= 32:
                        filter_strings[index] = str(val)
                    else:
                        filter_strings[index] = f"{str(val)}L"
                elif isinstance(val, datetime):
                    filter_strings[index] = f"datetime'{_to_utc_datetime(val)}'"
                elif isinstance(val, UUID):
                    filter_strings[index] = f"guid'{str(val)}'"
                elif isinstance(val, bytes):
                    v = str(hexlify(val))
                    v = v[2:-1]  # Python 3 adds a 'b' and quotations
                    filter_strings[index] = f"X'{v}'"
                else:
                    val = val.replace("'", "''")
                    filter_strings[index] = f"'{val}'"
        return " ".join(filter_strings)
    return query_filter


def serialize_iso(attr: Optional[Union[str, datetime]]) -> Optional[str]:
    """Serialize Datetime object into ISO-8601 formatted string.

    :param attr: Object to be serialized.
    :type attr: str or ~datetime.datetime or None
    :return: A ISO-8601 formatted string or None
    :rtype: str or None
    :raises ValueError: When unable to serialize the input object.
    :raises TypeError: When ISO-8601 object is an invalid datetime object.
    """
    if not attr:
        return None
    if isinstance(attr, str):
        # Pass a string through unaltered
        return attr
    try:
        utc = attr.utctimetuple()
        if utc.tm_year > 9999 or utc.tm_year < 1:
            raise OverflowError("Hit max or min date")

        date = f"{utc.tm_year:04}-{utc.tm_mon:02}-{utc.tm_mday:02}T{utc.tm_hour:02}:{utc.tm_min:02}:{utc.tm_sec:02}"
        return date + "Z"
    except (ValueError, OverflowError) as err:
        raise ValueError("Unable to serialize datetime object.") from err
    except AttributeError as err:
        raise TypeError("ISO-8601 object must be valid datetime object.") from err
