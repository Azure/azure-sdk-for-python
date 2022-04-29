# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING
from email.utils import parsedate_to_datetime, format_datetime
from uuid import uuid4
from datetime import datetime
from msrest.serialization import TZ_UTC
try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union, Tuple


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


RepeatabilityHeaders = TypedDict(
    'RepeatabilityHeaders',
    repeatability_request_id=str,
    repeatability_first_sent=str
)


def _add_repeatability_headers(
        **kwargs  # type: Any
):
    # type: (...) -> RepeatabilityHeaders
    """Returns repeatability headers if not provided

    """
    repeatability_request_id = kwargs.pop('repeatability_request_id', None)
    if repeatability_request_id is None:
        repeatability_request_id = str(uuid4())

    repeatability_first_sent = kwargs.pop('repeatability_first_sent', None)
    if repeatability_first_sent is None:
        repeatability_first_sent = format_datetime(
            datetime.utcnow().replace(tzinfo = TZ_UTC), True)
    else:
        repeatability_first_sent = _to_imf_date(repeatability_first_sent)

    return RepeatabilityHeaders(
        repeatability_request_id=repeatability_request_id,
        repeatability_first_sent=repeatability_first_sent)
