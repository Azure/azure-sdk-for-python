# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import re
from json import JSONDecodeError

import numpy as np

LOGGER = logging.getLogger(__name__)


class ScoreReasonParser(object):

    @staticmethod
    def parse(value, metric):
        try:
            value_json = json.loads(value)
            score = value_json.get("score")
            reason = value_json.get("reason")
        except JSONDecodeError as json_parse_error:
            LOGGER.debug(
                f"Error parsing metric {metric.name} value as returned json from LLM is not a valid json : {value}")
            if score is not None:
                reason = f"Error parsing reason. Output from LLM : {value}"
            if score is None:
                score = np.NaN
                reason = f"Error parsing LLM response. Output from LLM : {value}"
        except Exception as ex:
            score = np.NaN
            reason = str(value)

        return {metric.name: score, f"{metric.name}_reason": reason}


class ScoreParser(object):
    @staticmethod
    def parse(value, metric):
        try:
            match = re.search(r'\d', value)
            if match:
                score = match.group()
            score = float(score)
        except Exception as ex:
            score = np.NaN

        return {metric.name: score}