# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import logging
from typing import Union


LOGGER = logging.getLogger(__name__)


class JsonParser(object):
    @staticmethod
    def parse(value: Union[str, bytes, bytearray]):
        """
        Parse input value as json. Returns empty dict in case value cannot be parsed as valid json

        :keyword value: Value to be parsed.
        :paramtype value: Union[str, bytes, bytearray]
        """
        value_as_json = None
        try:
            value_as_json = json.loads(value)
        except json.JSONDecodeError:
            LOGGER.debug("Error parsing as a valid json : %s", value)

        return value_as_json


class NumberParser(object):
    @staticmethod
    def parse(value):
        value_as_number = None
        try:
            value_as_number = int(value)
        except ValueError:
            LOGGER.debug("Error parsing as a valid number : %s", value)

        return value_as_number
