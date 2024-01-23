# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import json5 as json
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

DEFAULT_INDENT = 2


class Encoding(Enum):
    JSON = 'json'
    XML = 'xml'


def encode_example(
    example: Dict[str, Any],
    encoding: Encoding = Encoding.JSON,
    indent: Optional[int] = DEFAULT_INDENT
) -> str:
    '''
    Encode examples into an encoding format.

    Args:
        example (Dict[str, Any]): example to encode
        encoding (Encoding): encoding format to use
        key_order (Optional[List[str]]): ordering of keys printed to string
        indent (Optional[int]): number of spaces to indent JSON output
    Returns:
        str: encoded example
    '''
    if encoding.value == Encoding.JSON.value:
        # Dump JSON with keys double-quoted and final comma removed
        return json.dumps(example, indent=indent, quote_keys=True, trailing_commas=False)
    elif encoding.value == Encoding.XML.value:
        raise NotImplementedError('XML encoding not implemented.')
    else:
        raise ValueError(f'Unknown encoding {encoding} ({type(encoding)}).')
