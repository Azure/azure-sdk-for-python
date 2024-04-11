from promptflow import tool
from typing import List
import numpy as np
import constants
from utils import get_harm_severity_level


# The inputs section will change based on the
# arguments of the tool function, after you save the code
# Adding type to arguments and return value will help
# the system show the types properly
# Please update the function name/signature per need
@tool
def format_service_output(parsed_responses: List[List[dict]]) -> dict:
    supported_metrics = constants.Metric.CONTENT_HARM_METRICS

    result = {}
    if parsed_responses:
        parsed_response = parsed_responses[0]
        for metric_dict in parsed_response:
            for key in metric_dict.keys():
                if key != "reasoning":
                    try:
                        harm_score = int(metric_dict[key])
                    except Exception:
                        harm_score = np.nan
                    result[key + "_score"] = harm_score
                    harm_severity_level = get_harm_severity_level(harm_score)
                    result[key + "_reason"] = metric_dict["reasoning"]
                    result[key] = harm_severity_level
    for metric_name in supported_metrics:
        if metric_name not in result:
            result[metric_name] = np.nan
            result[metric_name + "_score"] = np.nan
            result[metric_name + "_reason"] = np.nan
    return result
