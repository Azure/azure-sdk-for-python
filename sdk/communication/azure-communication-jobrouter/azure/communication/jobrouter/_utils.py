# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING
from email.utils import parsedate_to_datetime, format_datetime

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union
    from datetime import datetime


def _to_imf_date(
        value  # Union[str, datetime]
):
    # type: (...) -> str
    """Converts value to IMF datetime format timestamp

    :param
    """
    if isinstance(value, str):
        value = format_datetime(parsedate_to_datetime(value), True)
    elif isinstance(value, datetime):
        value = format_datetime(value, True)
    else:
        raise ValueError("Unable to generate IMF-formatted datetime")
    return value
