# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING
from datetime import datetime
from dateutil.parser import parse
from msrest.serialization import TZ_UTC
try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union, Tuple


# cSpell:ignore tzinfos
def _convert_str_to_datetime(
        datetime_as_str,  # type: str
        **kwargs,  # type: Any
):
    #  type: (...) -> datetime
    dt = parse(datetime_as_str, tzinfos = [TZ_UTC])
    return dt
