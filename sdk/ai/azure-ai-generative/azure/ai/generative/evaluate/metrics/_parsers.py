# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import logging
import re
from json import JSONDecodeError

import numpy as np

LOGGER = logging.getLogger(__name__)


class JsonParser(object):

    @staticmethod
    def parse(value):
        """
        Parse input value as json. Returns empty dict in case value cannot be parsed as valid json
        """
        value_as_json = None
        try:
            value_as_json = json.loads(value)
        except Exception as ex:
            LOGGER.debug(f"Error parsing as a valid json : {value}")

        return value_as_json


class NumberParser(object):
    @staticmethod
    def parse(value):
        value_as_number = None
        try:
            value_as_number = int(value)
        except Exception as ex:
            LOGGER.debug(f"Error parsing as a valid number : {value}")

        return value_as_number