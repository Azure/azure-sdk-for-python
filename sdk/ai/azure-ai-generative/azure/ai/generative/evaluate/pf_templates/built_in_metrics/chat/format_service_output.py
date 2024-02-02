from promptflow import tool
from typing import List
import numpy as np
import constants

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def format_service_output(parsed_responses: List[List[dict]]) -> dict:
    supported_metrics = constants.CONTENT_HARM_METRICS

    result = {}
    if parsed_responses:
        parsed_response = parsed_responses[0]
        for metric_dict in parsed_response:
            for key in metric_dict.keys():
                if key != "reasoning":
                    result[key] = metric_dict[key]
                    metric_name = key
                    result[key + "_reasoning"] = metric_dict["reasoning"]
    for metric_name in supported_metrics:
        if metric_name not in result:
            print(metric_name)
            result[metric_name] = np.nan
            result[metric_name + "_reasoning"] = np.nan
    return result
    #return parsed_response